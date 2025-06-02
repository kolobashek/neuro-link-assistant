from datetime import datetime, timedelta

import pytest

from core.db.models import User
from core.services.ai_model_service import AIModelService
from core.services.task_service import TaskService
from core.services.user_service import UserService


class TestUserService:
    def test_user_registration(self, db_session):
        """Тест интеграции сервиса регистрации пользователей с БД"""
        user_service = UserService(db_session)

        user_data = {
            "username": "integration_user",
            "email": "integration@example.com",
            "password": "secure_password123",
        }

        # Регистрируем пользователя
        user = user_service.register_user(**user_data)

        # ✅ Правильные проверки с getattr
        assert user is not None
        assert getattr(user, "username", None) == user_data["username"]
        assert getattr(user, "email", None) == user_data["email"]
        assert getattr(user, "password_hash", None) != user_data["password"]

        # Проверяем аутентификацию
        authenticated_user = user_service.authenticate_user(
            user_data["username"], user_data["password"]
        )

        assert authenticated_user is not None
        assert getattr(authenticated_user, "username", None) == getattr(user, "username", None)

        # Проверяем аутентификацию с неверным паролем
        incorrect_auth = user_service.authenticate_user(user_data["username"], "wrong_password")

        assert incorrect_auth is None

    def test_user_profile_update(self, db_session):
        """Тест обновления профиля пользователя"""
        user_service = UserService(db_session)

        # Создаем пользователя
        user = user_service.register_user(
            username="profile_user", email="profile@example.com", password="secure_password"
        )

        assert user is not None
        user_id = getattr(user, "id", None)
        assert user_id is not None

        # Обновляем профиль
        updated_user = user_service.update_user_profile(
            user_id,
            display_name="Test User",
            bio="Test biography",
            avatar_url="https://example.com/avatar.jpg",
        )

        # Проверяем результат, возвращаемый сервисом
        assert updated_user is not None
        assert getattr(updated_user, "display_name", None) == "Test User"
        assert getattr(updated_user, "bio", None) == "Test biography"
        assert getattr(updated_user, "avatar_url", None) == "https://example.com/avatar.jpg"

        # Проверяем, что изменения сохранены в БД
        db_session.expire_all()
        user_from_db = db_session.query(User).filter(User.id == user_id).first()

        assert user_from_db is not None
        assert getattr(user_from_db, "display_name", None) == "Test User"
        assert getattr(user_from_db, "bio", None) == "Test Biography"
        assert getattr(user_from_db, "avatar_url", None) == "https://example.com/avatar.jpg"


class TestTaskService:
    @pytest.fixture
    def test_user(self, db_session):
        """Создает тестового пользователя для сервиса задач"""
        user_service = UserService(db_session)
        return user_service.register_user(
            username="task_service_user", email="task_service@example.com", password="password"
        )

    def test_task_creation_and_retrieval(self, db_session, test_user):
        """Тест создания и получения задач через сервис"""
        task_service = TaskService(db_session)

        # Создаем задачу
        task = task_service.create_task(
            user_id=getattr(test_user, "id", 0),
            title="Integration Task",
            description="Test task through service",
            priority=2,
            due_date=datetime.now() + timedelta(days=3),
        )

        # Проверяем, что задача создана
        task_id = getattr(task, "id", None)
        assert task_id is not None
        assert getattr(task, "title", None) == "Integration Task"

        # Получаем задачу по ID
        retrieved_task = task_service.get_task_by_id(task_id)
        assert retrieved_task is not None
        assert getattr(retrieved_task, "id", None) == task_id

        # Получаем задачи пользователя
        user_tasks = task_service.get_user_tasks(getattr(test_user, "id", 0))
        assert len(user_tasks) >= 1
        assert any(getattr(t, "id", None) == task_id for t in user_tasks)

    def test_task_lifecycle(self, db_session, test_user):
        """Тест жизненного цикла задачи (создание -> обновление -> выполнение -> удаление)"""
        task_service = TaskService(db_session)

        # Создаем задачу
        task = task_service.create_task(
            user_id=getattr(test_user, "id", 0),
            title="Lifecycle Task",
            description="Task to test complete lifecycle",
        )

        task_id = getattr(task, "id", None)
        assert task_id is not None

        # Обновляем задачу
        updated_task = task_service.update_task(
            task_id, title="Updated Lifecycle Task", description="Updated description", priority=3
        )

        assert updated_task is not None
        assert getattr(updated_task, "title", None) == "Updated Lifecycle Task"
        assert getattr(updated_task, "priority", None) == 3

        # Отмечаем задачу как выполненную
        completed_task = task_service.complete_task(task_id)
        assert completed_task is not None
        assert getattr(completed_task, "status", None) == "completed"
        assert getattr(completed_task, "completed_at", None) is not None

        # Удаляем задачу
        result = task_service.delete_task(task_id)
        assert result is True

        # Проверяем, что задача удалена
        deleted_task = task_service.get_task_by_id(task_id)
        assert deleted_task is None


class TestAIModelService:
    def test_model_registration_and_usage(self, db_session):
        """Тест регистрации и использования моделей ИИ"""
        ai_service = AIModelService(db_session)

        # Регистрируем модель
        model = ai_service.register_model(
            name="GPT-3.5-Turbo",
            provider="OpenAI",
            is_api=True,
            base_url="https://api.openai.com/v1",
            configuration={"model": "gpt-3.5-turbo", "temperature": 0.7, "max_tokens": 2000},
        )

        assert model is not None
        model_id = getattr(model, "id", None)
        assert model_id is not None
        assert getattr(model, "name", None) == "GPT-3.5-Turbo"

        # Получаем модель по ID
        retrieved_model = ai_service.get_model_by_id(model_id)
        assert retrieved_model is not None
        assert getattr(retrieved_model, "id", None) == model_id

        # Получаем активные модели
        active_models = ai_service.get_active_models()
        assert len(active_models) >= 1
        assert any(getattr(m, "id", None) == model_id for m in active_models)

        # Обновляем конфигурацию модели
        updated_config = {
            "model": "gpt-3.5-turbo",
            "temperature": 0.5,  # Обновленное значение
            "max_tokens": 4000,  # Обновленное значение
            "top_p": 0.9,  # Новый параметр
        }

        updated_model = ai_service.update_model_configuration(model_id, updated_config)
        assert updated_model is not None
        model_config = getattr(updated_model, "configuration", {})
        assert model_config["temperature"] == 0.5
        assert model_config["max_tokens"] == 4000
        assert model_config["top_p"] == 0.9
