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
        for proc in psutil.process_iter(["pid", "name", "net_connections"]):
            try:
                for conn in proc.info.get("net_connections", []):
                    if conn.laddr.port == self.port:
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

    def is_port_occupied(self) -> bool:
        """Проверяет, занят ли порт"""
        try:
            import socket

            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
                sock.settimeout(1)
                result = sock.connect_ex(("localhost", self.port))
                return result == 0
        except:
            return False

    def start_app(self) -> bool:
        """Запускает приложение для тестов"""
        start_time = time.perf_counter()  # Высокая точность
        print(f"🚀 [APP] Запуск приложения для UI тестов...")

        # Проверяем, не запущено ли уже
        if self.is_app_running():
            elapsed = time.perf_counter() - start_time
            print(f"✅ [APP] Приложение уже работает на {self.app_url} (проверка: {elapsed:.2f}с)")
            return True

        # Очистка порта (исправленная логика)
        cleanup_start = time.perf_counter()
        if self.is_port_occupied():
            print(f"🧹 [APP] Порт {self.port} занят, требуется очистка...")
            self.cleanup_port()
            cleanup_time = time.perf_counter() - cleanup_start
            print(f"🧹 [APP] Очистка завершена за {cleanup_time:.2f}с")
        else:
            print(f"✅ [APP] Порт {self.port} свободен, очистка не нужна")

        try:
            launch_start = time.perf_counter()
            print(f"⏳ [APP] Запуск Flask приложения...")

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

            launch_time = time.perf_counter() - launch_start
            print(f"⚡ [APP] Процесс запущен за {launch_time:.2f}с (PID: {self.process.pid})")

            # Ожидание готовности
            wait_start = time.perf_counter()
            print(f"⏱️ [APP] Ожидание готовности (до {self.timeout}с)...")

            def _wait_for_ready_internal(self) -> bool:
                """Ожидание готовности приложения"""
                start_time = time.perf_counter()

                while (time.perf_counter() - start_time) < self.timeout:
                    if self.is_app_running():
                        total_time = time.perf_counter() - start_time
                        print(f"✅ [READY] Приложение готово за {total_time:.3f}с")
                        return True
                    time.sleep(0.5)

                total_time = time.perf_counter() - start_time
                print(f"❌ [READY] Таймаут после {total_time:.3f}с")
                return False

            if self._wait_for_ready_internal():
                wait_time = time.perf_counter() - wait_start
                total_time = time.perf_counter() - start_time
                print(f"✅ [APP] Приложение готово на {self.app_url}")
                print(f"📊 [APP] Время ожидания: {wait_time:.2f}с, общее время: {total_time:.2f}с")

                # Проверка стабильности
                stability_start = time.perf_counter()
                if self.health_check():
                    stability_time = time.perf_counter() - stability_start
                    print(
                        f"✅ [APP] Приложение стабильно работает (проверка: {stability_time:.2f}с)"
                    )
                    return True
                else:
                    print(f"❌ [APP] Приложение нестабильно")
                    self.stop_app()
                    return False
            else:
                total_time = time.perf_counter() - start_time
                print(f"❌ [APP] Таймаут ожидания готовности ({total_time:.2f}с)")
                self.stop_app()
                return False

        except Exception as e:
            total_time = time.perf_counter() - start_time
            print(f"❌ [APP] Ошибка запуска за {total_time:.2f}с: {e}")
            self.stop_app()
            return False

    def stop_app(self) -> bool:
        """Корректно останавливает приложение"""
        stop_start = time.perf_counter()
        print(f"🛑 [APP] Остановка приложения...")

        if not hasattr(self, "process") or self.process is None:
            print(f"ℹ️ [APP] Процесс не найден или уже завершен")
            return True

        try:
            # Проверяем, работает ли еще процесс
            if self.process.poll() is None:
                print(f"🔄 [APP] Корректное завершение процесса (PID: {self.process.pid})")

                # Сначала пытаемся мягко завершить
                if os.name == "nt":
                    self.process.send_signal(signal.CTRL_BREAK_EVENT)
                else:
                    self.process.terminate()

                # Ждем завершения
                try:
                    self.process.wait(timeout=10)
                    terminate_time = time.perf_counter() - stop_start
                    print(f"✅ [APP] Процесс завершен корректно за {terminate_time:.2f}с")
                except subprocess.TimeoutExpired:
                    print(f"⚠️ [APP] Мягкое завершение не сработало, принудительное...")
                    self.process.kill()
                    self.process.wait()
                    kill_time = time.perf_counter() - stop_start
                    print(f"🔪 [APP] Процесс принудительно завершен за {kill_time:.2f}с")
            else:
                print(f"✅ [APP] Процесс уже завершен (код: {self.process.returncode})")

            self.process = None

            # ИСПРАВЛЕНО: НЕ очищаем порт сразу после корректного завершения
            # Даем время процессу полностью освободить ресурсы
            time.sleep(1)

            total_stop_time = time.perf_counter() - stop_start
            print(f"✅ [APP] Приложение полностью остановлено за {total_stop_time:.2f}с")
            return True

        except Exception as e:
            error_time = time.perf_counter() - stop_start
            print(f"❌ [APP] Ошибка при остановке за {error_time:.2f}с: {e}")
            return False

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

    def _wait_for_ready_internal(self) -> bool:
        """Ожидание готовности приложения"""
        start_time = time.perf_counter()

        while (time.perf_counter() - start_time) < self.timeout:
            if self.is_app_running():
                total_time = time.perf_counter() - start_time
                print(f"✅ [READY] Приложение готово за {total_time:.3f}с")
                return True
            time.sleep(0.5)

        total_time = time.perf_counter() - start_time
        print(f"❌ [READY] Таймаут после {total_time:.3f}с")
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
