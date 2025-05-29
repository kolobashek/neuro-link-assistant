"""
Модели данных для работы с базой данных.
"""

from sqlalchemy import JSON, Boolean, Column, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from core.db.connection import Base


class User(Base):
    """Модель пользователя."""

    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(100), unique=True, index=True, nullable=False)
    email = Column(String(255), unique=True, index=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    display_name = Column(String(100))
    bio = Column(Text)
    avatar_url = Column(String(255))
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Отношения
    tasks = relationship("Task", back_populates="user")
    workflows = relationship("Workflow", back_populates="user")

    def __repr__(self):
        return f"<User {self.username}>"


class AIModel(Base):
    """Модель для AI моделей."""

    __tablename__ = "ai_models"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    provider = Column(String(100), nullable=False)
    is_api = Column(Boolean, default=True)
    base_url = Column(String(255))
    api_key_name = Column(String(100))
    is_active = Column(Boolean, default=True)
    configuration = Column(JSON)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    def __repr__(self):
        return f"<AIModel {self.name} ({self.provider})>"


class Task(Base):
    """Модель задачи."""

    __tablename__ = "tasks"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    title = Column(String(255), nullable=False)
    description = Column(Text)

    status = Column(String(50), default="created")  # created, in_progress, completed
    priority = Column(Integer, default=1)  # 1 - низкий, 2 - средний, 3 - высокий
    due_date = Column(DateTime(timezone=True))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    completed_at = Column(DateTime(timezone=True))

    # Отношения
    user = relationship("User", back_populates="tasks")
    executions = relationship("TaskExecution", back_populates="task", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Task {self.title} (Status: {self.status})>"


class TaskExecution(Base):
    """Модель выполнения задачи."""

    __tablename__ = "task_executions"

    id = Column(Integer, primary_key=True, index=True)
    task_id = Column(Integer, ForeignKey("tasks.id"), nullable=False)
    model_id = Column(Integer, ForeignKey("ai_models.id"))
    input_data = Column(Text)
    output_data = Column(Text)
    status = Column(String(50))
    started_at = Column(DateTime(timezone=True), server_default=func.now())
    completed_at = Column(DateTime(timezone=True))

    # Отношения
    task = relationship("Task", back_populates="executions")
    model = relationship("AIModel")

    def __repr__(self):
        return f"<TaskExecution {self.id} for Task {self.task_id}>"


class Workflow(Base):
    """Модель рабочего процесса (workflow)."""

    __tablename__ = "workflows"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    name = Column(String(255), nullable=False)
    description = Column(Text)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Отношения
    steps = relationship(
        "WorkflowStep",
        back_populates="workflow",
        cascade="all, delete-orphan",
        order_by="WorkflowStep.order",
    )
    user = relationship("User", back_populates="workflows")

    def __repr__(self):
        return f"<Workflow {self.name}>"


class WorkflowStep(Base):
    """Модель шага рабочего процесса."""

    __tablename__ = "workflow_steps"

    id = Column(Integer, primary_key=True, index=True)
    workflow_id = Column(Integer, ForeignKey("workflows.id"), nullable=False)
    name = Column(String(255), nullable=False)
    description = Column(Text)
    order = Column(Integer, nullable=False)
    configuration = Column(JSON)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Отношения
    workflow = relationship("Workflow", back_populates="steps")

    def __repr__(self):
        return f"<WorkflowStep {self.name} (Order: {self.order})>"


class RoutingRule(Base):
    """Модель правила маршрутизации."""

    __tablename__ = "routing_rules"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    description = Column(Text)
    rule_type = Column(String(50), nullable=False)
    pattern = Column(String(255), nullable=False)
    target_model_id = Column(Integer, ForeignKey("ai_models.id"))
    priority = Column(Integer, default=0)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Отношения
    target_model = relationship("AIModel")

    def __repr__(self):
        return f"<RoutingRule {self.name} (Type: {self.rule_type})>"
