import hashlib
import re
import secrets
from typing import Dict, Optional

from core.task.result import TaskResult


class AuthOperationsMixin:
    """
    Миксин для операций авторизации пользователей.
    """

    def _is_auth_operation(self):
        """Проверяет, является ли задача операцией авторизации."""
        auth_keywords = [
            "зарегистрировать пользователя",
            "регистрация",
            "создать пользователя",
            "войти как пользователь",
            "вход",
            "авторизация",
            "логин",
            "проверить права доступа",
            "права доступа",
            "токен",
        ]

        description_lower = self.description.lower()
        is_auth = any(keyword in description_lower for keyword in auth_keywords)
        print(f"DEBUG: Проверка операции авторизации: {is_auth}")
        return is_auth

    def _execute_auth_operation(self):
        """Выполняет операцию авторизации."""
        try:
            description_lower = self.description.lower()
            print(f"DEBUG: Выполнение операции авторизации: {self.description}")

            # Регистрация пользователя

            if (
                "зарегистрировать пользователя" in description_lower
                or "регистрация" in description_lower
            ):
                print("DEBUG: Выполняется регистрация пользователя")
                return self._register_user()
            # Вход пользователя
            elif "войти как пользователь" in description_lower or "вход" in description_lower:
                print("DEBUG: Выполняется вход пользователя")
                return self._login_user()
            # Проверка прав доступа

            elif (
                "проверить права доступа" in description_lower
                or "права доступа" in description_lower
            ):
                print("DEBUG: Выполняется проверка прав доступа")
                return self._check_access_rights()
            else:
                print("DEBUG: Неизвестная операция авторизации")
                return TaskResult(False, "Неизвестная операция авторизации")
        except Exception as e:
            print(f"DEBUG: Ошибка в операции авторизации: {e}")
            return TaskResult(False, f"Ошибка операции авторизации: {str(e)}")

    def _get_auth_storage(self):
        """Получает хранилище данных авторизации из реестра."""
        if not hasattr(self._registry, "_auth_storage"):
            # Инициализируем хранилище при первом обращении
            self._registry._auth_storage = {"users": {}, "tokens": {}, "current_user": None}
        return self._registry._auth_storage

    def _register_user(self):
        """Регистрирует нового пользователя."""
        # Извлекаем имя пользователя и пароль из описания

        username_match = re.search(r"пользователя\s+(\w+)", self.description)
        password_match = re.search(r"паролем\s+(\w+)", self.description)

        print(f"DEBUG: Поиск пользователя и пароля в: {self.description}")
        print(f"DEBUG: username_match: {username_match}")
        print(f"DEBUG: password_match: {password_match}")

        if not username_match or not password_match:
            return TaskResult(False, "Не удалось извлечь имя пользователя или пароль")
        username = username_match.group(1)
        password = password_match.group(1)

        print(f"DEBUG: Регистрация пользователя: {username}")

        storage = self._get_auth_storage()

        # Проверяем, не существует ли пользователь
        if username in storage["users"]:
            return TaskResult(False, f"Пользователь {username} уже существует")
        # Хешируем пароль
        password_hash = hashlib.sha256(password.encode()).hexdigest()
        # Сохраняем пользователя

        storage["users"][username] = {
            "password_hash": password_hash,
            "registered_at": "now",  # В реальной системе будет datetime
            "role": "user",
        }

        print(f"DEBUG: Пользователь {username} зарегистрирован")
        return TaskResult(True, f"Пользователь {username} успешно зарегистрирован")

    def _login_user(self):
        """Выполняет вход пользователя в систему."""
        # Извлекаем имя пользователя и пароль из описания

        username_match = re.search(r"пользователь\s+(\w+)", self.description)
        password_match = re.search(r"паролем\s+(\w+)", self.description)

        print(f"DEBUG: Поиск пользователя и пароля для входа в: {self.description}")
        print(f"DEBUG: username_match: {username_match}")
        print(f"DEBUG: password_match: {password_match}")

        if not username_match or not password_match:
            return TaskResult(False, "Не удалось извлечь имя пользователя или пароль")
        username = username_match.group(1)
        password = password_match.group(1)

        print(f"DEBUG: Попытка входа пользователя: {username}")

        storage = self._get_auth_storage()

        # Проверяем существование пользователя
        if username not in storage["users"]:
            print(f"DEBUG: Пользователь {username} не найден в {list(storage['users'].keys())}")
            return TaskResult(False, f"Пользователь {username} не найден")
        # Проверяем пароль
        password_hash = hashlib.sha256(password.encode()).hexdigest()
        stored_hash = storage["users"][username]["password_hash"]

        print(f"DEBUG: Проверка пароля для {username}")
        print(f"DEBUG: Введенный хеш: {password_hash}")
        print(f"DEBUG: Сохраненный хеш: {stored_hash}")

        if stored_hash != password_hash:
            return TaskResult(False, "Неверный пароль")
        # Генерируем токен
        token = secrets.token_hex(32)

        storage["tokens"][token] = username
        storage["current_user"] = username

        print(f"DEBUG: Пользователь {username} успешно вошел в систему, токен: {token}")
        return TaskResult(True, f"Пользователь {username} успешно вошел в систему. Токен: {token}")

    def _check_access_rights(self):
        """Проверяет права доступа текущего пользователя."""
        storage = self._get_auth_storage()
        current_user = storage.get("current_user")

        print(f"DEBUG: Проверка прав доступа для пользователя: {current_user}")

        if not current_user:
            return TaskResult(False, "Пользователь не авторизован")

        user_data = storage["users"].get(current_user)
        if not user_data:
            return TaskResult(False, "Данные пользователя не найдены")

        role = user_data.get("role", "user")
        rights = self._get_user_rights(role)

        print(f"DEBUG: Пользователь {current_user} имеет роль {role} с правами {rights}")
        return TaskResult(
            True, f"Пользователь {current_user} имеет роль '{role}' с правами: {', '.join(rights)}"
        )

    def _get_user_rights(self, role: str) -> list:
        """Возвращает список прав для роли."""
        rights_map = {
            "admin": ["read", "write", "delete", "manage_users"],
            "user": ["read", "write"],
            "guest": ["read"],
        }
        return rights_map.get(role, ["read"])
