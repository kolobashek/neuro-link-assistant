"""
Сервис для управления правами доступа.
"""

from typing import Dict, List, Optional

from sqlalchemy.orm import Session

from core.db.models import User
from core.services.auth_service import AuthService


class PermissionService:
    """Сервис для работы с правами доступа."""

    def __init__(self, db_session: Session):
        """
        Инициализирует сервис прав доступа.

        Args:
            db_session: Сессия базы данных
        """
        self.db = db_session
        self.auth_service = AuthService(db_session)

        # Определение прав доступа для ролей
        self._role_permissions = {
            "admin": ["read_all", "write_all", "delete_all", "manage_users", "manage_system"],
            "user": ["read_own", "write_own", "delete_own"],
            "guest": ["read_public"],
        }

    def check_permission(self, user_id: int, permission: str) -> bool:
        """
        Проверяет наличие прав у пользователя.

        Args:
            user_id: ID пользователя
            permission: Требуемое право

        Returns:
            bool: True если право есть
        """
        try:
            user = self.auth_service.user_repo.db.query(User).filter(User.id == user_id).first()
            if not user or not getattr(user, "is_active", False):
                return False

            user_role = getattr(user, "role", "guest")
            user_permissions = self._role_permissions.get(user_role, [])

            return permission in user_permissions

        except Exception as e:
            print(f"Ошибка проверки прав доступа: {e}")
            return False

    def get_user_permissions(self, user_id: int) -> List[str]:
        """
        Получает список прав пользователя.

        Args:
            user_id: ID пользователя

        Returns:
            List[str]: Список прав доступа
        """
        try:
            user = self.auth_service.user_repo.db.query(User).filter(User.id == user_id).first()
            if not user or not getattr(user, "is_active", False):
                return []

            user_role = getattr(user, "role", "guest")
            return self._role_permissions.get(user_role, [])

        except Exception as e:
            print(f"Ошибка получения прав пользователя: {e}")
            return []

    def get_role_permissions(self, role: str) -> List[str]:
        """
        Получает права для роли.

        Args:
            role: Название роли

        Returns:
            List[str]: Список прав доступа роли
        """
        return self._role_permissions.get(role, [])

    def add_role_permission(self, role: str, permission: str) -> bool:
        """
        Добавляет право для роли.

        Args:
            role: Название роли
            permission: Право доступа

        Returns:
            bool: True если право добавлено успешно
        """
        try:
            if role not in self._role_permissions:
                self._role_permissions[role] = []

            if permission not in self._role_permissions[role]:
                self._role_permissions[role].append(permission)
                return True
            return False

        except Exception as e:
            print(f"Ошибка добавления права: {e}")
            return False

    def remove_role_permission(self, role: str, permission: str) -> bool:
        """
        Удаляет право у роли.

        Args:
            role: Название роли
            permission: Право доступа

        Returns:
            bool: True если право удалено успешно
        """
        try:
            if role in self._role_permissions and permission in self._role_permissions[role]:
                self._role_permissions[role].remove(permission)
                return True
            return False

        except Exception as e:
            print(f"Ошибка удаления права: {e}")
            return False

    def create_role(self, role: str, permissions: Optional[List[str]] = None) -> bool:
        """
        Создает новую роль.

        Args:
            role: Название роли
            permissions: Список прав доступа

        Returns:
            bool: True если роль создана успешно
        """
        try:
            if role not in self._role_permissions:
                self._role_permissions[role] = permissions or []
                return True
            return False

        except Exception as e:
            print(f"Ошибка создания роли: {e}")
            return False

    def delete_role(self, role: str) -> bool:
        """
        Удаляет роль.

        Args:
            role: Название роли

        Returns:
            bool: True если роль удалена успешно
        """
        try:
            if role in self._role_permissions and role not in ["admin", "user", "guest"]:
                del self._role_permissions[role]
                return True
            return False

        except Exception as e:
            print(f"Ошибка удаления роли: {e}")
            return False

    def get_all_roles(self) -> List[str]:
        """
        Получает все доступные роли.

        Returns:
            List[str]: Список ролей
        """
        return list(self._role_permissions.keys())

    def check_resource_access(
        self,
        user_id: int,
        resource_type: str,
        resource_id: Optional[int] = None,
        action: str = "read",
    ) -> bool:
        """
        Проверяет доступ к ресурсу.

        Args:
            user_id: ID пользователя
            resource_type: Тип ресурса (task, file, etc.)
            resource_id: ID ресурса (опционально)
            action: Действие (read, write, delete)

        Returns:
            bool: True если доступ разрешен
        """
        try:
            user = self.auth_service.user_repo.db.query(User).filter(User.id == user_id).first()
            if not user or not getattr(user, "is_active", False):
                return False

            user_role = getattr(user, "role", "guest")

            # Админы имеют доступ ко всему
            if user_role == "admin":
                return True

            # Проверяем общие права
            general_permission = f"{action}_all"
            if self.check_permission(user_id, general_permission):
                return True

            # Проверяем права на собственные ресурсы
            own_permission = f"{action}_own"
            if self.check_permission(user_id, own_permission):
                # Здесь должна быть логика проверки, что ресурс принадлежит пользователю
                # Пока возвращаем True для упрощения
                return True

            # Проверяем права на публичные ресурсы
            if action == "read" and self.check_permission(user_id, "read_public"):
                # Здесь должна быть логика проверки, что ресурс публичный
                return True

            return False

        except Exception as e:
            print(f"Ошибка проверки доступа к ресурсу: {e}")
            return False
