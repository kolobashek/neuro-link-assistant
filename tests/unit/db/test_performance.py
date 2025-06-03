import time

import pytest
from sqlalchemy import text

# Удалён импорт get_db
from core.db.crud import create_ai_model, create_task, create_user
from core.db.models import Task, User  # noqa: F401, AIModel удалён, если не нужен

# Удалён импорт Session


class TestDatabasePerformance:
    @pytest.fixture
    def populated_db(self, db_session):
        """Создает набор тестовых данных"""
        # Создаем пользователя
        user = create_user(
            db_session, username="perftest", email="perf@example.com", password_hash="hash"
        )

        # Создаем моделb ИИ
        model = create_ai_model(db_session, name="Perf Model", provider="Test", is_api=True)

        # Создаем набор задач
        tasks = []
        for i in range(100):  # Создаем 100 задач для тестов производительности
            task = create_task(
                db_session,
                user_id=user.id,
                title=f"Task {i}",
                description=f"Description for performance test task {i}",
            )
            tasks.append(task)

        return user, model, tasks

    def test_select_performance(self, db_session, populated_db):
        """Тест производительности выборки данных"""
        user, _, _ = populated_db

        # Замеряем время выполнения запроса
        start_time = time.time()
        result = db_session.query(Task).filter(Task.user_id == user.id).all()
        end_time = time.time()

        # Проверяем, что запрос выполнялся быстро
        duration = end_time - start_time
        assert duration < 0.1, f"Выборка задач пользователя заняла {duration} сек (порог: 0.1 сек)"
        assert len(result) == 100, "Должно быть возвращено 100 задач"

    def test_join_performance(self, db_session, populated_db):
        """Тест производительности запросов с JOIN"""
        user, _, _ = populated_db

        # Запрос с соединением таблиц
        start_time = time.time()
        result = (
            db_session.query(Task, User)
            .join(User, Task.user_id == User.id)
            .filter(User.id == user.id)
            .all()
        )
        end_time = time.time()

        duration = end_time - start_time
        assert duration < 0.2, f"JOIN-запрос занял {duration} сек (порог: 0.2 сек)"
        assert len(result) == 100, "Должно быть возвращено 100 задач с данными пользователя"

    def test_complex_query_performance(self, db_session, populated_db):
        """Тест производительности сложных запросов"""
        user, _, _ = populated_db

        start_time = time.time()
        # Более сложный запрос с группировкой и агрегацией
        result = (
            db_session.query(Task.status, text("COUNT(*) as task_count"))
            .filter(Task.user_id == user.id)
            .group_by(Task.status)
            .all()
        )
        end_time = time.time()

        duration = end_time - start_time
        assert duration < 0.2, f"Сложный запрос занял {duration} сек (порог: 0.2 сек)"
        # Добавляем проверку, чтобы использовать результат
        assert len(result) > 0, "Запрос должен вернуть хотя бы одну строку"

    def test_transaction_performance(self, db_session, populated_db):
        """Тест производительности транзакций"""
        user, _, _ = populated_db

        start_time = time.time()
        # Обновляем несколько задач в одной транзакции
        tasks_to_update = db_session.query(Task).filter(Task.user_id == user.id).limit(10).all()
        for task in tasks_to_update:
            task.status = "in_progress"
        db_session.commit()
        end_time = time.time()

        duration = end_time - start_time
        assert duration < 0.3, f"Транзакция обновления заняла {duration} сек (порог: 0.3 сек)"

        # Проверяем, что изменения сохранились
        updated_count = (
            db_session.query(Task)
            .filter(Task.user_id == user.id, Task.status == "in_progress")
            .count()
        )
        assert updated_count == 10, "Должно быть обновлено 10 задач"
