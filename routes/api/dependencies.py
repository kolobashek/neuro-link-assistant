"""
Общие зависимости для API-маршрутов, такие как декораторы авторизации.
"""

import logging
from functools import wraps

from flask import g, jsonify, request

from core.db.connection import get_db
from core.services.auth_service import AuthService

logger = logging.getLogger("neuro_assistant")


def require_auth(f):
    """
    Декоратор для проверки JWT токена и добавления пользователя в контекст g.current_user.
    """

    @wraps(f)
    def decorated_function(*args, **kwargs):
        auth_header = request.headers.get("Authorization")
        if not auth_header or not auth_header.startswith("Bearer "):
            return jsonify({"success": False, "message": "Токен авторизации не предоставлен"}), 401

        token = auth_header.split(" ")[1]
        if not token:
            return jsonify({"success": False, "message": "Токен авторизации пуст"}), 401

        try:
            db_session = next(get_db())
            auth_service = AuthService(db_session)
            user = auth_service.get_current_user(token)

            if not user:
                return (
                    jsonify(
                        {"success": False, "message": "Недействительный или просроченный токен"}
                    ),
                    401,
                )

            # ✅ Главная задача декоратора: добавить пользователя в глобальный контекст запроса
            g.current_user = user
            return f(*args, **kwargs)

        except Exception as e:
            # Улучшенное логирование для будущей диагностики
            logger.error(f"Критическая ошибка в декораторе require_auth: {e}", exc_info=True)
            return (
                jsonify({"success": False, "message": "Внутренняя ошибка проверки авторизации"}),
                500,
            )

    return decorated_function
