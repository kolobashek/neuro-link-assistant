#!/usr/bin/env python3
"""Менеджер приложения специально для UI тестов"""

import os
import signal
import subprocess
import sys
import time
from pathlib import Path
from typing import Optional

import psutil
import requests


class TestAppManager:
    def __init__(self, port=5000, timeout=45):
        self.port = port
        self.app_url = f"http://localhost:{port}"
        self.timeout = timeout
        self.process: Optional[subprocess.Popen] = None
        self.app_dir = Path(__file__).parent.parent

    def cleanup_port(self) -> bool:
        """Очищает порт от зависших процессов"""
        print(f"🧹 [APP] Очистка порта {self.port}...")

        killed_count = 0
        for proc in psutil.process_iter(["pid", "name", "connections"]):
            try:
                connections = proc.info.get("connections", [])
                if not connections:
                    continue

                for conn in connections:
                    if hasattr(conn, "laddr") and conn.laddr.port == self.port:
                        print(
                            f"🔪 [APP] Завершаем процесс {proc.info['name']} (PID:"
                            f" {proc.info['pid']})"
                        )
                        psutil.Process(proc.info["pid"]).terminate()
                        killed_count += 1
                        break
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue

        if killed_count > 0:
            print(f"✅ [APP] Завершено {killed_count} процессов")
            time.sleep(3)  # Даем время на освобождение порта

        return True

    def is_app_running(self) -> bool:
        """Проверяет, работает ли приложение"""
        try:
            response = requests.get(self.app_url, timeout=3)
            return 200 <= response.status_code < 500
        except:
            return False

    def start_app(self) -> bool:
        """Запускает приложение для тестов"""
        print(f"🚀 [APP] Запуск приложения для UI тестов...")

        # Проверяем, не запущено ли уже
        if self.is_app_running():
            print(f"✅ [APP] Приложение уже работает на {self.app_url}")
            return True

        # Очищаем порт
        self.cleanup_port()

        try:
            # Переходим в директорию проекта
            os.chdir(self.app_dir)

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
                    "FLASK_ENV": "testing",
                    "TESTING": "true",
                    "PYTHONIOENCODING": "utf-8",
                    "PYTHONPATH": str(self.app_dir),
                }
            )

            print(f"⏳ [APP] Запуск Flask приложения...")

            # Запускаем приложение
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

            print(f"⏱️ [APP] Ожидание готовности (до {self.timeout}с)...")

            # Ждем готовности с прогресс-баром
            for i in range(self.timeout * 2):  # Проверяем каждые 0.5 сек
                if self.is_app_running():
                    print(f"✅ [APP] Приложение готово на {self.app_url} за {(i+1)*0.5:.1f}с")

                    # Дополнительная проверка стабильности
                    time.sleep(1)
                    if self.is_app_running():
                        print(f"✅ [APP] Приложение стабильно работает")
                        return True

                # Показываем прогресс каждые 5 секунд
                if (i + 1) % 10 == 0:
                    print(f"⏳ [APP] Ожидание... {(i+1)*0.5:.0f}с/{self.timeout}с")

                time.sleep(0.5)

            print(f"❌ [APP] Приложение не запустилось за {self.timeout}с")
            self._show_process_output()
            self.stop_app()
            return False

        except Exception as e:
            print(f"❌ [APP] Ошибка запуска: {e}")
            self._show_process_output()
            return False

    def stop_app(self):
        """Останавливает приложение"""
        print(f"🛑 [APP] Остановка приложения...")

        if self.process:
            try:
                if os.name == "nt":  # Windows
                    self.process.send_signal(signal.CTRL_BREAK_EVENT)
                else:  # Unix
                    self.process.terminate()

                # Ждем завершения
                try:
                    self.process.wait(timeout=5)
                    print(f"✅ [APP] Процесс завершен корректно")
                except subprocess.TimeoutExpired:
                    print(f"⚠️ [APP] Принудительное завершение процесса")
                    self.process.kill()
                    self.process.wait()

            except Exception as e:
                print(f"⚠️ [APP] Ошибка при остановке: {e}")

        # Дополнительная очистка порта
        self.cleanup_port()

        # Проверяем что остановлено
        time.sleep(1)
        if not self.is_app_running():
            print(f"✅ [APP] Приложение полностью остановлено")
        else:
            print(f"⚠️ [APP] Приложение все еще отвечает")

    def _show_process_output(self):
        """Показывает вывод процесса для диагностики"""
        if not self.process:
            return

        try:
            # Читаем последние строки stdout и stderr
            if self.process.stdout:
                stdout_data = self.process.stdout.read()
                if stdout_data:
                    print(f"\n📄 [APP STDOUT]:\n{stdout_data}")

            if self.process.stderr:
                stderr_data = self.process.stderr.read()
                if stderr_data:
                    print(f"\n📄 [APP STDERR]:\n{stderr_data}")

        except Exception as e:
            print(f"⚠️ [APP] Не удалось прочитать вывод процесса: {e}")

    def health_check(self) -> bool:
        """Детальная проверка здоровья приложения"""
        if not self.is_app_running():
            return False

        try:
            # Проверяем основные эндпоинты
            endpoints = ["/", "/health"] if hasattr(self, "_check_health_endpoint") else ["/"]

            for endpoint in endpoints:
                response = requests.get(f"{self.app_url}{endpoint}", timeout=5)
                if response.status_code >= 500:
                    return False

            return True
        except:
            return False


def main():
    """Утилита для ручного запуска/остановки приложения"""
    import argparse

    parser = argparse.ArgumentParser(description="Управление тестовым приложением")
    parser.add_argument("action", choices=["start", "stop", "restart", "status"])
    parser.add_argument("--port", type=int, default=5000, help="Порт приложения")
    parser.add_argument("--timeout", type=int, default=45, help="Таймаут запуска")

    args = parser.parse_args()

    manager = TestAppManager(port=args.port, timeout=args.timeout)

    if args.action == "start":
        success = manager.start_app()
        sys.exit(0 if success else 1)
    elif args.action == "stop":
        manager.stop_app()
    elif args.action == "restart":
        manager.stop_app()
        time.sleep(2)
        success = manager.start_app()
        sys.exit(0 if success else 1)
    elif args.action == "status":
        if manager.is_app_running():
            print(f"✅ [APP] Работает на {manager.app_url}")
            sys.exit(0)
        else:
            print(f"❌ [APP] Не работает")
            sys.exit(1)


if __name__ == "__main__":
    main()
