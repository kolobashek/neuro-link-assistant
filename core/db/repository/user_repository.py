"""
Репозиторий для работы с пользователями.
"""

from typing import List, Optional

from sqlalchemy import or_, select
from sqlalchemy.orm import Session

from core.db.models import User


class UserRepository:
    """Репозиторий для работы с пользователями."""

    def __init__(self, db_session: Session):
        self.db = db_session

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
            "password_hash",
            "salt",
        ]

        for key, value in kwargs.items():
            if key in allowed_fields and hasattr(user, key):
                setattr(user, key, value)

        self.db.commit()
        self.db.refresh(user)
        return user

    # ✅ ДОБАВЛЯЕМ НЕДОСТАЮЩИЕ МЕТОДЫ ДЛЯ ТЕСТОВ:

    def search(
        self,
        query: Optional[str] = None,
        username: Optional[str] = None,
        email: Optional[str] = None,
        limit: int = 50,
    ) -> List[User]:
        """
        Поиск пользователей (поддерживает разные типы поиска).

        Args:
            query: Общий поисковый запрос
            username: Поиск по имени пользователя
            email: Поиск по email
            limit: Максимальное количество результатов

        Returns:
            List[User]: Список найденных пользователей
        """
        conditions = []

        if query:
            conditions.extend(
                [
                    User.username.ilike(f"%{query}%"),
                    User.email.ilike(f"%{query}%"),
                    User.display_name.ilike(f"%{query}%"),
                ]
            )

        if username:
            conditions.append(User.username.ilike(f"%{username}%"))

        if email:
            conditions.append(User.email.ilike(f"%{email}%"))

        if not conditions:
            return []

        stmt = select(User).where(or_(*conditions)).limit(limit)
        return list(self.db.execute(stmt).scalars().all())

    def get_paginated(self, skip: int = 0, limit: int = 50) -> List[User]:
        """
        Получает пользователей с пагинацией.

        Args:
            skip: Количество пропускаемых записей
            limit: Максимальное количество записей

        Returns:
            List[User]: Список пользователей
        """
        stmt = select(User).offset(skip).limit(limit)
        return list(self.db.execute(stmt).scalars().all())

    def count_total(self) -> int:
        """
        Подсчитывает общее количество пользователей.

        Returns:
            int: Общее количество пользователей
        """
        return self.db.query(User).count()

    def count_active(self) -> int:
        """
        Подсчитывает количество активных пользователей.

        Returns:
            int: Количество активных пользователей
        """
        return self.db.query(User).filter(User.is_active == True).count()

    def get_by_role_paginated(self, role: str, skip: int = 0, limit: int = 50) -> List[User]:
        """
        Получает пользователей по роли с пагинацией.

        Args:
            role: Роль пользователей
            skip: Количество пропускаемых записей
            limit: Максимальное количество записей

        Returns:
            List[User]: Список пользователей с указанной ролью
        """
        if hasattr(User, "role"):
            stmt = select(User).where(getattr(User, "role") == role).offset(skip).limit(limit)
            return list(self.db.execute(stmt).scalars().all())
        return []

    def bulk_update_status(self, user_ids: List[int], is_active: bool) -> int:
        """
        Массовое обновление статуса пользователей.

        Args:
            user_ids: Список ID пользователей
            is_active: Новый статус активности

        Returns:
            int: Количество обновленных записей
        """
        updated_count = (
            self.db.query(User)
            .filter(User.id.in_(user_ids))
            .update({"is_active": is_active}, synchronize_session=False)
        )
        self.db.commit()
        return updated_count

    def delete(self, user_id: int) -> bool:
        """
        Удаляет пользователя.

        Args:
            user_id: ID пользователя

        Returns:
            bool: True если пользователь удален успешно
        """
        user = self.get_by_id(user_id)
        if user:
            self.db.delete(user)
            self.db.commit()
            return True
        return False

    def exists_by_username(self, username: str) -> bool:
        """
        Проверяет существование пользователя по имени.

        Args:
            username: Имя пользователя

        Returns:
            bool: True если пользователь существует
        """
        return self.get_by_username(username) is not None

    def exists_by_email(self, email: str) -> bool:
        """
        Проверяет существование пользователя по email.

        Args:
            email: Email пользователя

        Returns:
            bool: True если пользователь существует
        """
        return self.get_by_email(email) is not None
