"""
🤖 AI и модели - доменные маршруты
"""

import datetime
import logging
import time

from flask import Blueprint, jsonify, request

from config import Config
from core.db.connection import get_db
from core.db.models import AIModel
from services.ai_service import (
    check_ai_model_availability,
    get_ai_models,
    get_simple_ai_response,
    search_models,
    select_ai_model,
    update_models_from_huggingface,
)

ai_bp = Blueprint("ai_api", __name__)
logger = logging.getLogger("neuro_assistant")

# ============= AI ТЕСТИРОВАНИЕ =============


@ai_bp.route("/test", methods=["POST"])
def test_ai():
    try:
        data = request.get_json()
        # ✅ ИЗМЕНЕНО: Получаем всю историю сообщений
        messages = data.get("messages", [])
        if not messages:
            return jsonify({"success": False, "error": "Сообщения не предоставлены"}), 400

        # Последнее сообщение пользователя для логгирования
        prompt = messages[-1].get("content", "") if messages else ""

        # ✅ ИЗМЕНЕНО: Определяем модель, которую будем использовать
        model_name = "deepseek/deepseek-v3-0324"

        start_time = time.time()

        # ✅ ДОБАВЛЯЕМ ОТЛАДОЧНУЮ ИНФОРМАЦИЮ
        debug_info = {
            "api_key_present": bool(Config.HUGGINGFACE_TOKEN),
            "api_key_prefix": (
                Config.HUGGINGFACE_TOKEN[:10] + "..." if Config.HUGGINGFACE_TOKEN else "NOT_SET"
            ),
            "models_attempted": [],
            "errors": [],
        }

        # ✅ ИЗМЕНЕНО: Передаем всю историю в обработчик
        response = get_simple_ai_response(messages, model_name=model_name)
        end_time = time.time()

        return jsonify(
            {
                "success": True,
                "prompt": prompt,
                "response": response,
                "model": model_name,  # ✅ ИЗМЕНЕНО: Возвращаем реальное имя
                "tokens": len(response.split()),
                "response_time_ms": int((end_time - start_time) * 1000),
                "timestamp": datetime.datetime.now().isoformat(),
                # ✅ ДОБАВЛЯЕМ ОТЛАДКУ В ОТВЕТ
                "debug": debug_info,
            }
        )
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


# ============= УПРАВЛЕНИЕ МОДЕЛЯМИ =============


@ai_bp.route("/models", methods=["GET"])
def get_models():
    """Получить список AI моделей"""
    try:
        models = get_ai_models()
        return jsonify(models)
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@ai_bp.route("/models/check", methods=["POST"])
def check_ai_models():
    """Проверяет доступность нейросетей"""
    model_id = request.json.get("model_id", None) if request.json else None
    results = check_ai_model_availability(model_id)
    return jsonify(results)


@ai_bp.route("/models/select", methods=["POST"])
def select_ai_model_route():
    """Выбирает нейросеть для использования"""
    model_id = request.json.get("model_id", None) if request.json else None

    if not model_id:
        return jsonify({"success": False, "message": "Не указан ID нейросети"})

    result = select_ai_model(model_id)
    return jsonify(result)


@ai_bp.route("/models/active", methods=["GET"])
def get_active_models():
    """Получить список активных моделей"""
    try:
        db = next(get_db())
        try:
            models = db.query(AIModel).filter(AIModel.is_active.is_(True)).all()

            models_data = []
            for model in models:
                models_data.append(
                    {
                        "id": model.id,
                        "name": model.name,
                        "description": model.description or "",
                        "provider": model.provider,
                        "model_type": model.model_type,
                        "status": model.status,
                        "is_api": model.is_api,
                        "is_local": model.is_local,
                        "is_free": model.is_free,
                        "downloads": model.downloads or 0,
                        "likes": model.likes or 0,
                        "created_at": (
                            model.created_at.isoformat() if model.created_at is not None else None
                        ),
                    }
                )

            return jsonify({"success": True, "models": models_data, "total": len(models_data)})

        finally:
            db.close()

    except Exception as e:
        logger.error(f"Ошибка получения активных моделей: {e}")
        return jsonify({"success": False, "error": f"Ошибка получения моделей: {str(e)}"}), 500


@ai_bp.route("/models/catalog", methods=["GET"])
def get_catalog_models():
    """Получить каталог всех доступных моделей"""
    try:
        db = next(get_db())
        try:
            models = db.query(AIModel).order_by(AIModel.downloads.desc()).all()

            models_data = []
            for model in models:
                models_data.append(
                    {
                        "id": model.id,
                        "name": model.name,
                        "full_name": model.full_name,
                        "description": model.description or "",
                        "provider": model.provider,
                        "model_type": model.model_type,
                        "pipeline_tag": model.pipeline_tag,
                        "status": model.status,
                        "is_active": model.is_active,
                        "is_featured": model.is_featured,
                        "downloads": model.downloads or 0,
                        "likes": model.likes or 0,
                        "author": model.author,
                        "tags": model.tags or [],
                        "license": model.license,
                        "hf_model_id": model.hf_model_id,
                        "last_sync_at": (
                            model.last_sync_at.isoforma()
                            if model.last_sync_at is not None
                            else None
                        ),
                    }
                )

            return jsonify({"success": True, "models": models_data, "total": len(models_data)})

        finally:
            db.close()

    except Exception as e:
        logger.error(f"Ошибка получения каталога моделей: {e}")
        return jsonify({"success": False, "error": f"Ошибка получения каталога: {str(e)}"}), 500


