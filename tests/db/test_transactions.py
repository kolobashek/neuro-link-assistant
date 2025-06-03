import pytest
from sqlalchemy.exc import IntegrityError

from core.db.repository.task_repository import TaskRepository
from core.db.repository.user_repository import UserRepository
from core.db.transaction import TransactionManager, transaction


class TestTransactions:
    @pytest.fixture
    def repositories(self, db_session):
        """Создает репозитории для тестирования"""
        return {
            "user_repo": UserRepository(db_session),
            "task_repo": TaskRepository(db_session),
            "transaction": TransactionManager(db_session),
        }

    def test_successful_transaction(self, db_session, repositories):
        """Тест успешной транзакции"""
        user_repo = repositories["user_repo"]
        task_repo = repositories["task_repo"]
        tx = repositories["transaction"]

        # Выполняем несколько операций в одной транзакции
        with tx.begin():
            user = user_repo.create(
                username="tx_user", email="tx_user@example.com", password_hash="hash"
            )
            _ = task_repo.create(
                user_id=user.id, title="Transaction Task", description="Task created in transaction"
            )

        # Проверяем, что изменения сохранены в БД
        retrieved_user = user_repo.get_by_username("tx_user")
        assert retrieved_user is not None

        user_tasks = task_repo.get_by_user(retrieved_user.id)
        assert len(user_tasks) == 1
        assert user_tasks[0].title == "Transaction Task"

    def test_transaction_rollback(self, db_session, repositories):
        """Тест отката транзакции при ошибке"""
        user_repo = repositories["user_repo"]
        task_repo = repositories["task_repo"]
        tx = repositories["transaction"]

        # Создаем пользователя вне транзакции
        existing_user = user_repo.create(
            username="existing_user", email="existing@example.com", password_hash="hash"
        )

        # ✅ ИСПРАВЛЕНИЕ: Сохраняем ID до транзакции
        existing_user_id = existing_user.id

        # Пытаемся создать пользователя с тем же именем в транзакции
        with pytest.raises(IntegrityError):
            with tx.begin():
                # Эта операция должна пройти успешно
                _ = task_repo.create(
                    user_id=existing_user_id,  # ✅ Используем ID вместо объекта
                    title="Task Before Error",
                    description="This task should not be saved",
                )

                # Эта операция должна вызвать ошибку и откатить транзакцию
                _ = user_repo.create(
                    username="existing_user",  # Дублирующееся имя
                    email="another@example.com",
                    password_hash="hash",
                )

        # Проверяем, что задача не была сохранена (транзакция откатилась)
        user_tasks = task_repo.get_by_user(existing_user_id)  # ✅ Используем ID
        assert len(user_tasks) == 0

    def test_nested_transactions(self, db_session, repositories):
        """Тест вложенных транзакций"""
        user_repo = repositories["user_repo"]
        task_repo = repositories["task_repo"]
        tx = repositories["transaction"]

        with tx.begin():
            # Создаем пользователя во внешней транзакции
            user = user_repo.create(
                username="outer_tx_user", email="outer@example.com", password_hash="hash"
            )

            # Вложенная транзакция (должна быть savepoint)
            with tx.begin():
                # Создаем задачу во вложенной транзакции
                _ = task_repo.create(
                    user_id=user.id,
                    title="Nested Transaction Task",
                    description="Task created in nested transaction",
                )

            # Создаем еще одну задачу во внешней транзакции
            _ = task_repo.create(
                user_id=user.id,
                title="Outer Transaction Task",
                description="Task created in outer transaction",
            )

        # Проверяем, что все изменения сохранены
        retrieved_user = user_repo.get_by_username("outer_tx_user")
        assert retrieved_user is not None

        user_tasks = task_repo.get_by_user(retrieved_user.id)
        assert len(user_tasks) == 2

    def test_transaction_decorator(self, db_session, repositories):
        """Тест использования декоратора транзакций"""
        user_repo = repositories["user_repo"]
        task_repo = repositories["task_repo"]

        # Определяем функцию с декоратором транзакции
        @transaction(db_session)
        def create_user_with_tasks(username, email):
            user = user_repo.create(username=username, email=email, password_hash="hash")

            for i in range(3):
                task_repo.create(
                    user_id=user.id,
                    title=f"Task {i} for {username}",
                    description=f"Description {i}",
                )

            return user

        # Вызываем функцию, которая должна выполниться в транзакции
        user = create_user_with_tasks("decorator_user", "decorator@example.com")

        # Проверяем, что все операции выполнены успешно
        assert user is not None
        assert user.username == "decorator_user"

        # Проверяем, что задачи созданы
        tasks = task_repo.get_by_user(user.id)
        assert len(tasks) == 3

    def test_transaction_decorator_rollback(self, db_session, repositories):
        """Тест отката транзакции при использовании декоратора"""
        user_repo = repositories["user_repo"]
        task_repo = repositories["task_repo"]

        # Создаем пользователя для вызова ошибки дубликата
        user_repo.create(
            username="existing_decorator_user",
            email="existing_decorator@example.com",
            password_hash="hash",
        )

        # Определяем функцию с декоратором транзакции, которая вызовет ошибку
        @transaction(db_session)
        def create_duplicate_user():
            # Сначала создаем задачу
            _ = task_repo.create(
                user_id=1,  # Предполагаем, что ID 1 существует
                title="Task before error",
                description="Should be rolled back",
            )

            # Затем пытаемся создать пользователя с дублирующимся именем
            user = user_repo.create(
                username="existing_decorator_user",  # Дублирующееся имя
                email="another_decorator@example.com",
                password_hash="hash",
            )

            return user

        # Вызываем функцию и ожидаем ошибку
        with pytest.raises(IntegrityError):
            create_duplicate_user()

        # Проверяем, что задача не была создана (транзакция откатилась)
        tasks = task_repo.get_by_user(1)
        assert not any(task.title == "Task before error" for task in tasks)
