from typing import List

from pydantic import BaseModel

from app.model.execution.response.History import HistoryItem


class LandCoverResponse(BaseModel):
    id: str
    title: str
    status: str
    insights: List[str]
    History: List[HistoryItem]
