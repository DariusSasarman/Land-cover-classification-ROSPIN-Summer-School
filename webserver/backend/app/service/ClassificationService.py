from collections import Counter
from typing import List

import numpy as np
from PIL import Image

from app.model.execution.request.AreaSelection import AreaSelection
from app.model.execution.response.Classification import Classification
from app.imagery.GeoTiffUtils import read_bands, bands_to_rgb, tile_grid
from app.imagery.MaskBuilder import build_mask_image
from app.ml_engine.LandCoverClassifier import LandCoverClassifier
from app.satellite.CopernicusClient import CopernicusClient
from app.storage.ImageStore import save_period_images
from app.logger import get_logger

logger = get_logger("service.ClassificationService")

# Copernicus Process API caps output width/height at 2500px per request.
MAX_REQUEST_DIM = 2500


def _max_tiles_per_chunk(tile_px: int) -> int:
    return max(1, MAX_REQUEST_DIM // tile_px)


def _chunk_ranges(total_tiles: int, max_tiles: int):
    """Splits total_tiles into (start_tile, tile_count) chunks of at most max_tiles."""
    ranges = []
    start = 0
    while start < total_tiles:
        count = min(max_tiles, total_tiles - start)
        ranges.append((start, count))
        start += count
    return ranges


def _fetch_bands_mosaic(area: AreaSelection, time_from: str, time_to: str) -> np.ndarray:
    """
    Fetches all Sentinel-2 bands for the full AOI, splitting into multiple Copernicus
    requests and stitching them into one mosaic when the AOI exceeds the
    Process API's per-request pixel dimension limit.
    """
    tile_px = area.tile_px
    width_px = area.tile_count.x * tile_px
    height_px = area.tile_count.y * tile_px

    max_tiles = _max_tiles_per_chunk(tile_px)
    x_chunks = _chunk_ranges(area.tile_count.x, max_tiles)
    y_chunks = _chunk_ranges(area.tile_count.y, max_tiles)

    if len(x_chunks) == 1 and len(y_chunks) == 1:
        tiff_bytes = CopernicusClient.get_instance().fetch_geotiff(
            west=area.bbox_lonlat.west,
            south=area.bbox_lonlat.south,
            east=area.bbox_lonlat.east,
            north=area.bbox_lonlat.north,
            width=width_px,
            height=height_px,
            time_from=time_from,
            time_to=time_to,
        )
        return read_bands(tiff_bytes)

    logger.info(
        "AOI %dx%d px exceeds Copernicus %dpx limit, splitting into %dx%d chunk grid (%d requests)...",
        width_px, height_px, MAX_REQUEST_DIM, len(x_chunks), len(y_chunks), len(x_chunks) * len(y_chunks),
    )

    west, east = area.bbox_lonlat.west, area.bbox_lonlat.east
    north, south = area.bbox_lonlat.north, area.bbox_lonlat.south
    lon_span = east - west
    lat_span = north - south

    mosaic = np.zeros((height_px, width_px, 13), dtype=np.float32)

    for y_start_tile, y_count_tile in y_chunks:
        y0, y1 = y_start_tile * tile_px, (y_start_tile + y_count_tile) * tile_px
        chunk_north = north - (y0 / height_px) * lat_span
        chunk_south = north - (y1 / height_px) * lat_span

        for x_start_tile, x_count_tile in x_chunks:
            x0, x1 = x_start_tile * tile_px, (x_start_tile + x_count_tile) * tile_px
            chunk_west = west + (x0 / width_px) * lon_span
            chunk_east = west + (x1 / width_px) * lon_span

            logger.info(
                "Fetching chunk cols[%d:%d] rows[%d:%d] (%dx%d px)...",
                x0, x1, y0, y1, x1 - x0, y1 - y0,
            )
            tiff_bytes = CopernicusClient.get_instance().fetch_geotiff(
                west=chunk_west,
                south=chunk_south,
                east=chunk_east,
                north=chunk_north,
                width=x1 - x0,
                height=y1 - y0,
                time_from=time_from,
                time_to=time_to,
            )
            mosaic[y0:y1, x0:x1, :] = read_bands(tiff_bytes)

    return mosaic


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
    width_px = area.tile_count.x * tile_px
    height_px = area.tile_count.y * tile_px

    logger.info(
        "Classifying area '%s' (period '%s'): requesting GeoTIFF %dx%d (%d tiles x %d tiles)...",
        area_id,
        period_id,
        width_px,
        height_px,
        area.tile_count.x,
        area.tile_count.y,
    )

    bands = _fetch_bands_mosaic(area, time_from, time_to)
    rgb = bands_to_rgb(bands)
    tiles = tile_grid(bands, tile_px=tile_px)

    classifier = LandCoverClassifier.get_instance()
    predicted_grid: List[List[str]] = []
    predictions: List[str] = []

    logger.info("Running ML inference over %d grid tiles...", area.tile_count.x * area.tile_count.y)
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
    logger.info("Class distribution for area '%s' (period '%s'): %s", area_id, period_id, area_percentages)

    rgb_image = Image.fromarray(rgb)

    rgb_url, mask_url = save_period_images(
        area_id, period_id, rgb_image, build_mask_image(predicted_grid, rgb_image, tile_px)
    )

    return Classification(
        index=period_index,
        period_desc=period_desc,
        Percentages={class_id: f"{pct}%" for class_id, pct in area_percentages.items()},
        RGB_IMAGE=rgb_url,
        Masked_IMAGE=mask_url,
    )