from datetime import timedelta

import jwt
import pytest

from core.db.repository.task_repository import TaskRepository
from core.db.repository.user_repository import UserRepository
from core.security.jwt_handler import create_access_token, decode_token, verify_token
from core.security.password import hash_password, verify_password
from core.services.auth_service import AuthService
from core.services.permission_service import PermissionService

# from sqlalchemy.exc import IntegrityError


class TestPasswordSecurity:
    def test_password_hashing(self):
        """Тест хеширования и проверки паролей"""
        # Хешируем пароль
        password = "secure_password123"
        hashed = hash_password(password)

        # Проверяем, что хеш отличается от исходного пароля
        assert hashed != password

        # Проверяем корректный пароль
        assert verify_password(password, hashed) is True

        # Проверяем некорректный пароль
        assert verify_password("wrong_password", hashed) is False

        # Проверяем, что хеши разных паролей отличаются
        hashed2 = hash_password(password)
        assert hashed != hashed2  # Соль должна быть разной


class TestJWTTokens:
    def test_jwt_token_creation_and_verification(self):
        """Тест создания и проверки JWT токенов"""
        # Создаем JWT токен
        user_data = {"user_id": 123, "username": "testuser", "role": "user"}
        token = create_access_token(user_data)

        # Проверяем, что токен создан
        assert token is not None
        assert isinstance(token, str)

        # Декодируем токен
        decoded = decode_token(token)
        assert decoded["user_id"] == 123
        assert decoded["username"] == "testuser"
        assert decoded["role"] == "user"

        # Проверяем валидность токена
        assert verify_token(token) is True

        # Проверяем, что токен с неверной подписью не проходит валидацию
        parts = token.split(".")
        invalid_token = f"{parts[0]}.{parts[1]}.invalid_signature"
        with pytest.raises(jwt.InvalidSignatureError):
            verify_token(invalid_token)

    def test_token_expiration(self):
        """Тест истечения срока действия токена"""
        # Создаем токен с коротким сроком действия
        user_data = {"user_id": 456, "username": "expiration_test"}
        token = create_access_token(user_data, expires_delta=timedelta(seconds=1))

        # Токен должен быть валидным сразу после создания
        assert verify_token(token) is True

        # Ждем, пока токен истечет
        import time

        time.sleep(2)

        # Токен должен быть недействительным
        with pytest.raises(jwt.ExpiredSignatureError):
            verify_token(token)


class TestAuthorizationSecurity:
    @pytest.fixture
    def auth_service(self, db_session):
        """Создает сервис аутентификации"""
        user_repo = UserRepository(db_session)
        return AuthService(db_session, user_repo)

    @pytest.fixture
    def permission_service(self, db_session):
        """Создает сервис управления разрешениями"""
        return PermissionService(db_session)

    @pytest.fixture
    def test_users(self, db_session, auth_service):
        """Создает тестовых пользователей с разными ролями"""
        # Создаем администратора
        admin = auth_service.register_user(
            username="admin_user",
            email="admin@example.com",
            password="admin_password",
            role="admin",
        )

        # Создаем обычного пользователя
        user = auth_service.register_user(
            username="regular_user", email="user@example.com", password="user_password", role="user"
        )

        # Создаем еще одного пользователя для тестов доступа к ресурсам
        another_user = auth_service.register_user(
            username="another_user",
            email="another@example.com",
            password="another_password",
            role="user",
        )

        return {"admin": admin, "user": user, "another_user": another_user}

    def test_role_based_access(self, db_session, permission_service, test_users):
        """Тест доступа на основе ролей"""
        admin = test_users["admin"]
        user = test_users["user"]

        # Проверяем, что админ имеет доступ к админ-функциям
        assert permission_service.can_access_admin_panel(admin.id) is True
        assert permission_service.can_manage_users(admin.id) is True

        # Проверяем, что обычный пользователь не имеет доступа к админ-функциям
        assert permission_service.can_access_admin_panel(user.id) is False
        assert permission_service.can_manage_users(user.id) is False

    def test_resource_ownership_security(self, db_session, permission_service, test_users):
        """Тест безопасности владения ресурсами"""
        user = test_users["user"]
        another_user = test_users["another_user"]
        admin = test_users["admin"]

        # Создаем задачу для пользователя
        task_repo = TaskRepository(db_session)
        task = task_repo.create(
            user_id=user.id, title="Private Task", description="Task owned by user"
        )

        # Проверяем, что владелец имеет доступ к задаче
        assert permission_service.can_access_task(user.id, task.id) is True
        assert permission_service.can_modify_task(user.id, task.id) is True

        # Проверяем, что другой пользователь не имеет доступа к чужой задаче
        assert permission_service.can_access_task(another_user.id, task.id) is False
        assert permission_service.can_modify_task(another_user.id, task.id) is False

        # Проверяем, что админ имеет доступ к задаче любого пользователя
        assert permission_service.can_access_task(admin.id, task.id) is True
        assert permission_service.can_modify_task(admin.id, task.id) is True
