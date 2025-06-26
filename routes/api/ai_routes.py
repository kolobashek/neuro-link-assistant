"""
🤖 AI и модели - доменные маршруты
"""

import datetime
import logging
import time

from flask import Blueprint, jsonify, request

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
    """Тестовый AI запрос"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({"success": False, "error": "Данные не предоставлены"}), 400

        prompt = data.get("prompt", "").strip()
        if not prompt:
            return jsonify({"success": False, "error": "Пустой запрос"}), 400

        logger.info(f"AI тест запрос: {prompt}")

        start_time = time.time()

        response = get_simple_ai_response(prompt)

        end_time = time.time()
        response_time_ms = int((end_time - start_time) * 1000)

        estimated_tokens = len(prompt.split()) + len(response.split())

        return jsonify(
            {
                "success": True,
                "prompt": prompt,
                "response": response,
                "model": "HuggingFace AI (тест)",
                "tokens": estimated_tokens,
                "response_time_ms": response_time_ms,
                "timestamp": datetime.datetime.now().isoformat(),
            }
        )

    except Exception as e:
        logger.error(f"Ошибка в test_ai: {e}")
        return jsonify({"success": False, "error": f"Внутренняя ошибка: {str(e)}"}), 500


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
