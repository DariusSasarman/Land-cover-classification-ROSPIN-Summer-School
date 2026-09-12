
from pydantic import BaseModel


class TileCount(BaseModel):
    x: int
    y: int
    total: int  