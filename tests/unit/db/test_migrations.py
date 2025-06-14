import os
import subprocess
from urllib.parse import urlparse, urlunparse

import pytest
from alembic.config import Config
from alembic.runtime.migration import MigrationContext
from alembic.script import ScriptDirectory
from sqlalchemy import create_engine, inspect, text

from core.db.connection import DATABASE_URL


class TestMigrations:
    @pytest.fixture
    def alembic_config(self):
        """Создает конфигурацию Alembic"""
        config = Config("alembic.ini")
        return config

    def _create_test_db_url(self, test_db_name):
        """Создает URL для тестовой базы данных с правильным пользователем."""
        parsed = urlparse(DATABASE_URL)

        # Заменяем только имя базы данных, оставляя пользователя neurolink
        new_path = f"/{test_db_name}"

        # Пересобираем URL с новым именем БД
        new_parsed = parsed._replace(path=new_path)
        return urlunparse(new_parsed)

    def test_migrations_history(self, alembic_config):
        """Проверяет, что история миграций непрерывна"""
        script = ScriptDirectory.from_config(alembic_config)

        # Получаем все ревизии
        revisions = list(script.walk_revisions())
        # Проверяем, что каждая ревизия (кроме первой) имеет родителя
        for i, revision in enumerate(revisions[:-1]):  # Пропускаем последнюю (самую раннюю)
            assert (
                revision.down_revision == revisions[i + 1].revision
            ), f"Ревизия {revision.revision} не связана с предыдущей {revisions[i + 1].revision}"

    def test_migrations_apply_cleanly(self):
        """Проверяет, что миграции применяются без ошибок"""
        # Создаем временную БД для тестирования миграций
        test_db_name = f"neurolink_migration_test_{os.getpid()}"
        test_db_url = self._create_test_db_url(test_db_name)

        # Создаем тестовую БД
        main_db_url = self._create_test_db_url("neurolink")
        engine = create_engine(main_db_url)

        with engine.connect() as conn:
            conn.execute(text("COMMIT"))  # Закрываем любую открытую транзакцию
            # Проверяем, существует ли база данных
            result = conn.execute(
                text(f"SELECT 1 FROM pg_database WHERE datname = '{test_db_name}'")
            )
            if not result.fetchone():
                conn.execute(text(f"CREATE DATABASE {test_db_name}"))

        try:
            # Применяем миграции
            env = os.environ.copy()
            env["DATABASE_URL"] = test_db_url

            result = subprocess.run(
                ["alembic", "upgrade", "head"], env=env, capture_output=True, text=True
            )

            assert result.returncode == 0, f"Ошибка при применении миграций: {result.stderr}"

            # Проверяем, что все таблицы созданы
            test_engine = create_engine(test_db_url)
            inspector = inspect(test_engine)
            tables = inspector.get_table_names()

            expected_tables = [
                "users",
                "ai_models",
                "tasks",
                "task_executions",
                "workflows",
                "workflow_steps",
                "routing_rules",
            ]

            for table in expected_tables:
                assert table in tables, f"Таблица {table} не создана миграциями"

        finally:
            # Удаляем тестовую БД
            with engine.connect() as conn:
                conn.execute(text("COMMIT"))
                # Сначала завершаем все соединения с тестовой БД
                conn.execute(text(f"""
                    SELECT pg_terminate_backend(pid)
                    FROM pg_stat_activity
                    WHERE datname = '{test_db_name}' AND pid <> pg_backend_pid()
                """))
                conn.execute(text(f"DROP DATABASE IF EXISTS {test_db_name}"))

    def test_downgrade_migrations(self, alembic_config):
        """Проверяет, что миграции можно откатить"""
        script = ScriptDirectory.from_config(alembic_config)
        revisions = list(script.walk_revisions())

        # Проверяем, что у каждой миграции есть метод downgrade
        for revision in revisions:
            migration_script = script.get_revision(revision.revision)
            assert hasattr(
                migration_script.module, "downgrade"
            ), f"Миграция {revision.revision} не имеет метода downgrade"

        # Создаем временную БД для тестирования отката миграций
        test_db_name = f"neurolink_downgrade_test_{os.getpid()}"
        test_db_url = self._create_test_db_url(test_db_name)

        # Создаем тестовую БД
        main_db_url = self._create_test_db_url("neurolink")
        engine = create_engine(main_db_url)

        with engine.connect() as conn:
            conn.execute(text("COMMIT"))
            # Проверяем, существует ли база данных
            result = conn.execute(
                text(f"SELECT 1 FROM pg_database WHERE datname = '{test_db_name}'")
            )
            if not result.fetchone():
                conn.execute(text(f"CREATE DATABASE {test_db_name}"))

        try:
            env = os.environ.copy()
            env["DATABASE_URL"] = test_db_url

            # Применяем миграции
            upgrade_result = subprocess.run(
                ["alembic", "upgrade", "head"], env=env, capture_output=True, text=True
            )
            assert (
                upgrade_result.returncode == 0
            ), f"Ошибка при применении миграций: {upgrade_result.stderr}"

            # Получаем вторую от начала ревизию (чтобы было куда откатывать)
            revisions = list(script.walk_revisions("base", "head"))
            if len(revisions) >= 2:
                target_revision = revisions[-2].revision

                # Откатываем до предпоследней миграции
                downgrade_result = subprocess.run(
                    ["alembic", "downgrade", target_revision],
                    env=env,
                    capture_output=True,
                    text=True,
                )

                assert (
                    downgrade_result.returncode == 0
                ), f"Ошибка при откате миграций: {downgrade_result.stderr}"

                # Проверяем, что текущая ревизия соответствует ожидаемой
                test_engine = create_engine(test_db_url)
                with test_engine.connect() as conn:
                    context = MigrationContext.configure(conn)
                    current_rev = context.get_current_revision()
                    assert current_rev == target_revision, (
                        f"Откат не удался. Текущая ревизия: {current_rev}, ожидалась:"
                        f" {target_revision}"
                    )

        finally:
            # Удаляем тестовую БД
            with engine.connect() as conn:
                conn.execute(text("COMMIT"))
                # Завершаем соединения и удаляем БД
                conn.execute(text(f"""
                    SELECT pg_terminate_backend(pid)
                    FROM pg_stat_activity
                    WHERE datname = '{test_db_name}' AND pid <> pg_backend_pid()
                """))
                conn.execute(text(f"DROP DATABASE IF EXISTS {test_db_name}"))
