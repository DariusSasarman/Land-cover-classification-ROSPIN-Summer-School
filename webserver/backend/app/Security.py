import jwt
from fastapi import HTTPException
from app.config import JWT_SECRET_KEY, JWT_ALGORITHM
from app.logger import get_logger

logger = get_logger("Security")


def decode_jwt(token: str) -> dict:
    try:
        payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])
        logger.debug("Successfully decoded JWT for user sub: %s", payload.get("sub"))
        return payload
    except jwt.PyJWTError as exc:
        logger.warning("JWT decode/validation failed: %s", exc)
        raise HTTPException(status_code=401, detail="Invalid or expired token.")