import logging
import os
from datetime import datetime
from logging.handlers import RotatingFileHandler

from config import Config


def setup_logging(app):
    """Настройка системы логирования"""
    # Создаем директорию для логов, если она не существует
    os.makedirs(Config.LOGS_DIR, exist_ok=True)

    # Форматтер для логов
    formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")

    # Настройка логгера для истории команд (для пользователя)
    history_handler = RotatingFileHandler(
        Config.SUMMARY_LOG_FILE,
        maxBytes=Config.MAX_LOG_SIZE,
        backupCount=Config.LOG_BACKUP_COUNT,
        encoding="utf-8",
    )
    history_handler.setFormatter(formatter)
    history_handler.setLevel(logging.INFO)

    history_logger = logging.getLogger("command_history")
    history_logger.setLevel(logging.INFO)
    history_logger.addHandler(history_handler)

    # Настройка логгера для детальных логов (для разработчика)
    detailed_handler = RotatingFileHandler(
        Config.DETAILED_LOG_FILE,
        maxBytes=Config.MAX_LOG_SIZE,
        backupCount=Config.LOG_BACKUP_COUNT,
        encoding="utf-8",
    )
    detailed_handler.setFormatter(formatter)
    detailed_handler.setLevel(logging.DEBUG)

    detailed_logger = logging.getLogger("detailed_log")
    detailed_logger.setLevel(logging.DEBUG)
    detailed_logger.addHandler(detailed_handler)

    # Настройка логгера для системных сообщений (для разработчика)
    system_handler = RotatingFileHandler(
        Config.SYSTEM_LOG_FILE,
        maxBytes=Config.MAX_LOG_SIZE,
        backupCount=Config.LOG_BACKUP_COUNT,
        encoding="utf-8",
    )
    system_handler.setFormatter(formatter)
    system_handler.setLevel(logging.INFO)

    system_logger = logging.getLogger("neuro_assistant")
    system_logger.setLevel(logging.INFO)
    system_logger.addHandler(system_handler)

    # Добавляем обработчик для вывода в консоль в режиме отладки
    if app.debug:
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        console_handler.setLevel(logging.DEBUG)

        system_logger.addHandler(console_handler)
        detailed_logger.addHandler(console_handler)

    app.logger.info("Логирование настроено")
    return history_logger, detailed_logger, system_logger


def ensure_log_files_exist():
    """Проверяет существование файлов журнала и создает их при необходимости"""
    os.makedirs(Config.LOGS_DIR, exist_ok=True)

    log_files = [Config.DETAILED_LOG_FILE, Config.SUMMARY_LOG_FILE, Config.SYSTEM_LOG_FILE]
    for file in log_files:
        if not os.path.exists(file):
            # Добавляем encoding='utf-8'
            with open(file, "w", encoding="utf-8") as f:
                f.write(f"# Журнал команд создан {datetime.now().isoformat()}\n")


# Получаем логгеры
history_logger = logging.getLogger("command_history")
detailed_logger = logging.getLogger("detailed_log")
system_logger = logging.getLogger("neuro_assistant")


def filter_sensitive_data(text):
    """
    Фильтрует конфиденциальные данные из текста

    Args:
        text: Исходный текст

    Returns:
        Текст с замаскированными конфиденциальными данными
    """
    import re

    # Список паттернов для фильтрации
    patterns = [
        # API ключи (общий паттерн)
        (
            r'(api[_-]?key|apikey|api[_-]?token|access[_-]?token)[=:"\'\s]+([a-zA-Z0-9]{16,})',
            r"\1=***FILTERED***",
        ),
        # Пароли
        (r'(password|passwd|pwd)[=:"\'\s]+([^\s,;]{3,})', r"\1=***FILTERED***"),
        # Токены авторизации
        (r'(Authorization|Bearer)[=:"\'\s]+([^\s,;]{3,})', r"\1 ***FILTERED***"),
        # Учетные данные в URL
        (r"(https?://)([^:@\s]+):([^@\s]+)@", r"\1***FILTERED***:***FILTERED***@"),
    ]

    # Применяем каждый паттерн
    filtered_text = text
    for pattern, replacement in patterns:
        filtered_text = re.sub(pattern, replacement, filtered_text, flags=re.IGNORECASE)

    return filtered_text


def log_execution_summary(execution, final=False):
    """
    Логирует информацию о выполнении команды

    Args:
        execution: Объект CommandExecution с информацией о выполнении
        final: Флаг, указывающий, является ли это финальным логированием команды
    """
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # Фильтруем конфиденциальные данные
    filtered_command = filter_sensitive_data(execution.command_text)

    # Логируем в историю команд (для пользователя)
    history_entry = (
        f"{timestamp} - Выполнение команды\n"
        f"Команда: {filtered_command}\n"
        f"Статус: {execution.overall_status}\n"
        f"Выполнение: {execution.completion_percentage:.1f}%\n"
        f"Точность: {execution.accuracy_percentage:.1f}%\n"
        f"{'-' * 50}"
    )
    history_logger.info(history_entry)

    # Логируем детальную информацию (для разработчика)
    detailed_entry = (
        f"{timestamp} - Детальное выполнение команды\n"
        f"Команда: {filtered_command}\n"
        f"Время начала: {execution.start_time}\n"
        f"Время окончания: {execution.end_time}\n"
        f"Статус: {execution.overall_status}\n"
        f"Выполнение: {execution.completion_percentage:.1f}%\n"
        f"Точность: {execution.accuracy_percentage:.1f}%\n"
    )

    # Добавляем информацию о шагах
    if execution.steps:
        detailed_entry += "Шаги выполнения:\n"
        for step in execution.steps:
            # Фильтруем конфиденциальные данные в описании и результатах
            filtered_description = filter_sensitive_data(step.description)
            filtered_result = filter_sensitive_data(step.result) if step.result else None
            filtered_error = filter_sensitive_data(step.error) if step.error else None

            detailed_entry += (
                f"  Шаг {step.step_number}: {filtered_description}\n" f"  Статус: {step.status}\n"
            )
            if filtered_result:
                detailed_entry += f"  Результат: {filtered_result}\n"
            if filtered_error:
                detailed_entry += f"  Ошибка: {filtered_error}\n"
            detailed_entry += "  ---\n"

    detailed_entry += f"{'-' * 50}"
    detailed_logger.debug(detailed_entry)

    # Логируем системную информацию
    system_logger.info(
        f"Команда '{filtered_command}' выполнена со статусом '{execution.overall_status}'"
    )


def init_logging_system():
    """
    Инициализирует систему логирования при запуске приложения
    """
    from utils.log_maintenance import clean_old_logs, ensure_log_files_exist

    # Создаем необходимые файлы логов
    ensure_log_files_exist()

    # Очищаем старые логи (старше 30 дней)
    clean_old_logs(30)

    # Логируем информацию о запуске
    system_logger = logging.getLogger("neuro_assistant")
    system_logger.info("Система логирования инициализирована")

    # Добавляем запись в историю команд о запуске приложения
    history_logger = logging.getLogger("command_history")
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    history_logger.info(
        f"{timestamp} - Системное событие\n"
        f"Событие: Запуск приложения\n"
        f"Статус: completed\n"
        f"Выполнение: 100.0%\n"
        f"Точность: 100.0%\n"
        f"{'-' * 50}"
    )
