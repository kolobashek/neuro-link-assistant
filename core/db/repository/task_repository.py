"""
Репозиторий для работы с задачами.
"""

from datetime import datetime
from typing import List, Optional

from sqlalchemy import desc
from sqlalchemy.orm import Session

from core.db.models import Task


class TaskRepository:
    """Класс для работы с задачами в базе данных."""

    def __init__(self, db_session: Session):
        """
        Инициализирует репозиторий задач.

        Args:
            db_session (Session): Сессия SQLAlchemy для работы с БД.
        """
        self.db = db_session

    def create(
        self,
        user_id: int,
        title: str,
        description: Optional[str] = None,
        status: str = "created",
        priority: int = 1,
        due_date: Optional[datetime] = None,
    ) -> Task:
        """
        Создает новую задачу.

        Args:
            user_id (int): ID пользователя.
            title (str): Заголовок задачи.
            description (Optional[str], optional): Описание задачи. По умолчанию None.
            status (str, optional): Статус задачи. По умолчанию "created".
            priority (int, optional): Приоритет задачи (1-3). По умолчанию 1.
            due_date (Optional[datetime], optional): Срок выполнения. По умолчанию None.

        Returns:
            Task: Созданная задача.
        """
        task = Task(
            user_id=user_id,
            title=title,
            description=description,
            status=status,
            priority=priority,
            due_date=due_date,
        )
        self.db.add(task)
        self.db.commit()
        self.db.refresh(task)
        return task

    def get_by_id(self, task_id: int) -> Optional[Task]:
        """
        Получает задачу по ID.

        Args:
            task_id (int): ID задачи.

        Returns:
            Optional[Task]: Найденная задача или None.
        """
        return self.db.query(Task).filter(Task.id == task_id).first()

    def get_by_user_id(self, user_id: int) -> List[Task]:
        """
        Получает все задачи пользователя.

        Args:
            user_id (int): ID пользователя.

        Returns:
            List[Task]: Список задач.
        """
        return self.db.query(Task).filter(Task.user_id == user_id).all()

    def get_by_status(self, user_id: int, status: str) -> List[Task]:
        """
        Получает задачи пользователя с указанным статусом.

        Args:
            user_id (int): ID пользователя.
            status (str): Статус задачи.

        Returns:
            List[Task]: Список задач.
        """
        return self.db.query(Task).filter(Task.user_id == user_id, Task.status == status).all()

    def get_by_priority(self, user_id: int, priority: int) -> List[Task]:
        """
        Получает задачи пользователя с указанным приоритетом.

        Args:
            user_id (int): ID пользователя.
            priority (int): Приоритет задачи.

        Returns:
            List[Task]: Список задач.
        """
        return self.db.query(Task).filter(Task.user_id == user_id, Task.priority == priority).all()

    def get_by_due_date(self, user_id: int, due_date: datetime) -> List[Task]:
        """
        Получает задачи пользователя с указанной датой выполнения.

        Args:
            user_id (int): ID пользователя.
            due_date (datetime): Дата выполнения.

        Returns:
            List[Task]: Список задач.
        """
        return self.db.query(Task).filter(Task.user_id == user_id, Task.due_date == due_date).all()

    def get_overdue_tasks(self, user_id: int) -> List[Task]:
        """
        Получает просроченные задачи пользователя.

        Args:
            user_id (int): ID пользователя.

        Returns:
            List[Task]: Список просроченных задач.
        """
        now = datetime.now()
        return (
            self.db.query(Task)
            .filter(Task.user_id == user_id, Task.due_date < now, Task.status != "completed")
            .all()
        )

    def update(self, task_id: int, **kwargs) -> Optional[Task]:
        """
        Обновляет задачу.

        Args:
            task_id (int): ID задачи.
            **kwargs: Поля для обновления.

        Returns:
            Optional[Task]: Обновленная задача или None.
        """
        task = self.get_by_id(task_id)
        if not task:
            return None

        for key, value in kwargs.items():
            if hasattr(task, key):
                setattr(task, key, value)

        if kwargs.get("status") == "completed" and not task.completed_at:  # type: ignore
            task.completed_at = datetime.now().replace(microsecond=0)  # type: ignore

        self.db.commit()
        self.db.refresh(task)
        return task

    def delete(self, task_id: int) -> bool:
        """
        Удаляет задачу.

        Args:
            task_id (int): ID задачи.

        Returns:
            bool: True если задача удалена, иначе False.
        """
        task = self.get_by_id(task_id)
        if not task:
            return False

        self.db.delete(task)
        self.db.commit()
        return True

    def search(self, **filters) -> List[Task]:
        """
        Ищет задачи по заданным фильтрам.

        Args:
            **filters: Фильтры для поиска (user_id, title, status, priority, etc.).

        Returns:
            List[Task]: Список найденных задач.
        """
        query = self.db.query(Task)

        if "user_id" in filters:
            query = query.filter(Task.user_id == filters["user_id"])
        if "title" in filters:
            query = query.filter(Task.title.ilike(f"%{filters['title']}%"))
        if "status" in filters:
            query = query.filter(Task.status == filters["status"])
        if "priority" in filters:
            query = query.filter(Task.priority == filters["priority"])
        if "due_date_before" in filters:
            query = query.filter(Task.due_date <= filters["due_date_before"])
        if "due_date_after" in filters:
            query = query.filter(Task.due_date >= filters["due_date_after"])

        # Сортировка
        sort_by = filters.get("sort_by", "due_date")
        sort_order = filters.get("sort_order", "asc")

        if hasattr(Task, sort_by):
            if sort_order.lower() == "desc":
                query = query.order_by(desc(getattr(Task, sort_by)))
            else:
                query = query.order_by(getattr(Task, sort_by))

        # Пагинация
        limit = filters.get("limit")
        offset = filters.get("offset")

        if limit:
            query = query.limit(limit)
        if offset:
            query = query.offset(offset)

        return query.all()
