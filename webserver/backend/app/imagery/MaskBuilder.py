from typing import List, Tuple

import numpy as np
from PIL import Image

from app.ml_engine.EurosatColors import EUROSAT_COLORS


def _hex_to_rgb(hex_color: str) -> Tuple[int, int, int]:
    hex_color = hex_color.lstrip("#")
    return tuple(int(hex_color[i:i + 2], 16) for i in (0, 2, 4))

def build_mask_image(
    predicted_grid: List[List[str]],
    rgb_image: Image.Image,
    tile_px: int = 64,
    alpha: int = 100,
) -> Image.Image:
    rows = len(predicted_grid)
    cols = len(predicted_grid[0]) if rows else 0

    mask = Image.new("RGBA", rgb_image.size, (0, 0, 0, 0))

    mask_array = np.array(mask)

    for row in range(rows):
        for col in range(cols):
            color = _hex_to_rgb(EUROSAT_COLORS[predicted_grid[row][col]])

            y_start = row * tile_px
            y_end = (row + 1) * tile_px
            x_start = col * tile_px
            x_end = (col + 1) * tile_px

            mask_array[y_start:y_end, x_start:x_end, :3] = color
            mask_array[y_start:y_end, x_start:x_end, 3] = alpha

    mask = Image.fromarray(mask_array, "RGBA")

    return Image.alpha_composite(rgb_image.convert("RGBA"), mask)