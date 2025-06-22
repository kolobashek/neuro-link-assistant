"""add_salt_column_to_users

Revision ID: 13ee2f4ed3bb
Revises: 52f69517b81e
Create Date: 2025-06-22 12:08:00.951932

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "13ee2f4ed3bb"
down_revision: Union[str, None] = "52f69517b81e"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Добавляем столбец salt в таблицу users если его еще нет
    conn = op.get_bind()
    inspector = sa.inspect(conn)
    columns = [c["name"] for c in inspector.get_columns("users")]

    if "salt" not in columns:
        op.add_column("users", sa.Column("salt", sa.String(255), nullable=True))
        print("✅ Столбец salt добавлен в таблицу users")
    else:
        print("⚠️ Столбец salt уже существует в таблице users")


def downgrade() -> None:
    """Downgrade schema."""
    # Удаляем столбец salt из таблицы users
    conn = op.get_bind()
    inspector = sa.inspect(conn)
    columns = [c["name"] for c in inspector.get_columns("users")]

    if "salt" in columns:
        op.drop_column("users", "salt")
        print("✅ Столбец salt удален из таблицы users")
    else:
        print("⚠️ Столбец salt не найден в таблице users")
