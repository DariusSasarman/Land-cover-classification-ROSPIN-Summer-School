from collections import deque
from datetime import datetime, timedelta
from io import BytesIO
import threading
import time
from typing import Optional

from fastapi import HTTPException
import numpy as np
import requests
import tifffile
from oauthlib.oauth2 import BackendApplicationClient
from requests_oauthlib import OAuth2Session

from app.config import COPERNICUS_CLIENT_ID, COPERNICUS_CLIENT_SECRET
from app.logger import get_logger


SENTINEL_2_MIN_DATE = datetime(2017, 6, 1)

logger = get_logger("satellite.CopernicusClient")

TOKEN_URL = (
    "https://identity.dataspace.copernicus.eu/"
    "auth/realms/CDSE/protocol/openid-connect/token"
)

PROCESS_URL = "https://sh.dataspace.copernicus.eu/api/v1/process"


_RATE_LIMIT_REQUESTS_PER_MINUTE = 300
_RATE_LIMIT_WINDOW_SECONDS = 60
_RATE_LIMIT_MAX_CONCURRENT = 4

# Retry delays after HTTP 429
_RETRY_DELAYS = [60, 120, 300, 600]

# Reject images where more than 20% of pixels contain no usable data.
_MAX_BLANK_PIXEL_RATIO = 0.20

# If an image is too blank, move forward in time and try again.
#
# Attempts:
#   +0 days
#   +15 days
#   +30 days
#   +45 days
#   +60 days
#   +75 days
#   +90 days
_MAX_TIME_SHIFT_ATTEMPTS = 6
_TIME_SHIFT_STEP_DAYS = 15


EVALSCRIPT = """
//VERSION=3

function setup() {
    return {
        input: [{
            bands: [
                "B01", "B02", "B03", "B04", "B05", "B06", "B07",
                "B08", "B8A", "B09", "B10", "B11", "B12", "dataMask"
            ],
            units: "REFLECTANCE"
        }],
        mosaicking: Mosaicking.ORBIT,
        output: {
            id: "default",
            bands: 13,
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
    var bands = [];
    for (var band = 0; band < 13; band++) {
        bands.push([]);
    }

    for (var i = 0; i < samples.length; i++) {
        if (samples[i].dataMask == 1) {
            bands[0].push(samples[i].B01);
            bands[1].push(samples[i].B02);
            bands[2].push(samples[i].B03);
            bands[3].push(samples[i].B04);
            bands[4].push(samples[i].B05);
            bands[5].push(samples[i].B06);
            bands[6].push(samples[i].B07);
            bands[7].push(samples[i].B08);
            bands[8].push(samples[i].B8A);
            bands[9].push(samples[i].B09);
            bands[10].push(samples[i].B10);
            bands[11].push(samples[i].B11);
            bands[12].push(samples[i].B12);
        }
    }

    if (bands[0].length == 0) {
        return [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0];
    }

    var result = [];
    for (var j = 0; j < 13; j++) {
        result.push(median(bands[j]));
    }
    return result;
}
"""


def _shift_iso(iso_str: str, days: int) -> str:
    """
    Shift an ISO-8601 timestamp forward by a number of days while
    preserving whether the original string used a trailing Z.
    """
    has_z = iso_str.endswith("Z")

    dt = datetime.fromisoformat(
        iso_str.replace("Z", "+00:00")
    )

    shifted = dt + timedelta(days=days)

    return shifted.strftime("%Y-%m-%dT%H:%M:%S") + (
        "Z" if has_z else ""
    )


def _blank_pixel_ratio(content: bytes) -> float:
    """
    Return the fraction of pixels where every output band is zero.

    The evalscript returns zero for pixels where dataMask == 0, so
    these pixels represent no usable imagery.
    """

    try:
        array = tifffile.imread(BytesIO(content))

    except Exception as error:
        logger.warning(
            "Could not decode GeoTIFF for blank check: %s",
            error,
        )

        # Do not reject an otherwise valid response merely because
        # validation failed.
        return 0.0

    if array.ndim != 3:
        logger.warning(
            "Unexpected GeoTIFF shape for blank check: %s",
            array.shape,
        )
        return 0.0

    if array.shape[0] == 13 and array.shape[-1] != 13:
        array = np.moveaxis(array, 0, -1)

    # Expected shape is (H, W, 13).
    if array.shape[-1] != 13:
        logger.warning(
            "Unexpected number of GeoTIFF bands: %s",
            array.shape,
        )
        return 0.0

    blank_mask = np.all(array == 0, axis=-1)

    total_pixels = blank_mask.size

    if total_pixels == 0:
        return 0.0

    return float(
        np.count_nonzero(blank_mask)
    ) / total_pixels


