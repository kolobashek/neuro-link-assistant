from flask import Flask

# Импортируем все доменные Blueprint'ы из этого пакета
from .ai_routes import ai_bp
from .analytics_routes import analytics_bp
from .auth_routes import auth_bp
from .chat_routes import chat_bp
from .system_routes import system_bp
from .task_routes import task_bp


def register_api_blueprints(app: Flask):
    """
    Регистрирует все API Blueprint'ы в приложении Flask.

    Args:
        app (Flask): Экземпляр приложения Flask.
    """
    # Регистрируем каждый Blueprint с уникальным префиксом домена
    app.register_blueprint(ai_bp, url_prefix="/api/ai")
    app.register_blueprint(auth_bp, url_prefix="/api/auth")
    app.register_blueprint(task_bp, url_prefix="/api/tasks")
    app.register_blueprint(system_bp, url_prefix="/api/system")
    app.register_blueprint(analytics_bp, url_prefix="/api/analytics")
    app.register_blueprint(chat_bp, url_prefix="/api/chat")


# Экспортируем только функцию регистрации для использования в app.py
__all__ = ["register_api_blueprints"]
