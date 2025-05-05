import os
from dotenv import load_dotenv

# Загрузка переменных окружения
load_dotenv()

class Config:
    """Конфигурация приложения"""
    # Основные настройки Flask
    SECRET_KEY = os.getenv('SECRET_KEY', 'default-secret-key')
    DEBUG = os.getenv('DEBUG', 'True').lower() == 'true'
    HOST = os.getenv('HOST', '127.0.0.1')
    PORT = int(os.getenv('PORT', 5000))
    
    # Пути к файлам журналов
    LOG_DIR = os.getenv('LOG_DIR', 'logs')
    DETAILED_LOG_FILE = os.path.join(LOG_DIR, 'detailed_command_log.txt')
    SUMMARY_LOG_FILE = os.path.join(LOG_DIR, 'command_summary.txt')
    
    # API ключи
    HUGGINGFACE_API_KEY = os.getenv('HUGGINGFACE_API_KEY', '')
    
    # Настройки команд
    COMMAND_TIMEOUT = int(os.getenv('COMMAND_TIMEOUT', 30))  # Таймаут выполнения команды в секундах
    
    # Пути для скриншотов
    SCREENSHOT_DIR = os.path.join('static', 'screenshots')

    # Максимальное время ожидания ответа от API (в секундах)
    API_TIMEOUT = 10
    
    # Максимальное время ожидания загрузки страницы в браузере (в секундах)
    BROWSER_TIMEOUT = 10