"""add_role_column_to_users_fix

Revision ID: d09550ca714f
Revises: 5308b4d57cde
Create Date: 2025-06-22 14:30:00.000000

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "d09550ca714f"
down_revision: Union[str, None] = "5308b4d57cde"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Проверяем, есть ли уже поле role в таблице users
    conn = op.get_bind()
    inspector = sa.inspect(conn)
    columns = [col["name"] for col in inspector.get_columns("users")]

    if "role" not in columns:
        # Добавляем поле role если его нет
        op.add_column("users", sa.Column("role", sa.String(50), server_default="user"))
        print("✅ Поле 'role' добавлено в таблицу users")
    else:
        print("⚠️ Поле 'role' уже существует в таблице users")


def downgrade() -> None:
    """Downgrade schema."""
    # Удаляем поле role
    conn = op.get_bind()
    inspector = sa.inspect(conn)
    columns = [col["name"] for col in inspector.get_columns("users")]

    if "role" in columns:
        op.drop_column("users", "role")
        print("✅ Поле 'role' удалено из таблицы users")
