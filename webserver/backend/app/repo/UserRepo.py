from typing import Optional
from app.model.login.User import User
from app.storage.db import get_db, init_db
from app.logger import get_logger

logger = get_logger("repo.UserRepo")


class UserRepo:
    @classmethod
    def save(cls, user: User) -> User:
        init_db()
        logger.info("Saving user record for email: %s", user.email)
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                INSERT INTO users (email, name, organization, region, password)
                VALUES (?, ?, ?, ?, ?)
                ON CONFLICT(email) DO UPDATE SET
                    name=excluded.name,
                    organization=excluded.organization,
                    region=excluded.region,
                    password=excluded.password
                """,
                (user.email, user.name, user.organization, user.region, user.password),
            )
        return user

    @classmethod
    def get_by_email(cls, email: str) -> Optional[User]:
        init_db()
        logger.debug("Fetching user by email: %s", email)
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT email, name, organization, region, password FROM users WHERE email = ?",
                (email,),
            )
            row = cursor.fetchone()
            if not row:
                logger.debug("User not found for email: %s", email)
                return None
            return User(
                email=row["email"],
                name=row["name"],
                organization=row["organization"],
                region=row["region"],
                password=row["password"],
            )

    @classmethod
    def exists(cls, email: str) -> bool:
        init_db()
        logger.debug("Checking user existence for email: %s", email)
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT 1 FROM users WHERE email = ?", (email,))
            return cursor.fetchone() is not None