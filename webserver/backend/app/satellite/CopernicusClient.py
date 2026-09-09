from collections import deque
from datetime import datetime
import threading
import time
from typing import Optional

from fastapi import HTTPException
import requests
from oauthlib.oauth2 import BackendApplicationClient
from requests_oauthlib import OAuth2Session

from app.config import COPERNICUS_CLIENT_ID, COPERNICUS_CLIENT_SECRET
from app.logger import get_logger

SENTINEL_2_MIN_DATE = datetime(2015, 6, 23)
    
logger = get_logger("satellite.CopernicusClient")

TOKEN_URL = (
    "https://identity.dataspace.copernicus.eu/"
    "auth/realms/CDSE/protocol/openid-connect/token"
)
PROCESS_URL = "https://sh.dataspace.copernicus.eu/api/v1/process"

# ---------------------------------------------------------------------------
# Copernicus Dataspace quota limits for Copernicus General Users
# Source: https://documentation.dataspace.copernicus.eu/Quotas.html
#
# Sentinel Hub APIs column (the Process API used here):
#   - Requests per minute  : 300
#   - PU per minute        : 300
#   - Requests per month   : 10 000
#   - PU per month         : 10 000
#
# IAD (Immediately Available Data):
#   - Concurrent connections: 4
# ---------------------------------------------------------------------------
_RATE_LIMIT_REQUESTS_PER_MINUTE = 300   # Sentinel Hub: requests/min
_RATE_LIMIT_WINDOW_SECONDS      = 60    # sliding window length
_RATE_LIMIT_MAX_CONCURRENT      = 4     # IAD concurrent connections

EVALSCRIPT = """
//VERSION=3

function setup() {
    return {
        input: [{
            bands: ["B02", "B03", "B04", "B08", "B11", "B12", "dataMask"],
            units: "REFLECTANCE"
        }],
        mosaicking: Mosaicking.ORBIT,
        output: {
            id: "default",
            bands: 6,
            sampleType: "FLOAT32"
        }
    };
}

function median(values) {
    values.sort(function(a, b) { return a - b; });
    var middle = Math.floor(values.length / 2);
    if (values.length % 2 === 0) {
        return (values[middle - 1] + values[middle]) / 2;
    }
    return values[middle];
}

function evaluatePixel(samples) {
    var B02 = [], B03 = [], B04 = [], B08 = [], B11 = [], B12 = [];
    for (var i = 0; i < samples.length; i++) {
        if (samples[i].dataMask == 1) {
            B02.push(samples[i].B02);
            B03.push(samples[i].B03);
            B04.push(samples[i].B04);
            B08.push(samples[i].B08);
            B11.push(samples[i].B11);
            B12.push(samples[i].B12);
        }
    }
    if (B02.length == 0) {
        return [0, 0, 0, 0, 0, 0];
    }
    return [median(B02), median(B03), median(B04), median(B08), median(B11), median(B12)];
}
"""


class _SlidingWindowRateLimiter:
    """
    Thread-safe sliding-window rate limiter.

    Keeps a deque of timestamps for recent calls within `window_seconds`.
    If the deque is at capacity, the caller sleeps until the oldest call
    has aged out of the window before proceeding.
    """

    def __init__(self, max_calls: int, window_seconds: float) -> None:
        self._max_calls = max_calls
        self._window = window_seconds
        self._timestamps: deque = deque()
        self._lock = threading.Lock()

    def acquire(self) -> None:
        """Block until a request slot is available, then mark it as taken."""
        while True:
            with self._lock:
                now = time.monotonic()
                # Evict timestamps outside the current window
                while self._timestamps and now - self._timestamps[0] >= self._window:
                    self._timestamps.popleft()

                if len(self._timestamps) < self._max_calls:
                    self._timestamps.append(now)
                    return  # Slot acquired — proceed immediately

                # Calculate how long to wait until the oldest call expires
                wait_until = self._timestamps[0] + self._window
                sleep_for = wait_until - now

            # Sleep outside the lock so other threads can evict their own timestamps
            logger.debug(
                "Copernicus rate limit reached (%d req/%ds). "
                "Waiting %.2fs before next request.",
                self._max_calls, self._window, sleep_for,
            )
            time.sleep(max(sleep_for, 0.05))


