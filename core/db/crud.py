from datetime import datetime
from typing import List, Optional

from sqlalchemy import asc, desc, or_
from sqlalchemy.orm import Session

from core.db.models import AIModel, Task, User, Workflow

# Функции CRUD для пользователей


def create_user(db: Session, **kwargs) -> User:
    """Создает нового пользователя в базе данных"""
    user = User(**kwargs)
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def get_user_by_id(db: Session, user_id: int) -> Optional[User]:
    """Получает пользователя по ID"""
    return db.query(User).filter(User.id == user_id).first()


def get_user_by_username(db: Session, username: str) -> Optional[User]:
    """Получает пользователя по имени пользователя"""
    return db.query(User).filter(User.username == username).first()


def get_user_by_email(db: Session, email: str) -> Optional[User]:
    """Получает пользователя по email"""
    return db.query(User).filter(User.email == email).first()


def update_user(db: Session, user_id: int, **kwargs) -> Optional[User]:
    """Обновляет данные пользователя"""
    user = get_user_by_id(db, user_id)
    if not user:
        return None

    for key, value in kwargs.items():
        setattr(user, key, value)

    db.commit()
    db.refresh(user)
    return user


# Функции CRUD для моделей ИИ


def create_ai_model(db: Session, **kwargs) -> AIModel:
    """Создает новую модель ИИ в базе данных"""
    model = AIModel(**kwargs)
    db.add(model)
    db.commit()
    db.refresh(model)
    return model


def get_ai_model_by_id(db: Session, model_id: int) -> Optional[AIModel]:
    """Получает модель ИИ по ID"""
    return db.query(AIModel).filter(AIModel.id == model_id).first()


def get_ai_models(db: Session, is_api: Optional[bool] = None) -> List[AIModel]:
    """Получает список моделей ИИ с возможностью фильтрации"""
    query = db.query(AIModel)

    if is_api is not None:
        query = query.filter(AIModel.is_api == is_api)

    return query.all()


def update_ai_model(db: Session, model_id: int, **kwargs) -> Optional[AIModel]:
    """Обновляет данные модели ИИ"""
    model = get_ai_model_by_id(db, model_id)
    if not model:
        return None

    for key, value in kwargs.items():
        setattr(model, key, value)

    db.commit()
    db.refresh(model)
    return model


# Функции CRUD для задач


def create_task(db: Session, **kwargs) -> Task:
    """Создает новую задачу в базе данных"""
    task = Task(**kwargs)
    db.add(task)
    db.commit()
    db.refresh(task)
    return task


def get_task_by_id(db: Session, task_id: int) -> Optional[Task]:
    """Получает задачу по ID"""
    return db.query(Task).filter(Task.id == task_id).first()


def get_tasks_by_user(db: Session, user_id: int) -> List[Task]:
    """Получает список задач пользователя"""
    return db.query(Task).filter(Task.user_id == user_id).all()


def update_task(db: Session, task_id: int, **kwargs) -> Optional[Task]:
    """Обновляет данные задачи"""
    task = get_task_by_id(db, task_id)
    if not task:
        return None

    for key, value in kwargs.items():
        setattr(task, key, value)

    db.commit()
    db.refresh(task)
    return task


def update_task_status(db: Session, task_id: int, status: str) -> Optional[Task]:
    """Обновляет статус задачи"""
    task = get_task_by_id(db, task_id)
    if not task:
        return None

    # SQLAlchemy позволяет присваивать обычные значения колонкам,
    # несмотря на проблемы с типизацией
    task.status = status  # type: ignore

    # Используем безопасную проверку на None
    if status == "completed" and task.completed_at is None:
        task.completed_at = datetime.now()  # type: ignore

    db.commit()
    db.refresh(task)
    return task


def delete_task(db: Session, task_id: int) -> bool:
    """Удаляет задачу"""
    task = get_task_by_id(db, task_id)
    if not task:
        return False

    db.delete(task)
    db.commit()
    return True


# Функции CRUD для рабочих процессов (Workflow)


def create_workflow(db: Session, **kwargs) -> Workflow:
    """Создает новый рабочий процесс в базе данных"""
    workflow = Workflow(**kwargs)
    db.add(workflow)
    db.commit()
    db.refresh(workflow)
    return workflow


def get_workflow_by_id(db: Session, workflow_id: int) -> Optional[Workflow]:
    """Получает рабочий процесс по ID"""
    return db.query(Workflow).filter(Workflow.id == workflow_id).first()


def get_workflows_by_user(db: Session, user_id: int) -> List[Workflow]:
    """Получает список рабочих процессов пользователя"""
    return db.query(Workflow).filter(Workflow.user_id == user_id).all()


class Pagination:
    """Класс для представления результатов с пагинацией"""

    def __init__(self, items, page, per_page, total):
        self.items = items
        self.page = page
        self.per_page = per_page
        self.total = total

        # Вычисляем количество страниц
        self.pages = (total + per_page - 1) // per_page if total > 0 else 0

        # Определяем, есть ли предыдущая/следующая страницы
        self.has_prev = page > 1
        self.has_next = page < self.pages


def get_tasks_with_pagination(
    db: Session,
    user_id: int,
    page: int = 1,
    per_page: int = 10,
    status: Optional[str] = None,
    priority: Optional[int] = None,
    sort_by: Optional[str] = None,
    sort_order: str = "asc",
    search_query: Optional[str] = None,
) -> Pagination:
    """
    Получает список задач пользователя с пагинацией, фильтрацией и сортировкой.

    Args:
        db: Сессия базы данных
        user_id: ID пользователя
        page: Номер страницы
        per_page: Количество записей на странице
        status: Фильтр по статусу задачи
        priority: Фильтр по приоритету
        sort_by: Поле для сортировки
        sort_order: Порядок сортировки (asc/desc)
        search_query: Строка поиска

    Returns:
        Объект пагинации с задачами
    """
    # Базовый запрос - задачи пользователя
    query = db.query(Task).filter(Task.user_id == user_id)

    # Применяем фильтры, если они заданы
    if status:
        query = query.filter(Task.status == status)

    if priority:
        query = query.filter(Task.priority == priority)

    # Поиск по тексту (в заголовке и описании)
    if search_query:
        search_term = f"%{search_query}%"
        query = query.filter(
            or_(Task.title.ilike(search_term), Task.description.ilike(search_term))
        )

    # Определяем общее количество записей до применения пагинации
    total = query.count()

    # Применяем сортировку
    if sort_by:
        column = getattr(Task, sort_by, None)
        if column is not None:
            if sort_order.lower() == "desc":
                query = query.order_by(desc(column))
            else:
                query = query.order_by(asc(column))

    # Применяем пагинацию
    query = query.offset((page - 1) * per_page).limit(per_page)

    # Получаем результаты
    items = query.all()

    # Создаем и возвращаем объект пагинации
    return Pagination(items=items, page=page, per_page=per_page, total=total)
