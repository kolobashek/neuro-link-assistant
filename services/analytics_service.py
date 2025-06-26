import datetime
import logging
import os
from pathlib import Path

import psutil

from config import Config

logger = logging.getLogger("neuro_assistant")


class AnalyticsService:
    """Сервис аналитики для различных типов данных"""

    def __init__(self):
        self.config = Config

    def get_app_analytics(self):
        """Получить аналитику работы приложения"""
        try:
            # Статистика команд
            commands_stats = self._get_commands_statistics()

            # Использование моделей
            models_usage = self._get_models_usage()

            # Производительность
            performance_stats = self._get_performance_statistics()

            return {
                "commands": commands_stats,
                "models": models_usage,
                "performance": performance_stats,
                "period": "last_30_days",
            }
        except Exception as e:
            logger.error(f"Ошибка получения аналитики приложения: {e}")
            return {}

    def get_system_analytics(self):
        """Получить системную аналитику"""
        try:
            # Ресурсы системы
            system_resources = self._get_system_resources()

            # Процессы
            processes_info = self._get_processes_info()

            # Сетевая активность
            network_stats = self._get_network_statistics()

            return {
                "resources": system_resources,
                "processes": processes_info,
                "network": network_stats,
                "timestamp": datetime.datetime.now().isoformat(),
            }
        except Exception as e:
            logger.error(f"Ошибка получения системной аналитики: {e}")
            return {}

    def get_task_analytics(self, period="week", task_type="all"):
        """Получить аналитику задач"""
        try:
            # Статистика выполнения задач
            execution_stats = self._get_task_execution_stats(period, task_type)

            # Временные метрики
            time_metrics = self._get_task_time_metrics(period, task_type)

            # Типы задач
            task_types_stats = self._get_task_types_statistics(period)

            return {
                "execution": execution_stats,
                "time_metrics": time_metrics,
                "task_types": task_types_stats,
                "period": period,
                "filter": task_type,
            }
        except Exception as e:
            logger.error(f"Ошибка получения аналитики задач: {e}")
            return {}

    def _get_commands_statistics(self):
        """Статистика команд из логов"""
        try:
            if not os.path.exists(self.config.SUMMARY_LOG_FILE):
                return {"total": 0, "successful": 0, "failed": 0, "popular": []}

            # Простая статистика из логов
            total_commands = 0
            successful_commands = 0
            failed_commands = 0
            command_counts = {}

            with open(self.config.SUMMARY_LOG_FILE, "r", encoding="utf-8", errors="ignore") as f:
                for line in f:
                    if "Команда:" in line:
                        total_commands += 1
                        command = line.split("Команда:")[1].strip()
                        command_counts[command] = command_counts.get(command, 0) + 1
                    elif "Статус: completed" in line:
                        successful_commands += 1
                    elif "Статус: failed" in line:
                        failed_commands += 1

            # Топ-5 популярных команд
            popular_commands = sorted(command_counts.items(), key=lambda x: x[1], reverse=True)[:5]

            return {
                "total": total_commands,
                "successful": successful_commands,
                "failed": failed_commands,
                "success_rate": (
                    (successful_commands / total_commands * 100) if total_commands > 0 else 0
                ),
                "popular": [{"command": cmd, "count": count} for cmd, count in popular_commands],
            }
        except Exception as e:
            logger.error(f"Ошибка получения статистики команд: {e}")
            return {"total": 0, "successful": 0, "failed": 0, "popular": []}

    def _get_models_usage(self):
        """Статистика использования моделей"""
        try:
            from services.ai_service import get_ai_models

            models_data = get_ai_models()
            models = models_data.get("models", [])

            active_models = [m for m in models if m.get("is_active", False)]
            total_models = len(models)

            return {
                "total_models": total_models,
                "active_models": len(active_models),
                "current_model": next(
                    (m["name"] for m in models if m.get("is_current", False)), "Не выбрана"
                ),
                "ready_models": len([m for m in models if m.get("status") == "ready"]),
            }
        except Exception as e:
            logger.error(f"Ошибка получения статистики моделей: {e}")
            return {}

    def _get_performance_statistics(self):
        """Статистика производительности"""
        return {
            "avg_response_time": 1.2,  # Заглушка
            "total_requests": 156,  # Заглушка
            "error_rate": 5.2,  # Заглушка
            "uptime_hours": 24,  # Заглушка
        }

    def _get_system_resources(self):
        """Ресурсы системы"""
        try:
            cpu_percent = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage("/")

            return {
                "cpu": {"percent": round(cpu_percent, 1), "cores": psutil.cpu_count()},
                "memory": {
                    "percent": round(memory.percent, 1),
                    "total_gb": round(memory.total / (1024**3), 1),
                    "used_gb": round(memory.used / (1024**3), 1),
                },
                "disk": {
                    "percent": round(disk.percent, 1),
                    "total_gb": round(disk.total / (1024**3), 1),
                    "free_gb": round(disk.free / (1024**3), 1),
                },
            }
        except Exception as e:
            logger.error(f"Ошибка получения ресурсов системы: {e}")
            return {}

    def _get_processes_info(self):
        """Информация о процессах"""
        try:
            processes = []
            for proc in psutil.process_iter(["pid", "name", "cpu_percent", "memory_percent"]):
                try:
                    if proc.info["cpu_percent"] > 1.0 or proc.info["memory_percent"] > 1.0:
                        processes.append(
                            {
                                "pid": proc.info["pid"],
                                "name": proc.info["name"],
                                "cpu": round(proc.info["cpu_percent"], 1),
                                "memory": round(proc.info["memory_percent"], 1),
                            }
                        )
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue

            # Топ-10 по использованию CPU
            top_processes = sorted(processes, key=lambda x: x["cpu"], reverse=True)[:10]

            return {"total_processes": len(psutil.pids()), "top_cpu": top_processes}
        except Exception as e:
            logger.error(f"Ошибка получения информации о процессах: {e}")
            return {}

    def _get_network_statistics(self):
        """Сетевая статистика"""
        try:
            net_io = psutil.net_io_counters()
            return {
                "bytes_sent_mb": round(net_io.bytes_sent / (1024**2), 1),
                "bytes_recv_mb": round(net_io.bytes_recv / (1024**2), 1),
                "packets_sent": net_io.packets_sent,
                "packets_recv": net_io.packets_recv,
            }
        except Exception as e:
            logger.error(f"Ошибка получения сетевой статистики: {e}")
            return {}

    def _get_task_execution_stats(self, period, task_type):
        """Статистика выполнения задач (заглушка)"""
        return {
            "total_tasks": 45,
            "completed": 38,
            "failed": 5,
            "in_progress": 2,
            "success_rate": 84.4,
        }

    def _get_task_time_metrics(self, period, task_type):
        """Временные метрики задач (заглушка)"""
        return {
            "avg_execution_time": 2.3,
            "min_execution_time": 0.5,
            "max_execution_time": 12.8,
            "total_time_hours": 1.8,
        }

    def _get_task_types_statistics(self, period):
        """Статистика типов задач (заглушка)"""
        return [
            {"type": "Открытие приложений", "count": 15, "percent": 33.3},
            {"type": "Анализ текста", "count": 12, "percent": 26.7},
            {"type": "Поиск файлов", "count": 8, "percent": 17.8},
            {"type": "Системные команды", "count": 6, "percent": 13.3},
            {"type": "Другое", "count": 4, "percent": 8.9},
        ]
