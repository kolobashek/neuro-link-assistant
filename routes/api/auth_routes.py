"""
🔐 Авторизация - доменные маршруты
"""

import logging
from functools import wraps  # ✅ ДОБАВИТЬ

from flask import Blueprint, g, jsonify, request  # ✅ ДОБАВИТЬ g

from core.db.connection import get_db
from core.services.auth_service import AuthService

auth_bp = Blueprint("auth_api", __name__)
logger = logging.getLogger("neuro_assistant")


@auth_bp.route("/register", methods=["POST"])
def register():
    """Регистрирует нового пользователя"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({"success": False, "message": "Данные не предоставлены"}), 400

        username = data.get("username")
        email = data.get("email")
        password = data.get("password")
        display_name = data.get("display_name")

        if not all([username, email, password]):
            return jsonify({"success": False, "message": "Обязательные поля не заполнены"}), 400

        db_session = next(get_db())
        auth_service = AuthService(db_session)

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


@auth_bp.route("/login", methods=["POST"])
def login():
    """Аутентифицирует пользователя"""
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

        db_session = next(get_db())
        auth_service = AuthService(db_session)

        user = auth_service.authenticate_user(username, password)

        if not user:
            return jsonify({"success": False, "message": "Неверные учетные данные"}), 401

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


@auth_bp.route("/me", methods=["GET"])
def get_current_user():
    """Получает информацию о текущем пользователе"""
    try:
        auth_header = request.headers.get("Authorization")
        if not auth_header or not auth_header.startswith("Bearer "):
            return jsonify({"success": False, "message": "Токен не предоставлен"}), 401

        token = auth_header.split(" ")[1]

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
