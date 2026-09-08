import os
from typing import Tuple

from PIL import Image

STATIC_ROOT = os.path.join(os.path.dirname(os.path.dirname(__file__)), "static", "images")


def save_period_images(area_id: str, period_id: str, rgb_image: Image.Image, mask_image: Image.Image) -> Tuple[str, str]:
    area_dir = os.path.join(STATIC_ROOT, area_id)
    os.makedirs(area_dir, exist_ok=True)

    rgb_path = os.path.join(area_dir, f"{period_id}_rgb.png")
    mask_path = os.path.join(area_dir, f"{period_id}_mask.png")

    rgb_image.save(rgb_path)
    mask_image.save(mask_path)

    return f"/images/{area_id}/{period_id}_rgb.png", f"/images/{area_id}/{period_id}_mask.png"