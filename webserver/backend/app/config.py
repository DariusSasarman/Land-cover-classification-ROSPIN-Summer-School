import os
from dotenv import load_dotenv

load_dotenv()


def _require_env(key: str) -> str:
    value = os.environ.get(key)
    if not value:
        raise RuntimeError(f"Missing required environment variable: {key}. Check your .env file.")
    return value


JWT_SECRET_KEY = _require_env("JWT_SECRET_KEY")
JWT_ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")
JWT_EXPIRES_MINUTES = int(os.getenv("JWT_EXPIRES_MINUTES", "1440"))

COPERNICUS_CLIENT_ID = _require_env("COPERNICUS_CLIENT_ID")
COPERNICUS_CLIENT_SECRET = _require_env("COPERNICUS_CLIENT_SECRET")