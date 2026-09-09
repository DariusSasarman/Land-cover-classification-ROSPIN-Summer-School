from fastapi import HTTPException
from app.model.login.User import User
from app.repo import UserRepo
from app.logger import get_logger

logger = get_logger("service.AuthService")


def signup(payload: dict):
    email = payload.get("email")
    logger.info("Signup attempt for email: %s", email)
    if UserRepo.exists(email):
        logger.warning("Signup failed: Email '%s' already registered", email)
        raise HTTPException(status_code=409, detail="Email already registered.")

    user = User(
        name=payload["name"],
        email=email,
        organization=payload.get("organization"),
        password=payload["password"],
    )
    UserRepo.save(user)
    logger.info("Signup successful for email: %s", email)
    return {"token": user.get_jwt_token()}


def login(payload: dict):
    email = payload.get("email")
    logger.info("Login attempt for email: %s", email)
    user = UserRepo.get_by_email(email)
    if not user or not user.verify_password(payload["password"]):
        logger.warning("Login failed for email: %s (invalid credentials)", email)
        raise HTTPException(status_code=401, detail="Invalid email or password.")

    logger.info("Login successful for email: %s", email)
    return {"token": user.get_jwt_token()}