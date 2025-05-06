import subprocess
import psutil
import time
import os

class ProcessManager:
    """
    Менеджер процессов Windows.
    Предоставляет функции для запуска, завершения и управления процессами.
    """
    
    def start_process(self, command, args=None, shell=False, cwd=None):
        """
        Запускает процесс.
        
        Args:
            command (str): Команда или путь к исполняемому файлу
            args (list, optional): Аргументы командной строки
            shell (bool, optional): Использовать ли оболочку
            cwd (str, optional): Рабочая директория
            
        Returns:
            dict: Информация о запущенном процессе или None в случае ошибки
        """
        try:
            cmd = [command]
            if args:
                if isinstance(args, list):
                    cmd.extend(args)
                else:
                    cmd.append(args)
            
            process = subprocess.Popen(
                cmd if not shell else " ".join(cmd),
                shell=shell,
                cwd=cwd
            )
            
            # Даем процессу время на запуск
            time.sleep(0.5)
            
            # Проверяем, запустился ли процесс
            if process.poll() is not None:
                return None
            
            return {
                "pid": process.pid,
                "command": command,
                "args": args,
                "process": process
            }
        except Exception as e:
            print(f"Error starting process: {e}")
            return None
    
    def terminate_process(self, process_info=None, pid=None, name=None):
        """
        Завершает процесс.
        
        Args:
            process_info (dict, optional): Информация о процессе
            pid (int, optional): ID процесса
            name (str, optional): Имя процесса
            
        Returns:
            bool: True в случае успешного завершения
        """
        try:
            # Если передана информация о процессе
            if process_info:
                if "process" in process_info and process_info["process"]:
                    process_info["process"].terminate()
                    return True
                elif "pid" in process_info:
                    pid = process_info["pid"]
            
            # Если передан PID
            if pid:
                try:
                    process = psutil.Process(pid)
                    process.terminate()
                    return True
                except psutil.NoSuchProcess:
                    return False
            
            # Если передано имя процесса
            if name:
                terminated = False
                for process in psutil.process_iter(['pid', 'name']):
                    if name.lower() in process.info['name'].lower():
                        try:
                            process.terminate()
                            terminated = True
                        except psutil.NoSuchProcess:
                            pass
                return terminated
            
            return False
        except Exception as e:
            print(f"Error terminating process: {e}")
            return False
    
    def is_process_running(self, process_info=None, pid=None, name=None):
        """
        Проверяет, запущен ли процесс.
        
        Args:
            process_info (dict, optional): Информация о процессе
            pid (int, optional): ID процесса
            name (str, optional): Имя процесса
            
        Returns:
            bool: True, если процесс запущен
        """
        try:
            # Если передана информация о процессе
            if process_info:
                if "process" in process_info and process_info["process"]:
                    return process_info["process"].poll() is None
                elif "pid" in process_info:
                    pid = process_info["pid"]
            
            # Если передан PID
            if pid:
                return psutil.pid_exists(pid)
            
            # Если передано имя процесса
            if name:
                for process in psutil.process_iter(['pid', 'name']):
                    if name.lower() in process.info['name'].lower():
                        return True
                return False
            
            return False
        except Exception as e:
            print(f"Error checking if process is running: {e}")
            return False
    
    def get_process_info(self, pid=None, name=None):
        """
        Получает информацию о процессе.
        
        Args:
            pid (int, optional): ID процесса
            name (str, optional): Имя процесса
            
        Returns:
            dict: Информация о процессе или None, если процесс не найден
        """
        try:
            # Если передан PID
            if pid:
                try:
                    process = psutil.Process(pid)
                    return {
                        "pid": process.pid,
                        "name": process.name(),
                        "status": process.status(),
                        "cpu_percent": process.cpu_percent(),
                        "memory_percent": process.memory_percent(),
                        "create_time": process.create_time()
                    }
                except psutil.NoSuchProcess:
                    return None
            
            # Если передано имя процесса
            if name:
                for process in psutil.process_iter(['pid', 'name', 'status']):
                    if name.lower() in process.info['name'].lower():
                        process_info = process.as_dict(attrs=[
                            'pid', 'name', 'status', 'cpu_percent', 
                            'memory_percent', 'create_time'
                        ])
                        return process_info
                return None
            
            return None
        except Exception as e:
            print(f"Error getting process info: {e}")
            return None
    
    def get_all_processes(self):
        """
        Получает список всех запущенных процессов.
        
        Returns:
            list: Список словарей с информацией о каждом процессе
        """
        try:
            processes = []
            for process in psutil.process_iter(['pid', 'name', 'status']):
                try:
                    process_info = process.as_dict(attrs=[
                        'pid', 'name', 'status', 'cpu_percent', 
                        'memory_percent', 'create_time'
                    ])
                    processes.append(process_info)
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    pass
            return processes
        except Exception as e:
            print(f"Error getting all processes: {e}")
            return []