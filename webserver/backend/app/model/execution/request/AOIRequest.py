from typing import Optional

from pydantic import BaseModel, EmailStr

from app.model.execution.request.AreaSelection import AreaSelection


class Requester(BaseModel):
    name: str
    email: EmailStr
    organization: Optional[str] = None
    region: Optional[str] = None


class Monitoring(BaseModel):
    frequency: str
    startDate: Optional[str] = None
    endDate: Optional[str] = None
    notes: Optional[str] = None


class AOIRequest(BaseModel):
    requester: Requester
    monitoring: Monitoring
    area: AreaSelection
