"""
Репозиторий для работы с рабочими процессами (workflows).
"""

from typing import Dict, List, Optional

from sqlalchemy import desc
from sqlalchemy.orm import Session

from core.db.models import Workflow, WorkflowStep


class WorkflowRepository:
    """Класс для работы с рабочими процессами в базе данных."""

    def __init__(self, db_session: Session):
        """
        Инициализирует репозиторий рабочих процессов.

        Args:
            db_session (Session): Сессия SQLAlchemy для работы с БД.
        """
        self.db = db_session

    def create(self, user_id: int, name: str, description: Optional[str] = None) -> Workflow:
        """
        Создает новый рабочий процесс.

        Args:
            user_id (int): ID пользователя.
            name (str): Название рабочего процесса.
            description (Optional[str], optional): Описание. По умолчанию None.

        Returns:
            Workflow: Созданный рабочий процесс.
        """
        workflow = Workflow(
            user_id=user_id,
            name=name,
            description=description,
        )
        self.db.add(workflow)
        self.db.commit()
        self.db.refresh(workflow)
        return workflow

    def get_by_id(self, workflow_id: int) -> Optional[Workflow]:
        """
        Получает рабочий процесс по ID.

        Args:
            workflow_id (int): ID рабочего процесса.

        Returns:
            Optional[Workflow]: Найденный рабочий процесс или None.
        """
        return self.db.query(Workflow).filter(Workflow.id == workflow_id).first()

    def get_by_user_id(self, user_id: int) -> List[Workflow]:
        """
        Получает все рабочие процессы пользователя.

        Args:
            user_id (int): ID пользователя.

        Returns:
            List[Workflow]: Список рабочих процессов.
        """
        return self.db.query(Workflow).filter(Workflow.user_id == user_id).all()

    def get_active_workflows(self, user_id: int) -> List[Workflow]:
        """
        Получает активные рабочие процессы пользователя.

        Args:
            user_id (int): ID пользователя.

        Returns:
            List[Workflow]: Список активных рабочих процессов.
        """
        return (
            self.db.query(Workflow)
            .filter(Workflow.user_id == user_id, Workflow.is_active.is_(True))
            .all()
        )

    def update(self, workflow_id: int, **kwargs) -> Optional[Workflow]:
        """
        Обновляет рабочий процесс.

        Args:
            workflow_id (int): ID рабочего процесса.
            **kwargs: Поля для обновления.

        Returns:
            Optional[Workflow]: Обновленный рабочий процесс или None.
        """
        workflow = self.get_by_id(workflow_id)
        if not workflow:
            return None

        for key, value in kwargs.items():
            if hasattr(workflow, key):
                setattr(workflow, key, value)

        self.db.commit()
        self.db.refresh(workflow)
        return workflow

    def delete(self, workflow_id: int) -> bool:
        """
        Удаляет рабочий процесс.

        Args:
            workflow_id (int): ID рабочего процесса.

        Returns:
            bool: True если рабочий процесс удален, иначе False.
        """
        workflow = self.get_by_id(workflow_id)
        if not workflow:
            return False

        self.db.delete(workflow)
        self.db.commit()
        return True

    def search(self, **filters) -> List[Workflow]:
        """
        Ищет рабочие процессы по заданным фильтрам.

        Args:
            **filters: Фильтры для поиска.

        Returns:
            List[Workflow]: Список найденных рабочих процессов.
        """
        query = self.db.query(Workflow)

        if "user_id" in filters:
            query = query.filter(Workflow.user_id == filters["user_id"])
        if "name" in filters:
            query = query.filter(Workflow.name.ilike(f"%{filters['name']}%"))
        if "description" in filters:
            query = query.filter(Workflow.description.ilike(f"%{filters['description']}%"))
        if "is_active" in filters:
            query = query.filter(Workflow.is_active.is_(filters["is_active"]))

        # Сортировка
        sort_by = filters.get("sort_by", "created_at")
        sort_order = filters.get("sort_order", "desc")

        if hasattr(Workflow, sort_by):
            if sort_order.lower() == "desc":
                query = query.order_by(desc(getattr(Workflow, sort_by)))
            else:
                query = query.order_by(getattr(Workflow, sort_by))

        # Пагинация
        limit = filters.get("limit")
        offset = filters.get("offset")

        if limit:
            query = query.limit(limit)
        if offset:
            query = query.offset(offset)

        return query.all()

    # Методы для работы с шагами рабочего процесса

    def add_step(
        self,
        workflow_id: int,
        name: str,
        order: int,
        description: Optional[str] = None,
        configuration: Optional[Dict] = None,
    ) -> Optional[WorkflowStep]:
        """
        Добавляет шаг к рабочему процессу.

        Args:
            workflow_id (int): ID рабочего процесса.
            name (str): Название шага.
            order (int): Порядок шага.
            description (Optional[str], optional): Описание шага. По умолчанию None.
            configuration (Optional[Dict], optional): Конфигурация шага. По умолчанию None.

        Returns:
            Optional[WorkflowStep]: Созданный шаг или None.
        """
        workflow = self.get_by_id(workflow_id)
        if not workflow:
            return None

        # Проверяем, существует ли уже шаг с таким порядком
        existing_step = (
            self.db.query(WorkflowStep)
            .filter(WorkflowStep.workflow_id == workflow_id, WorkflowStep.order == order)
            .first()
        )

        # Если шаг с таким порядком существует, сдвигаем все последующие шаги
        if existing_step:
            steps_to_move = (
                self.db.query(WorkflowStep)
                .filter(WorkflowStep.workflow_id == workflow_id, WorkflowStep.order >= order)
                .all()
            )
            for step in steps_to_move:
                # Правильное назначение для SQLAlchemy
                new_order = step.order + 1
                setattr(step, "order", new_order)

        # Создаем новый шаг
        step = WorkflowStep(
            workflow_id=workflow_id,
            name=name,
            description=description,
            order=order,
            configuration=configuration or {},
        )
        self.db.add(step)
        self.db.commit()
        self.db.refresh(step)
        return step

    def get_step_by_id(self, step_id: int) -> Optional[WorkflowStep]:
        """
        Получает шаг рабочего процесса по ID.

        Args:
            step_id (int): ID шага.

        Returns:
            Optional[WorkflowStep]: Найденный шаг или None.
        """
        return self.db.query(WorkflowStep).filter(WorkflowStep.id == step_id).first()

    def get_steps(self, workflow_id: int) -> List[WorkflowStep]:
        """
        Получает все шаги рабочего процесса.

        Args:
            workflow_id (int): ID рабочего процесса.

        Returns:
            List[WorkflowStep]: Список шагов.
        """
        return (
            self.db.query(WorkflowStep)
            .filter(WorkflowStep.workflow_id == workflow_id)
            .order_by(WorkflowStep.order)
            .all()
        )

    def update_step(self, step_id: int, **kwargs) -> Optional[WorkflowStep]:
        """
        Обновляет шаг рабочего процесса.

        Args:
            step_id (int): ID шага.
            **kwargs: Поля для обновления.

        Returns:
            Optional[WorkflowStep]: Обновленный шаг или None.
        """
        step = self.get_step_by_id(step_id)
        if not step:
            return None

        old_order = step.order
        new_order = kwargs.get("order", old_order)

        # Если изменился порядок шага, обновляем порядок всех шагов
        if "order" in kwargs and old_order != new_order:
            if new_order > old_order:
                # Сдвигаем шаги вверх
                steps_to_move = (
                    self.db.query(WorkflowStep)
                    .filter(
                        WorkflowStep.workflow_id == step.workflow_id,
                        WorkflowStep.order > old_order,
                        WorkflowStep.order <= new_order,
                    )
                    .all()
                )
                for s in steps_to_move:
                    # Правильное назначение для SQLAlchemy
                    new_s_order = s.order - 1
                    setattr(s, "order", new_s_order)
            else:
                # Сдвигаем шаги вниз
                steps_to_move = (
                    self.db.query(WorkflowStep)
                    .filter(WorkflowStep.workflow_id == step.workflow_id)
                    .filter(WorkflowStep.order >= new_order)
                    .filter(WorkflowStep.order < old_order)
                    .all()
                )
                for s in steps_to_move:
                    # Правильное назначение для SQLAlchemy
                    new_s_order = s.order + 1
                    setattr(s, "order", new_s_order)

        # Обновляем атрибуты шага
        for key, value in kwargs.items():
            if hasattr(step, key):
                setattr(step, key, value)

        self.db.commit()
        self.db.refresh(step)
        return step

    def delete_step(self, step_id: int) -> bool:
        """
        Удаляет шаг рабочего процесса.

        Args:
            step_id (int): ID шага.

        Returns:
            bool: True если шаг удален, иначе False.
        """
        step = self.get_step_by_id(step_id)
        if not step:
            return False

        # Запоминаем порядок и ID рабочего процесса перед удалением
        workflow_id = step.workflow_id
        order = step.order

        # Удаляем шаг
        self.db.delete(step)

        # Обновляем порядок оставшихся шагов
        steps_to_update = (
            self.db.query(WorkflowStep)
            .filter(WorkflowStep.workflow_id == workflow_id)
            .filter(WorkflowStep.order > order)
            .all()
        )
        for step in steps_to_update:
            # Правильное назначение для SQLAlchemy
            new_order = step.order - 1
            setattr(step, "order", new_order)

        self.db.commit()
        return True

    def reorder_steps(self, workflow_id: int, step_order_mapping: Dict[int, int]) -> bool:
        """
        Изменяет порядок шагов рабочего процесса.

        Args:
            workflow_id (int): ID рабочего процесса.
            step_order_mapping (Dict[int, int]): Словарь {id_шага: новый_порядок}.

        Returns:
            bool: True при успешном выполнении.
        """
        workflow = self.get_by_id(workflow_id)
        if workflow is None:
            return False

        # Получаем все шаги рабочего процесса
        steps = self.get_steps(workflow_id)
        if not steps:
            return False

        # Проверяем, что все ID шагов существуют
        step_ids = {step.id for step in steps}
        step_order_keys = set(step_order_mapping.keys())
        if not step_order_keys.issubset(step_ids):
            return False
        # Проверяем, что новые порядковые номера уникальны и начинаются с 1
        order_values = list(step_order_mapping.values())
        if len(set(order_values)) != len(order_values) or min(order_values) < 1:
            return False

        # Создаем временное отображение, чтобы избежать конфликтов
        temp_order_base = 1000  # Достаточно большое значение для избежания конфликтов

        # Сначала устанавливаем временные порядковые номера
        for step_id, new_order in step_order_mapping.items():
            step = next((s for s in steps if s.id == step_id), None)  # type: ignore
            if step is not None:
                # Правильное назначение для SQLAlchemy
                temp_order = temp_order_base + new_order
                setattr(step, "order", temp_order)

        # Затем устанавливаем конечные порядковые номера
        for step_id, new_order in step_order_mapping.items():
            step = next((s for s in steps if s.id == step_id), None)  # type: ignore
            if step is not None:
                # Правильное назначение для SQLAlchemy
                setattr(step, "order", new_order)

        self.db.commit()
        return True

    def get_workflow_with_steps(self, workflow_id: int) -> Optional[Workflow]:
        """
        Получает рабочий процесс с его шагами.

        Args:
            workflow_id (int): ID рабочего процесса.

        Returns:
            Optional[Workflow]: Рабочий процесс со всеми шагами или None.
        """
        workflow = self.get_by_id(workflow_id)
        if not workflow:
            return None

        # Шаги уже загружены через relationship с параметром order_by
        return workflow
