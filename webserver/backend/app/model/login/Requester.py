
from typing import Optional
from pydantic import BaseModel, EmailStr


class Requester(BaseModel):
    name: str
    email: EmailStr
    organization: Optional[str] = None
    region: Optional[str] = None