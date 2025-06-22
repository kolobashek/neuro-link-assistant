import os

from dotenv import load_dotenv
from sqlalchemy import create_engine, text

load_dotenv()

DATABASE_URL = os.environ.get(
    "DATABASE_URL", "postgresql://neurolink:secure_password@localhost:5432/neurolink"
)

print(f"Подключаемся к: {DATABASE_URL}")

try:
    engine = create_engine(DATABASE_URL)

    with engine.connect() as conn:
        # Проверяем текущую версию
        result = conn.execute(text("SELECT version_num FROM alembic_version;"))
        current_version = result.fetchone()
        print(f"Текущая версия: {current_version}")

        # Удаляем неправильную версию и устанавливаем правильную
        conn.execute(text("DELETE FROM alembic_version;"))
        conn.execute(text("INSERT INTO alembic_version (version_num) VALUES ('5308b4d57cde');"))
        conn.commit()

        print("✅ Версия исправлена на 5308b4d57cde")

except Exception as e:
    print(f"❌ Ошибка: {e}")
    print("Возможно БД недоступна или таблица не существует")

    # Пробуем создать таблицу
    try:
        with engine.connect() as conn:
            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS alembic_version (
                    version_num VARCHAR(32) NOT NULL
                );
            """))
            conn.execute(text("INSERT INTO alembic_version (version_num) VALUES ('5308b4d57cde');"))
            conn.commit()
            print("✅ Таблица alembic_version создана")
    except Exception as e2:
        print(f"❌ Не удалось создать таблицу: {e2}")
