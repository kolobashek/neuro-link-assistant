"""Сервис для работы с пользователями."""

from typing import Optional

from sqlalchemy.orm import Session

from core.db.models import User
from core.services.auth_service import AuthService


class UserService(AuthService):
    """Расширенный сервис пользователей."""

    def update_user_profile(
        self,
        user_id: int,
        display_name: Optional[str] = None,
        bio: Optional[str] = None,
        avatar_url: Optional[str] = None,
    ) -> Optional[User]:
        """Обновление профиля пользователя."""
        user = self.db.query(User).filter(User.id == user_id).first()
        if user:
            if display_name is not None:
                setattr(user, "display_name", display_name)
            if bio is not None:
                setattr(user, "bio", bio)
            if avatar_url is not None:
                setattr(user, "avatar_url", avatar_url)
            self.db.commit()
            self.db.refresh(user)
        return user
