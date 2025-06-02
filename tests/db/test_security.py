"""
Тесты для системы безопасности.
"""

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from core.db.models import Base, User
from core.db.repository.user_repository import UserRepository
from core.security.jwt_handler import create_access_token, decode_token, verify_token
from core.security.password import hash_password, verify_password
from core.services.auth_service import AuthService
from core.services.permission_service import PermissionService


@pytest.fixture
def db_session():
    """Создает тестовую сессию базы данных."""
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    SessionLocal = sessionmaker(bind=engine)
    session = SessionLocal()
    yield session
    session.close()


@pytest.fixture
def user_repository(db_session):
    """Создает репозиторий пользователей для тестов."""
    return UserRepository(db_session)


@pytest.fixture
def auth_service(db_session):
    """Создает сервис аутентификации для тестов."""
    return AuthService(db_session)


@pytest.fixture
def permission_service(db_session):
    """Создает сервис прав доступа для тестов."""
    return PermissionService(db_session)


class TestPasswordSecurity:
    """Тесты безопасности паролей."""

    def test_password_hashing(self):
        """Тест хеширования пароля."""
        password = "test_password_123"
        password_hash, salt = hash_password(password)

        assert password_hash != password
        assert len(salt) > 0
        assert verify_password(password, password_hash, salt)

    def test_password_verification_fail(self):
        """Тест неудачной проверки пароля."""
        password = "test_password_123"
        wrong_password = "wrong_password"
        password_hash, salt = hash_password(password)

        assert not verify_password(wrong_password, password_hash, salt)

    def test_different_salts_different_hashes(self):
        """Тест что разные соли дают разные хеши."""
        password = "same_password"
        hash1, salt1 = hash_password(password)
        hash2, salt2 = hash_password(password)

        assert hash1 != hash2
        assert salt1 != salt2


class TestJWTSecurity:
    """Тесты безопасности JWT."""

    def test_token_creation_and_verification(self):
        """Тест создания и проверки токена."""
        data = {"user_id": 1, "username": "test_user"}
        token = create_access_token(data)

        assert token is not None
        assert len(token) > 0

        decoded_data = verify_token(token)
        assert decoded_data["user_id"] == 1
        assert decoded_data["username"] == "test_user"

    def test_token_decode_without_verification(self):
        """Тест декодирования токена без проверки."""
        data = {"user_id": 1, "username": "test_user"}
        token = create_access_token(data)

        decoded_data = decode_token(token)
        assert decoded_data["user_id"] == 1
        assert decoded_data["username"] == "test_user"


class TestUserRepository:
    """Тесты репозитория пользователей."""

    def test_create_user(self, user_repository):
        """Тест создания пользователя."""
        password_hash, salt = hash_password("test_password")

        user = user_repository.create(
            username="test_user",
            email="test@example.com",
            password_hash=password_hash,
            display_name="Test User",
            salt=salt,
            role="user",
        )

        assert user.username == "test_user"
        assert user.email == "test@example.com"
        assert user.display_name == "Test User"

    def test_get_user_by_username(self, user_repository):
        """Тест получения пользователя по имени."""
        password_hash, salt = hash_password("test_password")

        created_user = user_repository.create(
            username="test_user", email="test@example.com", password_hash=password_hash, salt=salt
        )

        found_user = user_repository.get_by_username("test_user")
        assert found_user is not None
        assert found_user.id == created_user.id

    def test_get_user_by_email(self, user_repository):
        """Тест получения пользователя по email."""
        password_hash, salt = hash_password("test_password")

        created_user = user_repository.create(
            username="test_user", email="test@example.com", password_hash=password_hash, salt=salt
        )

        found_user = user_repository.get_by_email("test@example.com")
        assert found_user is not None
        assert found_user.id == created_user.id


