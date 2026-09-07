from typing import Optional, ClassVar, Dict
from app.model.login.User import User


class UserRepo:
    _users_by_email: ClassVar[Dict[str, User]] = {}

    @classmethod
    def save(cls, user: User) -> User:
        cls._users_by_email[user.email] = user
        return user

    @classmethod
    def get_by_email(cls, email: str) -> Optional[User]:
        return cls._users_by_email.get(email)

    @classmethod
    def exists(cls, email: str) -> bool:
        return email in cls._users_by_email