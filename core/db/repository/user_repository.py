"""
Репозиторий для работы с пользователями.
"""

from typing import List, Optional

from sqlalchemy import select
from sqlalchemy.orm import Session

from core.db.models import User

# Если BaseRepository не существует, создайте базовый класс или уберите наследование


class UserRepository:
    """Репозиторий для работы с пользователями."""

    def __init__(self, db_session: Session):
        self.db = db_session  # Добавляем инициализацию атрибута db

    def get_by_username(self, username: str) -> Optional[User]:
        """
        Получает пользователя по имени пользователя.

        Args:
            username: Имя пользователя

        Returns:
            Optional[User]: Пользователь или None
        """
        stmt = select(User).where(User.username == username)
        return self.db.execute(stmt).scalar_one_or_none()

    def get_by_email(self, email: str) -> Optional[User]:
        """
        Получает пользователя по email.

        Args:
            email: Email пользователя

        Returns:
            Optional[User]: Пользователь или None
        """
        stmt = select(User).where(User.email == email)
        return self.db.execute(stmt).scalar_one_or_none()

    def get_by_id(self, user_id: int) -> Optional[User]:
        """
        Получает пользователя по ID.

        Args:
            user_id: ID пользователя

        Returns:
            Optional[User]: Пользователь или None
        """
        stmt = select(User).where(User.id == user_id)
        return self.db.execute(stmt).scalar_one_or_none()

    def create(
        self,
        username: str,
        email: str,
        password_hash: str,
        display_name: Optional[str] = None,
        salt: Optional[str] = None,
        role: str = "user",
        **kwargs,
    ) -> User:
        """
        Создает нового пользователя.

        Args:
            username: Имя пользователя
            email: Email пользователя
            password_hash: Хеш пароля
            display_name: Отображаемое имя
            salt: Соль для пароля
            role: Роль пользователя
            **kwargs: Дополнительные параметры

        Returns:
            User: Созданный пользователь
        """
        user = User(
            username=username, email=email, password_hash=password_hash, display_name=display_name
        )

        # Устанавливаем дополнительные атрибуты, если они поддерживаются моделью
        if salt is not None and hasattr(user, "salt"):
            setattr(user, "salt", salt)
        if hasattr(user, "role"):
            setattr(user, "role", role)

        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        return user

    def get_active_users(self) -> List[User]:
        """
        Получает всех активных пользователей.

        Returns:
            List[User]: Список активных пользователей
        """
        stmt = select(User).where(User.is_active == True)
        return list(self.db.execute(stmt).scalars().all())

    def get_users_by_role(self, role: str) -> List[User]:
        """
        Получает пользователей по роли.

        Args:
            role: Роль пользователей

        Returns:
            List[User]: Список пользователей с указанной ролью
        """
        if hasattr(User, "role"):
            stmt = select(User).where(getattr(User, "role") == role)
            return list(self.db.execute(stmt).scalars().all())
        return []

    def search_users(self, query: str) -> List[User]:
        """
        Поиск пользователей по имени пользователя или email.

        Args:
            query: Поисковый запрос

        Returns:
            List[User]: Список найденных пользователей
        """
        stmt = select(User).where(
            (User.username.ilike(f"%{query}%")) | (User.email.ilike(f"%{query}%"))
        )
        return list(self.db.execute(stmt).scalars().all())

    def search_by_name(self, name: str) -> List[User]:
        """
        Поиск пользователей по имени пользователя или отображаемому имени.

        Args:
            name: Имя для поиска

        Returns:
            List[User]: Список найденных пользователей
        """
        stmt = select(User).where(
            (User.username.ilike(f"%{name}%")) | (User.display_name.ilike(f"%{name}%"))
        )
        return list(self.db.execute(stmt).scalars().all())

    def search_by_email(self, domain: str) -> List[User]:
        """
        Поиск пользователей по домену email.

        Args:
            domain: Домен для поиска (например, "example.com")

        Returns:
            List[User]: Список найденных пользователей
        """
        stmt = select(User).where(User.email.ilike(f"%{domain}%"))
        return list(self.db.execute(stmt).scalars().all())

    def update(self, user_id: int, **kwargs) -> Optional[User]:
        """
        Обновляет данные пользователя.

        Args:
            user_id: ID пользователя
            **kwargs: Поля для обновления

        Returns:
            Optional[User]: Обновленный пользователь или None
        """
        user = self.get_by_id(user_id)
        if not user:
            return None

        # Обновляем разрешенные поля
        allowed_fields = [
            "username",
            "email",
            "display_name",
            "bio",
            "avatar_url",
            "is_active",
            "role",
        ]

        for key, value in kwargs.items():
            if key in allowed_fields and hasattr(user, key):
                setattr(user, key, value)

        self.db.commit()
        self.db.refresh(user)
        return user
