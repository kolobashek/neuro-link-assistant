"""Объединенный менеджер портов с полным функционалом"""

import re
import socket
import subprocess
import sys
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

import psutil
import requests


@dataclass
class PortConfig:
    """Конфигурация для работы с портами"""

    port: int = 5000
    host: str = "localhost"
    timeout: int = 30
    force_kill: bool = False
    safe_pids: List[int] = field(default_factory=lambda: [0, 4])  # Системные процессы Windows


class PortManager:
    """Универсальный менеджер портов"""

    def __init__(self, config: Optional[PortConfig] = None):
        self.config = config or PortConfig()

    def is_port_in_use(self) -> bool:
        """Проверяет, используется ли порт"""
        # Метод 1: через socket
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
                sock.settimeout(1)
                result = sock.connect_ex((self.config.host, self.config.port))
                if result == 0:
                    return True
        except:
            pass

        # Метод 2: через psutil
        for conn in psutil.net_connections():
            try:
                if hasattr(conn, "laddr") and conn.laddr:
                    if hasattr(conn.laddr, "port"):
                        if conn.laddr.port == self.config.port:
                            return True
                    elif isinstance(conn.laddr, tuple) and len(conn.laddr) >= 2:
                        if conn.laddr[1] == self.config.port:
                            return True
            except (AttributeError, IndexError):
                continue
        return False

    def find_process_by_port(self) -> Optional[Dict[str, Any]]:
        """Находит процесс, использующий порт"""
        for conn in psutil.net_connections():
            try:
                port_matches = False

                if hasattr(conn, "laddr") and conn.laddr:
                    if hasattr(conn.laddr, "port"):
                        port_matches = conn.laddr.port == self.config.port
                    elif isinstance(conn.laddr, tuple) and len(conn.laddr) >= 2:
                        port_matches = conn.laddr[1] == self.config.port

                if port_matches and hasattr(conn, "pid") and conn.pid:
                    try:
                        process = psutil.Process(conn.pid)
                        return {
                            "pid": conn.pid,
                            "name": process.name(),
                            "cmdline": " ".join(process.cmdline()),
                            "status": process.status(),
                            "create_time": process.create_time(),
                            "connection_status": conn.status,
                        }
                    except (psutil.NoSuchProcess, psutil.AccessDenied):
                        return {
                            "pid": conn.pid,
                            "name": "UNKNOWN",
                            "cmdline": "ACCESS_DENIED",
                            "status": "ZOMBIE",
                            "connection_status": conn.status,
                        }
            except (AttributeError, IndexError):
                continue
        return None

    def is_app_responding(self) -> bool:
        """Проверяет, отвечает ли приложение на HTTP запросы"""
        try:
            response = requests.get(f"http://{self.config.host}:{self.config.port}", timeout=2)
            return 200 <= response.status_code < 500
        except requests.RequestException:
            return False

    def kill_process_by_port(self) -> bool:
        """Безопасно завершает процесс на порту"""
        process_info = self.find_process_by_port()
        if not process_info:
            print(f"ℹ️ [PORT] Процесс на порту {self.config.port} не найден")
            return True

        pid = process_info["pid"]

        # Проверяем безопасность
        if pid in self.config.safe_pids:
            print(f"⚠️ [PORT] Пропускаем системный процесс (PID: {pid})")
            return False

        # Проверяем тип процесса
        cmdline = process_info["cmdline"].lower()
        if not any(keyword in cmdline for keyword in ["python", "flask", "app.py", "node"]):
            if not self.config.force_kill:
                print(f"⚠️ [PORT] Процесс не похож на веб-приложение: {process_info['name']}")
                print(f"     Командная строка: {process_info['cmdline'][:100]}...")
                print(f"     Используйте force_kill=True для принудительного завершения")
                return False

        try:
            process = psutil.Process(pid)
            print(f"🔧 [PORT] Завершаем процесс: {process_info['name']} (PID: {pid})")

            # Мягкое завершение
            process.terminate()

            # Ждем завершения
            try:
                process.wait(timeout=5)
                print(f"✅ [PORT] Процесс завершен корректно")
                return True
            except psutil.TimeoutExpired:
                if self.config.force_kill:
                    print(f"🔪 [PORT] Принудительное завершение")
                    process.kill()
                    process.wait(timeout=3)
                    return True
                else:
                    print(f"⚠️ [PORT] Процесс не завершился, требуется force_kill")
                    return False

        except psutil.NoSuchProcess:
            print(f"✅ [PORT] Процесс уже завершен")
            return True
        except Exception as e:
            print(f"❌ [PORT] Ошибка завершения процесса: {e}")
            return False

    def smart_cleanup(self) -> bool:
        """Умная очистка с проверкой отзывчивости"""
        if not self.is_port_in_use():
            print(f"✅ [PORT] Порт {self.config.port} свободен")
            return True

        print(f"🔍 [PORT] Порт {self.config.port} занят, анализ...")

        # Проверяем отзывчивость приложения
        if self.is_app_responding():
            print("ℹ️ [PORT] Приложение отвечает, возможно это рабочее приложение")
            return True  # Не убиваем работающее приложение

        print("⚠️ [PORT] Приложение не отвечает, завершаем процесс")
        success = self.kill_process_by_port()

        if success:
            # Ждем освобождения порта
            if self.wait_for_port_free():
                print(f"✅ [PORT] Порт {self.config.port} освобожден")
                return True
            else:
                print(f"❌ [PORT] Порт все еще занят")
                return False

        return success

    def wait_for_port_free(self, timeout: Optional[int] = None) -> bool:
        """Ждет освобождения порта"""
        actual_timeout = timeout or self.config.timeout
        start_time = time.time()

        while (time.time() - start_time) < actual_timeout:
            if not self.is_port_in_use():
                return True
            time.sleep(0.5)
        return False

    def cleanup_zombie_connections(self) -> bool:
        """Очищает зависшие соединения (Windows)"""
        try:
            # Windows: netsh для сброса TCP соединений
            result = subprocess.run(
                ["netsh", "int", "ip", "reset"], capture_output=True, text=True, timeout=10
            )
            if result.returncode == 0:
                print("✅ [PORT] TCP соединения сброшены")
                return True
            else:
                print("⚠️ [PORT] Не удалось сбросить TCP соединения")
                return False
        except Exception as e:
            print(f"❌ [PORT] Ошибка сброса соединений: {e}")
            return False

    def find_free_port(self, start_port: Optional[int] = None, max_attempts: int = 10) -> int:
        """Находит свободный порт"""
        actual_start_port = start_port or (self.config.port + 1)

        for port in range(actual_start_port, actual_start_port + max_attempts):
            try:
                with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
                    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                    sock.bind((self.config.host, port))
                    return port
            except OSError:
                continue

        raise Exception(
            "Не найден свободный порт в диапазоне"
            f" {actual_start_port}-{actual_start_port + max_attempts}"
        )

    def get_port_info(self) -> Dict[str, Any]:
        """Получает детальную информацию о порте"""
        return {
            "port": self.config.port,
            "in_use": self.is_port_in_use(),
            "responding": self.is_app_responding(),
            "process": self.find_process_by_port(),
            "config": {
                "host": self.config.host,
                "timeout": self.config.timeout,
                "force_kill": self.config.force_kill,
            },
        }


