# -*- coding: utf-8 -*-
"""
Реализация менеджера процессов для Windows с использованием psutil и subprocess.
"""
import subprocess
from typing import Any, Dict, List, Optional

import psutil

from core.common.error_handler import handle_error
from core.common.process.base import AbstractProcessManager


class Win32ProcessManager(AbstractProcessManager):
    """
    Менеджер процессов Windows, основанный на psutil и subprocess.
    """

    def start_process(
        self,
        executable: str,
        args: Optional[List[str]] = None,
        cwd: Optional[str] = None,
        wait: bool = False,
        shell: bool = False,
        env: Optional[Dict[str, str]] = None,
    ) -> Dict[str, Any]:
        """
        Запускает процесс.

        Args:
            executable (str): Путь к исполняемому файлу
            args (List[str], optional): Список аргументов командной строки
            cwd (str, optional): Рабочая директория
            wait (bool): Ожидать завершения процесса
            shell (bool): Использовать оболочку для запуска
            env (Dict[str, str], optional): Переменные окружения

        Returns:
            Dict[str, Any]: Информация о запущенном процессе
        """
        try:
            # Подготавливаем команду
            if args is not None:
                if shell:
                    cmd = f"{executable} {' '.join(args)}"
                else:
                    cmd = [executable] + args
            else:
                cmd = executable

            # Запускаем процесс
            process = subprocess.Popen(
                cmd,
                cwd=cwd,
                shell=shell,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                env=env,
            )

            # Если нужно ожидать завершения
            if wait:
                stdout, stderr = process.communicate()
                return {
                    "pid": process.pid,
                    "returncode": process.returncode,
                    "stdout": stdout,
                    "stderr": stderr,
                    "process": process,
                }
            else:
                return {"pid": process.pid, "process": process}
        except Exception as e:
            handle_error(f"Ошибка при запуске процесса: {e}", e, module="process")
            return {"error": str(e)}

    def run_command(
        self, command: str, cwd: Optional[str] = None, env: Optional[Dict[str, str]] = None
    ) -> Dict[str, Any]:
        """
        Выполняет команду в оболочке и ожидает завершения.

        Args:
            command (str): Команда для выполнения
            cwd (str, optional): Рабочая директория
            env (Dict[str, str], optional): Переменные окружения

        Returns:
            Dict[str, Any]: Результат выполнения команды
        """
        try:
            process = subprocess.Popen(
                command,
                cwd=cwd,
                shell=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                env=env,
            )

            stdout, stderr = process.communicate()

            return {
                "pid": process.pid,
                "returncode": process.returncode,
                "stdout": stdout,
                "stderr": stderr,
                "process": process,
            }
        except Exception as e:
            handle_error(f"Ошибка при выполнении команды: {e}", e, module="process")
            return {"error": str(e)}

    def terminate_process(self, pid: Optional[int] = None, name: Optional[str] = None) -> bool:
        """
        Завершает процесс по его PID или имени.

        Args:
            pid (int, optional): Идентификатор процесса
            name (str, optional): Имя процесса

        Returns:
            bool: True в случае успешного завершения
        """
        if pid is not None:
            try:
                process = psutil.Process(pid)
                process.terminate()
                return True
            except psutil.NoSuchProcess:
                handle_error(f"Процесс с PID {pid} не существует", module="process")
                return False
            except Exception as e:
                handle_error(f"Ошибка при завершении процесса: {e}", e, module="process")
                return False
        elif name is not None:
            processes = self.find_process_by_name(name)
            if not processes:
                handle_error(f"Процессы с именем {name} не найдены", module="process")
                return False

            success = False
            for process_info in processes:
                try:
                    process = psutil.Process(process_info["pid"])
                    process.terminate()
                    success = True
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    pass

            return success
        else:
            handle_error("Необходимо указать pid или name", module="process")
            return False

    def kill_process(self, pid: int) -> bool:
        """
        Принудительно завершает процесс по его PID.

        Args:
            pid (int): Идентификатор процесса

        Returns:
            bool: True в случае успешного завершения
        """
        try:
            process = psutil.Process(pid)
            process.kill()
            return True
        except psutil.NoSuchProcess:
            handle_error(f"Процесс с PID {pid} не существует", module="process")
            return False
        except Exception as e:
            handle_error(f"Ошибка при принудительном завершении процесса: {e}", e, module="process")
            return False

    def get_process_info(self, pid: int) -> Optional[Dict[str, Any]]:
        """
        Получает подробную информацию о процессе.

        Args:
            pid (int): Идентификатор процесса

        Returns:
            Optional[Dict[str, Any]]: Словарь с информацией о процессе или None, если процесс не найден
        """
        try:
            proc = psutil.Process(pid)

            # Получаем базовую информацию
            info = {
                "pid": proc.pid,
                "name": proc.name(),
                "status": proc.status(),
                "create_time": proc.create_time(),
                "cpu_percent": proc.cpu_percent(interval=0.1),
                "memory_percent": proc.memory_percent(),
                "num_threads": proc.num_threads(),
            }
            # Добавляем путь к исполняемому файлу
            try:
                info["exe"] = proc.exe()
            except (psutil.AccessDenied, psutil.NoSuchProcess):
                info["exe"] = ""

            # Добавляем командную строку
            try:
                info["cmdline"] = proc.cmdline()
            except (psutil.AccessDenied, psutil.NoSuchProcess):
                info["cmdline"] = []

            # Добавляем информацию о рабочей директории
            try:
                info["cwd"] = proc.cwd()
            except (psutil.AccessDenied, psutil.NoSuchProcess):
                info["cwd"] = ""

            # Добавляем информацию о пользователе
            try:
                info["username"] = proc.username()
            except (psutil.AccessDenied, psutil.NoSuchProcess):
                info["username"] = ""

            # Добавляем информацию о потреблении ресурсов
            try:
                mem_info = proc.memory_info()
                info["memory_rss"] = mem_info.rss
                info["memory_vms"] = mem_info.vms
            except (psutil.AccessDenied, psutil.NoSuchProcess):
                info["memory_rss"] = 0
                info["memory_vms"] = 0

            # Добавляем информацию о подключениях
            try:
                info["connections"] = [conn._asdict() for conn in proc.connections()]
            except (psutil.AccessDenied, psutil.NoSuchProcess):
                info["connections"] = []

            return info

        except psutil.NoSuchProcess:
            handle_error(f"Процесс с PID {pid} не найден", module="process")
            return None
        except Exception as e:
            handle_error(f"Ошибка при получении информации о процессе: {e}", e, module="process")
            return None

    def find_process_by_name(self, name: str) -> List[Dict[str, Any]]:
        """
        Находит процессы по имени.

        Args:
            name (str): Имя процесса (может быть частичным)

        Returns:
            List[Dict[str, Any]]: Список словарей с информацией о найденных процессах
        """
        try:
            result = []
            for proc in psutil.process_iter(["pid", "name", "exe", "cmdline"]):
                if name.lower() in proc.info["name"].lower():
                    try:
                        process_info = {
                            "pid": proc.info["pid"],
                            "name": proc.info["name"],
                            "exe": proc.info.get("exe", ""),
                            "cmdline": proc.info.get("cmdline", []),
                        }
                        result.append(process_info)
                    except (psutil.NoSuchProcess, psutil.AccessDenied):
                        pass
            return result
        except Exception as e:
            handle_error(f"Ошибка при поиске процессов по имени: {e}", e, module="process")
            return []

    def is_process_running(self, pid: Optional[int] = None, name: Optional[str] = None) -> bool:
        """
        Проверяет, запущен ли процесс.

        Args:
            pid (int, optional): Идентификатор процесса
            name (str, optional): Имя процесса

        Returns:
            bool: True, если процесс запущен
        """
        try:
            if pid is not None:
                return psutil.pid_exists(pid)
            elif name is not None:
                processes = self.find_process_by_name(name)
                return len(processes) > 0
            else:
                handle_error("Необходимо указать pid или name", module="process")
                return False
        except Exception as e:
            handle_error(f"Ошибка при проверке состояния процесса: {e}", e, module="process")
            return False

    def wait_for_process_exit(self, pid: int, timeout: Optional[int] = None) -> bool:
        """
        Ожидает завершения процесса.

        Args:
            pid (int): Идентификатор процесса
            timeout (int, optional): Таймаут в секундах

        Returns:
            bool: True, если процесс завершился, False в случае таймаута
        """
        try:
            process = psutil.Process(pid)
            process.wait(timeout=timeout)
            return True
        except psutil.TimeoutExpired:
            return False
        except psutil.NoSuchProcess:
            return True
        except Exception as e:
            handle_error(f"Ошибка при ожидании завершения процесса: {e}", e, module="process")
            return False

    def get_all_processes(self) -> List[Dict[str, Any]]:
        """
        Получает список всех запущенных процессов.

        Returns:
            List[Dict[str, Any]]: Список словарей с информацией о процессах
        """
        try:
            result = []
            for proc in psutil.process_iter(
                ["pid", "name", "exe", "cmdline", "username", "status"]
            ):
                try:
                    process_info = {
                        "pid": proc.info["pid"],
                        "name": proc.info["name"],
                        "exe": proc.info.get("exe", ""),
                        "cmdline": proc.info.get("cmdline", []),
                        "username": proc.info.get("username", ""),
                        "status": proc.info.get("status", ""),
                    }
                    result.append(process_info)
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    pass
            return result
        except Exception as e:
            handle_error(f"Ошибка при получении списка процессов: {e}", e, module="process")
            return []

    def set_process_priority(self, pid: int, priority: str) -> bool:
        """
        Устанавливает приоритет процесса.

        Args:
            pid (int): Идентификатор процесса
            priority (str): Приоритет процесса ('realtime', 'high', 'above_normal',
                        'normal', 'below_normal', 'idle')

        Returns:
            bool: True в случае успешной установки приоритета
        """
        try:
            import win32api
            import win32con
            import win32process

            # Словарь соответствия строковых приоритетов и констант Windows
            priority_map = {
                "realtime": win32process.REALTIME_PRIORITY_CLASS,
                "high": win32process.HIGH_PRIORITY_CLASS,
                "above_normal": win32process.ABOVE_NORMAL_PRIORITY_CLASS,
                "normal": win32process.NORMAL_PRIORITY_CLASS,
                "below_normal": win32process.BELOW_NORMAL_PRIORITY_CLASS,
                "idle": win32process.IDLE_PRIORITY_CLASS,
            }
            # Проверяем наличие приоритета в словаре
            if priority.lower() not in priority_map:
                handle_error(f"Неизвестный приоритет: {priority}", module="process")
                return False

            priority_value = priority_map[priority.lower()]

            # Получаем дескриптор процесса и устанавливаем приоритет
            handle = win32api.OpenProcess(win32con.PROCESS_ALL_ACCESS, False, pid)
            win32process.SetPriorityClass(handle, priority_value)

            return True
        except ImportError:
            handle_error(
                "Не удалось импортировать необходимые модули win32api/win32process",
                module="process",
            )
            return False
        except psutil.NoSuchProcess:
            handle_error(f"Процесс с PID {pid} не найден", module="process")
            return False
        except Exception as e:
            handle_error(f"Ошибка при установке приоритета процесса: {e}", e, module="process")
            return False
