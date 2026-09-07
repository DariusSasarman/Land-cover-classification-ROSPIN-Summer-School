from fastapi import HTTPException
from app.model.login.User import User
from app.repo import UserRepo


def signup(payload: dict):
    if UserRepo.exists(payload["email"]):
        raise HTTPException(status_code=409, detail="Email already registered.")

    user = User(
        name=payload["name"],
        email=payload["email"],
        organization=payload.get("organization"),
        password=payload["password"],
    )
    UserRepo.save(user)
    return {"token": user.get_jwt_token()}


def login(payload: dict):
    user = UserRepo.get_by_email(payload["email"])
    if not user or not user.verify_password(payload["password"]):
        raise HTTPException(status_code=401, detail="Invalid email or password.")

    return {"token": user.get_jwt_token()}