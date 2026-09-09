import io
from typing import List

import numpy as np
import tifffile
from PIL import Image
from app.logger import get_logger

logger = get_logger("imagery.GeoTiffUtils")

RED_BAND_INDEX = 2    # B04
GREEN_BAND_INDEX = 1  # B03
BLUE_BAND_INDEX = 0   # B02

TRUE_COLOR_GAIN = 3.5  # standard Sentinel Hub true-color stretch factor


def read_bands(tiff_bytes: bytes) -> np.ndarray:
    """Returns (height, width, bands) float32 array."""
    array = tifffile.imread(io.BytesIO(tiff_bytes)).astype(np.float32)

    # Some encoders return (bands, height, width) instead — normalize to HWC.
    if array.ndim == 3 and array.shape[0] <= 12 and array.shape[0] < array.shape[-1]:
        array = np.moveaxis(array, 0, -1)

    logger.debug("Read GeoTIFF bands array shape: %s", array.shape)
    return array


def bands_to_rgb(bands: np.ndarray) -> np.ndarray:
    """Converts reflectance bands to an (H, W, 3) uint8 true-color array."""
    rgb = bands[..., [RED_BAND_INDEX, GREEN_BAND_INDEX, BLUE_BAND_INDEX]]
    stretched = np.clip(rgb * TRUE_COLOR_GAIN, 0.0, 1.0)
    rgb_uint8 = (stretched * 255).astype(np.uint8)
    logger.debug("Converted reflectance bands to RGB uint8 array shape: %s", rgb_uint8.shape)
    return rgb_uint8


def tile_grid(rgb: np.ndarray, tile_px: int = 64) -> List[List[Image.Image]]:
    """Splits an (H, W, 3) uint8 array into a row-major grid of tile_px tiles.
    Partial edge tiles are dropped."""
    height, width, _ = rgb.shape
    rows, cols = height // tile_px, width // tile_px
    logger.debug("Splitting %dx%d RGB image into %dx%d tile grid (tile_px=%d, total tiles=%d)", width, height, rows, cols, tile_px, rows * cols)

    grid = []
    for row in range(rows):
        tile_row = []
        for col in range(cols):
            crop = rgb[row * tile_px:(row + 1) * tile_px, col * tile_px:(col + 1) * tile_px]
            tile_row.append(Image.fromarray(crop))
        grid.append(tile_row)
    return grid