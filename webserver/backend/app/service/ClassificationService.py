from collections import Counter
from typing import List

from PIL import Image

from app.model.execution.request.AreaSelection import AreaSelection
from app.model.execution.response.Classification import Classification
from app.imagery.GeoTiffUtils import read_bands, bands_to_rgb, tile_grid
from app.imagery.MaskBuilder import build_mask_image
from app.ml_engine.LandCoverClassifier import LandCoverClassifier
from app.satellite.CopernicusClient import CopernicusClient
from app.storage.ImageStore import save_period_images


def classify_area(
    area_id: str,
    period_id: str,
    period_desc: str,
    period_index: str,
    area: AreaSelection,
    time_from: str,
    time_to: str,
) -> Classification:
    tile_px = area.tile_px

    tiff_bytes = CopernicusClient.get_instance().fetch_geotiff(
        west=area.bbox_lonlat.west,
        south=area.bbox_lonlat.south,
        east=area.bbox_lonlat.east,
        north=area.bbox_lonlat.north,
        width=area.tile_count.x * tile_px,
        height=area.tile_count.y * tile_px,
        time_from=time_from,
        time_to=time_to,
    )

    rgb = bands_to_rgb(read_bands(tiff_bytes))
    tiles = tile_grid(rgb, tile_px=tile_px)

    classifier = LandCoverClassifier.get_instance()
    predicted_grid: List[List[str]] = []
    predictions: List[str] = []

    for row in tiles:
        predicted_row = []
        for tile in row:
            percentages = classifier.classify(tile)
            top_class = max(percentages, key=percentages.get)
            predicted_row.append(top_class)
            predictions.append(top_class)
        predicted_grid.append(predicted_row)

    total = len(predictions) or 1
    area_percentages = {
        class_id: round((count / total) * 100, 1)
        for class_id, count in Counter(predictions).items()
    }

    rgb_image = Image.fromarray(rgb)

    rgb_url, mask_url = save_period_images(
        area_id, period_id, rgb_image, build_mask_image(predicted_grid,rgb_image, tile_px)
    )

    return Classification(
        index=period_index,
        period_desc=period_desc,
        Percentages={class_id: f"{pct}%" for class_id, pct in area_percentages.items()},
        RGB_IMAGE=rgb_url,
        Masked_IMAGE=mask_url,
    )