def cleanup_port(port: int = 5000, force: bool = False) -> bool:
    """Функция для быстрой очистки порта"""
    config = PortConfig(port=port, force_kill=force)
    manager = PortManager(config)
    return manager.smart_cleanup()


def cleanup_all_flask_processes() -> int:
    """Завершает все Flask/Python веб-процессы"""
    killed_count = 0

    for proc in psutil.process_iter(["pid", "name", "cmdline"]):
        try:
            cmdline = " ".join(proc.info["cmdline"] or [])
            name = proc.info["name"].lower()

            # Ищем Python веб-приложения
            if "python" in name and any(
                keyword in cmdline.lower()
                for keyword in ["app.py", "flask", "werkzeug", "gunicorn"]
            ):
                print(
                    f"🔧 [CLEANUP] Завершаем веб-процесс: {proc.info['name']} (PID:"
                    f" {proc.info['pid']})"
                )
                proc.terminate()
                killed_count += 1

        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue

    if killed_count > 0:
        print(f"✅ [CLEANUP] Завершено {killed_count} веб-процессов")
        time.sleep(2)  # Даем время на завершение
    else:
        print("ℹ️ [CLEANUP] Веб-процессы не найдены")

    return killed_count


def update_config_files(new_port: int) -> List[str]:
    """Обновляет конфигурационные файлы с новым портом"""
    files_to_update = {
        "tests/conftest.py": [
            (
                r'TEST_CONFIG = {"base_url": "http://localhost:\d+"}',
                f'TEST_CONFIG = {{"base_url": "http://localhost:{new_port}"}}',
            ),
        ],
        "app.py": [
            (
                r"app\.run\([^)]*port=\d+[^)]*\)",
                f'app.run(host="127.0.0.1", port={new_port}, debug=False)',
            ),
        ],
    }

    updated_files = []
    for file_path, patterns in files_to_update.items():
        try:
            file_obj = Path(file_path)
            if not file_obj.exists():
                continue

            content = file_obj.read_text(encoding="utf-8")
            original_content = content

            for pattern, replacement in patterns:
                content = re.sub(pattern, replacement, content)

            if content != original_content:
                file_obj.write_text(content, encoding="utf-8")
                updated_files.append(file_path)
                print(f"✅ [CONFIG] Обновлен: {file_path}")

        except Exception as e:
            print(f"❌ [CONFIG] Ошибка обновления {file_path}: {e}")

    return updated_files


