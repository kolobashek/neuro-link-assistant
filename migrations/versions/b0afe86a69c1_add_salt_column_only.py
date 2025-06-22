"""add_salt_column_only

Revision ID: b0afe86a69c1
Revises: 13ee2f4ed3bb
Create Date: 2025-06-22 12:15:00.000000

"""

import sqlalchemy as sa
from alembic import op
from sqlalchemy import inspect

# revision identifiers, used by Alembic.
revision = "b0afe86a69c1"
down_revision = "13ee2f4ed3bb"
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Добавляем столбец salt в таблицу users если его нет."""

    # Получаем соединение и инспектор
    connection = op.get_bind()
    inspector = inspect(connection)

    try:
        # Проверяем существующие столбцы
        columns = [c["name"] for c in inspector.get_columns("users")]

        if "salt" not in columns:
            print("🔧 Добавляем столбец salt в таблицу users...")
            op.add_column("users", sa.Column("salt", sa.String(255), nullable=True))
            print("✅ Столбец salt успешно добавлен")
        else:
            print("⚠️ Столбец salt уже существует в таблице users")

    except Exception as e:
        print(f"❌ Ошибка при добавлении столбца salt: {e}")
        raise


def downgrade() -> None:
    """Удаляем столбец salt из таблицы users."""

    # Получаем соединение и инспектор
    connection = op.get_bind()
    inspector = inspect(connection)

    try:
        # Проверяем существующие столбцы
        columns = [c["name"] for c in inspector.get_columns("users")]

        if "salt" in columns:
            print("🔧 Удаляем столбец salt из таблицы users...")
            op.drop_column("users", "salt")
            print("✅ Столбец salt успешно удален")
        else:
            print("⚠️ Столбец salt не найден в таблице users")

    except Exception as e:
        print(f"❌ Ошибка при удалении столбца salt: {e}")
        raise