class TestAuthService:
    """Тесты сервиса аутентификации."""

    def test_register_user(self, auth_service):
        """Тест регистрации пользователя."""
        result = auth_service.register_user(
            username="new_user",
            email="new@example.com",
            password="secure_password",
            display_name="New User",
        )

        assert result is not None
        assert result["username"] == "new_user"
        assert result["email"] == "new@example.com"
        assert "id" in result

    def test_authenticate_user(self, auth_service):
        """Тест аутентификации пользователя."""
        # Сначала регистрируем пользователя
        auth_service.register_user(
            username="auth_user", email="auth@example.com", password="secure_password"
        )

        # Затем аутентифицируем
        result = auth_service.authenticate_user("auth_user", "secure_password")

        assert result is not None
        assert result["user"]["username"] == "auth_user"
        assert "access_token" in result

    def test_authenticate_user_wrong_password(self, auth_service):
        """Тест аутентификации с неверным паролем."""
        # Регистрируем пользователя
        auth_service.register_user(
            username="auth_user", email="auth@example.com", password="secure_password"
        )

        # Пытаемся войти с неверным паролем
        result = auth_service.authenticate_user("auth_user", "wrong_password")

        assert result is None

    def test_get_current_user(self, auth_service):
        """Тест получения текущего пользователя по токену."""
        # Регистрируем и аутентифицируем пользователя
        auth_service.register_user(
            username="token_user", email="token@example.com", password="secure_password"
        )

        auth_result = auth_service.authenticate_user("token_user", "secure_password")
        token = auth_result["access_token"]

        # Получаем пользователя по токену
        user_data = auth_service.get_current_user(token)

        assert user_data is not None
        assert user_data["username"] == "token_user"

    def test_change_password(self, auth_service):
        """Тест изменения пароля."""
        # Регистрируем пользователя
        user_data = auth_service.register_user(
            username="password_user", email="password@example.com", password="old_password"
        )

        # Меняем пароль
        success = auth_service.change_password(user_data["id"], "old_password", "new_password")

        assert success

        # Проверяем, что старый пароль не работает
        result = auth_service.authenticate_user("password_user", "old_password")
        assert result is None

        # Проверяем, что новый пароль работает
        result = auth_service.authenticate_user("password_user", "new_password")
        assert result is not None


class TestPermissionService:
    """Тесты сервиса прав доступа."""

    def test_check_admin_permissions(self, permission_service, auth_service):
        """Тест прав администратора."""
        # Создаем администратора
        admin_data = auth_service.register_user(
            username="admin", email="admin@example.com", password="admin_password", role="admin"
        )

        assert admin_data is not None

        # Проверяем права администратора
        assert permission_service.check_permission(admin_data["id"], "read_all")
        assert permission_service.check_permission(admin_data["id"], "write_all")
        assert permission_service.check_permission(admin_data["id"], "delete_all")
        assert permission_service.check_permission(admin_data["id"], "manage_users")

    def test_check_user_permissions(self, permission_service, auth_service):
        """Тест прав обычного пользователя."""
        # Создаем обычного пользователя
        user_data = auth_service.register_user(
            username="regular_user", email="user@example.com", password="user_password", role="user"
        )

        assert user_data is not None

        # Проверяем права пользователя
        assert permission_service.check_permission(user_data["id"], "read_own")
        assert permission_service.check_permission(user_data["id"], "write_own")
        assert permission_service.check_permission(user_data["id"], "delete_own")

        # Проверяем, что нет прав администратора
        assert not permission_service.check_permission(user_data["id"], "read_all")
        assert not permission_service.check_permission(user_data["id"], "manage_users")

    def test_check_guest_permissions(self, permission_service, auth_service):
        """Тест прав гостя."""
        # Создаем гостя
        guest_data = auth_service.register_user(
            username="guest_user",
            email="guest@example.com",
            password="guest_password",
            role="guest",
        )

        assert guest_data is not None

        # Проверяем права гостя
        assert permission_service.check_permission(guest_data["id"], "read_public")

        # Проверяем, что нет других прав
        assert not permission_service.check_permission(guest_data["id"], "read_own")
        assert not permission_service.check_permission(guest_data["id"], "write_own")

    def test_get_user_permissions(self, permission_service, auth_service):
        """Тест получения списка прав пользователя."""
        # Создаем пользователя
        user_data = auth_service.register_user(
            username="permissions_user", email="perms@example.com", password="password", role="user"
        )

        permissions = permission_service.get_user_permissions(user_data["id"])

        assert "read_own" in permissions
        assert "write_own" in permissions
        assert "delete_own" in permissions
        assert "read_all" not in permissions

    def test_role_management(self, permission_service):
        """Тест управления ролями."""
        # Создаем новую роль
        success = permission_service.create_role("moderator", ["read_all", "write_own"])
        assert success

        # Проверяем права роли
        permissions = permission_service.get_role_permissions("moderator")
        assert "read_all" in permissions
        assert "write_own" in permissions

        # Добавляем право
        success = permission_service.add_role_permission("moderator", "delete_own")
        assert success

        permissions = permission_service.get_role_permissions("moderator")
        assert "delete_own" in permissions

        # Удаляем право
        success = permission_service.remove_role_permission("moderator", "write_own")
        assert success

        permissions = permission_service.get_role_permissions("moderator")
        assert "write_own" not in permissions

    def test_resource_access(self, permission_service, auth_service):
        """Тест доступа к ресурсам."""
        # Создаем администратора
        admin_data = auth_service.register_user(
            username="admin_resource",
            email="admin_resource@example.com",
            password="password",
            role="admin",
        )

        # Создаем пользователя
        user_data = auth_service.register_user(
            username="user_resource",
            email="user_resource@example.com",
            password="password",
            role="user",
        )

        # Проверяем доступ администратора
        assert permission_service.check_resource_access(admin_data["id"], "task", 1, "read")
        assert permission_service.check_resource_access(admin_data["id"], "task", 1, "write")
        assert permission_service.check_resource_access(admin_data["id"], "task", 1, "delete")

        # Проверяем доступ пользователя к собственным ресурсам
        assert permission_service.check_resource_access(user_data["id"], "task", 1, "read")
        assert permission_service.check_resource_access(user_data["id"], "task", 1, "write")


