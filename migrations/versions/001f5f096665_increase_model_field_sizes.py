"""increase_model_field_sizes

Revision ID: 001f5f096665
Revises: 9409f9926cd0
Create Date: 2025-06-23 17:51:19.957504

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "001f5f096665"
down_revision: Union[str, None] = "9409f9926cd0"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Увеличиваем размеры полей для HuggingFace данных."""

    # Увеличиваем model_size с 50 до 200 символов
    op.alter_column(
        "ai_models",
        "model_size",
        existing_type=sa.String(50),
        type_=sa.String(200),
        existing_nullable=True,
    )

    # Увеличиваем pipeline_tag для безопасности
    op.alter_column(
        "ai_models",
        "pipeline_tag",
        existing_type=sa.String(100),
        type_=sa.String(200),
        existing_nullable=True,
    )


def downgrade() -> None:
    """Откатываем изменения."""
    op.alter_column(
        "ai_models",
        "model_size",
        existing_type=sa.String(200),
        type_=sa.String(50),
        existing_nullable=True,
    )

    op.alter_column(
        "ai_models",
        "pipeline_tag",
        existing_type=sa.String(200),
        type_=sa.String(100),
        existing_nullable=True,
    )
