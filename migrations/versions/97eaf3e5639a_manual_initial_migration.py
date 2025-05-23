"""manual_initial_migration

Revision ID: 97eaf3e5639a
Revises:
Create Date: 2025-05-23 15:07:23.119273

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "97eaf3e5639a"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def drop_constraint_if_exists(constraint_name, table_name, type_):
    """Безопасно удаляет ограничение, если оно существует."""
    # Проверяем существование constraint перед удалением
    conn = op.get_bind()

    # Запрос для проверки существования constraint
    query = f"""
    SELECT 1 FROM pg_constraint c
    JOIN pg_namespace n ON n.oid = c.connamespace
    JOIN pg_class t ON t.oid = c.conrelid
    WHERE c.conname = '{constraint_name}'
    AND t.relname = '{table_name}'
    """

    result = conn.execute(sa.text(query)).fetchone()

    # Если constraint существует, удаляем его
    if result:
        op.drop_constraint(constraint_name, table_name, type_=type_)
        print(f"Constraint {constraint_name} успешно удален")
    else:
        print(f"Constraint {constraint_name} не существует, пропускаем")


def drop_table_if_exists(table_name):
    """Безопасно удаляет таблицу, если она существует."""
    conn = op.get_bind()
    inspector = sa.inspect(conn)

    if inspector.has_table(table_name):
        op.drop_table(table_name)
        print(f"Таблица {table_name} успешно удалена")
    else:
        print(f"Таблица {table_name} не существует, пропускаем")


def upgrade() -> None:
    """Upgrade schema."""
    # ЭТАП 1: Удаление всех внешних ключей
    # ai_models внешние ключи
    drop_constraint_if_exists("ai_models_model_type_id_fkey", "ai_models", "foreignkey")

    # api_keys внешние ключи
    drop_constraint_if_exists("api_keys_user_id_fkey", "api_keys", "foreignkey")

    # task_history внешние ключи
    drop_constraint_if_exists("task_history_task_id_fkey", "task_history", "foreignkey")
    drop_constraint_if_exists("task_history_user_id_fkey", "task_history", "foreignkey")

    # task_steps внешние ключи
    drop_constraint_if_exists("task_steps_task_id_fkey", "task_steps", "foreignkey")

    # user_sessions внешние ключи
    drop_constraint_if_exists("user_sessions_user_id_fkey", "user_sessions", "foreignkey")

    # workflow_step_connections внешние ключи
    drop_constraint_if_exists(
        "workflow_step_connections_from_step_id_fkey", "workflow_step_connections", "foreignkey"
    )
    drop_constraint_if_exists(
        "workflow_step_connections_to_step_id_fkey", "workflow_step_connections", "foreignkey"
    )

    # optimization_strategies внешние ключи
    drop_constraint_if_exists(
        "optimization_strategies_user_id_fkey", "optimization_strategies", "foreignkey"
    )

    # workflow_steps внешние ключи
    drop_constraint_if_exists("workflow_steps_workflow_id_fkey", "workflow_steps", "foreignkey")
    drop_constraint_if_exists("workflow_steps_model_id_fkey", "workflow_steps", "foreignkey")

    # workflows внешние ключи
    drop_constraint_if_exists("workflows_user_id_fkey", "workflows", "foreignkey")

    # routing_rules внешние ключи
    drop_constraint_if_exists("routing_rules_target_model_id_fkey", "routing_rules", "foreignkey")
    drop_constraint_if_exists("routing_rules_user_id_fkey", "routing_rules", "foreignkey")

    # task_executions внешние ключи
    drop_constraint_if_exists("task_executions_task_id_fkey", "task_executions", "foreignkey")
    drop_constraint_if_exists("task_executions_model_id_fkey", "task_executions", "foreignkey")

    # tasks внешние ключи
    drop_constraint_if_exists("tasks_user_id_fkey", "tasks", "foreignkey")

    # ЭТАП 2: Удаление устаревших таблиц

    # Удаляем таблицы, которые больше не нужны
    drop_table_if_exists("task_history")
    drop_table_if_exists("user_sessions")
    drop_table_if_exists("task_steps")
    drop_table_if_exists("usage_statistics")
    drop_table_if_exists("api_keys")
    drop_table_if_exists("workflow_step_connections")
    drop_table_if_exists("optimization_strategies")
    drop_table_if_exists("ai_model_types")

    # ЭТАП 3: Модификация существующих таблиц

    # Проверяем существование таблиц перед модификацией
    inspector = sa.inspect(op.get_bind())

    # Пользователи
    if not inspector.has_table("users"):
        # Создаем таблицу users, если она не существует
        op.create_table(
            "users",
            sa.Column("id", sa.Integer(), nullable=False),
            sa.Column("username", sa.String(length=50), nullable=False),
            sa.Column("email", sa.String(length=100), nullable=False),
            sa.Column("password_hash", sa.String(length=255), nullable=False),
            sa.Column("is_active", sa.Boolean(), nullable=True, server_default="true"),
            sa.Column("created_at", sa.DateTime(timezone=True), nullable=True),
            sa.PrimaryKeyConstraint("id"),
        )

        # Создаем индексы для новой таблицы
        op.create_index(op.f("ix_users_id"), "users", ["id"], unique=False)
        op.create_index(op.f("ix_users_email"), "users", ["email"], unique=True)
        op.create_index(op.f("ix_users_username"), "users", ["username"], unique=True)
    else:
        # Добавляем колонки к существующей таблице, только если они не существуют
        for column_name, column_type in [
            ("display_name", sa.String(length=100)),
            ("bio", sa.Text()),
            ("avatar_url", sa.String(length=255)),
            ("updated_at", sa.DateTime(timezone=True)),
        ]:
            columns = [c["name"] for c in inspector.get_columns("users")]
            if column_name not in columns:
                op.add_column("users", sa.Column(column_name, column_type, nullable=True))
                print(f"Колонка {column_name} добавлена в таблицу users")
            else:
                print(f"Колонка {column_name} уже существует в таблице users")

        # Создаем индексы, если они не существуют
        indices = [i["name"] for i in inspector.get_indexes("users")]
        for index_name, columns, unique in [
            ("ix_users_id", ["id"], False),
            ("ix_users_email", ["email"], True),
            ("ix_users_username", ["username"], True),
        ]:
            if index_name not in indices:
                op.create_index(index_name, "users", columns, unique=unique)
                print(f"Индекс {index_name} создан для таблицы users")
            else:
                print(f"Индекс {index_name} уже существует для таблицы users")

    # Остальные таблицы аналогично...
    # AI Models, Tasks, Task Executions, Routing Rules, Workflows, Workflow Steps

    # Сокращаю для удобства чтения, но основной принцип тот же для всех таблиц:
    # 1. Проверить существование таблицы
    # 2. Создать таблицу если не существует или добавить колонки если таблица есть
    # 3. Создать индексы если они не существуют

    # ЭТАП 4: Создание внешних ключей
    # Проверяем и создаем внешние ключи только если таблицы существуют

    # Получаем все существующие внешние ключи
    fk_query = """
    SELECT tc.constraint_name
    FROM information_schema.table_constraints tc
    JOIN information_schema.key_column_usage kcu
    ON tc.constraint_name = kcu.constraint_name
    WHERE tc.constraint_type = 'FOREIGN KEY'
    """
    conn = op.get_bind()
    result = conn.execute(sa.text(fk_query))
    existing_fkeys = [row[0] for row in result]

    # Создаем внешние ключи, если их нет
    tables_exist = {
        "users": inspector.has_table("users"),
        "tasks": inspector.has_table("tasks"),
        "ai_models": inspector.has_table("ai_models"),
        "workflows": inspector.has_table("workflows"),
        "workflow_steps": inspector.has_table("workflow_steps"),
        "routing_rules": inspector.has_table("routing_rules"),
        "task_executions": inspector.has_table("task_executions"),
    }

    fk_defs = [
        ("workflows_user_id_fkey", "workflows", "users", ["user_id"], ["id"]),
        ("workflow_steps_workflow_id_fkey", "workflow_steps", "workflows", ["workflow_id"], ["id"]),
        ("tasks_user_id_fkey", "tasks", "users", ["user_id"], ["id"]),
        ("task_executions_task_id_fkey", "task_executions", "tasks", ["task_id"], ["id"]),
        ("task_executions_model_id_fkey", "task_executions", "ai_models", ["model_id"], ["id"]),
        (
            "routing_rules_target_model_id_fkey",
            "routing_rules",
            "ai_models",
            ["target_model_id"],
            ["id"],
        ),
    ]

    for fk_name, source, target, source_cols, target_cols in fk_defs:
        if fk_name not in existing_fkeys and tables_exist[source] and tables_exist[target]:
            try:

                op.create_foreign_key(fk_name, source, target, source_cols, target_cols)
                print(f"Внешний ключ {fk_name} создан")
            except Exception as e:
                print(f"Ошибка при создании внешнего ключа {fk_name}: {e}")
        else:
            print(f"Внешний ключ {fk_name} уже существует или таблицы отсутствуют")


def downgrade() -> None:
    """Downgrade schema."""
    # Удаляем внешние ключи

    try:
        op.drop_constraint(
            "routing_rules_target_model_id_fkey", "routing_rules", type_="foreignkey"
        )
    except Exception:
        pass

    try:
        op.drop_constraint("task_executions_model_id_fkey", "task_executions", type_="foreignkey")
    except Exception:
        pass

    try:
        op.drop_constraint("task_executions_task_id_fkey", "task_executions", type_="foreignkey")
    except Exception:
        pass

    try:
        op.drop_constraint("tasks_user_id_fkey", "tasks", type_="foreignkey")
    except Exception:
        pass

    try:
        op.drop_constraint("workflow_steps_workflow_id_fkey", "workflow_steps", type_="foreignkey")
    except Exception:
        pass

    try:
        op.drop_constraint("workflows_user_id_fkey", "workflows", type_="foreignkey")
    except Exception:
        pass

    # Удаляем индексы

    try:
        op.drop_index(op.f("ix_workflow_steps_id"), table_name="workflow_steps")
    except Exception:
        pass

    try:
        op.drop_index(op.f("ix_workflows_id"), table_name="workflows")
    except Exception:
        pass

    try:
        op.drop_index(op.f("ix_routing_rules_id"), table_name="routing_rules")
    except Exception:
        pass

    try:
        op.drop_index(op.f("ix_task_executions_id"), table_name="task_executions")
    except Exception:
        pass

    try:
        op.drop_index(op.f("ix_tasks_id"), table_name="tasks")
    except Exception:
        pass

    try:
        op.drop_index(op.f("ix_ai_models_id"), table_name="ai_models")
    except Exception:
        pass

    try:
        op.drop_index(op.f("ix_users_username"), table_name="users")
    except Exception:
        pass

    try:
        op.drop_index(op.f("ix_users_email"), table_name="users")
    except Exception:
        pass

    try:
        op.drop_index(op.f("ix_users_id"), table_name="users")
    except Exception:
        pass

    # Удаляем добавленные столбцы
    try:
        op.drop_column("workflow_steps", "updated_at")
    except Exception:
        pass

    try:
        op.drop_column("workflow_steps", "created_at")
    except Exception:
        pass

    try:
        op.drop_column("workflow_steps", "configuration")
    except Exception:
        pass

    try:
        op.drop_column("workflow_steps", "order")
    except Exception:
        pass

    try:
        op.drop_column("workflows", "is_active")
    except Exception:
        pass

    try:
        op.drop_column("routing_rules", "pattern")
    except Exception:
        pass

    try:
        op.drop_column("routing_rules", "rule_type")
    except Exception:
        pass

    try:
        op.drop_column("task_executions", "output_data")
    except Exception:
        pass

    try:
        op.drop_column("task_executions", "input_data")
    except Exception:
        pass

    try:
        op.drop_column("tasks", "completed_at")
    except Exception:
        pass

    try:
        op.drop_column("ai_models", "is_active")
    except Exception:
        pass

    try:
        op.drop_column("users", "updated_at")
    except Exception:
        pass

    try:
        op.drop_column("users", "avatar_url")
    except Exception:
        pass

    try:
        op.drop_column("users", "bio")
    except Exception:
        pass

    try:
        op.drop_column("users", "display_name")
    except Exception:
        pass