@ai_bp.route("/models/<int:model_id>/config", methods=["GET"])
def get_model_config(model_id):
    """Получить конфигурацию модели"""
    try:
        db = next(get_db())
        try:
            model = db.query(AIModel).filter(AIModel.id == model_id).first()
            if not model:
                return jsonify({"success": False, "error": "Модель не найдена"}), 404

            config = model.configuration or {}

            return jsonify(
                {
                    "success": True,
                    "config": {
                        "model_id": model.id,
                        "api_key": config.get("api_key", ""),
                        "temperature": config.get("temperature", 0.7),
                        "max_tokens": config.get("max_tokens", 150),
                        "top_p": config.get("top_p", 0.9),
                        "frequency_penalty": config.get("frequency_penalty", 0),
                        "presence_penalty": config.get("presence_penalty", 0),
                        "is_active": model.is_active,
                    },
                }
            )

        finally:
            db.close()

    except Exception as e:
        logger.error(f"Ошибка получения конфигурации: {e}")
        return jsonify({"success": False, "error": f"Ошибка получения конфигурации: {str(e)}"}), 500


@ai_bp.route("/models/<int:model_id>/config", methods=["PUT"])
def update_model_config(model_id):
    """Обновить конфигурацию модели"""
    try:
        data = request.get_json()

        db = next(get_db())
        try:
            model = db.query(AIModel).filter(AIModel.id == model_id).first()
            if not model:
                return jsonify({"success": False, "error": "Модель не найдена"}), 404

            config = model.configuration or {}
            config.update(
                {
                    "api_key": data.get("api_key", ""),
                    "temperature": float(data.get("temperature", 0.7)),
                    "max_tokens": int(data.get("max_tokens", 150)),
                    "top_p": float(data.get("top_p", 0.9)),
                    "frequency_penalty": float(data.get("frequency_penalty", 0)),
                    "presence_penalty": float(data.get("presence_penalty", 0)),
                }
            )

            db.query(AIModel).filter(AIModel.id == model_id).update(
                {"configuration": config, "is_active": data.get("is_active", True)}
            )

            db.commit()

            return jsonify({"success": True, "message": "Конфигурация модели обновлена"})

        finally:
            db.close()

    except Exception as e:
        logger.error(f"Ошибка обновления конфигурации: {e}")
        return (
            jsonify({"success": False, "error": f"Ошибка обновления конфигурации: {str(e)}"}),
            500,
        )


@ai_bp.route("/models/check-all", methods=["POST"])
def check_all_models():
    """Проверить доступность всех моделей"""
    try:
        db = next(get_db())
        try:
            models = db.query(AIModel).all()
            available = 0
            unavailable = 0

            for model in models:
                try:
                    provider = str(model.provider or "")
                    config = model.configuration or {}

                    if provider == "huggingface":
                        db.query(AIModel).filter(AIModel.id == model.id).update({"status": "ready"})
                        available += 1
                    elif isinstance(config, dict) and config.get("api_key"):
                        db.query(AIModel).filter(AIModel.id == model.id).update({"status": "ready"})
                        available += 1
                    else:
                        db.query(AIModel).filter(AIModel.id == model.id).update(
                            {"status": "unavailable"}
                        )
                        unavailable += 1

                except Exception as e:
                    logger.warning(f"Ошибка проверки модели {model.id}: {e}")
                    db.query(AIModel).filter(AIModel.id == model.id).update(
                        {"status": "unavailable"}
                    )
                    unavailable += 1

            db.commit()

            return jsonify(
                {
                    "success": True,
                    "available": available,
                    "unavailable": unavailable,
                    "total": len(models),
                }
            )

        finally:
            db.close()

    except Exception as e:
        logger.error(f"Ошибка проверки моделей: {e}")
        return jsonify({"success": False, "error": f"Ошибка проверки моделей: {str(e)}"}), 500


# ============= HUGGINGFACE ИНТЕГРАЦИЯ =============


@ai_bp.route("/models/update-from-huggingface", methods=["POST"])
def update_models_from_huggingface_route():
    """Обновляет список моделей с HuggingFace Hub"""
    try:
        result = update_models_from_huggingface()
        return jsonify(result)
    except Exception as e:
        logger.error(f"Ошибка при обновлении списка моделей: {str(e)}")
        return jsonify(
            {"success": False, "message": f"Ошибка при обновлении списка моделей: {str(e)}"}
        )


