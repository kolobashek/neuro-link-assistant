import os

from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

# Принудительно загружаем .env файл
load_dotenv()

# Получаем URL для подключения к базе данных из переменной окружения или используем значение по умолчанию
DATABASE_URL = os.environ.get("DATABASE_URL", "postgresql://postgres:postgres@localhost/neurolink")

print(f"Using DATABASE_URL: {DATABASE_URL}")  # Отладочный вывод

# Создаем движок SQLAlchemy
engine = create_engine(DATABASE_URL)

# Создаем фабрику сессий
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class Base(DeclarativeBase):
    pass


def get_engine():
    """
    Возвращает движок SQLAlchemy.
    Полезно для тестов и инициализации.
    """
    return engine


def get_db():
    """
    Генератор для получения сессии базы данных.
    Используется для внедрения зависимостей в FastAPI.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def create_tables():
    """
    Создает все таблицы в базе данных.
    Используется для инициализации схемы.
    """
    Base.metadata.create_all(bind=engine)


def drop_tables():
    """
    Удаляет все таблицы из базы данных.
    Используется для очистки в тестах.
    """
    Base.metadata.drop_all(bind=engine)
