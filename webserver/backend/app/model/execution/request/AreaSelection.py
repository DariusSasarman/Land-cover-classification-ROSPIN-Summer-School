from typing import List

from pydantic import BaseModel, Field


class TileGridRange(BaseModel):
    gx: List[int] = Field(min_length=2, max_length=2)
    gy: List[int] = Field(min_length=2, max_length=2)


class TileCount(BaseModel):
    x: int
    y: int
    total: int


class BBoxLonLat(BaseModel):
    west: float
    south: float
    east: float
    north: float


class BBoxMercator(BaseModel):
    minX: float
    minY: float
    maxX: float
    maxY: float


class AreaSelection(BaseModel):
    tile_grid_range: TileGridRange
    tile_count: TileCount
    pixel_size_m: float
    tile_px: int
    area_km2: float
    bbox_lonlat: BBoxLonLat
    bbox_mercator: BBoxMercator