def main():
    """CLI для управления портами"""
    import argparse

    parser = argparse.ArgumentParser(description="Управление портами")
    parser.add_argument("action", choices=["cleanup", "info", "find-free", "kill-all"])
    parser.add_argument("--port", type=int, default=5000, help="Порт для работы")
    parser.add_argument("--force", action="store_true", help="Принудительное завершение")
    parser.add_argument("--update-config", action="store_true", help="Обновить конфиги")

    args = parser.parse_args()

    config = PortConfig(port=args.port, force_kill=args.force)
    manager = PortManager(config)

    if args.action == "cleanup":
        success = manager.smart_cleanup()
        if args.update_config and not success:
            print("🔧 [CONFIG] Ищем свободный порт...")
            try:
                new_port = manager.find_free_port()
                print(f"✅ [CONFIG] Найден свободный порт: {new_port}")
                update_config_files(new_port)
            except Exception as e:
                print(f"❌ [CONFIG] Ошибка: {e}")
        sys.exit(0 if success else 1)

    elif args.action == "info":
        info = manager.get_port_info()
        print(f"📊 Информация о порте {info['port']}:")
        print(f"  🔌 Занят: {'Да' if info['in_use'] else 'Нет'}")
        print(f"  🌐 Отвечает: {'Да' if info['responding'] else 'Нет'}")
        if info["process"]:
            proc = info["process"]
            print(f"  📋 Процесс: {proc['name']} (PID: {proc['pid']})")
            print(f"  📝 Команда: {proc['cmdline'][:80]}...")

    elif args.action == "find-free":
        try:
            free_port = manager.find_free_port()
            print(f"✅ Свободный порт: {free_port}")
        except Exception as e:
            print(f"❌ Ошибка поиска: {e}")
            sys.exit(1)

    elif args.action == "kill-all":
        count = cleanup_all_flask_processes()
        print(f"📊 Завершено процессов: {count}")


if __name__ == "__main__":
    main()
