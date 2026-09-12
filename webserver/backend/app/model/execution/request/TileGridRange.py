
from typing import List

from pydantic import BaseModel


class TileGridRange(BaseModel):
    gx: List[int]
    gy: List[int]