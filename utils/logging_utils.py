import logging
import os
import datetime
from config import Config

def setup_loggers():
    """Настройка всех логгеров приложения"""
    # Создаем директорию для логов, если она не существует
    os.makedirs(Config.LOG_DIR, exist_ok=True)
    
    # Основной логгер
    logger = logging.getLogger('neuro_assistant')
    logger.setLevel(logging.INFO)
    handler = logging.StreamHandler()
    handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
    logger.addHandler(handler)
    
    # Подробный логгер
    detailed_logger = logging.getLogger('detailed_log')
    detailed_logger.setLevel(logging.INFO)
    # Добавляем encoding='utf-8'
    detailed_handler = logging.FileHandler(Config.DETAILED_LOG_FILE, encoding='utf-8')
    detailed_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
    detailed_logger.addHandler(detailed_handler)
    
    # Краткий логгер
    summary_logger = logging.getLogger('summary_log')
    summary_logger.setLevel(logging.INFO)
    # Добавляем encoding='utf-8'
    summary_handler = logging.FileHandler(Config.SUMMARY_LOG_FILE, encoding='utf-8')
    summary_handler.setFormatter(logging.Formatter('%(asctime)s - %(message)s'))
    summary_logger.addHandler(summary_handler)
    
    return logger, detailed_logger, summary_logger

def ensure_log_files_exist():
    """Проверяет существование файлов журнала и создает их при необходимости"""
    os.makedirs(Config.LOG_DIR, exist_ok=True)
    
    log_files = [Config.DETAILED_LOG_FILE, Config.SUMMARY_LOG_FILE]
    for file in log_files:
        if not os.path.exists(file):
            # Добавляем encoding='utf-8'
            with open(file, 'w', encoding='utf-8') as f:
                f.write(f"# Журнал команд создан {datetime.datetime.now().isoformat()}\n")

def log_execution_summary(execution, final=False):
    """
    Записывает краткую информацию о выполнении команды в журнал
    """
    summary_logger = logging.getLogger('summary_log')
    
    status_text = execution.overall_status
    if status_text == 'interrupted':
        status_text = "прервано пользователем"
    elif not final:
        status_text = f"в процессе ({execution.completion_percentage:.1f}% выполнено)"
    
    summary_text = (
        f"Команда: {execution.command_text}\n"
        f"Статус: {status_text}\n"
        f"Выполнение: {execution.completion_percentage:.1f}%\n"
        f"Точность: {execution.accuracy_percentage:.1f}%\n"
    )
    
    if final:
        summary_text += f"Время выполнения: {execution.start_time} - {execution.end_time}\n"
        
        # Добавляем информацию о шагах
        if len(execution.steps) > 1:
            summary_text += f"Шаги ({len(execution.steps)}):\n"
            for step in execution.steps:
                step_status = step.status
                if step_status == 'interrupted':
                    step_status = "прервано"
                summary_text += f"  - Шаг {step.step_number}: {step.description} ({step_status})\n"
    
    summary_logger.info(summary_text)