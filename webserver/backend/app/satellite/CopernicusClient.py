import time
from typing import Optional

from fastapi import HTTPException
import requests
from oauthlib.oauth2 import BackendApplicationClient
from requests_oauthlib import OAuth2Session

from app.config import COPERNICUS_CLIENT_ID, COPERNICUS_CLIENT_SECRET

TOKEN_URL = (
    "https://identity.dataspace.copernicus.eu/"
    "auth/realms/CDSE/protocol/openid-connect/token"
)
PROCESS_URL = "https://sh.dataspace.copernicus.eu/api/v1/process"

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


class CopernicusClient:
    _instance: Optional["CopernicusClient"] = None

    def __init__(self):
        self._access_token = None
        self._expires_at = 0.0

    @classmethod
    def get_instance(cls) -> "CopernicusClient":
        if cls._instance is None:
            cls._instance = CopernicusClient()
        return cls._instance

    def _ensure_token(self) -> None:
        if self._access_token and time.time() < self._expires_at - 30:
            return

        client = BackendApplicationClient(client_id=COPERNICUS_CLIENT_ID)
        oauth = OAuth2Session(client=client)

        token = oauth.fetch_token(
            token_url=TOKEN_URL,
            client_secret=COPERNICUS_CLIENT_SECRET,
            include_client_id=True,
        )

        self._access_token = token["access_token"]
        self._expires_at = time.time() + token.get("expires_in", 300)

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
        self._ensure_token()

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
        except requests.HTTPError as error:
            raise HTTPException(
                status_code=502,
                detail=f"Copernicus request failed: {error.response.status_code} {error.response.text}",
            ) from error
        except requests.RequestException as error:
            raise HTTPException(status_code=502, detail=f"Copernicus request failed: {error}") from error

        return response.content