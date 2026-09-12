from datetime import datetime, timedelta, timezone
from typing import Optional

import jwt
from passlib.context import CryptContext
from pydantic import BaseModel, EmailStr

from app.config import JWT_ALGORITHM, JWT_EXPIRES_MINUTES, JWT_SECRET_KEY

_PASSWORDS = CryptContext(schemes=["bcrypt"], deprecated="auto")


class User(BaseModel):
    name: str
    email: EmailStr
    organization: Optional[str] = None
    region: Optional[str] = None
    password: str

    def get_jwt_token(self) -> str:
        now = datetime.now(timezone.utc)
        return jwt.encode(
            {
                "sub": str(self.email),
                "email": str(self.email),
                "name": self.name,
                "organization": self.organization,
                "region": self.region,
                "iat": now,
                "exp": now + timedelta(minutes=JWT_EXPIRES_MINUTES),
            },
            JWT_SECRET_KEY,
            algorithm=JWT_ALGORITHM,
        )

    def verify_password(self, password: str) -> bool:
        return _PASSWORDS.verify(password, self.password)

    @classmethod
    def hash_password(cls, password: str) -> str:
        return _PASSWORDS.hash(password)
