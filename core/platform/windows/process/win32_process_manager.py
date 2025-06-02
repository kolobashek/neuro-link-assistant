# -*- coding: utf-8 -*-
"""
Windows-специфичный менеджер процессов на базе win32api и psutil.
"""

import subprocess
from typing import Any, Dict, List, Optional

import psutil

from core.common.process.base import AbstractProcessManager


class Win32ProcessManager(AbstractProcessManager):
    """
    Windows-реализация менеджера процессов.
    Реализует AbstractProcessManager для Windows-платформы.
    """

    def __init__(self):
        """Инициализация менеджера процессов Windows."""
        pass

    def start_process(
        self,
        executable: str,
        args: Optional[List[str]] = None,
        cwd: Optional[str] = None,
        wait: bool = False,
        shell: bool = False,
        env: Optional[Dict[str, str]] = None,
    ) -> Dict[str, Any]:
        """Запускает процесс."""
        try:
            cmd = [executable]
            if args:
                cmd.extend(args)

            process = subprocess.Popen(cmd, cwd=cwd, shell=shell, env=env)

            if wait:
                process.wait()

            return {"success": True, "pid": process.pid, "process": process}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def run_command(
        self, command: str, cwd: Optional[str] = None, env: Optional[Dict[str, str]] = None
    ) -> Dict[str, Any]:
        """Выполняет команду в оболочке и ожидает завершения."""
        try:
            result = subprocess.run(
                command, shell=True, cwd=cwd, env=env, capture_output=True, text=True
            )

            return {
                "success": result.returncode == 0,
                "returncode": result.returncode,
                "stdout": result.stdout,
                "stderr": result.stderr,
            }
        except Exception as e:
            return {"success": False, "error": str(e)}

    def terminate_process(self, pid: Optional[int] = None, name: Optional[str] = None) -> bool:
        """Завершает процесс по его PID или имени."""
        try:
            if pid:
                process = psutil.Process(pid)
                process.terminate()
                return True
            elif name:
                for proc in psutil.process_iter(["pid", "name"]):
                    if proc.info["name"].lower() == name.lower():
                        proc.terminate()
                        return True
            return False
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            return False
        except Exception:
            return False

    def kill_process(self, pid: int) -> bool:
        """Принудительно завершает процесс по его PID."""
        try:
            process = psutil.Process(pid)
            process.kill()
            return True
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            return False
        except Exception:
            return False

    def get_process_info(self, pid: int) -> Optional[Dict[str, Any]]:
        """Получает подробную информацию о процессе."""
        try:
            process = psutil.Process(pid)
            return {
                "pid": process.pid,
                "name": process.name(),
                "exe": process.exe(),
                "status": process.status(),
                "cpu_percent": process.cpu_percent(),
                "memory_percent": process.memory_percent(),
                "create_time": process.create_time(),
                "username": process.username(),
                "cmdline": process.cmdline(),
                "memory_info": process.memory_info()._asdict(),
            }
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            return None
        except Exception:
            return None

    def find_process_by_name(self, name: str) -> List[Dict[str, Any]]:
        """Находит процессы по имени."""
        processes = []
        try:
            for proc in psutil.process_iter(["pid", "name", "status"]):
                if name.lower() in proc.info["name"].lower():
                    processes.append(proc.info)
        except Exception:
            pass
        return processes

    def is_process_running(self, pid: Optional[int] = None, name: Optional[str] = None) -> bool:
        """Проверяет, запущен ли процесс."""
        try:
            if pid:
                process = psutil.Process(pid)
                return process.is_running()
            elif name:
                for proc in psutil.process_iter(["name"]):
                    if proc.info["name"].lower() == name.lower():
                        return True
            return False
        except Exception:
            return False

    def wait_for_process_exit(self, pid: int, timeout: Optional[int] = None) -> bool:
        """Ожидает завершения процесса."""
        try:
            process = psutil.Process(pid)
            process.wait(timeout=timeout)
            return True
        except (psutil.NoSuchProcess, psutil.TimeoutExpired):
            return False
        except Exception:
            return False

    def get_all_processes(self) -> List[Dict[str, Any]]:
        """Получает список всех запущенных процессов."""
        processes = []
        try:
            for proc in psutil.process_iter(["pid", "name", "status", "cpu_percent"]):
                try:
                    processes.append(proc.info)
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    pass
        except Exception:
            pass
        return processes

    def set_process_priority(self, pid: int, priority: str) -> bool:
        """Устанавливает приоритет процесса."""
        priority_map = {
            "realtime": psutil.REALTIME_PRIORITY_CLASS,
            "high": psutil.HIGH_PRIORITY_CLASS,
            "above_normal": psutil.ABOVE_NORMAL_PRIORITY_CLASS,
            "normal": psutil.NORMAL_PRIORITY_CLASS,
            "below_normal": psutil.BELOW_NORMAL_PRIORITY_CLASS,
            "idle": psutil.IDLE_PRIORITY_CLASS,
        }

        try:
            if priority.lower() not in priority_map:
                return False

            process = psutil.Process(pid)
            process.nice(priority_map[priority.lower()])
            return True
        except Exception:
            return False
