import jwt
from fastapi import HTTPException
from app.config import JWT_SECRET_KEY, JWT_ALGORITHM

def decode_jwt(token: str) -> dict:
    try:
        return jwt.decode(token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])
    except jwt.PyJWTError:
        raise HTTPException(status_code=401, detail="Invalid or expired token.")