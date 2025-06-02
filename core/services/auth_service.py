"""
Сервис аутентификации и авторизации.
"""

import secrets
from typing import Optional

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
    ) -> Optional[User]:  # ✅ Возвращаем User объект
        """
        Регистрирует нового пользователя.

        Args:
            username: Имя пользователя
            email: Email пользователя
            password: Пароль пользователя
            display_name: Отображаемое имя (опционально)
            role: Роль пользователя

        Returns:
            User: Созданный пользователь или None при ошибке
        """
        try:
            # Проверяем, существует ли пользователь
            if self.user_repo.get_by_username(username):
                return None

            if self.user_repo.get_by_email(email):
                return None

            # Генерируем соль и хешируем пароль
            salt = secrets.token_hex(16)
            password_hash, _ = hash_password(password, salt)

            # Создаем пользователя
            user = self.user_repo.create(
                username=username,
                email=email,
                password_hash=password_hash,
                display_name=display_name,
                salt=salt,
                role=role,
            )

            return user  # ✅ Возвращаем объект User

        except Exception as e:
            print(f"Ошибка регистрации пользователя: {e}")
            return None

    def authenticate_user(self, username: str, password: str) -> Optional[User]:  # ✅ User объект
        """
        Аутентифицирует пользователя.

        Args:
            username: Имя пользователя
            password: Пароль

        Returns:
            User: Объект пользователя или None при ошибке
        """
        try:
            user = self.user_repo.get_by_username(username)
            if not user:
                return None

            # Проверяем пароль
            salt = getattr(user, "salt", "")
            stored_hash = str(user.password_hash)  # Приводим к строке
            if not verify_password(password, stored_hash, salt):
                return None

            return user  # ✅ Возвращаем объект User

        except Exception as e:
            print(f"Ошибка аутентификации пользователя: {e}")
            return None

    def get_current_user(self, token: str) -> Optional[dict]:
        """
        Получает текущего пользователя по токену.

        Args:
            token: JWT токен

        Returns:
            dict: Информация о пользователе или None при ошибке
        """
        try:
            payload = verify_token(token)
            user_id = payload.get("user_id")

            if not user_id:
                return None

            user = self.user_repo.db.query(User).filter(User.id == user_id).first()
            if not user:
                return None

            return {
                "id": user.id,
                "username": user.username,
                "email": user.email,
                "display_name": user.display_name,
                "role": getattr(user, "role", "user"),
                "is_active": user.is_active,
            }

        except Exception as e:
            print(f"Ошибка получения текущего пользователя: {e}")
            return None

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
            user = self.user_repo.db.query(User).filter(User.id == user_id).first()
            if not user:
                return False

            # Проверяем старый пароль
            salt = getattr(user, "salt", "")
            stored_hash = str(user.password_hash)  # Приводим к строке
            if not verify_password(old_password, stored_hash, salt):
                return False

            # Генерируем новую соль и хешируем новый пароль
            new_salt = secrets.token_hex(16)
            new_password_hash, _ = hash_password(new_password, new_salt)

            # Обновляем пароль
            update_data = {"password_hash": new_password_hash}
            if hasattr(user, "salt"):
                update_data["salt"] = new_salt

                user = self.user_repo.db.query(User).filter(User.id == user_id).first()
                if user:
                    for key, value in update_data.items():
                        setattr(user, key, value)
                    self.user_repo.db.commit()
                    updated_user = user
                else:
                    updated_user = None
                    return updated_user is not None

        except Exception as e:
            print(f"Ошибка изменения пароля: {e}")
            return False
        return True  # Добавить в конце функции change_password

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
            user = self.user_repo.db.query(User).filter(User.id == user_id).first()
            if user:
                for key, value in {"role": new_role}.items():  # для update_user_role
                    setattr(user, key, value)
                self.user_repo.db.commit()
                return True
            return False
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
            user = self.user_repo.db.query(User).filter(User.id == user_id).first()
            if user:
                setattr(user, "is_active", False)
                self.user_repo.db.commit()  # Важно: добавить commit
                self.user_repo.db.refresh(user)  # Обновить объект после commit
                return True
            return False
        except Exception as e:
            print(f"Ошибка деактивации пользователя: {e}")
            self.user_repo.db.rollback()  # Откатить изменения при ошибке
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
            user = self.user_repo.db.query(User).filter(User.id == user_id).first()
            if user:
                setattr(user, "is_active", True)  # для activate_user
                self.user_repo.db.commit()
                self.user_repo.db.refresh(user)
                return True
            return False
        except Exception as e:
            print(f"Ошибка активации пользователя: {e}")
            self.user_repo.db.rollback()
            return False
