"""
⚡ Задачи и команды - доменные маршруты
"""

import datetime
import logging

from flask import Blueprint, jsonify, request

from models.command_models import CommandExecution, CommandStep
from services.command_service import (
    execute_command_with_error_handling,
    execute_command_with_steps,
    execute_python_code,
    process_command,
)
from utils.logging_utils import log_execution_summary

task_bp = Blueprint("task_api", __name__)
logger = logging.getLogger("neuro_assistant")


@task_bp.route("/query", methods=["POST"])
def query():
    """Основной эндпоинт для выполнения команд"""
    if request.json is None:
        return jsonify({"error": "Ожидался JSON в теле запроса"}), 400

    user_input = request.json.get("input", "").lower()

    # Проверяем составную команду
    if any(sep in user_input for sep in [" и ", " затем ", " после этого ", " потом ", ", "]):
        execution_result = execute_command_with_steps(user_input)

        steps_info = []
        for step in execution_result.steps:
            step_info = {
                "number": step.step_number,
                "description": step.description,
                "status": step.status,
                "result": step.result if step.status == "completed" else step.error,
            }
            steps_info.append(step_info)

        return jsonify(
            {
                "response": f"Выполнение команды: {user_input}",
                "is_compound": True,
                "steps": steps_info,
                "overall_status": execution_result.overall_status,
                "completion_percentage": execution_result.completion_percentage,
                "accuracy_percentage": execution_result.accuracy_percentage,
                "message": (
                    f"Команда выполнена с точностью {execution_result.accuracy_percentage:.1f}% и"
                    f" завершенностью {execution_result.completion_percentage:.1f}%"
                ),
            }
        )
    else:
        # Простая команда
        response, code = process_command(user_input)

        if code:
            execution_result = execute_python_code(code)

            step = CommandStep(
                step_number=1,
                description=user_input,
                status="completed" if "Ошибка" not in execution_result else "failed",
                result=execution_result if "Ошибка" not in execution_result else None,
                error=execution_result if "Ошибка" in execution_result else None,
                completion_percentage=100.0 if "Ошибка" not in execution_result else 0.0,
            )

            execution = CommandExecution(
                command_text=user_input,
                steps=[step],
                start_time=datetime.datetime.now().isoformat(),
                end_time=datetime.datetime.now().isoformat(),
                overall_status="completed" if "Ошибка" not in execution_result else "failed",
                completion_percentage=100.0 if "Ошибка" not in execution_result else 0.0,
                accuracy_percentage=90.0 if "Ошибка" not in execution_result else 0.0,
            )

            log_execution_summary(execution, final=True)

            return jsonify(
                {
                    "response": response,
                    "code": code,
                    "execution_result": execution_result,
                    "is_compound": False,
                    "overall_status": execution.overall_status,
                    "completion_percentage": execution.completion_percentage,
                    "accuracy_percentage": execution.accuracy_percentage,
                }
            )
        else:
            return jsonify(
                {
                    "response": response,
                    "code": None,
                    "execution_result": "Не удалось сгенерировать код для выполнения команды",
                    "is_compound": False,
                    "overall_status": "failed",
                    "completion_percentage": 0.0,
                    "accuracy_percentage": 0.0,
                    "message": (
                        "Пожалуйста, уточните команду или используйте предустановленные команды"
                    ),
                }
            )


@task_bp.route("/clarify", methods=["POST"])
def clarify():
    """Обрабатывает запросы на уточнение"""
    if request.json is None:
        return jsonify({"error": "Ожидался JSON в теле запроса"}), 400

    user_input = request.json.get("input", "")
    original_command = request.json.get("original_command", "")
    error_context = request.json.get("error_context", {})

    logger.debug(f"Получен контекст ошибки: {error_context}")
    logger.info(f"Получено уточнение от пользователя: {user_input}")

    new_command = f"{original_command} ({user_input})"
    response, code = process_command(new_command)

    if code:
        result = execute_command_with_error_handling(new_command, code)
        return jsonify(
            {
                "response": response,
                "code": code,
                "execution_result": result.get("execution_result"),
                "verification_result": result.get("verification_result"),
                "error_analysis": result.get("error_analysis", {}),
                "screenshot": result.get("screenshot"),
                "message": result.get("message"),
            }
        )
    else:
        return jsonify(
            {
                "response": "Не удалось сгенерировать код даже с учетом уточнения",
                "code": None,
                "execution_result": "Не удалось сгенерировать код для выполнения команды",
                "message": (
                    "Пожалуйста, используйте предустановленные команды или сформулируйте запрос"
                    " иначе"
                ),
            }
        )


@task_bp.route("/confirm", methods=["POST"])
def confirm_action():
    """Обрабатывает подтверждение действия"""
    if request.json is None:
        return jsonify({"error": "Ожидался JSON в теле запроса"}), 400

    user_confirmation = request.json.get("confirmation", False)
    command = request.json.get("command", "")
    code = request.json.get("code", "")

    if not user_confirmation:
        return jsonify(
            {
                "response": "Действие отменено пользователем",
                "code": code,
                "execution_result": None,
                "message": "Команда не была выполнена по решению пользователя",
            }
        )

    result = execute_command_with_error_handling(command, code)

    return jsonify(
        {
            "response": f"Команда подтверждена и выполнена: {command}",
            "code": code,
            "execution_result": result.get("execution_result"),
            "verification_result": result.get("verification_result"),
            "error_analysis": result.get("error_analysis", {}),
            "screenshot": result.get("screenshot"),
            "message": result.get("message"),
        }
    )


@task_bp.route("/interrupt", methods=["POST"])
def interrupt_command():
    """Прерывает выполнение текущей команды"""
    global command_interrupt_flag
    command_interrupt_flag = True

    logger.info("Получен запрос на прерывание команды")

    return jsonify(
        {
            "success": True,
            "message": (
                "Запрос на прерывание команды получен. Выполнение будет остановлено при первой"
                " возможности."
            ),
        }
    )


@task_bp.route("/recent", methods=["GET"])
def get_recent_tasks():
    """Возвращает последние задачи для Dashboard"""
    try:
        count = int(request.args.get("count", 5))

        # Мок-данные для демонстрации
        mock_activities = [
            {
                "id": 1,
                "description": "Открытие браузера",
                "time": (datetime.datetime.now() - datetime.timedelta(minutes=5)).isoformat(),
                "status": "success",
                "result": "Браузер успешно открыт",
            },
            {
                "id": 2,
                "description": "Поиск файла report.pdf",
                "time": (datetime.datetime.now() - datetime.timedelta(minutes=15)).isoformat(),
                "status": "success",
                "result": "Файл найден",
            },
            {
                "id": 3,
                "description": "Создание папки проекты",
                "time": (datetime.datetime.now() - datetime.timedelta(minutes=30)).isoformat(),
                "status": "running",
                "result": "В процессе выполнения",
            },
        ]

        activities = mock_activities[:count]

        return jsonify(
            {
                "success": True,
                "activities": activities,
                "active": 1,
                "queued": 2,
                "total": len(activities),
            }
        )

    except Exception as e:
        logger.error(f"Ошибка получения последних задач: {str(e)}")
        return (
            jsonify(
                {
                    "success": False,
                    "error": f"Ошибка получения задач: {str(e)}",
                    "activities": [],
                    "active": 0,
                    "queued": 0,
                }
            ),
            500,
        )
