# mypy: disable-error-code="annotation-unchecked"
# pylint: disable=no-member
# pyright: reportGeneralTypeIssues=false
# pyright: reportArgumentType=false

from datetime import datetime, timedelta

import pytest
from sqlalchemy.exc import IntegrityError

from core.db.crud import (
    create_ai_model,
    create_task,
    create_user,
    get_ai_model_by_id,
    get_ai_models,
    get_tasks_by_user,
    get_user_by_id,
    get_user_by_username,
    update_task_status,
)
from core.db.models import AIModel, Task, User, Workflow  # noqa: F401


class TestUserCRUD:
    def test_create_user(self, db_session):
        """Тест создания пользователя"""
        user_data = {
            "username": "testuser",
            "email": "test@example.com",
            "password_hash": "hashed_password",
        }

        user = create_user(db_session, **user_data)

        assert user.id is not None
        assert user.username == user_data["username"]
        assert user.email == user_data["email"]
        assert user.password_hash == user_data["password_hash"]

    def test_unique_constraints(self, db_session):
        """Тест уникальности имени и email пользователя"""
        user_data = {
            "username": "uniqueuser",
            "email": "unique@example.com",
            "password_hash": "hashed_password",
        }

        create_user(db_session, **user_data)
        db_session.commit()  # Важно: сохраняем изменения в БД!

        # Пытаемся создать пользователя с тем же username
        with pytest.raises(IntegrityError):
            create_user(
                db_session, username="uniqueuser", email="another@example.com", password_hash="hash"
            )
            db_session.flush()  # Выполняем flush для проверки ограничений
        db_session.rollback()  # Откатываем изменения после ошибки

        # Пытаемся создать пользователя с тем же email
        with pytest.raises(IntegrityError):
            create_user(
                db_session, username="anotheruser", email="unique@example.com", password_hash="hash"
            )
            db_session.flush()  # Выполняем flush для проверки ограничений

    def test_get_user(self, db_session):
        """Тест получения пользователя"""
        user = create_user(
            db_session, username="getuser", email="get@example.com", password_hash="hash"
        )

        # Получаем пользователя по ID
        found_user = get_user_by_id(db_session, user.id)
        assert found_user is not None
        assert found_user.id == user.id

        # Получаем пользователя по username
        found_user = get_user_by_username(db_session, "getuser")
        assert found_user is not None
        assert found_user.username == "getuser"

        # Проверяем, что несуществующий пользователь не найден
        not_found = get_user_by_id(db_session, 999999)
        assert not_found is None


class TestAIModelCRUD:
    def test_create_ai_model(self, db_session):
        """Тест создания модели ИИ"""
        model_data = {
            "name": "Test GPT",
            "provider": "OpenAI",
            "is_api": True,
            "base_url": "https://api.example.com",
            "configuration": {"model": "test-model"},
        }

        model = create_ai_model(db_session, **model_data)

        assert model.id is not None
        assert model.name == model_data["name"]
        assert model.provider == model_data["provider"]
        assert model.is_api == model_data["is_api"]
        assert model.configuration == model_data["configuration"]

    def test_get_ai_models(self, db_session):
        """Тест получения списка моделей ИИ"""
        # Создаем несколько моделей

        model1 = create_ai_model(db_session, name="Model 1", provider="Provider 1", is_api=True)
        # model2 = create_ai_model(db_session, name="Model 2", provider="Provider 2", is_api=False)
        db_session.commit()  # Сохраняем изменения в БД!

        # Получаем все модели
        models = get_ai_models(db_session)
        assert len(models) >= 2

        # Получаем только API модели
        api_models = get_ai_models(db_session, is_api=True)
        assert all(model.is_api for model in api_models)

        # Получаем модель по ID
        model = get_ai_model_by_id(db_session, model1.id)  # Используем ID созданной модели
        assert model is not None
        assert model.id == model1.id


class TestTaskCRUD:
    @pytest.fixture
    def test_user(self, db_session):
        """Создает тестового пользователя"""
        user = create_user(
            db_session, username="taskuser", email="task@example.com", password_hash="hash"
        )
        return user

    def test_create_task(self, db_session, test_user):
        """Тест создания задачи"""
        task_data = {
            "user_id": test_user.id,
            "title": "Test Task",
            "description": "Test description",
            "priority": 2,
            "due_date": datetime.now() + timedelta(days=1),
        }

        task = create_task(db_session, **task_data)

        assert task.id is not None
        assert task.title == task_data["title"]
        assert task.user_id == test_user.id
        assert task.status == "created"  # Проверяем значение по умолчанию

    def test_get_tasks_by_user(self, db_session, test_user):
        """Тест получения задач пользователя"""
        # Создаем несколько задач для пользователя
        for i in range(3):
            create_task(
                db_session, user_id=test_user.id, title=f"Task {i}", description=f"Description {i}"
            )

        # Получаем задачи пользователя
        tasks = get_tasks_by_user(db_session, test_user.id)
        assert len(tasks) >= 3
        assert all(task.user_id == test_user.id for task in tasks)

    def test_update_task_status(self, db_session, test_user):
        """Тест обновления статуса задачи"""
        task = create_task(
            db_session,
            user_id=test_user.id,
            title="Status Task",
            description="Task to update status",
        )

        # Проверяем начальный статус
        assert task.status == "created"

        # Обновляем статус
        updated_task = update_task_status(db_session, task.id, "in_progress")
        assert updated_task is not None, "Задача не найдена в базе данных"
        assert updated_task.status == "in_progress"

        # Проверяем, что изменения сохранены в БД
        db_session.expire_all()
        task_from_db = db_session.query(Task).filter(Task.id == task.id).first()
        assert task_from_db.status == "in_progress"
