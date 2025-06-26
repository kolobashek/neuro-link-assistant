import logging
import threading
import time
from datetime import datetime

import psutil

logger = logging.getLogger("neuro_assistant")


class SystemMonitorService:
    """Сервис мониторинга системы"""

    def __init__(self):
        self.monitoring_enabled = False
        self.monitoring_thread = None
        self.monitoring_data = {}
        self.lock = threading.Lock()

    def toggle_monitoring(self, enabled):
        """Включение/выключение мониторинга"""
        try:
            with self.lock:
                if enabled and not self.monitoring_enabled:
                    self.monitoring_enabled = True
                    self.start_monitoring()
                    logger.info("Системный мониторинг включен")
                elif not enabled and self.monitoring_enabled:
                    self.monitoring_enabled = False
                    self.stop_monitoring()
                    logger.info("Системный мониторинг выключен")

                return self.monitoring_enabled
        except Exception as e:
            logger.error(f"Ошибка переключения мониторинга: {e}")
            return False

    def start_monitoring(self):
        """Запуск потока мониторинга"""
        if self.monitoring_thread is None or not self.monitoring_thread.is_alive():
            self.monitoring_thread = threading.Thread(target=self._monitoring_loop, daemon=True)
            self.monitoring_thread.start()

    def stop_monitoring(self):
        """Остановка мониторинга"""
        self.monitoring_enabled = False
        if self.monitoring_thread and self.monitoring_thread.is_alive():
            self.monitoring_thread.join(timeout=1)

    def _monitoring_loop(self):
        """Основной цикл мониторинга"""
        while self.monitoring_enabled:
            try:
                # Обновляем данные мониторинга
                with self.lock:
                    self.monitoring_data = self._collect_system_data()

                # Ждем 5 секунд до следующего обновления
                time.sleep(5)
            except Exception as e:
                logger.error(f"Ошибка в цикле мониторинга: {e}")
                time.sleep(10)  # Увеличиваем интервал при ошибке

    def get_live_metrics(self):
        """Получить текущие метрики в реальном времени"""
        try:
            with self.lock:
                if self.monitoring_enabled and self.monitoring_data:
                    return {
                        "success": True,
                        "data": self.monitoring_data.copy(),
                        "monitoring_enabled": True,
                        "timestamp": datetime.now().isoformat(),
                    }
                else:
                    # Если мониторинг выключен, получаем данные один раз
                    return {
                        "success": True,
                        "data": self._collect_system_data(),
                        "monitoring_enabled": False,
                        "timestamp": datetime.now().isoformat(),
                    }
        except Exception as e:
            logger.error(f"Ошибка получения live метрик: {e}")
            return {
                "success": False,
                "error": str(e),
                "monitoring_enabled": self.monitoring_enabled,
            }

    def _collect_system_data(self):
        """Сбор системных данных"""
        try:
            # CPU
            cpu_percent = psutil.cpu_percent(interval=0.1)
            cpu_freq = psutil.cpu_freq()

            # Память
            memory = psutil.virtual_memory()

            # Диски
            disk_usage = psutil.disk_usage("/")
            disk_io = psutil.disk_io_counters()

            # Сеть
            net_io = psutil.net_io_counters()

            # Процессы
            processes = self._get_top_processes()

            return {
                "cpu": {
                    "percent": round(cpu_percent, 1),
                    "count": psutil.cpu_count(),
                    "frequency": {
                        "current": round(cpu_freq.current, 0) if cpu_freq else 0,
                        "max": round(cpu_freq.max, 0) if cpu_freq else 0,
                    },
                },
                "memory": {
                    "percent": round(memory.percent, 1),
                    "total": round(memory.total / (1024**3), 2),
                    "available": round(memory.available / (1024**3), 2),
                    "used": round(memory.used / (1024**3), 2),
                },
                "disk": {
                    "percent": round(disk_usage.percent, 1),
                    "total": round(disk_usage.total / (1024**3), 2),
                    "free": round(disk_usage.free / (1024**3), 2),
                    "io": {
                        "read_mb": round(disk_io.read_bytes / (1024**2), 1) if disk_io else 0,
                        "write_mb": round(disk_io.write_bytes / (1024**2), 1) if disk_io else 0,
                    },
                },
                "network": {
                    "bytes_sent": round(net_io.bytes_sent / (1024**2), 1),
                    "bytes_recv": round(net_io.bytes_recv / (1024**2), 1),
                    "packets_sent": net_io.packets_sent,
                    "packets_recv": net_io.packets_recv,
                },
                "processes": processes,
                "uptime": self._get_uptime(),
            }
        except Exception as e:
            logger.error(f"Ошибка сбора системных данных: {e}")
            return {}

    def _get_top_processes(self, limit=10):
        """Получить топ процессов по использованию ресурсов"""
        try:
            processes = []
            for proc in psutil.process_iter(["pid", "name", "cpu_percent", "memory_percent"]):
                try:
                    pinfo = proc.info
                    if pinfo["cpu_percent"] > 0.1 or pinfo["memory_percent"] > 0.1:
                        processes.append(
                            {
                                "pid": pinfo["pid"],
                                "name": pinfo["name"][:20],  # Ограничиваем длину имени
                                "cpu": round(pinfo["cpu_percent"], 1),
                                "memory": round(pinfo["memory_percent"], 1),
                            }
                        )
                except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                    continue

            # Сортируем по CPU и берем топ
            processes.sort(key=lambda x: x["cpu"], reverse=True)
            return {"total": len(psutil.pids()), "top": processes[:limit]}
        except Exception as e:
            logger.error(f"Ошибка получения процессов: {e}")
            return {"total": 0, "top": []}

    def _get_uptime(self):
        """Получить время работы системы"""
        try:
            boot_time = psutil.boot_time()
            uptime_seconds = time.time() - boot_time
            uptime_hours = uptime_seconds / 3600
            return round(uptime_hours, 1)
        except Exception as e:
            logger.error(f"Ошибка получения uptime: {e}")
            return 0

    def get_system_info(self):
        """Получить общую информацию о системе"""
        try:
            import platform

            return {
                "os": {
                    "name": platform.system(),
                    "version": platform.version(),
                    "machine": platform.machine(),
                    "processor": platform.processor(),
                },
                "python": {
                    "version": platform.python_version(),
                    "implementation": platform.python_implementation(),
                },
                "hardware": {
                    "cpu_count": psutil.cpu_count(),
                    "memory_total": round(psutil.virtual_memory().total / (1024**3), 2),
                },
            }
        except Exception as e:
            logger.error(f"Ошибка получения информации о системе: {e}")
            return {}
