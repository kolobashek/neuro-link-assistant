import os
import signal
import subprocess
import time
from typing import Optional

import psutil
import requests


class AppManager:
    def __init__(self, app_url="http://localhost:5000", timeout=45):  # Увеличили timeout
        self.app_url = app_url
        self.timeout = timeout
        self.process: Optional[subprocess.Popen] = None

    def start_app(self) -> bool:
        """Запускает приложение и ждет готовности"""
        print(f"🔍 [APP] Проверяем, не запущено ли приложение...")

        # СНАЧАЛА быстро проверяем, не запущено ли уже
        if self.is_app_running():
            print(f"✅ [APP] Приложение уже запущено на {self.app_url}")
            return True

        print(f"🚀 [APP] Запуск приложения...")

        # Убиваем процессы на порту 5000 если есть
        self._kill_port_processes(5000)

        try:
            # ИСПРАВЛЯЕМ: добавляем правильную кодировку для Windows
            startup_info = None
            if os.name == "nt":  # Windows
                startup_info = subprocess.STARTUPINFO()
                startup_info.dwFlags |= subprocess.STARTF_USESHOWWINDOW
                startup_info.wShowWindow = subprocess.SW_HIDE

            # Запускаем приложение с правильной кодировкой
            self.process = subprocess.Popen(
                ["poetry", "run", "python", "app.py"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                startupinfo=startup_info,
                encoding="utf-8",  # ДОБАВЛЯЕМ явную кодировку
                errors="replace",  # ДОБАВЛЯЕМ обработку ошибок кодировки
                creationflags=subprocess.CREATE_NEW_PROCESS_GROUP if os.name == "nt" else 0,
            )

            print(f"⏳ [APP] Ожидание готовности приложения (до {self.timeout}с)...")

            # Ждем готовности с более частыми проверками
            for i in range(self.timeout * 2):  # Проверяем каждые 0.5 секунды
                if self.is_app_running():
                    print(f"✅ [APP] Приложение готово на {self.app_url} (за {(i+1)*0.5:.1f}с)")
                    return True
                time.sleep(0.5)  # Уменьшили с 1 до 0.5 секунды

            print(f"❌ [APP] Приложение не запустилось за {self.timeout}с")
            self.stop_app()
            return False

        except Exception as e:
            print(f"❌ [APP] Ошибка запуска: {e}")
            return False

    def stop_app(self):
        """Останавливает приложение"""
        print(f"🛑 [APP] Остановка приложения...")

        # Останавливаем наш процесс
        if self.process:
            try:
                if os.name == "nt":  # Windows
                    self.process.send_signal(signal.CTRL_BREAK_EVENT)
                else:  # Unix
                    self.process.terminate()

                # Ждем завершения
                try:
                    self.process.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    print(f"⚠️ [APP] Принудительное завершение процесса...")
                    self.process.kill()
                    self.process.wait(timeout=3)

                print(f"✅ [APP] Основной процесс остановлен")
            except Exception as e:
                print(f"⚠️ [APP] Проблема остановки основного процесса: {e}")

        # Дополнительно убиваем процессы на порту
        self._kill_port_processes(5000)

        # Проверяем что действительно остановлено
        time.sleep(2)
        if not self.is_app_running():
            print(f"✅ [APP] Приложение полностью остановлено")
        else:
            print(f"⚠️ [APP] Приложение все еще отвечает")

    def is_app_running(self) -> bool:
        """Проверяет доступность приложения (быстро)"""
        try:
            response = requests.get(self.app_url, timeout=1)  # Уменьшили timeout с 3 до 1
            return response.status_code == 200
        except:
            return False

    def health_check(self) -> bool:
        """Детальная проверка здоровья приложения (быстро)"""
        try:
            response = requests.get(f"{self.app_url}/", timeout=2)  # Уменьшили с 5 до 2
            return 200 <= response.status_code < 500
        except:
            return False

    def _kill_port_processes(self, port: int):
        """Убивает процессы на указанном порту"""
        killed_count = 0
        try:
            for proc in psutil.process_iter(["pid", "name", "connections"]):
                try:
                    for conn in proc.info["connections"] or []:
                        if conn.laddr.port == port:
                            print(
                                f"🔪 [APP] Убиваем процесс {proc.info['name']} (PID:"
                                f" {proc.info['pid']})"
                            )
                            psutil.Process(proc.info["pid"]).terminate()
                            killed_count += 1
                            break
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue
        except Exception as e:
            print(f"⚠️ [APP] Ошибка при очистке порта {port}: {e}")

        if killed_count > 0:
            print(f"🔪 [APP] Завершено {killed_count} процессов на порту {port}")

    def _debug_process_output(self):
        """Выводит отладочную информацию о процессе"""
        if self.process:
            try:
                stdout, stderr = self.process.communicate(timeout=1)
                if stdout:
                    print(f"📤 [APP] STDOUT: {stdout.decode('utf-8', errors='ignore')}")
                if stderr:
                    print(f"📤 [APP] STDERR: {stderr.decode('utf-8', errors='ignore')}")
            except subprocess.TimeoutExpired:
                print(f"⚠️ [APP] Процесс не отвечает")
            except Exception as e:
                print(f"⚠️ [APP] Ошибка получения вывода процесса: {e}")
