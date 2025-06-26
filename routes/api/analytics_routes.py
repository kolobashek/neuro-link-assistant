"""
📊 Аналитика - доменные маршруты
"""

import datetime
import logging

from flask import Blueprint, jsonify, request

analytics_bp = Blueprint("analytics_api", __name__)
logger = logging.getLogger("neuro_assistant")


@analytics_bp.route("/dashboard", methods=["GET"])
def get_dashboard_analytics():
    """Возвращает аналитические данные для dashboard"""
    try:
        # Мок-данные для демонстрации
        analytics_data = {
            "commands_today": 15,
            "success_rate": 87.5,
            "avg_response_time": 1.2,
            "active_models": 3,
            "chart_data": {
                "hourly_activity": [2, 4, 1, 6, 8, 12, 9, 7, 5, 3, 1, 0],
                "command_types": {"system": 8, "web": 4, "file": 3},
            },
        }

        return jsonify(
            {
                "success": True,
                "analytics": analytics_data,
                "timestamp": datetime.datetime.now().isoformat(),
            }
        )

    except Exception as e:
        logger.error(f"Ошибка получения аналитики dashboard: {str(e)}")
        return jsonify({"success": False, "error": f"Ошибка получения аналитики: {str(e)}"}), 500


@analytics_bp.route("/reports", methods=["GET"])
def get_reports():
    """Возвращает отчеты по использованию"""
    try:
        period = request.args.get("period", "week")  # day, week, month

        # Мок-данные отчетов
        reports_data = {
            "period": period,
            "total_commands": 156,
            "successful_commands": 143,
            "failed_commands": 13,
            "most_used_models": [
                {"name": "GPT-3.5", "usage": 45},
                {"name": "Claude", "usage": 32},
                {"name": "Llama2", "usage": 23},
            ],
            "peak_hours": [14, 15, 16],
            "command_categories": {"automation": 67, "information": 45, "system": 44},
        }

        return jsonify(
            {
                "success": True,
                "reports": reports_data,
                "generated_at": datetime.datetime.now().isoformat(),
            }
        )

    except Exception as e:
        logger.error(f"Ошибка получения отчетов: {str(e)}")
        return jsonify({"success": False, "error": f"Ошибка получения отчетов: {str(e)}"}), 500
