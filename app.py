print("🔍 Импорт Flask...")
from flask import Flask, render_template, request

print("🔍 Импорт routes...")
from routes.api_routes import api_bp
from routes.main_routes import main_bp

print("🔍 Импорт utils...")
from utils.logging_utils import setup_logging

print("✅ Все импорты выполнены")

# Глобальная переменная для отслеживания прерывания команды
command_interrupt_flag = False

# Создание приложения Flask
app = Flask(__name__)


@app.route("/ai_models")
def ai_models_page():
    """Страница управления нейросетями"""
    return render_template("ai_models.html")


@app.route("/health")
def health_check():
    """Health check для мониторинга и UI тестов"""
    import time

    print(f"🔍 Health check called at {time.time()}")
    return {"status": "ok", "timestamp": time.time()}, 200


@app.route("/")
def index():
    """Главная страница - тоже нужна для health check"""
    print(f"🔍 Index page called")
    return render_template("index.html")


def init_app():
    """Инициализация приложения"""
    global command_interrupt_flag

    print("🔍 Начало init_app()")

    try:
        # Инициализация системы логирования
        from utils.logging_utils import init_logging_system

        print("🔍 Инициализация логирования...")
        init_logging_system()
        print("✅ Логирование инициализировано")
        # Регистрация маршрутов
        print("🔍 Регистрация маршрутов...")
        app.register_blueprint(main_bp)
        app.register_blueprint(api_bp, url_prefix="/api")
        print("✅ Маршруты зарегистрированы")

        # Настройка логирования
        print("🔍 Настройка логирования...")
        history_logger, detailed_logger, system_logger = setup_logging(app)
        print("✅ Логирование настроено")

        # Создаем необходимые файлы логов
        print("🔍 Создание файлов логов...")
        from utils.log_maintenance import ensure_log_files_exist

        ensure_log_files_exist()
        print("✅ Файлы логов созданы")

        # Настройка конфигурации приложения
        print("🔍 Настройка конфигурации...")
        app.config.from_object("config.Config")
        print("✅ Конфигурация настроена")
        # Сбрасываем флаг прерывания
        command_interrupt_flag = False
        print("✅ init_app() завершена успешно")

        # Логируем запуск приложения
        system_logger.info("Приложение запущено")

    except Exception as e:
        print(f"❌ Ошибка в init_app(): {e}")
        import traceback

        traceback.print_exc()
        raise


def run_app(port: int | None = None):
    """Запускает приложение Flask"""
    print(f"🚀 Начало run_app(), port={port}")

    try:
        init_app()
        print("✅ init_app() завершена")
    except Exception as e:
        print(f"❌ Ошибка в init_app(): {e}")
        return

    # Если порт не указан, ищем свободный начиная с 5000
    if port is None:
        try:
            from scripts.network.port_manager import PortManager

            port = PortManager.find_any_free_port(5000)
            print(f"🔍 Используем свободный порт: {port}")

        except Exception as e:
            print(f"⚠️ Ошибка поиска порта: {e}, используем 5000")
            port = 5000

    # Определяем режим debug из переменной окружения
    import os

    debug_mode = os.environ.get("FLASK_ENV") != "testing"

    print(f"🚀 Запуск Flask на порту {port}, debug={debug_mode}")

    try:
        app.run(host="127.0.0.1", port=port, debug=debug_mode, use_reloader=False)
    except Exception as e:
        print(f"❌ Ошибка запуска Flask: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Neuro-Link Assistant")
    parser.add_argument("--port", type=int, help="Порт для запуска приложения")
    parser.add_argument("port_positional", nargs="?", type=int, help="Порт (позиционный аргумент)")
    parser.add_argument("--debug", action="store_true", help="Включить debug режим")
    parser.add_argument("--host", default="127.0.0.1", help="Хост для привязки")

    args = parser.parse_args()

    # Приоритет: --port > позиционный аргумент > None
    port = args.port or args.port_positional

    if port is not None:
        print(f"🔍 Используем указанный порт: {port}")

    run_app(port)
