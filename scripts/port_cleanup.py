"""Утилита для очистки зависших портов и процессов"""

import subprocess
import time
from typing import List, Optional

import psutil
import requests


class PortManager:
    def __init__(self, port: int = 5000):
        self.port = port
        self.app_process = None

    def is_port_in_use(self) -> bool:
        """Проверяет, используется ли порт"""
        for conn in psutil.net_connections():
            try:
                # Обрабатываем разные типы соединений
                if hasattr(conn, "laddr") and conn.laddr:
                    if hasattr(conn.laddr, "port"):
                        # Объект с атрибутом port
                        if conn.laddr.port == self.port:
                            return True
                    elif isinstance(conn.laddr, tuple) and len(conn.laddr) >= 2:
                        # Tuple (ip, port)
                        if conn.laddr[1] == self.port:
                            return True
            except (AttributeError, IndexError):
                continue
        return False

    def find_process_by_port(self) -> Optional[int]:
        """Находит PID процесса, использующего порт"""
        for conn in psutil.net_connections():
            try:
                port_matches = False

                # Проверяем разные форматы laddr
                if hasattr(conn, "laddr") and conn.laddr:
                    if hasattr(conn.laddr, "port"):
                        port_matches = conn.laddr.port == self.port
                    elif isinstance(conn.laddr, tuple) and len(conn.laddr) >= 2:
                        port_matches = conn.laddr[1] == self.port

                if port_matches and hasattr(conn, "pid") and conn.pid:
                    return conn.pid
            except (AttributeError, IndexError):
                continue
        return None

    def kill_process_by_port(self) -> bool:
        """Безопасно завершает процесс на порту"""
        try:
            result = subprocess.run(["netstat", "-ano"], capture_output=True, text=True, timeout=5)

            for line in result.stdout.split("\n"):
                if f":{self.port}" in line and "LISTENING" in line:
                    parts = line.strip().split()
                    if len(parts) >= 5:
                        pid_str = parts[-1]

                        try:
                            pid = int(pid_str)

                            # ИСПРАВЛЕНО: Не завершаем системные процессы
                            if pid <= 4:  # PID 0, 4 - системные процессы
                                print(f"⚠️ [PORT] Пропускаем системный процесс (PID: {pid})")
                                continue

                            # Получаем информацию о процессе
                            try:
                                process_info = subprocess.run(
                                    ["tasklist", "/FI", f"PID eq {pid}", "/FO", "CSV"],
                                    capture_output=True,
                                    text=True,
                                    timeout=3,
                                )

                                if (
                                    "python" in process_info.stdout.lower()
                                    or "flask" in process_info.stdout.lower()
                                ):
                                    print(f"🔧 [PORT] Завершаем Python/Flask процесс (PID: {pid})")

                                    # Мягкое завершение сначала
                                    subprocess.run(["taskkill", "/PID", str(pid)], timeout=5)
                                    time.sleep(2)

                                    # Проверяем, завершился ли
                                    check = subprocess.run(
                                        ["tasklist", "/FI", f"PID eq {pid}"],
                                        capture_output=True,
                                        timeout=3,
                                    )

                                    if f"{pid}" in check.stdout.decode():
                                        print(f"🔪 [PORT] Принудительное завершение (PID: {pid})")
                                        subprocess.run(
                                            ["taskkill", "/PID", str(pid), "/F"], timeout=5
                                        )

                                    return True
                                else:
                                    print(
                                        f"⚠️ [PORT] Процесс не похож на наше приложение (PID: {pid})"
                                    )
                                    # Можно добавить интерактивный запрос пользователю
                                    return False

                            except subprocess.TimeoutExpired:
                                print(
                                    f"⏱️ [PORT] Таймаут получения информации о процессе (PID: {pid})"
                                )
                                return False

                        except ValueError:
                            print(f"❌ [PORT] Некорректный PID: {pid_str}")
                            continue

            print(f"ℹ️ [PORT] Процесс на порту {self.port} не найден в netstat")
            return False

        except subprocess.TimeoutExpired:
            print(f"⏱️ [PORT] Таймаут выполнения netstat")
            return False
        except Exception as e:
            print(f"❌ [PORT] Ошибка завершения процесса: {e}")
            return False

    def cleanup_zombie_connections(self):
        """Очищает зависшие соединения"""
        try:
            # Windows: netsh для сброса TCP соединений
            subprocess.run(["netsh", "int", "ip", "reset"], capture_output=True, check=True)
            print("✅ TCP соединения сброшены")
        except subprocess.CalledProcessError:
            print("⚠️ Не удалось сбросить TCP соединения")

    def wait_for_port_free(self, timeout: int = 30) -> bool:
        """Ждет освобождения порта"""
        start_time = time.time()
        while time.time() - start_time < timeout:
            if not self.is_port_in_use():
                return True
            time.sleep(0.5)
        return False

    def is_app_responding(self) -> bool:
        """Проверяет, отвечает ли приложение на HTTP запросы"""
        try:
            response = requests.get(f"http://localhost:{self.port}", timeout=2)
            return response.status_code == 200
        except requests.RequestException:
            return False

    def smart_cleanup(self) -> bool:
        """Умная очистка: проверяет отзывчивость перед завершением"""
        if not self.is_port_in_use():
            print(f"✅ [PORT] Порт {self.port} уже свободен")
            return True

        print(f"🔍 [PORT] Порт {self.port} занят, анализ процесса...")

        # ИСПРАВЛЕНО: сначала проверяем отзывчивость
        if self.is_app_responding():
            print("ℹ️ [PORT] Приложение отвечает, возможно это наше приложение")
            return True  # Не убиваем отвечающее приложение
        else:
            print("⚠️ [PORT] Приложение не отвечает, завершаем процесс")

        if self.is_port_in_use():
            print(f"🔧 [PORT] Завершаем зависший процесс на порту {self.port}")
            success = self.kill_process_by_port()

            if success and self.wait_for_port_free():
                print(f"✅ [PORT] Порт {self.port} освобожден")
                return True
            else:
                print(f"❌ [PORT] Не удалось освободить порт {self.port}")
                return False

        return True


def cleanup_port(port: int = 5000) -> bool:
    """Функция для быстрой очистки порта"""
    manager = PortManager(port)
    return manager.smart_cleanup()


def cleanup_all_flask_processes():
    """Завершает все Flask процессы"""
    killed_count = 0
    for proc in psutil.process_iter(["pid", "name", "cmdline"]):
        try:
            cmdline = " ".join(proc.info["cmdline"] or [])
            if "python" in proc.info["name"].lower() and (
                "app.py" in cmdline or "flask" in cmdline.lower()
            ):
                print(f"🔧 Завершаем Flask процесс: {proc.info['pid']}")
                proc.terminate()
                killed_count += 1

        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue

    if killed_count > 0:
        print(f"✅ Завершено {killed_count} Flask процессов")
        time.sleep(2)  # Даем время на завершение

    return killed_count


if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1:
        port = int(sys.argv[1])
    else:
        port = 5000

    print(f"🧹 Очистка порта {port}...")
    success = cleanup_port(port)

    if not success:
        print("🔧 Пробуем очистить все Flask процессы...")
        cleanup_all_flask_processes()

        # Повторная проверка
        manager = PortManager(port)
        if manager.wait_for_port_free():
            print("✅ Порт успешно освобожден")
        else:
            print("❌ Порт все еще занят")
            sys.exit(1)