@ai_bp.route("/models/search", methods=["GET"])
def search_hf_models():
    """Поиск моделей на HuggingFace"""
    query = request.args.get("q", "")
    limit = min(int(request.args.get("limit", 20)), 50)

    if not query or len(query) < 2:
        return jsonify({"success": False, "error": "Запрос должен содержать минимум 2 символа"})

    from services.huggingface_service import search_models_for_ui

    result = search_models_for_ui(query, limit)
    return jsonify(result)


@ai_bp.route("/models/add", methods=["POST"])
def add_hf_model():
    """Добавляет модель HuggingFace в базу"""
    data = request.get_json()
    model_id = data.get("model_id")

    if not model_id:
        return jsonify({"success": False, "error": "model_id обязателен"})

    from services.huggingface_service import add_single_model_to_db

    result = add_single_model_to_db(model_id)
    return jsonify(result)


@ai_bp.route("/current-model", methods=["GET"])
def get_current_model():
    """Получить информацию о текущей активной модели"""
    try:
        from services.ai_service import get_current_ai_model

        current_model = get_current_ai_model()
        if current_model:
            return jsonify(
                {
                    "success": True,
                    "model": {
                        "name": current_model.get("name", "Неизвестная модель"),
                        "status": current_model.get("status", "unknown"),
                        "description": current_model.get("description", ""),
                        "is_available": current_model.get("status") == "ready",
                    },
                }
            )
        else:
            return jsonify({"success": False, "message": "Активная модель не выбрана"})
    except Exception as e:
        logger.error(f"Ошибка получения текущей модели: {e}")
        return jsonify({"success": False, "message": f"Ошибка: {str(e)}"}), 500


@ai_bp.route("/check-api-key", methods=["GET"])
def check_api_key():
    """Проверяет валидность HuggingFace API ключа"""
    try:
        import requests

        # Проверяем через whoami endpoint
        whoami_url = "https://huggingface.co/api/whoami"
        headers = {"Authorization": f"Bearer {Config.HUGGINGFACE_TOKEN}"}

        response = requests.get(whoami_url, headers=headers, timeout=10)

        if response.status_code == 200:
            user_info = response.json()
            return jsonify(
                {
                    "success": True,
                    "message": "API ключ действителен",
                    "user_info": {
                        "name": user_info.get("name", "Unknown"),
                        "type": user_info.get("type", "Unknown"),
                    },
                }
            )
        else:
            return jsonify(
                {
                    "success": False,
                    "message": f"API ключ недействителен: HTTP {response.status_code}",
                    "details": response.text[:200],
                }
            )

    except Exception as e:
        return jsonify({"success": False, "message": f"Ошибка проверки API ключа: {str(e)}"}), 500


@ai_bp.route("/debug-config", methods=["GET"])
def debug_config():
    """Отладка конфигурации API ключей"""
    try:
        import os

        from config import Config

        debug_info = {
            "env_HUGGINGFACE_API_KEY": os.getenv("HUGGINGFACE_API_KEY", "NOT_SET"),
            "env_HUGGINGFACE_TOKEN": os.getenv("HUGGINGFACE_TOKEN", "NOT_SET"),
            "config_HUGGINGFACE_TOKEN": getattr(Config, "HUGGINGFACE_TOKEN", "NOT_SET"),
        }

        # Безопасно показываем только префиксы
        for key, value in debug_info.items():
            if value and value != "NOT_SET" and len(value) > 10:
                debug_info[key] = f"{value[:10]}...({len(value)} символов)"

        return jsonify({"success": True, "debug": debug_info})

    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@ai_bp.route("/debug-bearer", methods=["GET"])
def debug_bearer():
    """Отладка Bearer токена"""
    try:
        import os

        from config import Config

        # Прямая проверка переменных окружения
        raw_token = os.getenv("HUGGINGFACE_TOKEN")
        raw_api_key = os.getenv("HUGGINGFACE_API_KEY")

        debug_data = {
            "raw_env_vars": {
                "HUGGINGFACE_TOKEN": repr(raw_token),  # repr покажет скрытые символы
                "HUGGINGFACE_API_KEY": repr(raw_api_key),
            },
            "config_vars": {
                "HUGGINGFACE_TOKEN": repr(getattr(Config, "HUGGINGFACE_TOKEN", None)),
                "HUGGINGFACE_API_KEY": repr(getattr(Config, "HUGGINGFACE_API_KEY", None)),
            },
            "bearer_formation": {
                "raw_token": f"Bearer {raw_token}" if raw_token else "None",
                "config_token": (
                    f"Bearer {Config.HUGGINGFACE_TOKEN}"
                    if hasattr(Config, "HUGGINGFACE_TOKEN")
                    else "None"
                ),
            },
        }

        # Безопасно скрываем ключи
        for category in debug_data.values():
            for key, value in category.items():
                if isinstance(value, str) and "hf_" in value and len(value) > 15:
                    # Показываем только первые 10 и последние 5 символов
                    visible_part = value[:15] + "***" + value[-8:]
                    category[key] = visible_part

        return jsonify({"success": True, "debug": debug_data})

    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500
