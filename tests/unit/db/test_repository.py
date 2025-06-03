from datetime import datetime, timedelta

import pytest

# from core.db.models import Task, User, Workflow, WorkflowStep
from core.db.repository.task_repository import TaskRepository
from core.db.repository.user_repository import UserRepository
from core.db.repository.workflow_repository import WorkflowRepository


class TestUserRepository:
    def test_user_repository_operations(self, db_session):
        """Тест операций репозитория пользователей"""
        user_repo = UserRepository(db_session)

        # Создаем пользователя
        user = user_repo.create(
            username="repo_user",
            email="repo@example.com",
            password_hash="hashed_password",
            display_name="Repository Test User",
        )

        # Получаем пользователя по ID
        retrieved_user = user_repo.get_by_id(user.id)
        assert retrieved_user is not None
        assert retrieved_user.id == user.id

        # Получаем пользователя по имени
        user_by_name = user_repo.get_by_username("repo_user")
        assert user_by_name is not None
        assert user_by_name.id == user.id

        # Обновляем пользователя
        updated_user = user_repo.update(user.id, display_name="Updated Name", bio="New bio")
        assert updated_user.display_name == "Updated Name"
        assert updated_user.bio == "New bio"

        # Проверка обновления в БД
        db_session.expire_all()
        user_from_db = user_repo.get_by_id(user.id)
        assert user_from_db.display_name == "Updated Name"

    def test_user_repository_search(self, db_session):
        """Тест поиска пользователей"""
        user_repo = UserRepository(db_session)

        # Создаем несколько пользователей с похожими именами
        user_repo.create(username="john_doe", email="john@example.com", password_hash="hash1")
        user_repo.create(username="jane_doe", email="jane@example.com", password_hash="hash2")
        user_repo.create(username="john_smith", email="jsmith@example.com", password_hash="hash3")

        # Поиск по части имени пользователя
        users_john = user_repo.search_by_name("john")
        assert len(users_john) == 2
        assert all("john" in user.username.lower() for user in users_john)

        # Поиск по email домену
        users_example = user_repo.search_by_email("example.com")
        assert len(users_example) == 3

        # Поиск с несколькими критериями
        users_filtered = user_repo.search(username="doe", limit=10)
        assert len(users_filtered) == 2
        assert all("doe" in user.username.lower() for user in users_filtered)


class TestTaskRepository:
    @pytest.fixture
    def test_user(self, db_session):
        """Создает тестового пользователя для задач"""
        user_repo = UserRepository(db_session)
        return user_repo.create(
            username="task_repo_user", email="taskrepo@example.com", password_hash="hash"
        )

    def test_task_repository_basic_operations(self, db_session, test_user):
        """Тест основных операций репозитория задач"""
        task_repo = TaskRepository(db_session)

        # Создаем задачу
        task = task_repo.create(
            user_id=test_user.id,
            title="Repository Task",
            description="Task for repository testing",
            priority=2,
            due_date=datetime.now() + timedelta(days=2),
        )

        # Получаем задачу по ID
        retrieved_task = task_repo.get_by_id(task.id)
        assert retrieved_task is not None
        assert retrieved_task.id == task.id
        assert retrieved_task.title == "Repository Task"

        # Обновляем задачу
        updated_task = task_repo.update(task.id, title="Updated Repository Task", priority=3)
        assert updated_task.title == "Updated Repository Task"
        assert updated_task.priority == 3

        # Проверяем, что изменения сохранены в БД
        db_session.expire_all()
        task_from_db = task_repo.get_by_id(task.id)
        assert task_from_db.title == "Updated Repository Task"

        # Отмечаем задачу как выполненную
        completed_task = task_repo.mark_as_completed(task.id)
        assert completed_task.status == "completed"
        assert completed_task.completed_at is not None

        # Удаляем задачу
        result = task_repo.delete(task.id)
        assert result is True

        # Проверяем, что задача удалена
        assert task_repo.get_by_id(task.id) is None

    def test_task_repository_filtering(self, db_session, test_user):
        """Тест фильтрации задач"""
        task_repo = TaskRepository(db_session)

        # Создаем несколько задач с разными статусами и приоритетами
        for i in range(5):
            task_repo.create(
                user_id=test_user.id, title=f"High priority task {i}", priority=3, status="created"
            )

        for i in range(3):
            task_repo.create(
                user_id=test_user.id,
                title=f"Medium priority task {i}",
                priority=2,
                status="in_progress",
            )

        for i in range(2):
            task = task_repo.create(
                user_id=test_user.id, title=f"Low priority task {i}", priority=1, status="created"
            )
            task_repo.mark_as_completed(task.id)

        # Фильтрация по статусу
        created_tasks = task_repo.get_by_status(test_user.id, "created")
        assert len(created_tasks) == 5
        assert all(task.status == "created" for task in created_tasks)

        # Фильтрация по приоритету
        high_priority_tasks = task_repo.get_by_priority(test_user.id, 3)
        assert len(high_priority_tasks) == 5
        assert all(task.priority == 3 for task in high_priority_tasks)

        # Фильтрация по статусу и приоритету
        filtered_tasks = task_repo.get_by_filters(
            user_id=test_user.id, status="in_progress", priority=2
        )
        assert len(filtered_tasks) == 3
        assert all(task.status == "in_progress" and task.priority == 2 for task in filtered_tasks)

        # Получение задач с сортировкой
        sorted_tasks = task_repo.get_by_user_sorted(
            user_id=test_user.id, sort_by="priority", sort_order="desc"
        )

        # Проверяем, что задачи отсортированы по приоритету по убыванию
        priorities = [task.priority for task in sorted_tasks]
        assert priorities == sorted(priorities, reverse=True)