class CopernicusClient:
    _instance: Optional["CopernicusClient"] = None

    def __init__(self):
        self._access_token = None
        self._expires_at = 0.0
        # Rate limiter: 300 requests per 60-second sliding window
        self._rate_limiter = _SlidingWindowRateLimiter(
            max_calls=_RATE_LIMIT_REQUESTS_PER_MINUTE,
            window_seconds=_RATE_LIMIT_WINDOW_SECONDS,
        )
        # Semaphore: max 4 concurrent in-flight requests (IAD limit)
        self._concurrency = threading.Semaphore(_RATE_LIMIT_MAX_CONCURRENT)

    @classmethod
    def get_instance(cls) -> "CopernicusClient":
        if cls._instance is None:
            cls._instance = CopernicusClient()
        return cls._instance

    def _ensure_token(self) -> None:
        if self._access_token and time.time() < self._expires_at - 30:
            return

        logger.info("Requesting OAuth token from Copernicus Dataspace CDSE...")
        client = BackendApplicationClient(client_id=COPERNICUS_CLIENT_ID)
        oauth = OAuth2Session(client=client)

        token = oauth.fetch_token(
            token_url=TOKEN_URL,
            client_secret=COPERNICUS_CLIENT_SECRET,
            include_client_id=True,
        )

        self._access_token = token["access_token"]
        expires_in = token.get("expires_in", 300)
        self._expires_at = time.time() + expires_in
        logger.info("Copernicus OAuth token acquired successfully (valid for %ds)", expires_in)

    def fetch_geotiff(
        self,
        west: float,
        south: float,
        east: float,
        north: float,
        width: int,
        height: int,
        time_from: str,
        time_to: str,
        max_cloud_coverage: int = 20,
    ) -> bytes:
        requested_date = datetime.fromisoformat(time_from.replace("Z", "+00:00"))

        if requested_date.replace(tzinfo=None) < SENTINEL_2_MIN_DATE:
            raise HTTPException(
                status_code=400,
                detail="Sentinel-2 imagery is not available before June 23, 2015.",
            )

        # Enforce rate limit (300 req/min sliding window) before acquiring concurrency slot
        self._rate_limiter.acquire()

        with self._concurrency:
            self._ensure_token()

            logger.info(
                "Fetching GeoTIFF from Copernicus API: bbox=[%.4f, %.4f, %.4f, %.4f], size=%dx%d, time=%s to %s, max_cloud=%d%%",
                west,
                south,
                east,
                north,
                width,
                height,
                time_from,
                time_to,
                max_cloud_coverage,
            )

            payload = {
                "input": {
                    "bounds": {"bbox": [west, south, east, north]},
                    "data": [
                        {
                            "type": "sentinel-2-l2a",
                            "dataFilter": {
                                "timeRange": {"from": time_from, "to": time_to},
                                "maxCloudCoverage": max_cloud_coverage,
                            },
                            "processing": {"harmonizeValues": True},
                        }
                    ],
                },
                "output": {
                    "width": width,
                    "height": height,
                    "responses": [{"identifier": "default", "format": {"type": "image/tiff"}}],
                },
                "evalscript": EVALSCRIPT,
            }

            try:
                response = requests.post(
                    PROCESS_URL,
                    headers={
                        "Content-Type": "application/json",
                        "Authorization": f"Bearer {self._access_token}",
                    },
                    json=payload,
                )
                response.raise_for_status()
                logger.info("Received GeoTIFF from Copernicus (bytes length: %d)", len(response.content))
            except requests.HTTPError as error:
                logger.error(
                    "Copernicus API HTTP failure: status=%s, response=%s",
                    error.response.status_code, error.response.text,
                )
                raise HTTPException(
                    status_code=502,
                    detail=f"Copernicus request failed: {error.response.status_code} {error.response.text}",
                ) from error
            except requests.RequestException as error:
                logger.error("Copernicus API network exception: %s", error)
                raise HTTPException(status_code=502, detail=f"Copernicus request failed: {error}") from error

        return response.content