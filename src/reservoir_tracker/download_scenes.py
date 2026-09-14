import os
import requests
from oauthlib.oauth2 import BackendApplicationClient
from requests_oauthlib import OAuth2Session

# Tarnița Reservoir AOI (approximate bounding box)
TARNITA_BBOX = [23.1800, 46.6800, 23.3200, 46.7400]

EVALSCRIPT = """
//VERSION=3
function setup() {
    return {
        input: [{ bands: ["B02", "B03", "B04", "B08", "B11", "B12", "dataMask"], units: "REFLECTANCE" }],
        mosaicking: Mosaicking.ORBIT,
        output: { id: "default", bands: 6, sampleType: "FLOAT32" }
    };
}
function median(v) {
    v.sort((a,b) => a - b);
    var mid = Math.floor(v.length / 2);
    return v.length % 2 === 0 ? (v[mid - 1] + v[mid]) / 2 : v[mid];
}
function evaluatePixel(samples) {
    var b2=[], b3=[], b4=[], b8=[], b11=[], b12=[];
    for (var i=0; i<samples.length; i++) {
        if (samples[i].dataMask == 1) {
            b2.push(samples[i].B02); b3.push(samples[i].B03); b4.push(samples[i].B04);
            b8.push(samples[i].B08); b11.push(samples[i].B11); b12.push(samples[i].B12);
        }
    }
    if (b2.length === 0) return [0,0,0,0,0,0];
    return [median(b2), median(b3), median(b4), median(b8), median(b11), median(b12)];
}
"""

def fetch_composite(client_id, client_secret, time_range, output_path):
    client = BackendApplicationClient(client_id=client_id)
    oauth = OAuth2Session(client=client)
    token = oauth.fetch_token(
        token_url="https://identity.dataspace.copernicus.eu/auth/realms/CDSE/protocol/openid-connect/token",
        client_secret=client_secret,
        include_client_id=True
    )

    headers = {"Content-Type": "application/json", "Authorization": f"Bearer {token['access_token']}"}
    payload = {
        "input": {
            "bounds": {"bbox": TARNITA_BBOX},
            "data": [{
                "type": "sentinel-2-l2a",
                "dataFilter": {"timeRange": time_range, "maxCloudCoverage": 30},
                "processing": {"harmonizeValues": True}
            }]
        },
        "output": {"width": 1100, "height": 600, "responses": [{"identifier": "default", "format": {"type": "image/tiff"}}]},
        "evalscript": EVALSCRIPT
    }

    print(f"Downloading composite for {time_range['from']} to {time_range['to']}...")
    res = requests.post("https://sh.dataspace.copernicus.eu/api/v1/process", headers=headers, json=payload)
    if res.ok:
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        with open(output_path, "wb") as f:
            f.write(res.content)
        print(f"Saved: {output_path}")
    else:
        raise RuntimeError(f"Download failed: {res.text}")

if __name__ == "__main__":
    c_id = input("Copernicus Client ID: ")
    c_secret = input("Copernicus Client Secret: ")
    
    # Scene 1: Spring Baseline (widen window and allow up to 30% cloud filter)
    fetch_composite(
        c_id, 
        c_secret, 
        {"from": "2025-04-01T00:00:00Z", "to": "2025-06-30T23:59:59Z"}, 
        "src/reservoir_tracker/data/t0_spring.tif"
    )
    
    # Scene 2: Late Summer / Early Fall
    fetch_composite(
        c_id, 
        c_secret, 
        {"from": "2025-08-01T00:00:00Z", "to": "2025-09-30T23:59:59Z"}, 
        "src/reservoir_tracker/data/t1_summer.tif"
    )