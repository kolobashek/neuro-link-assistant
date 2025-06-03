"""
Сервис аутентификации и авторизации.
"""

import secrets
from typing import Any, Dict, Optional

from sqlalchemy.orm import Session

from core.db.models import User
from core.db.repository.user_repository import UserRepository
from core.security.jwt_handler import create_access_token, verify_token
from core.security.password import hash_password, verify_password


class AuthService:
    """Сервис для работы с аутентификацией и авторизацией."""

    def __init__(self, db_session: Session):
        """
        Инициализирует сервис аутентификации.

        Args:
            db_session: Сессия базы данных
        """
        self.db = db_session
        self.user_repo = UserRepository(db_session)

    def register_user(
        self,
        username: str,
        email: str,
        password: str,
        display_name: Optional[str] = None,
        role: str = "user",
    ) -> Optional[User]:  # ✅ Возвращаем User
        """Регистрирует нового пользователя."""
        try:
            if self.user_repo.get_by_username(username):
                return None
            if self.user_repo.get_by_email(email):
                return None

            salt = secrets.token_hex(16)
            password_hash, _ = hash_password(password, salt)

            user = self.user_repo.create(
                username=username,
                email=email,
                password_hash=password_hash,
                display_name=display_name,
                salt=salt,
                role=role,
            )
            return user
        except Exception as e:
            print(f"Ошибка регистрации пользователя: {e}")
            return None

    def authenticate_user(
        self, username: str, password: str
    ) -> Optional[User]:  # ✅ Возвращаем User
        """Аутентифицирует пользователя."""
        try:
            user = self.user_repo.get_by_username(username)
            if not user:
                return None

            salt = getattr(user, "salt", "")
            stored_hash = str(user.password_hash)
            if not verify_password(password, stored_hash, salt):
                return None

            if not getattr(user, "is_active", True):
                return None

            return user
        except Exception as e:
            print(f"Ошибка аутентификации пользователя: {e}")
            return None

    def get_current_user(self, token: str) -> Optional[User]:  # ✅ Возвращаем User
        """Получает текущего пользователя по токену."""
        try:
            payload = verify_token(token)
            user_id = payload.get("user_id")
            if not user_id:
                return None
            return self.user_repo.get_by_id(user_id)
        except Exception as e:
            print(f"Ошибка получения текущего пользователя: {e}")
            return None

    def create_access_token_for_user(self, user: User) -> str:  # ✅ Новый метод
        """Создает токен доступа для пользователя."""
        token_data = {"user_id": user.id, "username": user.username}
        return create_access_token(token_data)

    def change_password(self, user_id: int, old_password: str, new_password: str) -> bool:
        """
        Изменяет пароль пользователя.

        Args:
            user_id: ID пользователя
            old_password: Старый пароль
            new_password: Новый пароль

        Returns:
            bool: True если пароль изменен успешно
        """
        try:
            user = self.user_repo.get_by_id(user_id)  # ✅ ИСПРАВЛЕНО: используем репозиторий
            if not user:
                return False

            # Проверяем старый пароль
            salt = getattr(user, "salt", "")
            stored_hash = str(user.password_hash)
            if not verify_password(old_password, stored_hash, salt):
                return False

            # Генерируем новую соль и хешируем новый пароль
            new_salt = secrets.token_hex(16)
            new_password_hash, _ = hash_password(new_password, new_salt)

            # Обновляем пароль через репозиторий
            update_data = {"password_hash": new_password_hash}
            if hasattr(user, "salt"):
                update_data["salt"] = new_salt

            updated_user = self.user_repo.update(
                user_id, **update_data
            )  # ✅ ИСПРАВЛЕНО: через репозиторий
            return updated_user is not None

        except Exception as e:
            print(f"Ошибка изменения пароля: {e}")
            return False

    def update_user_role(self, user_id: int, new_role: str) -> bool:
        """
        Обновляет роль пользователя.

        Args:
            user_id: ID пользователя
            new_role: Новая роль

        Returns:
            bool: True если роль обновлена успешно
        """
        try:
            updated_user = self.user_repo.update(
                user_id, role=new_role
            )  # ✅ ИСПРАВЛЕНО: через репозиторий
            return updated_user is not None
        except Exception as e:
            print(f"Ошибка обновления роли пользователя: {e}")
            return False

    def deactivate_user(self, user_id: int) -> bool:
        """
        Деактивирует пользователя.

        Args:
            user_id: ID пользователя

        Returns:
            bool: True если пользователь деактивирован успешно
        """
        try:
            updated_user = self.user_repo.update(
                user_id, is_active=False
            )  # ✅ ИСПРАВЛЕНО: через репозиторий
            return updated_user is not None
        except Exception as e:
            print(f"Ошибка деактивации пользователя: {e}")
            return False

    def activate_user(self, user_id: int) -> bool:
        """
        Активирует пользователя.

        Args:
            user_id: ID пользователя

        Returns:
            bool: True если пользователь активирован успешно
        """
        try:
            updated_user = self.user_repo.update(
                user_id, is_active=True
            )  # ✅ ИСПРАВЛЕНО: через репозиторий
            return updated_user is not None
        except Exception as e:
            print(f"Ошибка активации пользователя: {e}")
            return False
