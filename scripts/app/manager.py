"""Объединенный менеджер приложений с полным функционалом"""

import os
import signal  # ✅ Для корректной остановки процессов
import socket  # ✅ Для работы с портами
import subprocess
import sys
import time
from enum import Enum
from pathlib import Path
from typing import Any, Dict, Optional

import requests


# ✅ Добавляем определение AppMode если его нет
class AppMode(Enum):
    TESTING = "testing"
    DEVELOPMENT = "development"
    PRODUCTION = "production"
    EXTERNAL = "external"


# ✅ ИСПРАВЛЯЕМ AppConfig - добавляем недостающие атрибуты
class AppConfig:
    def __init__(
        self,
        port: int = 5000,
        host: str = "127.0.0.1",
        mode: AppMode = AppMode.DEVELOPMENT,
        debug: bool = False,
        auto_cleanup: bool = True,
        force_kill: bool = False,
        timeout: int = 45,  # ✅ ДОБАВЛЯЕМ
        health_endpoints: Optional[list] = None,  # ✅ ДОБАВЛЯЕМ
    ):
        self.port = port
        self.host = host
        self.mode = mode
        self.debug = debug
        self.auto_cleanup = auto_cleanup
        self.force_kill = force_kill
        self.timeout = timeout  # ✅ ДОБАВЛЯЕМ
        self.health_endpoints = health_endpoints or ["/", "/health"]  # ✅ ДОБАВЛЯЕМ

    def get_port_config(self) -> Dict[str, Any]:
        """Возвращает конфигурацию для PortManager"""
        return {"port": self.port, "host": self.host, "auto_cleanup": self.auto_cleanup}


# ✅ УБИРАЕМ проблемный импорт HealthChecker
# from .health_check import HealthChecker  # ❌ УБИРАЕМ

# ✅ ИСПРАВЛЯЕМ импорт PortManager - делаем безопасным
try:
    from ..network.port_manager import PortManager
except ImportError:
    print("⚠️ PortManager не найден, используем заглушку")
    PortManager = None


