"""
🛠️ Система и логи - доменные маршруты
"""

import datetime
import logging
import os
import platform

import psutil
from flask import Blueprint, jsonify, make_response, request

from config import Config

system_bp = Blueprint("system_api", __name__)
logger = logging.getLogger("neuro_assistant")


@system_bp.route("/history", methods=["GET"])
def get_history():
    """Возвращает историю выполненных команд"""
    try:
        if not os.path.exists(Config.SUMMARY_LOG_FILE):
            return jsonify({"history": [], "count": 0, "message": "История команд пуста"})

        # Пробуем различные кодировки для чтения файла
        encodings = ["utf-8", "cp1251", "latin-1"]
        summary_content = None

        for encoding in encodings:
            try:
                with open(Config.SUMMARY_LOG_FILE, "r", encoding=encoding) as f:
                    summary_content = f.read()
                break
            except UnicodeDecodeError:
                continue

        if summary_content is None:
            with open(Config.SUMMARY_LOG_FILE, "rb") as f:
                binary_content = f.read()
                summary_content = binary_content.decode("utf-8", errors="ignore")

        # Разбиваем на отдельные записи
        entries = []
        current_entry = {}
        lines = summary_content.split("\n")

        for line in lines:
            if line.startswith("20"):  # Начало новой записи (с даты)
                if current_entry:
                    entries.append(current_entry)
                    current_entry = {}
                parts = line.split(" - ", 1)
                if len(parts) > 1:
                    current_entry["timestamp"] = parts[0]
            elif line.startswith("Команда:"):
                current_entry["command"] = line.replace("Команда:", "").strip()
            elif line.startswith("Статус:"):
                current_entry["status"] = line.replace("Статус:", "").strip()
            elif line.startswith("Выполнение:"):
                current_entry["completion"] = line.replace("Выполнение:", "").strip()
            elif line.startswith("Точность:"):
                current_entry["accuracy"] = line.replace("Точность:", "").strip()

        if current_entry:
            entries.append(current_entry)

        return jsonify({"history": entries, "count": len(entries)})
    except Exception as e:
        logger.error(f"Ошибка при чтении истории: {str(e)}")
        return jsonify({"error": f"Ошибка при чтении истории: {str(e)}", "history": []})


@system_bp.route("/detailed_history/<command_timestamp>", methods=["GET"])
def get_detailed_history(command_timestamp):
    """Возвращает подробную информацию о выполнении команды"""
    try:
        if not os.path.exists(Config.DETAILED_LOG_FILE):
            return jsonify(
                {
                    "command_timestamp": command_timestamp,
                    "details": [],
                    "message": "Детальная история команд пуста",
                }
            )

        with open(Config.DETAILED_LOG_FILE, "r", encoding="utf-8") as f:
            log_content = f.read()

        command_details = []
        command_found = False

        lines = log_content.split("\n")
        for line in lines:
            if command_timestamp in line and "Детальное выполнение команды" in line:
                command_found = True
                command_details.append(line)
            elif command_found:
                command_details.append(line)
                if line.startswith("-" * 50):
                    break

        return jsonify({"command_timestamp": command_timestamp, "details": command_details})
    except Exception as e:
        logger.error(f"Ошибка при чтении подробной истории: {str(e)}")
        return jsonify({"error": f"Ошибка при чтении подробной истории: {str(e)}", "details": []})


@system_bp.route("/logs", methods=["GET"])
def get_system_logs():
    """Возвращает системные логи (только для разработчиков)"""
    developer_mode = request.args.get("developer_mode") == "true"
    developer_key = request.args.get("developer_key", "")

    if not developer_mode or developer_key != Config.DEVELOPER_KEY:
        return jsonify({"error": "Доступ запрещен. Требуется ключ разработчика."}), 403

    try:
        if not os.path.exists(Config.SYSTEM_LOG_FILE):
            return jsonify({"logs": [], "message": "Системные логи пусты"})

        max_lines = int(request.args.get("max_lines", 100))

        with open(Config.SYSTEM_LOG_FILE, "r", encoding="utf-8") as f:
            lines = f.readlines()
            last_lines = lines[-max_lines:] if len(lines) > max_lines else lines

        return jsonify({"logs": last_lines, "count": len(last_lines), "total_lines": len(lines)})
    except Exception as e:
        logger.error(f"Ошибка при чтении системных логов: {str(e)}")
        return jsonify({"error": f"Ошибка при чтении системных логов: {str(e)}", "logs": []}), 500


