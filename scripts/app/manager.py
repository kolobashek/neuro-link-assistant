"""Объединенный менеджер приложений с полным функционалом"""

import os
import signal
import subprocess
import sys
import time
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional

import requests

# НОВЫЙ ИМПОРТ
from scripts.network.port_manager import PortConfig, PortManager


class AppMode(Enum):
    """Режимы работы приложения"""

    PRODUCTION = "production"
    TESTING = "testing"
    DEVELOPMENT = "development"
    EXTERNAL = "external"


@dataclass
class AppConfig:
    """Конфигурация приложения"""

    port: int = 5000  # ← Изменили с 5001 на 5000
    host: str = "127.0.0.1"
    timeout: int = 45
    mode: AppMode = AppMode.TESTING
    debug: bool = False
    auto_cleanup: bool = True
    health_endpoints: List[str] = field(default_factory=lambda: ["/", "/health"])

    # НОВОЕ: Настройки для PortManager
    force_kill: bool = False
    safe_pids: List[int] = field(default_factory=lambda: [0, 4])

    def get_port_config(self) -> PortConfig:
        """Создает PortConfig из AppConfig"""
        return PortConfig(
            port=self.port,
            host=self.host,
            timeout=self.timeout,
            force_kill=self.force_kill,
            safe_pids=self.safe_pids,
        )

    def __post_init__(self):
        if self.health_endpoints is None:
            self.health_endpoints = ["/", "/health"]


