"""fix_updated_at_constraint

Revision ID: 9409f9926cd0
Revises: ab8cfc8817f6
Create Date: 2025-06-23 16:59:56.970361

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy import text

# revision identifiers, used by Alembic.
revision: str = "9409f9926cd0"
down_revision: Union[str, None] = "ab8cfc8817f6"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Исправляем constraint для updated_at."""

    # Устанавливаем значение по умолчанию для updated_at
    op.execute(
        "UPDATE ai_models SET updated_at = COALESCE(updated_at, NOW()) WHERE updated_at IS NULL"
    )

    # ✅ ИСПРАВЛЕНО: используем text() для SQL выражения
    op.alter_column(
        "ai_models",
        "updated_at",
        existing_type=sa.DateTime(timezone=True),
        server_default=text("NOW()"),  # ✅ Правильный тип
        nullable=True,
    )


def downgrade() -> None:
    """Откатываем изменения."""
    # ✅ ИСПРАВЛЕНО: убираем server_default полностью
    op.alter_column(
        "ai_models",
        "updated_at",
        existing_type=sa.DateTime(timezone=True),
        # server_default убран - это и есть способ удалить default
    )