class TestWorkflowRepository:
    @pytest.fixture
    def test_user(self, db_session):
        """Создает тестового пользователя для рабочих процессов"""
        user_repo = UserRepository(db_session)
        return user_repo.create(
            username="workflow_repo_user", email="workflowrepo@example.com", password_hash="hash"
        )

    def test_workflow_repository_operations(self, db_session, test_user):
        """Тест операций репозитория рабочих процессов"""
        workflow_repo = WorkflowRepository(db_session)

        # Создаем рабочий процесс
        workflow = workflow_repo.create(
            user_id=test_user.id,
            name="Test Workflow",
            description="Workflow for repository testing",
        )

        assert workflow.id is not None
        assert workflow.name == "Test Workflow"

        # Добавляем шаги рабочего процесса
        step1 = workflow_repo.add_step(
            workflow_id=workflow.id,
            name="Step 1",
            description="First step",
            order=1,
            configuration={"action": "collect_data", "parameters": {"source": "web"}},
        )

        step2 = workflow_repo.add_step(
            workflow_id=workflow.id,
            name="Step 2",
            description="Second step",
            order=2,
            configuration={"action": "process_data", "parameters": {"method": "summarize"}},
        )

        # Получаем рабочий процесс с шагами
        retrieved_workflow = workflow_repo.get_by_id_with_steps(workflow.id)
        assert retrieved_workflow is not None
        assert len(retrieved_workflow.steps) == 2

        # Проверяем порядок шагов
        steps = sorted(retrieved_workflow.steps, key=lambda s: s.order)
        assert steps[0].name == "Step 1"
        assert steps[1].name == "Step 2"

        # Обновляем рабочий процесс
        updated_workflow = workflow_repo.update(
            workflow.id, name="Updated Workflow", is_active=True
        )
        assert updated_workflow.name == "Updated Workflow"
        assert updated_workflow.is_active is True

        # Обновляем шаг
        updated_step = workflow_repo.update_step(
            step1.id,
            name="Updated Step 1",
            configuration={
                "action": "collect_data",
                "parameters": {"source": "api", "format": "json"},
            },
        )
        assert updated_step.name == "Updated Step 1"
        assert updated_step.configuration["parameters"]["source"] == "api"

        # Удаляем шаг
        result = workflow_repo.delete_step(step2.id)
        assert result is True

        # Проверяем, что шаг удален
        updated_workflow = workflow_repo.get_by_id_with_steps(workflow.id)
        assert len(updated_workflow.steps) == 1

        # Удаляем рабочий процесс
        result = workflow_repo.delete(workflow.id)
        assert result is True

        # Проверяем, что рабочий процесс удален
        assert workflow_repo.get_by_id(workflow.id) is None
