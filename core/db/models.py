"""
Расширенные модели данных для работы с базой данных.
"""

import datetime

from sqlalchemy import JSON, Boolean, Column, DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy.dialects import postgresql
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from core.db.connection import Base


class User(Base):
    """Расширенная модель пользователя."""

    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(100), unique=True, index=True, nullable=False)
    email = Column(String(255), unique=True, index=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    salt = Column(String(255))
    role = Column(String(50), default="user")
    display_name = Column(String(100))
    bio = Column(Text)
    avatar_url = Column(String(255))
    is_active = Column(Boolean, default=True)

    # Настройки пользователя
    preferred_language = Column(String(10), default="ru")
    timezone = Column(String(50), default="UTC")
    preferences = Column(JSON)

    # Статистика
    total_commands = Column(Integer, default=0)
    successful_commands = Column(Integer, default=0)
    last_activity_at = Column(DateTime(timezone=True))

    # ✅ ИСПРАВЛЕНО: добавляем server_default для updated_at
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Отношения
    tasks = relationship("Task", back_populates="user")
    workflows = relationship("Workflow", back_populates="user")
    commands = relationship("Command", back_populates="user")

    def __repr__(self):
        return f"<User {self.username}>"


class AIModel(Base):
    """Модель для AI моделей."""

    __tablename__ = "ai_models"

    # Основные поля
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    model_type_id = Column(Integer)
    provider = Column(String(100), nullable=False)

    # API настройки
    is_api = Column(Boolean, default=True)
    is_local = Column(Boolean, default=False)
    is_free = Column(Boolean, default=False)
    base_url = Column(String(255))
    api_key_name = Column(String(100))
    api_key_required = Column(Boolean, default=False)

    # Статус и активность
    status = Column(String(50), default="active")
    is_active = Column(Boolean, default=True)
    is_featured = Column(Boolean, default=False)

    # HuggingFace специфичные поля
    full_name = Column(String(255))
    hf_model_id = Column(String(255), index=True)
    hf_url = Column(String(500))
    author = Column(String(255))
    description = Column(Text)
    tags = Column(JSON)
    downloads = Column(Integer, default=0)
    likes = Column(Integer, default=0)
    pipeline_tag = Column(String(100))
    model_size = Column(String(50))
    license = Column(String(100))
    library_name = Column(String(100))
    model_type = Column(String(100))
    language = Column(postgresql.ARRAY(String()))

    # ✅ ИСПРАВЛЕНО: добавляем server_default для всех DateTime полей
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    created_at_hf = Column(DateTime(timezone=True))
    last_modified_hf = Column(DateTime(timezone=True))
    last_sync_at = Column(DateTime(timezone=True))

    # Синхронизация
    sync_status = Column(String(50), default="pending")
    sync_error = Column(Text)

    # Конфигурация
    configuration = Column(JSON)
    capabilities = Column(JSON)

    # ✅ RELATIONSHIPS исправлены
    task_executions = relationship("TaskExecution", back_populates="model")
    command_executions = relationship("CommandExecution", back_populates="ai_model")
    performance_metrics = relationship("ModelPerformance", back_populates="model")

    def __repr__(self):
        return f"<AIModel {self.name} ({self.provider})>"


class Task(Base):
    """Модель задачи."""

    __tablename__ = "tasks"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    title = Column(String(255), nullable=False)
    description = Column(Text)

    status = Column(String(50), default="created")
    priority = Column(Integer, default=1)
    due_date = Column(DateTime(timezone=True))

    # ✅ ИСПРАВЛЕНО: server_default добавлен
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
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
    model = relationship("AIModel", back_populates="task_executions")

    def __repr__(self):
        return f"<TaskExecution {self.id} for Task {self.task_id}>"


class Workflow(Base):
    """Модель рабочего процесса."""

    __tablename__ = "workflows"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    name = Column(String(255), nullable=False)
    description = Column(Text)
    is_active = Column(Boolean, default=True)

    # ✅ ИСПРАВЛЕНО: server_default добавлен
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

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

    # ✅ ИСПРАВЛЕНО: server_default добавлен
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

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

    # ✅ ИСПРАВЛЕНО: server_default добавлен
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Отношения
    target_model = relationship("AIModel")

    def __repr__(self):
        return f"<RoutingRule {self.name} (Type: {self.rule_type})>"


class Command(Base):
    """Модель для хранения команд пользователей."""

    __tablename__ = "commands"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)

    # Основная информация команды
    command_text = Column(Text, nullable=False)
    command_type = Column(String(100))
    category = Column(String(100))

    # Статус выполнения
    status = Column(String(50), default="pending")
    priority = Column(Integer, default=1)

    # Результаты
    result_summary = Column(Text)
    completion_percentage = Column(Float, default=0.0)
    accuracy_percentage = Column(Float, default=0.0)

    # Временные метки
    created_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)
    started_at = Column(DateTime(timezone=True))
    completed_at = Column(DateTime(timezone=True))
    duration_seconds = Column(Float)

    # Метаданные
    source_ip = Column(String(45))
    user_agent = Column(String(500))
    session_id = Column(String(100))

    # Отношения
    user = relationship("User", back_populates="commands")
    executions = relationship(
        "CommandExecution", back_populates="command", cascade="all, delete-orphan"
    )
    steps = relationship("CommandStep", back_populates="command", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Command {self.id}: {self.command_text[:50]}...>"


class CommandStep(Base):
    """Модель для шагов выполнения команды."""

    __tablename__ = "command_steps"

    id = Column(Integer, primary_key=True, index=True)
    command_id = Column(Integer, ForeignKey("commands.id"), nullable=False)

    # Информация о шаге
    step_number = Column(Integer, nullable=False)
    step_type = Column(String(100))
    description = Column(Text)

    # Код и результат
    generated_code = Column(Text)
    execution_result = Column(Text)
    error_message = Column(Text)

    # Статус
    status = Column(String(50))
    completion_percentage = Column(Float, default=0.0)

    # Временные метки
    started_at = Column(DateTime(timezone=True))
    completed_at = Column(DateTime(timezone=True))
    duration_seconds = Column(Float)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Отношения
    command = relationship("Command", back_populates="steps")

    def __repr__(self):
        return f"<CommandStep {self.step_number} for Command {self.command_id}>"


class CommandExecution(Base):
    """Модель для выполнения команд с AI моделями."""

    __tablename__ = "command_executions"

    id = Column(Integer, primary_key=True, index=True)
    command_id = Column(Integer, ForeignKey("commands.id"), nullable=False)
    ai_model_id = Column(Integer, ForeignKey("ai_models.id"), nullable=True)

    # Параметры выполнения
    input_prompt = Column(Text)
    model_response = Column(Text)
    processed_result = Column(Text)

    # Метрики производительности
    tokens_used = Column(Integer)
    response_time_ms = Column(Integer)
    cost_estimate = Column(Float)

    # Статус
    status = Column(String(50))
    error_code = Column(String(100))
    error_message = Column(Text)

    # Временные метки
    started_at = Column(DateTime(timezone=True), server_default=func.now())
    completed_at = Column(DateTime(timezone=True))

    # ✅ RELATIONSHIPS исправлены
    command = relationship("Command", back_populates="executions")
    ai_model = relationship("AIModel", back_populates="command_executions")

    def __repr__(self):
        return f"<CommandExecution {self.id} for Command {self.command_id}>"


class SystemLog(Base):
    """Модель для системных логов."""

    __tablename__ = "system_logs"

    id = Column(Integer, primary_key=True, index=True)

    # Основная информация лога
    level = Column(String(20), nullable=False)  # INFO, DEBUG, WARNING, ERROR, CRITICAL
    message = Column(Text, nullable=False)
    source = Column(String(100))  # Источник лога (модуль/функция)
    category = Column(String(50))  # Категория (auth, api, db, etc.)

    # Контекст
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    session_id = Column(String(100))
    request_id = Column(String(100))

    # Дополнительные данные
    extra_data = Column(JSON)
    stack_trace = Column(Text)

    # Временная метка
    created_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)

    # Отношения
    user = relationship("User")

    def __repr__(self):
        return f"<SystemLog {self.level}: {self.message[:50]}...>"