class _SlidingWindowRateLimiter:
    def __init__(
        self,
        max_calls: int,
        window_seconds: float,
    ) -> None:
        self._max_calls = max_calls
        self._window = window_seconds
        self._timestamps: deque = deque()
        self._lock = threading.Lock()

    def acquire(self) -> None:
        while True:
            with self._lock:
                now = time.monotonic()

                while (
                    self._timestamps
                    and now - self._timestamps[0] >= self._window
                ):
                    self._timestamps.popleft()

                if len(self._timestamps) < self._max_calls:
                    self._timestamps.append(now)
                    return

                wait_until = (
                    self._timestamps[0] + self._window
                )

                sleep_for = wait_until - now

            logger.debug(
                "Copernicus rate limit reached (%d req/%ds). "
                "Waiting %.2fs before next request.",
                self._max_calls,
                self._window,
                sleep_for,
            )

            time.sleep(max(sleep_for, 0.05))


class CopernicusClient:
    _instance: Optional["CopernicusClient"] = None

    def __init__(self):
        self._access_token = None
        self._expires_at = 0.0

        self._rate_limiter = _SlidingWindowRateLimiter(
            max_calls=_RATE_LIMIT_REQUESTS_PER_MINUTE,
            window_seconds=_RATE_LIMIT_WINDOW_SECONDS,
        )

        self._concurrency = threading.Semaphore(
            _RATE_LIMIT_MAX_CONCURRENT
        )

        self._429_count = 0
        self._429_lock = threading.Lock()

    @classmethod
    def get_instance(cls) -> "CopernicusClient":
        if cls._instance is None:
            cls._instance = CopernicusClient()

        return cls._instance

    def _ensure_token(self) -> None:
        if (
            self._access_token
            and time.time() < self._expires_at - 30
        ):
            return

        logger.info(
            "Requesting OAuth token from Copernicus Dataspace CDSE..."
        )

        client = BackendApplicationClient(
            client_id=COPERNICUS_CLIENT_ID
        )

        oauth = OAuth2Session(client=client)

        token = oauth.fetch_token(
            token_url=TOKEN_URL,
            client_secret=COPERNICUS_CLIENT_SECRET,
            include_client_id=True,
        )

        self._access_token = token["access_token"]

        expires_in = token.get("expires_in", 300)

        self._expires_at = time.time() + expires_in

        logger.info(
            "Copernicus OAuth token acquired successfully "
            "(valid for %ds)",
            expires_in,
        )

    def _handle_rate_limit(self) -> None:
        with self._429_lock:
            self._429_count += 1

            retry_number = self._429_count

            delay_index = min(
                retry_number - 1,
                len(_RETRY_DELAYS) - 1,
            )

            delay = _RETRY_DELAYS[delay_index]

        logger.warning(
            "Copernicus rate limit hit (429 #%d). "
            "Waiting %ds before retrying.",
            retry_number,
            delay,
        )

        time.sleep(delay)

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
        """
        Fetch a GeoTIFF from Copernicus.

        If the returned image contains more than
        _MAX_BLANK_PIXEL_RATIO blank pixels, the requested
        time window is shifted forward by 15 days and retried.

        The search continues for up to 90 days.
        """

        requested_date = datetime.fromisoformat(
            time_from.replace("Z", "+00:00")
        )

        requested_to = datetime.fromisoformat(
            time_to.replace("Z", "+00:00")
        )

        # Compare against the current date dynamically rather than
        # using a datetime captured when the module was imported.
        now = datetime.now(
            tz=requested_date.tzinfo
        )

        if (
            requested_date.replace(tzinfo=None)
            < SENTINEL_2_MIN_DATE
        ):
            raise HTTPException(
                status_code=400,
                detail=(
                    "Sentinel-2 imagery is not available "
                    "before June 23, 2015."
                ),
            )

        if requested_date > now:
            raise HTTPException(
                status_code=400,
                detail=(
                    "Sentinel-2 imagery cannot be requested "
                    "from the future."
                ),
            )

        original_duration = requested_to - requested_date

        last_ratio = 0.0

        for attempt in range(
            _MAX_TIME_SHIFT_ATTEMPTS + 1
        ):
            offset_days = (
                attempt * _TIME_SHIFT_STEP_DAYS
            )

            shifted_from = _shift_iso(
                time_from,
                offset_days,
            )

            shifted_to = _shift_iso(
                time_to,
                offset_days,
            )

            shifted_date = datetime.fromisoformat(
                shifted_from.replace("Z", "+00:00")
            )

            now = datetime.now(
                tz=shifted_date.tzinfo
            )

            if shifted_date > now:
                logger.warning(
                    "Reached present date while searching for "
                    "usable imagery; stopping time-shift search."
                )
                break

            logger.info(
                "Trying Sentinel-2 imagery: "
                "%s to %s (fallback +%dd)",
                shifted_from,
                shifted_to,
                offset_days,
            )

            content = self._fetch_once(
                west=west,
                south=south,
                east=east,
                north=north,
                width=width,
                height=height,
                time_from=shifted_from,
                time_to=shifted_to,
                max_cloud_coverage=max_cloud_coverage,
            )

            blank_ratio = _blank_pixel_ratio(content)

            last_ratio = blank_ratio

            if (
                blank_ratio
                <= _MAX_BLANK_PIXEL_RATIO
            ):
                if attempt > 0:
                    logger.info(
                        "Usable image found after shifting "
                        "+%d days (blank ratio: %.1f%%)",
                        offset_days,
                        blank_ratio * 100,
                    )

                return content

            logger.warning(
                "Image %.1f%% blank/clouded "
                "(threshold %.0f%%) for %s to %s. "
                "Shifting forward %d days and retrying.",
                blank_ratio * 100,
                _MAX_BLANK_PIXEL_RATIO * 100,
                shifted_from,
                shifted_to,
                _TIME_SHIFT_STEP_DAYS,
            )

        logger.error(
            "No usable Sentinel-2 imagery found within "
            "the searched time range."
        )

        raise HTTPException(
            status_code=404,
            detail=(
                "No usable Sentinel-2 imagery was found "
                "for the requested date or within the "
                "90-day forward search window. "
                f"Last result was "
                f"{last_ratio * 100:.1f}% blank/clouded."
            ),
        )

    def _fetch_once(
        self,
        west: float,
        south: float,
        east: float,
        north: float,
        width: int,
        height: int,
        time_from: str,
        time_to: str,
        max_cloud_coverage: int,
    ) -> bytes:

        self._rate_limiter.acquire()

        with self._concurrency:
            self._ensure_token()

            logger.info(
                "Fetching GeoTIFF from Copernicus API: "
                "bbox=[%.4f, %.4f, %.4f, %.4f], "
                "size=%dx%d, time=%s to %s, max_cloud=%d%%",
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
                    "bounds": {
                        "bbox": [
                            west,
                            south,
                            east,
                            north,
                        ]
                    },
                    "data": [
                        {
                            # L1C exposes all 13 bands, including B10.
                            "type": "sentinel-2-l1c",
                            "dataFilter": {
                                "timeRange": {
                                    "from": time_from,
                                    "to": time_to,
                                },
                                "maxCloudCoverage": (
                                    max_cloud_coverage
                                ),
                            },
                            "processing": {
                                "harmonizeValues": True
                            },
                        }
                    ],
                },
                "output": {
                    "width": width,
                    "height": height,
                    "responses": [
                        {
                            "identifier": "default",
                            "format": {
                                "type": "image/tiff"
                            },
                        }
                    ],
                },
                "evalscript": EVALSCRIPT,
            }

            max_attempts = len(_RETRY_DELAYS) + 1

            for attempt in range(
                1,
                max_attempts + 1,
            ):
                try:
                    response = requests.post(
                        PROCESS_URL,
                        headers={
                            "Content-Type": (
                                "application/json"
                            ),
                            "Authorization": (
                                f"Bearer "
                                f"{self._access_token}"
                            ),
                        },
                        json=payload,
                    )

                    if response.status_code == 429:
                        if attempt >= max_attempts:
                            logger.error(
                                "Copernicus rate limit persisted "
                                "after %d attempts.",
                                attempt,
                            )

                            response.raise_for_status()

                        self._handle_rate_limit()
                        continue

                    response.raise_for_status()

                    with self._429_lock:
                        self._429_count = 0

                    logger.info(
                        "Received GeoTIFF from Copernicus "
                        "(bytes length: %d)",
                        len(response.content),
                    )

                    return response.content

                except requests.HTTPError as error:
                    logger.error(
                        "Copernicus API HTTP failure: "
                        "status=%s, response=%s",
                        error.response.status_code,
                        error.response.text,
                    )

                    raise HTTPException(
                        status_code=502,
                        detail=(
                            "Copernicus request failed: "
                            f"{error.response.status_code} "
                            f"{error.response.text}"
                        ),
                    ) from error

                except requests.RequestException as error:
                    logger.error(
                        "Copernicus API network exception: %s",
                        error,
                    )

                    raise HTTPException(
                        status_code=502,
                        detail=(
                            f"Copernicus request failed: "
                            f"{error}"
                        ),
                    ) from error

            raise HTTPException(
                status_code=502,
                detail=(
                    "Copernicus request failed after "
                    "all retry attempts."
                ),
            )
