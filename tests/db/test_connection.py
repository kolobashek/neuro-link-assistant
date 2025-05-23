import psycopg2
import pytest
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
from sqlalchemy import create_engine, inspect
from sqlalchemy.orm import Session

from core.db.connection import get_db
from core.db.models import Base  # Импортируем ваши модели


@pytest.fixture(scope="module")
def db_engine():
    """Создает тестовый движок БД"""

    # Формируем строку подключения с правильными учетными данными
    # но сохраняем логику использования отдельной тестовой БД
    db_user = "neurolink"
    db_password = "secure_password"
    db_host = "localhost"
    db_port = "5432"

    # Используем тестовую БД с тем же именем, что и в исходном коде
    test_db_name = "neurolink_test_db"

    # Сначала подключаемся к базе данных postgres для создания тестовой БД
    conn = psycopg2.connect(
        user=db_user,
        password=db_password,
        host=db_host,
        port=db_port,
        database="neurolink_db",  # Подключаемся к существующей БД
    )
    conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)  # Важно для создания БД
    cursor = conn.cursor()

    # Проверяем, существует ли БД, и если нет - создаем
    cursor.execute("SELECT 1 FROM pg_catalog.pg_database WHERE datname = %s", (test_db_name,))
    db_exists = cursor.fetchone()
    if not db_exists:
        cursor.execute(f"CREATE DATABASE {test_db_name}")

    cursor.close()
    conn.close()

    # Теперь подключаемся к созданной тестовой БД
    test_db_url = f"postgresql://{db_user}:{db_password}@{db_host}:{db_port}/{test_db_name}"
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