class ModelPerformance(Base):
    """Модель для отслеживания производительности AI моделей."""

    __tablename__ = "model_performance"

    id = Column(Integer, primary_key=True, index=True)
    model_id = Column(Integer, ForeignKey("ai_models.id"), nullable=False)

    # Метрики производительности
    total_requests = Column(Integer, default=0)
    successful_requests = Column(Integer, default=0)
    failed_requests = Column(Integer, default=0)

    # Временные метрики
    avg_response_time_ms = Column(Float)
    min_response_time_ms = Column(Float)
    max_response_time_ms = Column(Float)

    # Финансовые метрики
    total_tokens_used = Column(Integer, default=0)
    total_cost_usd = Column(Float, default=0.0)
    avg_cost_per_request = Column(Float)

    # Качественные метрики
    avg_user_rating = Column(Float)
    success_rate_percentage = Column(Float)

    # Периодические данные
    measurement_period = Column(String(20))  # hourly, daily, weekly, monthly
    period_start = Column(DateTime(timezone=True))
    period_end = Column(DateTime(timezone=True))

    # Временные метки
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # ✅ RELATIONSHIP исправлен
    model = relationship("AIModel", back_populates="performance_metrics")

    def __repr__(self):
        return f"<ModelPerformance for Model {self.model_id} ({self.measurement_period})>"


