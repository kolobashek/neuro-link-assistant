import pytest
from sqlalchemy import create_engine, inspect
from sqlalchemy.orm import Session

from core.db.connection import DATABASE_URL, get_db
from core.db.models import Base  # Импортируем ваши модели


@pytest.fixture(scope="module")
def db_engine():
    """Создает тестовый движок БД"""
    # Используем тестовую БД или ту же с другой схемой
    test_db_url = DATABASE_URL.replace("/neurolink_db", "/neurolink_test_db")
    engine = create_engine(test_db_url)

    # Создаем все таблицы
    Base.metadata.create_all(engine)

    yield engine

    # Удаляем таблицы после тестов
    Base.metadata.drop_all(engine)


@pytest.fixture
def db_session(db_engine):
    """Создает сессию БД для тестов"""
    connection = db_engine.connect()
    # Запускаем транзакцию
    transaction = connection.begin()

    session = Session(bind=connection)

    yield session

    # Откатываем изменения после теста
    session.close()
    transaction.rollback()
    connection.close()


class TestDatabaseConnection:

    def test_connection(self, db_engine):
        """Проверяем подключение к БД"""
        connection = db_engine.connect()
        assert connection is not None
        connection.close()

    def test_tables_exist(self, db_engine):
        """Проверяем, что все необходимые таблицы созданы"""
        inspector = inspect(db_engine)
        tables = inspector.get_table_names()

        # Проверяем наличие ключевых таблиц
        expected_tables = [
            "users",
            "ai_models",
            "tasks",
            "task_executions",
            "workflows",
            "workflow_steps",
            "routing_rules",
        ]

        for table in expected_tables:
            assert table in tables, f"Таблица {table} не найдена в БД"

    def test_db_session_factory(self):
        """Тестирует функцию получения сессии БД"""
        session = next(get_db())
        assert session is not None
        session.close()
