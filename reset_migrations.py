import os

from dotenv import load_dotenv
from sqlalchemy import create_engine, text

load_dotenv()

DATABASE_URL = os.environ.get(
    "DATABASE_URL", "postgresql://neurolink:secure_password@localhost:5432/neurolink"
)
engine = create_engine(DATABASE_URL)

try:
    with engine.connect() as conn:
        # Удаляем таблицу версий
        conn.execute(text("DROP TABLE IF EXISTS alembic_version;"))
        conn.commit()
        print("✅ Таблица alembic_version удалена")

except Exception as e:
    print(f"Ошибка: {e}")
