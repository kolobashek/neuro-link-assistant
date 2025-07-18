import os

from dotenv import load_dotenv

# Загрузка переменных окружения
load_dotenv()


class Config:
    """Конфигурация приложения"""

    # Основные настройки Flask
    SECRET_KEY = os.getenv("SECRET_KEY", "default-secret-key")
    DEBUG = os.getenv("DEBUG", "True").lower() == "true"
    HOST = os.getenv("HOST", "127.0.0.1")
    PORT = int(os.getenv("PORT", 5000))

    # Настройки логирования
    LOGS_DIR = "logs"  # Директория для хранения логов
    SUMMARY_LOG_FILE = os.path.join(
        LOGS_DIR, "command_history.log"
    )  # История команд для пользователя
    DETAILED_LOG_FILE = os.path.join(
        LOGS_DIR, "detailed_command.log"
    )  # Детальные логи для разработчика
    SYSTEM_LOG_FILE = os.path.join(LOGS_DIR, "system.log")  # Системные логи для разработчика

    # Максимальный размер файла лога перед ротацией (10 МБ)
    MAX_LOG_SIZE = 10 * 1024 * 1024

    # Количество файлов для ротации
    LOG_BACKUP_COUNT = 5

    # API ключи
    HUGGINGFACE_API_KEY = os.getenv("HUGGINGFACE_API_KEY", "")

    # Настройки команд
    COMMAND_TIMEOUT = int(os.getenv("COMMAND_TIMEOUT", 30))  # Таймаут выполнения команды в секундах

    # Пути для скриншотов
    SCREENSHOT_DIR = os.path.join("static", "screenshots")

    # Максимальное время ожидания ответа от API (в секундах)
    API_TIMEOUT = 10

    # Максимальное время ожидания загрузки страницы в браузере (в секундах)
    BROWSER_TIMEOUT = 10

    # Ключ для доступа к функциям разработчика
    DEVELOPER_KEY = os.environ.get("DEVELOPER_KEY", "dev_key_12345")

    # HuggingFace настройки (улучшенные)
    @staticmethod
    def debug_env_loading():
        import os

        return {
            "env_file_exists": os.path.exists(".env"),
            "HUGGINGFACE_TOKEN_raw": repr(os.getenv("HUGGINGFACE_TOKEN")),
            "HUGGINGFACE_API_KEY_raw": repr(os.getenv("HUGGINGFACE_API_KEY")),
        }

    # Основные настройки
    HUGGINGFACE_TOKEN = os.getenv("HUGGINGFACE_TOKEN", "").strip()
    HUGGINGFACE_API_KEY = os.getenv("HUGGINGFACE_API_KEY", "").strip()

    # Резервные модели для тестирования (бесплатные)
    HUGGINGFACE_TEST_MODELS = [
        "microsoft/DialoGPT-medium",
        "facebook/blenderbot-400M-distill",
        "microsoft/DialoGPT-small",
        "gpt2",
    ]

    # Таймауты для AI запросов
    AI_REQUEST_TIMEOUT = int(os.getenv("AI_REQUEST_TIMEOUT", 30))
    AI_MAX_RETRIES = int(os.getenv("AI_MAX_RETRIES", 3))

    # Директория для хранения моделей
    MODELS_DIR = os.path.join("BASE_DIR", "models")

    # Директория для хранения данных
    DATA_DIR = os.path.join("BASE_DIR", "data")
