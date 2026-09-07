from fastapi import APIRouter
from app.service.AuthService import signup, login
router = APIRouter(prefix="/api/auth", tags=["auth"])

@router.post("/signup")
def signup_(payload: dict):
    return signup(payload)


@router.post("/login")
def login_(payload: dict):
    return login(payload)