@system_bp.route("/export_history", methods=["GET"])
def export_history_logs():
    """Экспортирует историю команд в файл"""
    try:
        if not os.path.exists(Config.SUMMARY_LOG_FILE):
            return jsonify({"error": "Файл истории команд не найден"}), 404

        with open(Config.SUMMARY_LOG_FILE, "r", encoding="utf-8") as f:
            content = f.read()

        response = make_response(content)
        response.headers["Content-Type"] = "text/plain"
        response.headers["Content-Disposition"] = "attachment; filename=command_history.txt"

        return response
    except Exception as e:
        logger.error(f"Ошибка при экспорте истории команд: {str(e)}")
        return jsonify({"error": f"Ошибка при экспорте истории команд: {str(e)}"}), 500


@system_bp.route("/export_detailed", methods=["GET"])
def export_detailed_logs():
    """Экспортирует детальные логи в файл"""
    try:
        if not os.path.exists(Config.DETAILED_LOG_FILE):
            return jsonify({"error": "Файл детальных логов не найден"}), 404

        with open(Config.DETAILED_LOG_FILE, "r", encoding="utf-8") as f:
            content = f.read()

        response = make_response(content)
        response.headers["Content-Type"] = "text/plain"
        response.headers["Content-Disposition"] = "attachment; filename=detailed_logs.txt"

        return response
    except Exception as e:
        logger.error(f"Ошибка при экспорте детальных логов: {str(e)}")
        return jsonify({"error": f"Ошибка при экспорте детальных логов: {str(e)}"}), 500


@system_bp.route("/maintenance/ensure_logs", methods=["POST"])
def ensure_log_files_exist_route():
    """Создает необходимые файлы логов, если они не существуют"""
    try:
        from utils.log_maintenance import ensure_log_files_exist

        ensure_log_files_exist()
        return jsonify({"success": True, "message": "Проверка файлов логов выполнена"})
    except Exception as e:
        logger.error(f"Ошибка при создании файлов логов: {str(e)}")
        return jsonify({"success": False, "error": f"Ошибка при создании файлов логов: {str(e)}"})


@system_bp.route("/maintenance/clean_logs", methods=["POST"])
def clean_old_logs_route():
    """Удаляет старые файлы логов"""
    try:
        from utils.log_maintenance import clean_old_logs

        max_age_days = request.json.get("max_age_days", 30) if request.json else 30
        clean_old_logs(max_age_days)
        return jsonify({"success": True, "message": f"Удалены логи старше {max_age_days} дней"})
    except Exception as e:
        logger.error(f"Ошибка при удалении старых логов: {str(e)}")
        return jsonify({"success": False, "error": f"Ошибка при удалении старых логов: {str(e)}"})


@system_bp.route("/monitor", methods=["GET"])
def get_system_monitor():
    """Возвращает детальную системную информацию"""
    try:
        system_info = {
            "os": {
                "name": platform.system(),
                "version": platform.version(),
                "machine": platform.machine(),
                "processor": platform.processor(),
            },
            "cpu": {
                "percent": psutil.cpu_percent(interval=1),
                "count": psutil.cpu_count(),
                "freq": psutil.cpu_freq()._asdict() if psutil.cpu_freq() else {},
            },
            "memory": {
                "total": psutil.virtual_memory().total,
                "available": psutil.virtual_memory().available,
                "percent": psutil.virtual_memory().percent,
                "used": psutil.virtual_memory().used,
            },
            "disk": [],
            "network": psutil.net_io_counters()._asdict(),
            "processes": len(psutil.pids()),
        }

        # Информация о дисках
        for partition in psutil.disk_partitions():
            try:
                partition_usage = psutil.disk_usage(partition.mountpoint)
                system_info["disk"].append(
                    {
                        "device": partition.device,
                        "mountpoint": partition.mountpoint,
                        "fstype": partition.fstype,
                        "total": partition_usage.total,
                        "used": partition_usage.used,
                        "free": partition_usage.free,
                        "percent": (partition_usage.used / partition_usage.total) * 100,
                    }
                )
            except PermissionError:
                continue

        return jsonify(
            {
                "success": True,
                "system": system_info,
                "timestamp": datetime.datetime.now().isoformat(),
            }
        )

    except Exception as e:
        logger.error(f"Ошибка получения системной информации: {str(e)}")
        return (
            jsonify(
                {"success": False, "error": f"Ошибка получения системной информации: {str(e)}"}
            ),
            500,
        )


