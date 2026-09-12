from typing import Dict

from pydantic import BaseModel


class Classification(BaseModel):
    index: str
    period_desc: str
    Percentages: Dict[str, str]
    RGB_IMAGE: str
    Masked_IMAGE: str
