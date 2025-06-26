"""add_huggingface_fields_to_ai_models

Revision ID: 343ecf78d9bf
Revises: d09550ca714f
Create Date: 2025-06-23 10:29:18.476611

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy import inspect

# revision identifiers, used by Alembic.
revision: str = "343ecf78d9bf"
down_revision: Union[str, None] = "d09550ca714f"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Добавляем поля для HuggingFace интеграции."""

    connection = op.get_bind()
    inspector = inspect(connection)

    try:
        # Получаем существующие столбцы
        columns = [c["name"] for c in inspector.get_columns("ai_models")]

        # Добавляем недостающие столбцы
        fields_to_add = [
            ("full_name", sa.String(255)),
            ("hf_model_id", sa.String(255)),
            ("hf_url", sa.String(500)),
            ("author", sa.String(255)),
            ("description", sa.Text()),
            ("tags", sa.JSON()),
            ("downloads", sa.Integer(), {"default": 0}),
            ("likes", sa.Integer(), {"default": 0}),
            ("pipeline_tag", sa.String(100)),
            ("model_size", sa.String(50)),
            ("license", sa.String(100)),
            ("library_name", sa.String(100)),
            ("model_type", sa.String(100)),
            ("is_featured", sa.Boolean(), {"default": False}),
            ("created_at_hf", sa.DateTime(timezone=True)),
            ("last_modified_hf", sa.DateTime(timezone=True)),
            ("last_sync_at", sa.DateTime(timezone=True)),
            ("sync_status", sa.String(50), {"default": "pending"}),
            ("sync_error", sa.Text()),
        ]

        for field_name, field_type, *options in fields_to_add:
            if field_name not in columns:
                print(f"🔧 Добавляем поле {field_name}...")
                kwargs = options[0] if options else {}
                op.add_column("ai_models", sa.Column(field_name, field_type, **kwargs))
                print(f"✅ Поле {field_name} добавлено")
            else:
                print(f"⚠️ Поле {field_name} уже существует")

        # Добавляем индексы
        existing_indexes = [idx["name"] for idx in inspector.get_indexes("ai_models")]
        if "ix_ai_models_hf_model_id" not in existing_indexes:
            print("🔧 Создаем индекс для hf_model_id...")
            op.create_index("ix_ai_models_hf_model_id", "ai_models", ["hf_model_id"])
            print("✅ Индекс создан")

    except Exception as e:
        print(f"❌ Ошибка при добавлении полей: {e}")
        raise


def downgrade() -> None:
    """Удаляем поля HuggingFace интеграции."""

    connection = op.get_bind()
    inspector = inspect(connection)

    try:
        # Удаляем индексы
        existing_indexes = [idx["name"] for idx in inspector.get_indexes("ai_models")]
        if "ix_ai_models_hf_model_id" in existing_indexes:
            op.drop_index("ix_ai_models_hf_model_id", "ai_models")

        # Удаляем столбцы
        columns = [c["name"] for c in inspector.get_columns("ai_models")]

        fields_to_remove = [
            "full_name",
            "hf_model_id",
            "hf_url",
            "author",
            "description",
            "tags",
            "downloads",
            "likes",
            "pipeline_tag",
            "model_size",
            "license",
            "library_name",
            "model_type",
            "is_featured",
            "created_at_hf",
            "last_modified_hf",
            "last_sync_at",
            "sync_status",
            "sync_error",
        ]

        for field_name in fields_to_remove:
            if field_name in columns:
                print(f"🔧 Удаляем поле {field_name}...")
                op.drop_column("ai_models", field_name)
                print(f"✅ Поле {field_name} удалено")

    except Exception as e:
        print(f"❌ Ошибка при удалении полей: {e}")
        raise