class AppManager:
    """Универсальный менеджер приложений"""

    def __init__(self, config: Optional[AppConfig] = None):
        self.config = config or AppConfig()
        self.app_url = f"http://{self.config.host}:{self.config.port}"
        self.process: Optional[subprocess.Popen] = None
        self.app_dir = Path(__file__).parent.parent.parent
        self._start_time: Optional[float] = None
        self._metrics: Dict[str, Any] = {}

        # ✅ ТОЛЬКО ErrorHandler, никакого logging
        self.error_handler = None

        try:
            # Попытка получить ErrorHandler через систему проекта
            from core.common.error_handler import get_error_handler

            self.error_handler = get_error_handler()

            # Проверяем работоспособность
            if self.error_handler and hasattr(self.error_handler, "log_info"):
                self.error_handler.log_info("🚀 AppManager инициализирован с ErrorHandler")
            else:
                print("⚠️ ErrorHandler получен, но не имеет ожидаемых методов")
                self.error_handler = None

        except ImportError as e:
            print(f"⚠️ Модуль ErrorHandler не найден: {e}")
            self.error_handler = None
        except Exception as e:
            print(f"⚠️ Ошибка инициализации ErrorHandler: {e}")
            self.error_handler = None

        # ✅ ИСПРАВЛЯЕМ инициализацию PortManager
        self.port_manager: Optional[Any] = None
        try:
            if PortManager is not None:
                # ✅ ИСПРАВЛЯЕМ - создаем PortConfig вместо прямых параметров
                from ..network.port_manager import PortConfig

                port_config = PortConfig(
                    port=self.config.port,
                    host=self.config.host,
                    # auto_cleanup не существует в PortConfig, убираем
                )
                self.port_manager = PortManager(config=port_config)

                if self.error_handler:
                    self.error_handler.log_info("🔌 PortManager инициализирован")
        except Exception as e:
            print(f"⚠️ Не удалось инициализировать PortManager: {e}")
            self.port_manager = None

    # === ОСНОВНЫЕ МЕТОДЫ ===

    def start_app(self) -> bool:
        """Запускает приложение с полной диагностикой"""
        self._start_time = time.perf_counter()
        self._log(
            "🚀 Запуск приложения", {"mode": self.config.mode.value, "port": self.config.port}
        )

        # Быстрая проверка существующего приложения
        if self.is_app_running():
            elapsed = time.perf_counter() - self._start_time
            self._log("✅ Приложение уже работает", {"check_time": f"{elapsed:.3f}s"})
            return True

        # Режим внешнего приложения
        if self.config.mode == AppMode.EXTERNAL:
            return self._handle_external_app()

        # ✅ Используем безопасные обертки вместо прямых вызовов
        if self.config.auto_cleanup and self._is_port_in_use(self.config.port):
            self._log("🧹 Очистка порта", {"port": self.config.port})

            # Используем безопасную очистку
            if not self._cleanup_port(self.config.port):
                self._log("❌ Не удалось очистить порт, ищем свободный...")
                try:
                    new_port = self._find_free_port()
                    self._log("✅ Найден свободный порт", {"new_port": new_port})

                    # Обновляем конфигурацию
                    self.config.port = new_port
                    # Пересоздаем PortManager с новым портом
                    try:
                        if PortManager is not None:
                            from ..network.port_manager import PortConfig

                            port_config = PortConfig(
                                port=self.config.port,
                                host=self.config.host,
                                # auto_cleanup не существует в PortConfig
                            )

                            self.port_manager = PortManager(config=port_config)
                    except Exception:
                        pass  # Не критично, если PortManager не создался
                    self.app_url = f"http://{self.config.host}:{self.config.port}"

                except Exception as e:
                    self._log_error("❌ Не найден свободный порт", e)
                    return False

        # Запуск приложения
        try:
            if not self._launch_subprocess():
                return False

            # ✅ Используем безопасную обертку
            if not self._wait_for_port_free(self.config.port, timeout=2):
                time.sleep(1)  # Небольшая задержка

            if not self._wait_for_ready():
                self.stop_app()
                return False

            # Финальная проверка стабильности
            if not self.health_check():
                self._log("❌ Приложение нестабильно")
                self.stop_app()
                return False

            total_time = time.perf_counter() - self._start_time
            self._log(
                "✅ Приложение успешно запущено",
                {
                    "total_time": f"{total_time:.3f}s",
                    "url": self.app_url,
                    "pid": self.process.pid if self.process else None,
                },
            )
            return True

        except Exception as e:
            self._log_error("❌ Ошибка запуска", e)
            self.stop_app()
            return False

    def stop_app(self) -> bool:
        """Корректно останавливает приложение"""
        stop_start = time.perf_counter()
        self._log("🛑 Остановка приложения")

        # Внешнее приложение не останавливаем
        if self.config.mode == AppMode.EXTERNAL:
            self._log("ℹ️ Внешнее приложение остается работать")
            return True

        success = True

        # Остановка нашего процесса
        if self.process and self.process.poll() is None:
            try:
                self._log("🔄 Корректное завершение процесса", {"pid": self.process.pid})

                # Мягкое завершение
                if os.name == "nt":
                    try:
                        self.process.send_signal(signal.CTRL_BREAK_EVENT)
                    except (AttributeError, OSError):
                        # Если CTRL_BREAK_EVENT недоступен, используем terminate
                        self.process.terminate()
                else:
                    self.process.terminate()

                # Ждем завершения
                try:
                    self.process.wait(timeout=10)
                    self._log("✅ Процесс завершен корректно")
                except subprocess.TimeoutExpired:
                    self._log("⚠️ Принудительное завершение")
                    self.process.kill()
                    self.process.wait()

            except Exception as e:
                self._log_error("❌ Ошибка остановки процесса", e)
                success = False

        self.process = None

        # ✅ Используем безопасную обертку
        if self.config.auto_cleanup:
            time.sleep(1)  # Даем время на освобождение ресурсов
            if self._is_port_in_use(self.config.port):
                self._log("🧹 Дополнительная очистка порта")
                self._cleanup_port(self.config.port)

        stop_time = time.perf_counter() - stop_start
        self._log("✅ Остановка завершена", {"time": f"{stop_time:.3f}s"})
        return success

    def restart_app(self) -> bool:
        """Перезапускает приложение"""
        self._log("🔄 Перезапуск приложения")
        self.stop_app()
        time.sleep(2)
        return self.start_app()

    # === ПРОВЕРКИ СОСТОЯНИЯ ===

    def is_app_running(self) -> bool:
        """Быстрая проверка доступности приложения"""
        try:
            response = requests.get(self.app_url, timeout=2)
            return 200 <= response.status_code < 500
        except:
            return False

    def health_check(self) -> bool:
        """Детальная проверка здоровья приложения"""
        if not self.is_app_running():
            return False

        try:
            for endpoint in self.config.health_endpoints:
                response = requests.get(f"{self.app_url}{endpoint}", timeout=5)
                if response.status_code >= 500:
                    return False
            return True
        except:
            return False

    def get_status(self) -> Dict[str, Any]:
        """Получает детальный статус приложения"""
        return {
            "running": self.is_app_running(),
            "healthy": self.health_check(),
            "port_occupied": self._is_port_in_use(self.config.port),  # ✅ БЕЗОПАСНАЯ ОБЕРТКА
            "process_alive": self.process and self.process.poll() is None,
            "config": {
                "port": self.config.port,
                "mode": self.config.mode.value,
                "url": self.app_url,
            },
            "metrics": self._metrics,
        }

    # === ВНУТРЕННИЕ МЕТОДЫ ===

    def _handle_external_app(self) -> bool:
        """Обработка внешнего приложения"""
        if self.is_app_running():
            self._log("✅ Внешнее приложение доступно")
            return True
        else:
            self._log("❌ Внешнее приложение недоступно")
            return False

    def _launch_subprocess(self) -> bool:
        """Запускает subprocess приложения"""
        try:
            launch_start = time.perf_counter()

            # Настройки для subprocess
            startup_info = None
            creation_flags = 0

            if os.name == "nt":  # Windows
                startup_info = subprocess.STARTUPINFO()
                startup_info.dwFlags |= subprocess.STARTF_USESHOWWINDOW
                startup_info.wShowWindow = subprocess.SW_HIDE
                creation_flags = subprocess.CREATE_NEW_PROCESS_GROUP

            # Переменные окружения с правильным портом
            env = os.environ.copy()
            env.update(
                {
                    "FLASK_ENV": self.config.mode.value,
                    "TESTING": "true" if self.config.mode == AppMode.TESTING else "false",
                    "PYTHONIOENCODING": "utf-8",
                    "PYTHONPATH": str(self.app_dir),
                    "APP_PORT": str(self.config.port),
                    "TEST_PORT": str(self.config.port),
                }
            )

            # Запуск с передачей порта
            self.process = subprocess.Popen(
                [sys.executable, "-m", "app", "--port", str(self.config.port)],
                cwd=self.app_dir,
                env=env,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                startupinfo=startup_info,
                creationflags=creation_flags,
                text=True,
            )

            launch_time = time.perf_counter() - launch_start
            self._log(
                "🚀 Subprocess запущен",
                {"pid": self.process.pid, "launch_time": f"{launch_time:.3f}s"},
            )
            return True

        except Exception as e:
            self._log_error("❌ Ошибка запуска subprocess", e)
            return False

    def _wait_for_ready(self) -> bool:
        """Ожидает готовности приложения"""
        wait_start = time.perf_counter()
        max_wait_time = self.config.timeout
        check_interval = 0.5

        self._log("⏳ Ожидание готовности приложения", {"timeout": max_wait_time})

        while (time.perf_counter() - wait_start) < max_wait_time:
            if not self.process or self.process.poll() is not None:
                self._log("❌ Процесс завершился преждевременно")
                return False

            if self.is_app_running():
                wait_time = time.perf_counter() - wait_start
                self._log("✅ Приложение готово", {"wait_time": f"{wait_time:.3f}s"})
                return True

            time.sleep(check_interval)

        self._log("❌ Timeout ожидания готовности")
        return False

    def _log_info(self, message: str, extra: Optional[Dict[str, Any]] = None) -> None:
        """Логирование через ErrorHandler или print"""
        full_message = message
        if extra:
            extra_str = ", ".join(f"{k}: {v}" for k, v in extra.items())
            full_message = f"{message} | {extra_str}"

        if self.error_handler and hasattr(self.error_handler, "log_info"):
            try:
                self.error_handler.log_info(full_message)
                return
            except Exception as e:
                print(f"[ERROR] ErrorHandler failed: {e}")

        # Fallback: простой print
        print(f"[INFO] {full_message}")

    def _log_debug(self, message: str, extra: Optional[Dict[str, Any]] = None) -> None:
        """Логирование отладки через ErrorHandler или print"""
        full_message = message
        if extra:
            extra_str = ", ".join(f"{k}: {v}" for k, v in extra.items())
            full_message = f"{message} | {extra_str}"

        if self.error_handler and hasattr(self.error_handler, "log_debug"):
            try:
                self.error_handler.log_debug(full_message)
                return
            except Exception as e:
                print(f"[ERROR] ErrorHandler debug failed: {e}")

        # Fallback: print только в debug режиме
        if self.config.debug:
            print(f"[DEBUG] {full_message}")

    def _log_error(self, message: str, error: Exception, context: str = "AppManager") -> None:
        """Логирование ошибок через ErrorHandler или print"""
        if self.error_handler and hasattr(self.error_handler, "handle_error"):
            try:
                self.error_handler.handle_error(error, f"{context}: {message}")
                return
            except Exception as e:
                print(f"[ERROR] ErrorHandler.handle_error failed: {e}")

        # Fallback: простой print
        print(f"[ERROR] {context}: {message} | Error: {error}")

    def _is_process_alive(self) -> bool:
        """Проверяет, жив ли процесс приложения"""
        if not self.process:
            return False
        try:
            return self.process.poll() is None
        except Exception:
            return False

    def _log(self, message: str, details: Optional[Dict[str, Any]] = None):
        """Универсальное логирование"""
        if self.error_handler and hasattr(self.error_handler, "log_info"):
            full_message = f"{message}"
            if details:
                detail_str = ", ".join([f"{k}={v}" for k, v in details.items()])
                full_message += f" ({detail_str})"
            self.error_handler.log_info(full_message)
        else:
            detail_str = ""
            if details:
                detail_str = " " + str(details)
            print(f"[AppManager] {message}{detail_str}")

    def _is_port_in_use(self, port: int) -> bool:
        """Безопасная проверка использования порта"""
        if self.port_manager:
            try:
                return self.port_manager.is_port_in_use(port)
            except Exception as e:
                self._log_debug(f"Ошибка проверки порта через PortManager: {e}")

        # Fallback: простая проверка через socket
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
                sock.settimeout(1)
                result = sock.connect_ex(("127.0.0.1", port))
                return result == 0
        except Exception:
            return False

    def _cleanup_port(self, port: int) -> bool:
        """Безопасная очистка порта"""
        if self.port_manager:
            try:
                return self.port_manager.smart_cleanup(port)
            except Exception as e:
                self._log_debug(f"Ошибка очистки порта через PortManager: {e}")

        # Fallback: простая очистка
        self._log_debug(f"PortManager недоступен, пропускаем очистку порта {port}")
        return True

    def _find_free_port(self, start_port: int = 5000) -> int:
        """Безопасный поиск свободного порта"""
        if self.port_manager:
            try:
                return self.port_manager.find_free_port(start_port)
            except Exception as e:
                self._log_debug(f"Ошибка поиска свободного порта через PortManager: {e}")

        # ✅ ИСПРАВЛЯЕМ fallback - правильный вызов socket.bind
        for port in range(start_port, start_port + 100):
            try:
                with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
                    sock.bind(("127.0.0.1", port))  # ✅ ИСПРАВЛЯЕМ - правильный кортеж
                    return port
            except OSError:
                continue

        raise Exception(f"Не найден свободный порт в диапазоне {start_port}-{start_port + 100}")

    def _wait_for_port_free(self, port: int, timeout: int = 30) -> bool:
        """Безопасное ожидание освобождения порта"""
        if self.port_manager:
            try:
                return self.port_manager.wait_for_port_free(port, timeout)
            except Exception as e:
                self._log_debug(f"Ошибка ожидания освобождения порта через PortManager: {e}")

        # Fallback: простое ожидание
        start_time = time.time()
        while (time.time() - start_time) < timeout:
            if not self._is_port_in_use(port):
                return True
            time.sleep(1)
        return False


