from flask import Flask
from routes.main_routes import main_bp
from routes.api_routes import api_bp
from utils.logging_utils import setup_loggers

# Инициализация логгеров
logger, detailed_logger, summary_logger = setup_loggers()

# Создание приложения Flask
app = Flask(__name__)

# Регистрация маршрутов
app.register_blueprint(main_bp)
app.register_blueprint(api_bp, url_prefix='/api')

# Глобальная переменная для отслеживания прерывания команды
command_interrupt_flag = False

def init_app():
    """Инициализация приложения"""
    global command_interrupt_flag
    
    # Сбрасываем флаг прерывания
    command_interrupt_flag = False
    
    # Логируем запуск приложения
    logger.info("Приложение запущено")
    detailed_logger.info("Приложение запущено")
    summary_logger.info("Приложение запущено")

if __name__ == '__main__':
    init_app()
    app.run(debug=True)