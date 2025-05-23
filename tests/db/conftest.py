import psycopg2
import pytest
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from core.db.crud import create_user
from core.db.models import Base


@pytest.fixture(scope="module")
def db_engine():
    """
    Создает тестовый движок БД с изолированной тестовой базой данных.

    Эта фикстура:
    1. Подключается к PostgreSQL
    2. Создает отдельную тестовую БД, если она не существует
    3. Настраивает схему таблиц
    4. Очищает таблицы после всех тестов
    """
    # Настройки подключения
    db_user = "neurolink"
    db_password = "secure_password"
    db_host = "localhost"
    db_port = "5432"

    test_db_name = "neurolink_test_db"
    # Создаем тестовую БД, если она не существует
    conn = psycopg2.connect(
        user=db_user,
        password=db_password,
        host=db_host,
        port=db_port,
        database="neurolink_db",  # Основная БД для начального подключения
    )
    conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
    cursor = conn.cursor()

    cursor.execute("SELECT 1 FROM pg_catalog.pg_database WHERE datname = %s", (test_db_name,))
    db_exists = cursor.fetchone()
    if not db_exists:
        cursor.execute(f"CREATE DATABASE {test_db_name}")
    cursor.close()
    conn.close()
    # Подключаемся к тестовой БД и создаем схему
    test_db_url = f"postgresql://{db_user}:{db_password}@{db_host}:{db_port}/{test_db_name}"
    engine = create_engine(test_db_url)
    # Создаем все таблицы
    Base.metadata.create_all(engine)

    yield engine

    # Удаляем таблицы после всех тестов
    Base.metadata.drop_all(engine)


@pytest.fixture
def db_session(db_engine):
    """
    Создает изолированную сессию БД для каждого теста.

    Каждый тест получает "чистую" транзакцию, которая откатывается после
    завершения теста, обеспечивая изоляцию между тестами.
    """
    connection = db_engine.connect()
    transaction = connection.begin()
    session = Session(bind=connection)

    yield session

    # Правильный порядок закрытия ресурсов
    session.close()
    if transaction.is_active:
        transaction.rollback()
    connection.close()


@pytest.fixture
def test_user(db_session):
    """
    Создает тестового пользователя для использования в тестах.

    Внимание: если тесту нужно видеть этого пользователя в БД,
    необходимо сделать commit в фикстуре.
    """
    user_data = {
        "username": "test_user",
        "email": "test@example.com",
        "password_hash": "hashed_password",
    }

    user = create_user(db_session, **user_data)
    db_session.commit()  # Важно: делаем commit, чтобы пользователь был доступен в БД

    return user