@system_bp.route("/status", methods=["GET"])
def get_dashboard_status():
    """Возвращает общий статус системы для главной страницы"""
    try:
        from services.ai_service import get_ai_models

        models_data = get_ai_models()
        current_model = None

        if models_data.get("success") and models_data.get("models"):
            for model in models_data["models"]:
                if model.get("is_active"):
                    current_model = {
                        "name": model.get("name", "Неизвестная модель"),
                        "status": model.get("status", "unavailable"),
                        "provider": model.get("provider", ""),
                    }
                    break

        if not current_model:
            current_model = {"name": "Не выбрана", "status": "unavailable", "provider": ""}

        # Получаем системные метрики
        system_metrics = {
            "cpu": round(psutil.cpu_percent(interval=1), 1),
            "ram": round(psutil.virtual_memory().percent, 1),
            "disk": (
                round(psutil.disk_usage("/").percent, 1)
                if hasattr(psutil.disk_usage("/"), "percent")
                else 0
            ),
        }

        # Получаем информацию о последней активности
        last_activity = None
        try:
            if os.path.exists(Config.SUMMARY_LOG_FILE):
                with open(Config.SUMMARY_LOG_FILE, "r", encoding="utf-8", errors="ignore") as f:
                    lines = f.readlines()
                    if lines:
                        for line in reversed(lines[-10:]):
                            if line.startswith("20"):
                                parts = line.split(" - ", 1)
                                if len(parts) > 1:
                                    last_activity = {
                                        "time": parts[0],
                                        "result": "Выполнено",
                                        "status": "success",
                                    }
                                    break
        except Exception as e:
            logger.warning(f"Ошибка чтения последней активности: {e}")

        if not last_activity:
            last_activity = {"time": "", "result": "Нет данных", "status": "unknown"}

        return jsonify(
            {
                "success": True,
                "model": current_model,
                "system": system_metrics,
                "lastActivity": last_activity,
                "timestamp": datetime.datetime.now().isoformat(),
            }
        )

    except Exception as e:
        logger.error(f"Ошибка получения статуса dashboard: {str(e)}")
        return (
            jsonify(
                {
                    "success": False,
                    "error": f"Ошибка получения статуса: {str(e)}",
                    "model": {"name": "Ошибка", "status": "error"},
                    "system": {"cpu": 0, "ram": 0},
                    "lastActivity": {"time": "", "result": "Ошибка", "status": "error"},
                }
            ),
            500,
        )


@system_bp.route("/monitor/toggle", methods=["POST"])
def toggle_system_monitoring():
    """Включение/выключение системного мониторинга"""
    try:
        from services.system_monitor_service import SystemMonitorService

        data = request.get_json()
        enabled = data.get("enabled", True)

        service = SystemMonitorService()
        result = service.toggle_monitoring(enabled)

        return jsonify(
            {
                "success": True,
                "monitoring_enabled": result,
                "message": f"Мониторинг {'включен' if result else 'выключен'}",
            }
        )

    except Exception as e:
        logger.error(f"Ошибка переключения мониторинга: {str(e)}")
        return (
            jsonify({"success": False, "error": f"Ошибка переключения мониторинга: {str(e)}"}),
            500,
        )