class TestSecurityIntegration:
    """Интеграционные тесты безопасности."""

    def test_full_auth_workflow(self, auth_service, permission_service):
        """Тест полного цикла аутентификации и авторизации."""
        # Регистрация
        user_data = auth_service.register_user(
            username="integration_user",
            email="integration@example.com",
            password="secure_password",
            role="user",
        )

        assert user_data is not None

        # Аутентификация
        auth_result = auth_service.authenticate_user("integration_user", "secure_password")

        assert auth_result is not None
        token = auth_result["access_token"]

        # Получение пользователя по токену
        current_user = auth_service.get_current_user(token)
        assert current_user is not None
        assert current_user["username"] == "integration_user"

        # Проверка прав
        permissions = permission_service.get_user_permissions(user_data["id"])
        assert len(permissions) > 0
        assert "read_own" in permissions

    def test_security_edge_cases(self, auth_service):
        """Тест граничных случаев безопасности."""
        # Попытка регистрации с существующим именем пользователя
        auth_service.register_user(
            username="duplicate_user", email="first@example.com", password="password"
        )

        result = auth_service.register_user(
            username="duplicate_user", email="second@example.com", password="password"
        )

        assert result is None  # Должна быть ошибка

        # Попытка регистрации с существующим email
        result = auth_service.register_user(
            username="another_user", email="first@example.com", password="password"
        )

        assert result is None  # Должна быть ошибка

    def test_token_security(self, auth_service):
        """Тест безопасности токенов."""
        # Регистрируем пользователя
        user_data = auth_service.register_user(
            username="token_test_user", email="token_test@example.com", password="password"
        )

        # Получаем токен
        auth_result = auth_service.authenticate_user("token_test_user", "password")
        token = auth_result["access_token"]

        # Проверяем валидный токен
        user = auth_service.get_current_user(token)
        assert user is not None

        # Проверяем невалидный токен
        invalid_user = auth_service.get_current_user("invalid_token")
        assert invalid_user is None

        # Проверяем пустой токен
        empty_user = auth_service.get_current_user("")
        assert empty_user is None

    def test_password_security_requirements(self):
        """Тест требований безопасности паролей."""
        # Тест различных паролей
        passwords = [
            "simple",
            "Complex123!",
            "very_long_password_with_numbers_123",
            "!@#$%^&*()",
            "пароль_на_русском_123",
        ]

        for password in passwords:
            hash1, salt1 = hash_password(password)
            hash2, salt2 = hash_password(password)

            # Каждый раз должен быть разный хеш и соль
            assert hash1 != hash2
            assert salt1 != salt2

            # Но проверка должна работать
            assert verify_password(password, hash1, salt1)
            assert verify_password(password, hash2, salt2)

    def test_user_deactivation(self, auth_service, permission_service):
        """Тест деактивации пользователя."""
        # Создаем пользователя
        user_data = auth_service.register_user(
            username="deactivation_user", email="deactivation@example.com", password="password"
        )

        # Проверяем начальные права
        assert permission_service.check_permission(user_data["id"], "read_own")

        # Деактивируем пользователя
        success = auth_service.deactivate_user(user_data["id"])
        assert success

        # Проверяем, что права пропали
        assert not permission_service.check_permission(user_data["id"], "read_own")

        # Активируем обратно
        success = auth_service.activate_user(user_data["id"])
        assert success

        # Проверяем, что права вернулись
        assert permission_service.check_permission(user_data["id"], "read_own")

    def test_role_update(self, auth_service, permission_service):
        """Тест обновления роли пользователя."""
        # Создаем обычного пользователя
        user_data = auth_service.register_user(
            username="role_update_user",
            email="role_update@example.com",
            password="password",
            role="user",
        )

        # Проверяем начальные права
        assert permission_service.check_permission(user_data["id"], "read_own")
        assert not permission_service.check_permission(user_data["id"], "read_all")

        # Повышаем до администратора
        success = auth_service.update_user_role(user_data["id"], "admin")
        assert success

        # Проверяем новые права
        assert permission_service.check_permission(user_data["id"], "read_all")
        assert permission_service.check_permission(user_data["id"], "manage_users")

        # Понижаем до гостя
        success = auth_service.update_user_role(user_data["id"], "guest")
        assert success

        # Проверяем ограниченные права
        assert permission_service.check_permission(user_data["id"], "read_public")
        assert not permission_service.check_permission(user_data["id"], "read_own")
