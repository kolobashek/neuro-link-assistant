from flask import Flask, render_template

from routes.api_routes import api_bp
from routes.main_routes import main_bp
from utils.logging_utils import setup_logging

# Глобальная переменная для отслеживания прерывания команды
command_interrupt_flag = False

# Создание приложения Flask
app = Flask(__name__)


@app.route("/ai_models")
def ai_models_page():
    """Страница управления нейросетями"""
    return render_template("ai_models.html")


def init_app():
    """Инициализация приложения"""
    global command_interrupt_flag

    # Инициализация системы логирования
    from utils.logging_utils import init_logging_system

    init_logging_system()

    # Регистрация маршрутов
    app.register_blueprint(main_bp)
    app.register_blueprint(api_bp, url_prefix="/api")

    # Настройка логирования
    history_logger, detailed_logger, system_logger = setup_logging(app)

    # Создаем необходимые файлы логов
    from utils.log_maintenance import ensure_log_files_exist

    ensure_log_files_exist()

    # Настройка конфигурации приложения
    app.config.from_object("config.Config")

    # Сбрасываем флаг прерывания
    command_interrupt_flag = False

    # Логируем запуск приложения
    system_logger.info("Приложение запущено")


def run_app(port: int = None):
    """Запускает приложение Flask"""
    init_app()

    # Если порт не указан, ищем свободный начиная с 5000
    if port is None:
        from scripts.network.port_manager import PortManager

        try:
            port = PortManager.find_any_free_port(5000)
            print(f"🔍 Используем свободный порт: {port}")
        except Exception:
            port = 5000  # Fallback

    app.run(host="127.0.0.1", port=port, debug=True)


if __name__ == "__main__":
    import sys

    # Позволяем передать порт как аргумент
    port = None
    if len(sys.argv) > 1:
        try:
            port = int(sys.argv[1])
        except ValueError:
            print("⚠️ Неверный формат порта, используем автопоиск")

    run_app(port)
