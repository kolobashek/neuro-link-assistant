import logging

from flask import Blueprint, g, jsonify, request

from core.db.connection import get_db
from core.db.models import ChatMessage, ChatSession

# ✅ ИСПРАВИТЬ ИМПОРТ
from routes.api.dependencies import require_auth
from services.ai_service import get_simple_ai_response

chat_bp = Blueprint("chat_api", __name__)
logger = logging.getLogger("neuro_assistant")


@chat_bp.route("/chats", methods=["GET"])
@require_auth
def get_chat_list():
    """Получить список чатов для текущего пользователя."""
    db = next(get_db())
    # g.current_user устанавливается в декораторе require_auth
    sessions = (
        db.query(ChatSession)
        .filter(ChatSession.user_id == g.current_user.id)
        .order_by(ChatSession.updated_at.desc())
        .all()
    )
    return jsonify([{"id": s.id, "title": s.title} for s in sessions])


@chat_bp.route("/chats", methods=["POST"])
@require_auth
def create_chat():
    """Создать новый чат."""
    db = next(get_db())
    new_session = ChatSession(user_id=g.current_user.id, title="Новый чат")
    db.add(new_session)
    db.commit()
    db.refresh(new_session)
    return jsonify({"id": new_session.id, "title": new_session.title}), 201


@chat_bp.route("/chats/<int:session_id>/messages", methods=["GET"])
@require_auth
def get_chat_messages(session_id):
    """Получить все сообщения для конкретного чата."""
    db = next(get_db())
    messages = (
        db.query(ChatMessage)
        .filter(ChatMessage.session_id == session_id)
        .order_by(ChatMessage.timestamp.asc())
        .all()
    )
    # Убедимся, что пользователь имеет доступ к этому чату
    session = (
        db.query(ChatSession)
        .filter(ChatSession.id == session_id, ChatSession.user_id == g.current_user.id)
        .first()
    )
    if not session:
        return jsonify({"error": "Чат не найден или доступ запрещен"}), 404
    return jsonify([{"role": m.role, "content": m.content} for m in messages])


@chat_bp.route("/chats/<int:session_id>", methods=["DELETE"])
@require_auth
def delete_chat(session_id):
    """Удалить чат и все его сообщения."""
    db = next(get_db())
    session = (
        db.query(ChatSession)
        .filter(ChatSession.id == session_id, ChatSession.user_id == g.current_user.id)
        .first()
    )
    if session:
        db.delete(session)
        db.commit()
        return jsonify({"success": True, "message": "Чат удален"}), 200
    return jsonify({"error": "Чат не найден или доступ запрещен"}), 404


@chat_bp.route("/chats/<int:session_id>/messages", methods=["POST"])
@require_auth
def post_message(session_id):
    """Отправить сообщение в чат и получить ответ AI."""
    db = next(get_db())
    data = request.get_json()
    user_prompt = data.get("prompt")

    if not user_prompt:
        return jsonify({"error": "Prompt не может быть пустым"}), 400

    # 1. Сохраняем сообщение пользователя в базу НЕМЕДЛЕННО.
    # Это гарантирует, что оно не потеряется, даже если AI сервис упадет.
    user_message = ChatMessage(session_id=session_id, role="user", content=user_prompt)
    db.add(user_message)
    db.commit()

    # 2. Собираем контекст из базы (для будущих, более умных моделей).
    # Текущая простая модель его не использует, но логика полезна.
    db_messages = (
        db.query(ChatMessage)
        .filter(ChatMessage.session_id == session_id)
        .order_by(ChatMessage.timestamp.asc())
        .all()
    )
    context = [{"role": m.role, "content": m.content} for m in db_messages]

    try:
        # 3. ✅ ИСПРАВЛЕНО: Получаем ответ от AI, передавая только сам промпт (строку).
        #    Функция get_simple_ai_response ожидает строку, а не список.
        ai_response_content = get_simple_ai_response(user_prompt)

        # 4. Сохраняем ответ AI в базу.
        ai_message = ChatMessage(
            session_id=session_id, role="assistant", content=ai_response_content
        )
        db.add(ai_message)
        db.commit()

        # 5. Отправляем ответ на фронтенд.
        return jsonify({"role": "assistant", "content": ai_response_content})

    except Exception as e:
        # ✅ УЛУЧШЕНО: Ловим ошибки от AI сервиса и возвращаем корректный ответ.
        logger.error(f"Ошибка при получении ответа от AI сервиса: {e}", exc_info=True)
        return jsonify({"error": "Внутренняя ошибка при обращении к AI сервису"}), 500
