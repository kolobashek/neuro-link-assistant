from datetime import datetime, timedelta

import pytest
from sqlalchemy.exc import DataError, IntegrityError

from core.db.crud import create_ai_model, create_task, create_user
from core.db.models import AIModel, Task, User


class TestDataValidation:
    def test_required_fields(self, db_session):
        """Тест обязательных полей"""
        # Проверка пользователя без обязательного поля
        with pytest.raises(IntegrityError):
            db_session.add(User(email="missing_username@example.com", password_hash="hash"))
            db_session.flush()

        db_session.rollback()

        # Проверка задачи без обязательного поля
        with pytest.raises(IntegrityError):
            db_session.add(Task(description="No title task"))
            db_session.flush()

        db_session.rollback()

        # Проверка модели ИИ без обязательного поля
        with pytest.raises(IntegrityError):
            db_session.add(AIModel(provider="Missing name provider"))
            db_session.flush()

    def test_field_length_limits(self, db_session):
        """Тест ограничений длины полей"""
        # Генерируем строку, превышающую максимальную длину
        long_name = "a" * 256  # Предполагаем, что ограничение username - 100 символов

        with pytest.raises(DataError):
            create_user(
                db_session, username=long_name, email="toolong@example.com", password_hash="hash"
            )

    def test_data_relationships(self, db_session):
        """Тест ограничений внешних ключей"""
        # Пытаемся создать задачу с несуществующим пользователем
        with pytest.raises(IntegrityError):
            create_task(
                db_session,
                user_id=9999,  # Несуществующий ID
                title="Task with invalid user",
                description="This should fail",
            )

    def test_date_validation(self, db_session):
        """Тест валидации дат"""
        # Создаем пользователя
        user = create_user(
            db_session, username="dateuser", email="date@example.com", password_hash="hash"
        )

        # Создаем задачу с прошедшей датой
        past_date = datetime.now() - timedelta(days=30)
        task = create_task(
            db_session,
            user_id=user.id,
            title="Past due task",
            description="Task with past due date",
            due_date=past_date,
        )

        # Проверяем, что дата сохранена корректно
        assert task.due_date.date() == past_date.date()

        # Проверяем работу с текущей датой
        current_task = create_task(
            db_session, user_id=user.id, title="Current task", description="Task with default date"
        )

        assert current_task.created_at is not None
        assert isinstance(current_task.created_at, datetime)

    def test_json_validation(self, db_session):
        """Тест валидации JSON-полей"""
        # Проверяем сохранение и извлечение JSON-данных
        complex_config = {
            "parameters": {"temperature": 0.7, "top_p": 0.9, "max_tokens": 2000},
            "prompts": ["template1", "template2"],
            "enabled_features": ["feature1", "feature2"],
            "nested": {"level1": {"level2": {"value": 42}}},
        }

        model = create_ai_model(
            db_session,
            name="JSON Test Model",
            provider="Test",
            is_api=True,
            configuration=complex_config,
        )

        # Получаем модель заново из БД
        db_session.expire_all()
        retrieved_model = db_session.query(AIModel).filter(AIModel.id == model.id).first()

        # Проверяем, что JSON сохранен и извлечен корректно
        assert retrieved_model.configuration == complex_config
        assert retrieved_model.configuration["parameters"]["temperature"] == 0.7
        assert retrieved_model.configuration["nested"]["level1"]["level2"]["value"] == 42
