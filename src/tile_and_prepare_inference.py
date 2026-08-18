import rasterio
from rasterio.windows import Window
import numpy as np
import os

os.makedirs("data/processed/tiles", exist_ok=True)

PATCH_SIZE = 64

with rasterio.open("data/raw/sentinel2_aoi.tif") as src:
    width, height = src.width, src.height
    print(f"Image size: {width} x {height}")
    print(f"Number of bands: {src.count}")

    n_cols = width // PATCH_SIZE
    n_rows = height // PATCH_SIZE
    print(f"Grid: {n_rows} rows x {n_cols} cols = {n_rows * n_cols} patches")

    patches = []
    positions = []

    for row in range(n_rows):
        for col in range(n_cols):
            window = Window(col * PATCH_SIZE, row * PATCH_SIZE, PATCH_SIZE, PATCH_SIZE)
            patch = src.read(window=window)  # shape: (bands, 64, 64)
            patches.append(patch)
            positions.append((row, col))

    print(f"Extracted {len(patches)} patches")

    patches_array = np.stack(patches)  # shape: (n_patches, bands, 64, 64)
    np.save("data/processed/tiles/patches.npy", patches_array)
    np.save("data/processed/tiles/positions.npy", np.array(positions))

    rgb_patches = patches_array[:, [2, 1, 0], :, :]
    np.save("data/processed/tiles/patches_rgb.npy", rgb_patches)
    print("RGB patches saved:", rgb_patches.shape)

    meta = {
        "n_rows": n_rows,
        "n_cols": n_cols,
        "patch_size": PATCH_SIZE,
        "transform": src.transform,
        "crs": str(src.crs)
    }
    print("Metadata:", meta)

print("Tiling complete. Patches saved to data/processed/tiles/")