
from pydantic import BaseModel


class BBoxLonLat(BaseModel):
    west: float
    south: float
    east: float
    north: float