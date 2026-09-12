
from typing import Optional
from pydantic import BaseModel


class Monitoring(BaseModel):
    frequency: str  # "monthly" | "quarterly" | "annual"
    startDate: Optional[str] = None
    endDate: Optional[str] = None
    notes: Optional[str] = None
    