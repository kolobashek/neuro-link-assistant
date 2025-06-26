"""
API модули - доменное разбиение
"""

from flask import Blueprint

# Импортируем все доменные Blueprint'ы
from .ai_routes import ai_bp
from .analytics_routes import analytics_bp
from .auth_routes import auth_bp
from .system_routes import system_bp
from .task_routes import task_bp


def register_api_blueprints(app):
    """Регистрирует все API Blueprint'ы"""

    # Регистрируем с префиксами доменов
    app.register_blueprint(ai_bp, url_prefix="/api/ai")
    app.register_blueprint(auth_bp, url_prefix="/api/auth")
    app.register_blueprint(task_bp, url_prefix="/api/tasks")
    app.register_blueprint(system_bp, url_prefix="/api/system")
    app.register_blueprint(analytics_bp, url_prefix="/api/analytics")


# Экспортируем функцию регистрации
__all__ = ["register_api_blueprints"]
