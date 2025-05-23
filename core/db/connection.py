import os

from sqlalchemy import create_engine

# from sqlalchemy.ext.declarative import declarative_base
# Базовый класс для моделей
from sqlalchemy.orm import DeclarativeBase, sessionmaker

# Получаем URL для подключения к базе данных из переменной окружения или используем значение по умолчанию
DATABASE_URL = os.environ.get(
    "DATABASE_URL", "postgresql://postgres:postgres@localhost/neurolink_db"
)

# Создаем движок SQLAlchemy
engine = create_engine(DATABASE_URL)

# Создаем фабрику сессий
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class Base(DeclarativeBase):
    pass


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
