import pytest
from core.db.crud import create_task, create_user, get_tasks_with_pagination
from core.db.models import Task, User  # noqa: F401

# Импорт desc удалён, так как не используется


@pytest.fixture
def user_with_many_tasks(db_session):
    """Создает пользователя с большим количеством задач для тестов пагинации"""
    user = create_user(
        db_session, username="pageuser", email="page@example.com", password_hash="hash"
    )

    # Создаем 50 задач разных типов
    for i in range(50):
        status = "completed" if i % 5 == 0 else "in_progress" if i % 3 == 0 else "created"
        priority = (i % 3) + 1  # приоритеты 1, 2, 3

        create_task(
            db_session,
            user_id=user.id,
            title=f"Task {i}",
            description=f"Description {i}",
            status=status,
            priority=priority,
        )

    return user


class TestPaginationAndFiltering:

    def test_basic_pagination(self, db_session, user_with_many_tasks):
        """Тест базовой пагинации"""
        user = user_with_many_tasks

        # Первая страница (10 элементов)
        page1 = get_tasks_with_pagination(db_session, user_id=user.id, page=1, per_page=10)
        assert len(page1.items) == 10
        assert page1.total == 50
        assert page1.pages == 5

        assert page1.has_next is True  # Исправлено: == True -> is True
        assert page1.has_prev is False  # Исправлено: == False -> is False

        # Вторая страница
        page2 = get_tasks_with_pagination(db_session, user_id=user.id, page=2, per_page=10)
        assert len(page2.items) == 10
        assert page2.page == 2

        assert page2.has_next is True  # Исправлено: == True -> is True
        assert page2.has_prev is True  # Исправлено: == True -> is True

        # Проверяем, что элементы разные на разных страницах
        page1_ids = [task.id for task in page1.items]
        page2_ids = [task.id for task in page2.items]
        assert not set(page1_ids).intersection(set(page2_ids))

        # Последняя страница
        page5 = get_tasks_with_pagination(db_session, user_id=user.id, page=5, per_page=10)
        assert len(page5.items) == 10

        assert page5.has_next is False  # Исправлено: == False -> is False
        assert page5.has_prev is True  # Исправлено: == True -> is True

    def test_pagination_with_filtering(self, db_session, user_with_many_tasks):
        """Тест пагинации с фильтрацией"""
        user = user_with_many_tasks

        # Фильтруем по статусу "completed"
        completed_tasks = get_tasks_with_pagination(
            db_session, user_id=user.id, page=1, per_page=10, status="completed"
        )

        assert all(task.status == "completed" for task in completed_tasks.items)
        assert completed_tasks.total == 10  # 50 / 5 = 10 задач со статусом "completed"

        # Фильтруем по высокому приоритету
        high_priority_tasks = get_tasks_with_pagination(
            db_session, user_id=user.id, page=1, per_page=10, priority=3
        )

        assert all(task.priority == 3 for task in high_priority_tasks.items)

        # Комбинированная фильтрация
        filtered_tasks = get_tasks_with_pagination(
            db_session, user_id=user.id, page=1, per_page=10, status="in_progress", priority=2
        )

        assert all(
            task.status == "in_progress" and task.priority == 2 for task in filtered_tasks.items
        )

    def test_pagination_with_sorting(self, db_session, user_with_many_tasks):
        """Тест пагинации с сортировкой"""
        user = user_with_many_tasks

        # Сортировка по приоритету (по убыванию)
        tasks_by_priority = get_tasks_with_pagination(
            db_session, user_id=user.id, page=1, per_page=10, sort_by="priority", sort_order="desc"
        )

        # Проверяем, что сортировка работает
        priorities = [task.priority for task in tasks_by_priority.items]
        assert priorities == sorted(priorities, reverse=True)

        # Сортировка по дате создания (по возрастанию)
        tasks_by_created = get_tasks_with_pagination(
            db_session, user_id=user.id, page=1, per_page=10, sort_by="created_at", sort_order="asc"
        )

        created_dates = [task.created_at for task in tasks_by_created.items]
        assert created_dates == sorted(created_dates)

    def test_search_pagination(self, db_session, user_with_many_tasks):
        """Тест пагинации с поиском по тексту"""
        user = user_with_many_tasks

        # Создаем задачу с уникальным заголовком для поиска
        create_task(
            db_session,
            user_id=user.id,
            title="Unique search keyword test",
            description="This task should be found by search",
        )

        # Ищем по части заголовка
        search_results = get_tasks_with_pagination(
            db_session, user_id=user.id, page=1, per_page=10, search_query="unique keyword"
        )

        assert search_results.total >= 1
        assert any("unique" in task.title.lower() for task in search_results.items)