# === ФАБРИЧНЫЕ ФУНКЦИИ ===


def create_test_manager(port: int = 5000) -> AppManager:
    """Создает менеджер для тестирования"""
    config = AppConfig(
        port=port,
        mode=AppMode.TESTING,
        debug=True,
        auto_cleanup=True,
        force_kill=True,
        timeout=45,
    )
    return AppManager(config)


def create_external_manager(port: int = 5000) -> AppManager:
    """Создает менеджер для работы с внешним приложением"""
    config = AppConfig(
        port=port,
        mode=AppMode.EXTERNAL,
        debug=False,
        auto_cleanup=False,
        force_kill=False,
        timeout=10,
    )
    return AppManager(config)


def create_dev_manager(port: int = 5000) -> AppManager:
    """Создает менеджер для разработки"""
    config = AppConfig(
        port=port,
        mode=AppMode.DEVELOPMENT,
        debug=True,
        auto_cleanup=True,
        force_kill=False,
        timeout=30,
    )
    return AppManager(config)


# === ENTRY POINT ===


def main():
    """Точка входа для запуска из командной строки"""
    import argparse

    parser = argparse.ArgumentParser(description="Управление приложением")
    parser.add_argument("--port", type=int, default=5000, help="Порт приложения")
    parser.add_argument("--mode", choices=["test", "dev", "external"], default="dev")
    parser.add_argument("--debug", action="store_true", help="Режим отладки")

    args = parser.parse_args()

    # Создаем менеджер в зависимости от режима
    if args.mode == "test":
        manager = create_test_manager(args.port)
    elif args.mode == "external":
        manager = create_external_manager(args.port)
    else:
        manager = create_dev_manager(args.port)

    # Запускаем приложение
    if manager.start_app():
        print(f"✅ Приложение запущено: {manager.app_url}")
        try:
            # Ждем сигнала завершения
            while manager.is_app_running():
                time.sleep(1)
        except KeyboardInterrupt:
            print("\n🛑 Получен сигнал завершения")
        finally:
            manager.stop_app()
    else:
        print("❌ Не удалось запустить приложение")
        sys.exit(1)


if __name__ == "__main__":
    main()
