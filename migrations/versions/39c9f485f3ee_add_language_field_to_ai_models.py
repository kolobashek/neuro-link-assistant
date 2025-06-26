"""add_language_field_to_ai_models

Revision ID: 39c9f485f3ee
Revises: 343ecf78d9bf
Create Date: 2025-06-23 16:33:22.794402

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = "39c9f485f3ee"
down_revision: Union[str, None] = "343ecf78d9bf"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Добавляем поле language."""
    # Проверяем есть ли уже поле
    from sqlalchemy import inspect

    connection = op.get_bind()
    inspector = inspect(connection)
    existing_columns = [c["name"] for c in inspector.get_columns("ai_models")]

    if "language" not in existing_columns:
        op.add_column(
            "ai_models", sa.Column("language", postgresql.ARRAY(sa.String()), nullable=True)
        )
        print("Добавлено поле language")

    if "api_key_required" not in existing_columns:
        op.add_column(
            "ai_models", sa.Column("api_key_required", sa.Boolean(), nullable=True, default=False)
        )
        print("Добавлено поле api_key_required")

    if "is_active" not in existing_columns:
        op.add_column(
            "ai_models", sa.Column("is_active", sa.Boolean(), nullable=True, default=True)
        )
        print("Добавлено поле is_active")


def downgrade() -> None:
    """Удаляем добавленные поля."""
    try:
        op.drop_column("ai_models", "is_active")
        op.drop_column("ai_models", "api_key_required")
        op.drop_column("ai_models", "language")
    except:
        pass
