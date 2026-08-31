"""
Downloads and extracts the EuroSAT *multispectral* dataset (13 Sentinel-2
bands per patch, GeoTIFF), which is what makes B08 / B11 / B12 available.

The regular `torchvision.datasets.EuroSAT` used by the rest of this repo
(see src/train_baseline_rf.py, notebooks/CNN_*.ipynb) only ships the
3-band RGB JPEG version - it has no NIR/SWIR bands at all. This script
gets the companion "all bands" release so we can build a real spectral
feature set to compare against the RGB baseline.
"""

import os
import zipfile
import requests

# Maintained copy of the EuroSAT all-bands (MS) release used by TorchGeo.
# The former DFKI mirror now returns HTTP 403.
URL = (
    "https://huggingface.co/datasets/torchgeo/eurosat/resolve/"
    "1ce6f1bfb56db63fd91b6ecc466ea67f2509774c/EuroSATallBands.zip"
)


def download_allbands(target_dir):
    os.makedirs(target_dir, exist_ok=True)
    zip_path = os.path.join(target_dir, "EuroSATallBands.zip")

    if not os.path.exists(zip_path):
        print(f"Downloading {URL} ...")
        with requests.get(
            URL,
            stream=True,
            timeout=60,
            headers={"User-Agent": "land-cover-classification"},
        ) as r:
            r.raise_for_status()
            total = int(r.headers.get("content-length", 0))
            done = 0
            with open(zip_path, "wb") as f:
                for chunk in r.iter_content(chunk_size=1 << 20):
                    f.write(chunk)
                    done += len(chunk)
                    if total:
                        pct = 100 * done / total
                        print(f"\r{done/1e6:.1f}/{total/1e6:.1f} MB ({pct:.1f}%)", end="")
        print("\nDownload complete.")
    else:
        print("Zip already present, skipping download.")

    print("Extracting (this can take a while, ~2-3 GB uncompressed)...")
    with zipfile.ZipFile(zip_path) as z:
        z.extractall(target_dir)

    print(f"Done. Files extracted under: {target_dir}")
    print(
        "train_spectral_rf.py will auto-discover the 10 class folders "
        "(AnnualCrop, Forest, ...) no matter how deep they're nested inside "
        "this directory, so you shouldn't need to move anything."
    )


if __name__ == "__main__":
    # Mirrors the "run from repo root, save under data/raw" convention used
    # by download_model.py / download_sentinel2.py.
    repo_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    target_dir = os.path.join(repo_root, "data", "raw", "EuroSATallBands")
    download_allbands(target_dir)
