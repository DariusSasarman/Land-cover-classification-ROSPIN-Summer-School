from pydantic import BaseModel

from app.model.execution.response.Classification import Classification


class HistoryItem(BaseModel):
    Classification: Classification