class UserSession(Base):
    """Модель для пользовательских сессий."""

    __tablename__ = "user_sessions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    # Данные сессии
    session_token = Column(String(255), unique=True, nullable=False, index=True)
    is_active = Column(Boolean, default=True)

    # Информация о клиенте
    user_agent = Column(String(500))
    ip_address = Column(String(45))
    device_info = Column(JSON)

    # Временные метки
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    last_activity_at = Column(DateTime(timezone=True), server_default=func.now())
    expires_at = Column(DateTime(timezone=True))

    # Отношения
    user = relationship("User")

    def __repr__(self):
        return f"<UserSession {self.id} for User {self.user_id}>"


class APIKey(Base):
    """Модель для хранения API ключей."""

    __tablename__ = "api_keys"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    # Информация о ключе
    name = Column(String(100), nullable=False)  # Название/назначение ключа
    provider = Column(String(100), nullable=False)  # openai, anthropic, huggingface, etc.
    key_value = Column(String(255), nullable=False)  # Зашифрованный ключ

    # Статус
    is_active = Column(Boolean, default=True)
    is_default = Column(Boolean, default=False)

    # Лимиты и использование
    monthly_limit_usd = Column(Float)
    current_usage_usd = Column(Float, default=0.0)

    # Временные метки
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    last_used_at = Column(DateTime(timezone=True))
    expires_at = Column(DateTime(timezone=True))

    # Отношения
    user = relationship("User")

    def __repr__(self):
        return f"<APIKey {self.name} ({self.provider}) for User {self.user_id}>"


class ChatSession(Base):
    """Модель для сессии (диалога) чата."""

    __tablename__ = "chat_sessions"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    title = Column(String(200), nullable=False, default="Новый чат")
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(
        DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow
    )

    user = relationship("User")
    messages = relationship("ChatMessage", back_populates="session", cascade="all, delete-orphan")


class ChatMessage(Base):
    """Модель для одного сообщения в чате."""

    __tablename__ = "chat_messages"

    id = Column(Integer, primary_key=True)
    session_id = Column(Integer, ForeignKey("chat_sessions.id"), nullable=False)
    role = Column(String(50), nullable=False)  # 'user' или 'assistant'
    content = Column(Text, nullable=False)
    timestamp = Column(DateTime, default=datetime.datetime.now(datetime.timezone.utc))

    session = relationship("ChatSession", back_populates="messages")


# ✅ ИНДЕКСЫ для производительности
from sqlalchemy import Index

# Индексы для частых запросов
Index("idx_ai_models_provider_status", AIModel.provider, AIModel.status)
Index("idx_ai_models_hf_sync", AIModel.hf_model_id, AIModel.last_sync_at)
Index("idx_commands_user_created", Command.user_id, Command.created_at)
Index("idx_command_executions_model_status", CommandExecution.ai_model_id, CommandExecution.status)
Index("idx_tasks_user_status", Task.user_id, Task.status)
Index("idx_system_logs_level_created", SystemLog.level, SystemLog.created_at)
Index("idx_user_sessions_token_active", UserSession.session_token, UserSession.is_active)
Index("idx_api_keys_user_provider", APIKey.user_id, APIKey.provider, APIKey.is_active)