class AppManager:
    """Универсальный менеджер приложений"""

    def __init__(self, config: Optional[AppConfig] = None):
        self.config = config or AppConfig()
        self.app_url = f"http://{self.config.host}:{self.config.port}"
        self.process: Optional[subprocess.Popen] = None
        self.app_dir = Path(__file__).parent.parent.parent
        self._start_time: Optional[float] = None
        self._metrics: Dict[str, Any] = {}

        # НОВОЕ: Используем PortManager
        self.port_manager = PortManager(self.config.get_port_config())

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

        # ЗАМЕНЯЕМ: Используем PortManager для очистки
        if self.config.auto_cleanup and self.port_manager.is_port_in_use():
            self._log("🧹 Очистка порта", {"port": self.config.port})

            # НОВОЕ: Если очистка не удалась, ищем свободный порт
            if not self.port_manager.smart_cleanup():
                self._log("❌ Не удалось очистить порт, ищем свободный...")
                try:
                    new_port = self.port_manager.find_free_port()
                    self._log("✅ Найден свободный порт", {"new_port": new_port})

                    # Обновляем конфигурацию
                    self.config.port = new_port
                    self.port_manager = PortManager(self.config.get_port_config())
                    self.app_url = f"http://{self.config.host}:{self.config.port}"

                except Exception as e:
                    self._log("❌ Не найден свободный порт", {"error": str(e)})
                    return False

        # Запуск приложения
        try:
            if not self._launch_subprocess():
                return False

            # ЗАМЕНЯЕМ: Используем PortManager для ожидания
            if not self.port_manager.wait_for_port_free(timeout=2):  # Ждем освобождения
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
            self._log("❌ Ошибка запуска", {"error": str(e)})
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
                    self.process.send_signal(signal.CTRL_BREAK_EVENT)
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
                self._log("❌ Ошибка остановки процесса", {"error": str(e)})
                success = False

        self.process = None

        # ЗАМЕНЯЕМ: Используем PortManager для дополнительной очистки
        if self.config.auto_cleanup:
            time.sleep(1)  # Даем время на освобождение ресурсов
            if self.port_manager.is_port_in_use():
                self._log("🧹 Дополнительная очистка порта")
                self.port_manager.smart_cleanup()

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
            "port_occupied": self.port_manager.is_port_in_use(),  # ЗАМЕНЯЕМ
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

            # Переменные окружения
            env = os.environ.copy()
            env.update(
                {
                    "FLASK_ENV": self.config.mode.value,
                    "TESTING": "true" if self.config.mode == AppMode.TESTING else "false",
                    "PYTHONIOENCODING": "utf-8",
                    "PYTHONPATH": str(self.app_dir),
                }
            )

            # Запуск
            self.process = subprocess.Popen(
                [sys.executable, "app.py"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                startupinfo=startup_info,
                creationflags=creation_flags,
                env=env,
                encoding="utf-8",
                errors="replace",
                cwd=self.app_dir,
            )

            launch_time = time.perf_counter() - launch_start
            self._log(
                "⚡ Процесс запущен",
                {"pid": self.process.pid, "launch_time": f"{launch_time:.3f}s"},
            )
            return True

        except Exception as e:
            self._log("❌ Ошибка запуска subprocess", {"error": str(e)})
            return False

    def _wait_for_ready(self) -> bool:
        """Ожидание готовности приложения"""
        wait_start = time.perf_counter()
        self._log("⏱️ Ожидание готовности", {"timeout": f"{self.config.timeout}s"})

        while (time.perf_counter() - wait_start) < self.config.timeout:
            if self.is_app_running():
                wait_time = time.perf_counter() - wait_start
                self._log("✅ Приложение готово", {"wait_time": f"{wait_time:.3f}s"})
                return True
            time.sleep(0.5)

        wait_time = time.perf_counter() - wait_start
        self._log("❌ Таймаут ожидания", {"wait_time": f"{wait_time:.3f}s"})
        return False

    def _log(self, message: str, data: Optional[Dict[str, Any]] = None):
        """Логирование с метаданными"""
        if self.config.debug:
            timestamp = time.strftime("%H:%M:%S")
            log_data = f" | {data}" if data else ""
            print(f"[{timestamp}] [APP] {message}{log_data}")

        # Сохраняем метрики
        if data:
            self._metrics.update(data)


# === ФАБРИЧНЫЕ МЕТОДЫ ===


def create_test_manager(port: int = 5000, debug: bool = True) -> AppManager:
    """Создает менеджер для тестирования"""
    config = AppConfig(
        port=port,
        mode=AppMode.TESTING,
        debug=debug,
        timeout=45,
        auto_cleanup=True,
        force_kill=True,  # ← ДОБАВИТЬ для тестов
    )
    return AppManager(config)


def create_production_manager(port: int = 5000, debug: bool = False) -> AppManager:
    """Создает менеджер для продакшена"""
    config = AppConfig(
        port=port, mode=AppMode.PRODUCTION, debug=debug, timeout=30, auto_cleanup=False
    )
    return AppManager(config)


def create_external_manager(port: int = 5000) -> AppManager:
    """Создает менеджер для внешнего приложения"""
    config = AppConfig(port=port, mode=AppMode.EXTERNAL, debug=False, timeout=5, auto_cleanup=False)
    return AppManager(config)


# === CLI УТИЛИТА ===


def main():
    """CLI для управления приложением"""
    import argparse

    parser = argparse.ArgumentParser(description="Управление приложением")
    parser.add_argument("action", choices=["start", "stop", "restart", "status"])
    parser.add_argument("--port", type=int, default=5000, help="Порт приложения")
    parser.add_argument(
        "--mode",
        choices=["testing", "production", "external"],
        default="testing",
        help="Режим работы",
    )
    parser.add_argument("--debug", action="store_true", help="Включить отладку")
    parser.add_argument("--timeout", type=int, default=45, help="Таймаут запуска")

    args = parser.parse_args()

    # Создаем конфигурацию
    config = AppConfig(
        port=args.port, mode=AppMode(args.mode), debug=args.debug, timeout=args.timeout
    )

    manager = AppManager(config)

    if args.action == "start":
        success = manager.start_app()
        sys.exit(0 if success else 1)
    elif args.action == "stop":
        manager.stop_app()
    elif args.action == "restart":
        success = manager.restart_app()
        sys.exit(0 if success else 1)
    elif args.action == "status":
        status = manager.get_status()
        print(f"📊 Статус приложения:")
        for key, value in status.items():
            if isinstance(value, dict):
                print(f"  {key}:")
                for k, v in value.items():
                    print(f"    {k}: {v}")
            else:
                icon = "✅" if value else "❌" if isinstance(value, bool) else "ℹ️"
                print(f"  {icon} {key}: {value}")

        sys.exit(0 if status["running"] else 1)


if __name__ == "__main__":
    main()
