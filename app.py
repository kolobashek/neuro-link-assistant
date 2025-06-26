print("🔍 Импорт Flask...")
import logging

from flask import Flask, jsonify, render_template, request

print("🔍 Импорт routes...")
from routes.api import register_api_blueprints
from routes.main_routes import main_bp

print("🔍 Импорт utils...")
from utils.logging_utils import setup_logging

print("✅ Все импорты выполнены")

# Глобальная переменная для отслеживания прерывания команды
command_interrupt_flag = False

# Создание приложения Flask
app = Flask(__name__)

# Настройка логирования
logger = logging.getLogger("neuro_assistant")


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


# ✅ НОВОЕ: Обработчик ошибки 404
@app.errorhandler(404)
def not_found_error(error):
    """Обработчик ошибки 404 - страница не найдена"""
    print(f"🔍 404 error for URL: {request.url}")
    return render_template("404.html"), 404


# ✅ НОВОЕ: Обработчик ошибки 500 (на будущее)
@app.errorhandler(500)
def internal_error(error):
    """Обработчик внутренней ошибки сервера"""
    print(f"🔍 500 error: {error}")
    return render_template("500.html"), 500


# ✅ НОВОЕ: API endpoints для аутентификации (добавляем здесь для тестов)
@app.route("/api/auth/register", methods=["POST"])
def auth_register():
    """Регистрирует нового пользователя."""
    try:
        data = request.get_json()
        if not data:
            return jsonify({"success": False, "message": "Данные не предоставлены"}), 400

        username = data.get("username")
        email = data.get("email")
        password = data.get("password")
        display_name = data.get("display_name")

        # Базовая валидация
        if not all([username, email, password]):
            return jsonify({"success": False, "message": "Обязательные поля не заполнены"}), 400

        if len(username) < 3:
            return (
                jsonify(
                    {
                        "success": False,
                        "message": "Имя пользователя должно содержать минимум 3 символа",
                    }
                ),
                400,
            )

        from core.db.connection import get_db
        from core.services.auth_service import AuthService

        db_session = next(get_db())
        auth_service = AuthService(db_session)

        # Регистрируем пользователя
        user = auth_service.register_user(
            username=username, email=email, password=password, display_name=display_name
        )

        if not user:
            return (
                jsonify(
                    {
                        "success": False,
                        "message": "Пользователь с таким именем или email уже существует",
                    }
                ),
                409,
            )

        # Создаем токен доступа
        access_token = auth_service.create_access_token_for_user(user)

        return (
            jsonify(
                {
                    "success": True,
                    "message": "Пользователь успешно зарегистрирован",
                    "access_token": access_token,
                    "user": {
                        "id": user.id,
                        "username": user.username,
                        "email": user.email,
                        "display_name": user.display_name,
                    },
                }
            ),
            201,
        )

    except Exception as e:
        logger.error(f"Ошибка при регистрации: {str(e)}")
        return jsonify({"success": False, "message": "Внутренняя ошибка сервера"}), 500


@app.route("/api/auth/login", methods=["POST"])
def auth_login():
    """Аутентифицирует пользователя."""
    try:
        data = request.get_json()
        if not data:
            return jsonify({"success": False, "message": "Данные не предоставлены"}), 400

        username = data.get("username")
        password = data.get("password")

        if not all([username, password]):
            return (
                jsonify({"success": False, "message": "Имя пользователя и пароль обязательны"}),
                400,
            )

        from core.db.connection import get_db
        from core.services.auth_service import AuthService

        db_session = next(get_db())
        auth_service = AuthService(db_session)

        # Аутентифицируем пользователя
        user = auth_service.authenticate_user(username, password)

        if not user:
            return jsonify({"success": False, "message": "Неверные учетные данные"}), 401

        # Создаем токен доступа
        access_token = auth_service.create_access_token_for_user(user)

        return (
            jsonify(
                {
                    "success": True,
                    "message": "Успешная аутентификация",
                    "access_token": access_token,
                    "user": {
                        "id": user.id,
                        "username": user.username,
                        "email": user.email,
                        "display_name": user.display_name,
                    },
                }
            ),
            200,
        )

    except Exception as e:
        logger.error(f"Ошибка при аутентификации: {str(e)}")
        return jsonify({"success": False, "message": "Внутренняя ошибка сервера"}), 500


@app.route("/api/auth/me", methods=["GET"])
def auth_me():
    """Получает информацию о текущем пользователе по токену."""
    try:
        # Получаем токен из заголовка Authorization
        auth_header = request.headers.get("Authorization")
        if not auth_header or not auth_header.startswith("Bearer "):
            return jsonify({"success": False, "message": "Токен не предоставлен"}), 401

        token = auth_header.split(" ")[1]

        # Проверяем токен и получаем пользователя
        from core.db.connection import get_db
        from core.services.auth_service import AuthService

        db_session = next(get_db())
        auth_service = AuthService(db_session)

        user = auth_service.get_current_user(token)
        if not user:
            return jsonify({"success": False, "message": "Неверный токен"}), 401

        return (
            jsonify(
                {
                    "success": True,
                    "user": {
                        "id": user.id,
                        "username": user.username,
                        "email": user.email,
                        "display_name": user.display_name,
                        "role": getattr(user, "role", "user"),
                    },
                }
            ),
            200,
        )

    except Exception as e:
        logger.error(f"Ошибка при получении текущего пользователя: {str(e)}")
        return jsonify({"success": False, "message": "Внутренняя ошибка сервера"}), 500


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

        # ✅ НОВОЕ: Используем доменную регистрацию
        register_api_blueprints(app)
        print("✅ Доменные API маршруты зарегистрированы")

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

        logger.info("Приложение запущено")
        return app

    except Exception as e:
        print(f"❌ Ошибка при инициализации приложения: {e}")
        logger.error(f"Ошибка при инициализации приложения: {e}")
        raise


def run_app():
    """Запуск приложения"""
    try:
        print("🚀 Запуск Нейро-Линк Ассистента...")

        # Инициализируем приложение
        flask_app = init_app()

        # Запускаем Flask сервер
        from config import Config

        flask_app.run(
            host=Config.HOST,
            port=Config.PORT,
            debug=Config.DEBUG,
            use_reloader=False,  # Отключаем reloader для стабильности
        )

    except KeyboardInterrupt:
        print("\n🛑 Приложение остановлено пользователем")
    except Exception as e:
        print(f"❌ Критическая ошибка при запуске: {e}")
        logger.error(f"Критическая ошибка при запуске: {e}")
        raise


if __name__ == "__main__":
    run_app()
