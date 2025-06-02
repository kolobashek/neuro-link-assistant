"""Сервис для работы с задачами."""

from datetime import datetime
from typing import List, Optional

from sqlalchemy.orm import Session

from core.db.models import Task


class TaskService:
    """Сервис управления задачами."""

    def __init__(self, db_session: Session):
        self.db = db_session

    def create_task(
        self,
        user_id: int,
        title: str,
        description: Optional[str] = None,
        priority: int = 1,
        due_date: Optional[datetime] = None,
    ) -> Task:
        """Создание задачи."""
        task = Task(
            user_id=user_id,
            title=title,
            description=description,
            priority=priority,
            due_date=due_date,
        )
        self.db.add(task)
        self.db.commit()
        self.db.refresh(task)
        return task

    def get_task_by_id(self, task_id: int) -> Optional[Task]:
        """Получение задачи по ID."""
        return self.db.query(Task).filter(Task.id == task_id).first()

    def get_user_tasks(self, user_id: int) -> List[Task]:
        """Получение задач пользователя."""
        return self.db.query(Task).filter(Task.user_id == user_id).all()

    def update_task(self, task_id: int, **kwargs) -> Optional[Task]:
        """Обновление задачи."""
        task = self.get_task_by_id(task_id)
        if task:
            for key, value in kwargs.items():
                if hasattr(task, key):
                    setattr(task, key, value)
            self.db.commit()
            self.db.refresh(task)
        return task

    def complete_task(self, task_id: int) -> Optional[Task]:
        """Завершение задачи."""
        task = self.get_task_by_id(task_id)
        if task:
            # Используем setattr для избежания ошибок типизации
            setattr(task, "status", "completed")
            setattr(task, "completed_at", datetime.now())
            self.db.commit()
            self.db.refresh(task)
        return task

    def delete_task(self, task_id: int) -> bool:
        """Удаление задачи."""
        task = self.get_task_by_id(task_id)
        if task:
            self.db.delete(task)
            self.db.commit()
            return True
        return False
