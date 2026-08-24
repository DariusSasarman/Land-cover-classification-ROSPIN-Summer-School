from oauthlib.oauth2 import BackendApplicationClient
from requests_oauthlib import OAuth2Session
import os
import requests

# ============================================================
# 1. COPERNICUS DATA SPACE AUTHENTICATION
# ============================================================

print("Please enter your Copernicus OAuth client credentials.")
print(
    "You can obtain them at:"
    "\nhttps://shapps.dataspace.copernicus.eu/dashboard/#/account/settings\n"
)
print('By accessing "Create OAuth client".\n')
print(
    "Tutorial:"
    "\nhttps://documentation.dataspace.copernicus.eu/APIs/SentinelHub/Overview/Authentication.html\n"
)

client_id = input("Client ID: ")
client_secret = input("Client Secret: ")

client = BackendApplicationClient(client_id=client_id)

oauth = OAuth2Session(client=client)

token = oauth.fetch_token(
    token_url=(
        "https://identity.dataspace.copernicus.eu/"
        "auth/realms/CDSE/protocol/openid-connect/token"
    ),
    client_secret=client_secret,
    include_client_id=True
)

access_token = token["access_token"]
print("Successfully authenticated with Copernicus Data Space.")

# ============================================================
# 2. AREA OF INTEREST
# ============================================================

lat_min, lat_max = 46.743444, 46.800056
lon_min, lon_max = 23.530639, 23.706639

bbox = [
    lon_min,
    lat_min,
    lon_max,
    lat_max
]

print(f"Area of interest :{bbox}")

# ============================================================
# 3. PROCESS API
# ============================================================

url = "https://sh.dataspace.copernicus.eu/api/v1/process"

headers = {
    "Content-Type": "application/json",
    "Authorization": f"Bearer {access_token}"
}


# ============================================================
# 4. EVALSCRIPT
#
# Equivalent to:
#
# collection.median()
#
# We request all observations in the requested time range
# using ORBIT mosaicking and calculate the median for every
# output pixel.
# ============================================================

evalscript = """
//VERSION=3

function setup() {
    return {
        input: [{
            bands: [
                "B02",
                "B03",
                "B04",
                "B08",
                "B11",
                "B12",
                "dataMask"
            ],
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
    values.sort(function(a, b) {
        return a - b;
    });
    var middle = Math.floor(values.length / 2);
    if (values.length % 2 === 0) {
        return (
            values[middle - 1] +
            values[middle]
        ) / 2;
    }
    return values[middle];
}


function evaluatePixel(samples) {
    var B02 = [];
    var B03 = [];
    var B04 = [];
    var B08 = [];
    var B11 = [];
    var B12 = [];
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

    // No valid observations for this pixel.
    if (B02.length == 0) {
        return [0, 0, 0, 0, 0, 0];
    }

    return [
        median(B02),
        median(B03),
        median(B04),
        median(B08),
        median(B11),
        median(B12)
    ];
}
"""


# ============================================================
# 5. REQUEST
# ============================================================

data = {
    "input": {
        "bounds": {
            "bbox": bbox
        },
        "data": [
            {
                "type": "sentinel-2-l2a",
                "dataFilter": {
                    "timeRange": {
                        "from": "2025-06-01T00:00:00Z",
                        "to": "2025-08-31T23:59:59Z"
                    },
                    "maxCloudCoverage": 20
                },
                "processing": {
                    "harmonizeValues": True
                }
            }
        ]
    },
    "output": {
        # Approximately 10 m output.
        #
        # The AOI is roughly 13.6 km wide and 6.3 km high,
        # therefore approximately:
        #
        # width  ~= 13600 / 10 = 1360
        # height ~=  6300 / 10 =  630
        #
        # Using explicit dimensions gives us a predictable
        # raster covering the requested AOI.
        "width": 1360,
        "height": 630,
        "responses": [
            {
                "identifier": "default",
                "format": {
                    "type": "image/tiff"
                }
            }
        ]
    },
    "evalscript": evalscript
}


# ============================================================
# 6. SEND REQUEST
# ============================================================

print("Requesting Sentinel-2 data...")

response = requests.post(
    url,
    headers=headers,
    json=data
)


# ============================================================
# 7. SAVE RESULT
# ============================================================

print("HTTP status:", response.status_code)


if response.ok:

    # Suppose it's ran from /src
    output_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), "../data/raw/sentinel2_aoi.tif")
    os.makedirs(os.path.dirname(output_file), exist_ok=True)

    with open(output_file, "wb") as file:
        file.write(response.content)

    print()
    print("Sentinel-2 export completed successfully.")
    print(f"Output: {output_file}")
    print(
        f"Size: "
        f"{len(response.content) / (1024 * 1024):.2f} MB"
    )
else:
    print()
    print("Sentinel-2 request failed.")
    print(response.text)