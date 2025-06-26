"""add_missing_fields_to_ai_models

Revision ID: ab8cfc8817f6
Revises: 39c9f485f3ee
Create Date: 2025-06-23 16:51:34.300480

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = "ab8cfc8817f6"
down_revision: Union[str, None] = "39c9f485f3ee"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Добавляем недостающие поля."""
    # Проверяем какие поля уже есть
    from sqlalchemy import inspect

    connection = op.get_bind()
    inspector = inspect(connection)
    existing_columns = [c["name"] for c in inspector.get_columns("ai_models")]

    print(f"🔍 Существующие поля: {existing_columns}")

    # Добавляем недостающие поля
    if "language" not in existing_columns:
        op.add_column(
            "ai_models", sa.Column("language", postgresql.ARRAY(sa.String()), nullable=True)
        )
        print("✅ Добавлено поле: language")

    if "api_key_required" not in existing_columns:
        op.add_column(
            "ai_models", sa.Column("api_key_required", sa.Boolean(), nullable=True, default=False)
        )
        print("✅ Добавлено поле: api_key_required")

    if "is_active" not in existing_columns:
        op.add_column(
            "ai_models", sa.Column("is_active", sa.Boolean(), nullable=True, default=True)
        )
        print("✅ Добавлено поле: is_active")

    # Устанавливаем значения по умолчанию для существующих записей
    op.execute("UPDATE ai_models SET api_key_required = false WHERE api_key_required IS NULL")
    op.execute("UPDATE ai_models SET is_active = true WHERE is_active IS NULL")


def downgrade() -> None:
    """Удаляем добавленные поля."""
    try:
        op.drop_column("ai_models", "is_active")
        op.drop_column("ai_models", "api_key_required")
        op.drop_column("ai_models", "language")
    except:
        pass  # Поля могут не существовать
