"""add_role_column_to_users

Revision ID: 5308b4d57cde
Revises: b0afe86a69c1
Create Date: 2025-06-22 12:25:00.000000

"""

import sqlalchemy as sa
from alembic import op
from sqlalchemy import inspect

# revision identifiers, used by Alembic.
revision = "5308b4d57cde"
down_revision = "b0afe86a69c1"
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Добавляем столбец role в таблицу users если его нет."""

    # Получаем соединение и инспектор
    connection = op.get_bind()
    inspector = inspect(connection)

    try:
        # Проверяем существующие столбцы
        columns = [c["name"] for c in inspector.get_columns("users")]

        if "role" not in columns:
            print("🔧 Добавляем столбец role в таблицу users...")
            op.add_column("users", sa.Column("role", sa.String(50), nullable=True, default="user"))
            print("✅ Столбец role успешно добавлен")
        else:
            print("⚠️ Столбец role уже существует в таблице users")

    except Exception as e:
        print(f"❌ Ошибка при добавлении столбца role: {e}")
        raise


def downgrade() -> None:
    """Удаляем столбец role из таблицы users."""

    # Получаем соединение и инспектор
    connection = op.get_bind()
    inspector = inspect(connection)

    try:
        # Проверяем существующие столбцы
        columns = [c["name"] for c in inspector.get_columns("users")]

        if "role" in columns:
            print("🔧 Удаляем столбец role из таблицы users...")
            op.drop_column("users", "role")
            print("✅ Столбец role успешно удален")
        else:
            print("⚠️ Столбец role не найден в таблице users")

    except Exception as e:
        print(f"❌ Ошибка при удалении столбца role: {e}")
        raise
