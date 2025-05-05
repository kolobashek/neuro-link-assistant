import os
import logging
from config import Config

def ensure_log_files_exist():
    """
    Проверяет существование необходимых файлов логов и создает их при необходимости
    """
    logger = logging.getLogger('neuro_assistant')
    
    # Создаем директорию для логов, если она не существует
    if not os.path.exists(Config.LOGS_DIR):
        os.makedirs(Config.LOGS_DIR)
        logger.info(f"Создана директория для логов: {Config.LOGS_DIR}")
    
    # Список файлов логов, которые должны существовать
    log_files = [
        Config.SUMMARY_LOG_FILE,
        Config.DETAILED_LOG_FILE,
        Config.SYSTEM_LOG_FILE
    ]
    
    # Создаем каждый файл, если он не существует
    for log_file in log_files:
        if not os.path.exists(log_file):
            # Создаем директории, если они не существуют
            directory = os.path.dirname(log_file)
            if directory and not os.path.exists(directory):
                os.makedirs(directory, exist_ok=True)
            
            # Создаем пустой файл
            with open(log_file, 'w', encoding='utf-8') as f:
                f.write('')
            
            logger.info(f"Создан пустой файл лога: {log_file}")

def clean_old_logs(max_age_days=30):
    """
    Удаляет старые файлы логов
    
    Args:
        max_age_days: Максимальный возраст файлов в днях
    """
    import time
    from datetime import datetime, timedelta
    
    logger = logging.getLogger('neuro_assistant')
    
    # Вычисляем пороговую дату
    threshold_date = datetime.now() - timedelta(days=max_age_days)
    threshold_timestamp = threshold_date.timestamp()
    
    # Проверяем все файлы в директории логов
    for root, dirs, files in os.walk(Config.LOGS_DIR):
        for file in files:
            # Пропускаем текущие файлы логов
            if file in [os.path.basename(f) for f in [
                Config.SUMMARY_LOG_FILE,
                Config.DETAILED_LOG_FILE,
                Config.SYSTEM_LOG_FILE
            ]]:
                continue
            
            file_path = os.path.join(root, file)
            
            # Получаем время последней модификации файла
            file_mtime = os.path.getmtime(file_path)
            
            # Если файл старше порогового значения, удаляем его
            if file_mtime < threshold_timestamp:
                try:
                    os.remove(file_path)
                    logger.info(f"Удален старый файл лога: {file_path}")
                except Exception as e:
                    logger.error(f"Ошибка при удалении старого файла лога {file_path}: {str(e)}")