"""
Репозиторий для работы с пользователями.
"""

from typing import List, Optional

from sqlalchemy.orm import Session

from core.db.models import User


class UserRepository:
    """Класс для работы с пользователями в базе данных."""

    def __init__(self, db_session: Session):
        """
        Инициализирует репозиторий пользователей.

        Args:
            db_session (Session): Сессия SQLAlchemy для работы с БД.
        """
        self.db = db_session

    def create(
        self, username: str, email: str, password_hash: str, display_name: Optional[str] = None
    ) -> User:
        """
        Создаёт нового пользователя.

        Args:
            username (str): Имя пользователя.
            email (str): Email пользователя.
            password_hash (str): Хеш пароля пользователя.
            display_name (Optional[str], optional): Отображаемое имя. По умолчанию None.

        Returns:
            User: Созданный пользователь.
        """
        user = User(
            username=username,
            email=email,
            password_hash=password_hash,
            display_name=display_name,
        )
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        return user

    def get_by_id(self, user_id: int) -> Optional[User]:
        """
        Получает пользователя по ID.

        Args:
            user_id (int): ID пользователя.

        Returns:
            Optional[User]: Найденный пользователь или None.
        """
        return self.db.query(User).filter(User.id == user_id).first()

    def get_by_username(self, username: str) -> Optional[User]:
        """
        Получает пользователя по имени пользователя.

        Args:
            username (str): Имя пользователя.

        Returns:
            Optional[User]: Найденный пользователь или None.
        """
        return self.db.query(User).filter(User.username == username).first()

    def get_by_email(self, email: str) -> Optional[User]:
        """
        Получает пользователя по email.

        Args:
            email (str): Email пользователя.

        Returns:
            Optional[User]: Найденный пользователь или None.
        """
        return self.db.query(User).filter(User.email == email).first()

    def update(self, user_id: int, **kwargs) -> Optional[User]:
        """
        Обновляет пользователя.

        Args:
            user_id (int): ID пользователя.
            **kwargs: Поля для обновления.

        Returns:
            Optional[User]: Обновленный пользователь или None.
        """
        user = self.get_by_id(user_id)
        if not user:
            return None

        for key, value in kwargs.items():
            if hasattr(user, key):
                setattr(user, key, value)

        self.db.commit()
        self.db.refresh(user)
        return user

    def delete(self, user_id: int) -> bool:
        """
        Удаляет пользователя.

        Args:
            user_id (int): ID пользователя.

        Returns:
            bool: True если пользователь удален, иначе False.
        """
        user = self.get_by_id(user_id)
        if not user:
            return False

        self.db.delete(user)
        self.db.commit()
        return True

    def search_by_name(self, name_part: str) -> List[User]:
        """
        Ищет пользователей по части имени.

        Args:
            name_part (str): Часть имени для поиска.

        Returns:
            List[User]: Список найденных пользователей.
        """
        return self.db.query(User).filter(User.username.ilike(f"%{name_part}%")).all()

    def search_by_email(self, email_part: str) -> List[User]:
        """
        Ищет пользователей по части email.

        Args:
            email_part (str): Часть email для поиска.

        Returns:
            List[User]: Список найденных пользователей.
        """
        return self.db.query(User).filter(User.email.ilike(f"%{email_part}%")).all()

    def search(self, **filters) -> List[User]:
        """
        Ищет пользователей по заданным фильтрам.

        Args:
            **filters: Фильтры для поиска (username, email, display_name, is_active).

        Returns:
            List[User]: Список найденных пользователей.
        """
        query = self.db.query(User)
        limit = filters.pop("limit", None)
        offset = filters.pop("offset", None)

        if "username" in filters:
            query = query.filter(User.username.ilike(f"%{filters['username']}%"))
        if "email" in filters:
            query = query.filter(User.email.ilike(f"%{filters['email']}%"))
        if "display_name" in filters:
            query = query.filter(User.display_name.ilike(f"%{filters['display_name']}%"))
        if "is_active" in filters:
            query = query.filter(User.is_active == filters["is_active"])

        if limit:
            query = query.limit(limit)
        if offset:
            query = query.offset(offset)

        return query.all()
