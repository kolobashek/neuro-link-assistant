import subprocess
import psutil
import win32process
import win32con

class ProcessManager:
    """
    Менеджер процессов Windows.
    Предоставляет функции для запуска, завершения и управления процессами.
    """
    
    def start_process(self, executable, args=None, cwd=None, wait=False, shell=False):
        """
        Запускает процесс.
        
        Args:
            executable (str): Путь к исполняемому файлу
            args (list, optional): Список аргументов командной строки
            cwd (str, optional): Рабочая директория
            wait (bool): Ожидать завершения процесса
            shell (bool): Использовать оболочку для запуска
            
        Returns:
            dict: Информация о запущенном процессе
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
                text=True
            )
            
            # Если нужно ожидать завершения
            if wait:
                stdout, stderr = process.communicate()
                return {
                    "pid": process.pid,
                    "returncode": process.returncode,
                    "stdout": stdout,
                    "stderr": stderr,
                    "process": process
                }
            else:
                return {
                    "pid": process.pid,
                    "process": process
                }
        except Exception as e:
            print(f"Error starting process: {e}")
            return None
    
    def run_command(self, command, cwd=None):
        """
        Выполняет команду в оболочке и ожидает завершения.
        
        Args:
            command (str): Команда для выполнения
            cwd (str, optional): Рабочая директория
            
        Returns:
            dict: Результат выполнения команды
        """
        try:
            process = subprocess.Popen(
                command,
                cwd=cwd,
                shell=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            stdout, stderr = process.communicate()
            
            return {
                "pid": process.pid,
                "returncode": process.returncode,
                "stdout": stdout,
                "stderr": stderr,
                "process": process
            }
        except Exception as e:
            print(f"Error running command: {e}")
            return None
    
    def terminate_process(self, pid=None, name=None):
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
                print(f"Process with PID {pid} does not exist")
                return False
            except Exception as e:
                print(f"Error terminating process: {e}")
                return False
        elif name is not None:
            processes = self.find_process_by_name(name)
            if not processes:
                print(f"No processes found with name {name}")
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
            print("Either pid or name must be specified")
            return False
    
    def kill_process(self, pid):
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
            print(f"Process with PID {pid} does not exist")
            return False
        except Exception as e:
            print(f"Error killing process: {e}")
            return False
    
    def get_process_info(self, pid):
        """
        Получает информацию о процессе по его PID.
        
        Args:
            pid (int): Идентификатор процесса
            
        Returns:
            dict: Информация о процессе или None, если процесс не найден
        """
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
                "cmdline": process.cmdline()
            }
        except psutil.NoSuchProcess:
            print(f"Process with PID {pid} does not exist")
            return None
        except Exception as e:
            print(f"Error getting process info: {e}")
            return None
    
    def find_process_by_name(self, name):
        """
        Находит процессы по имени.
        
        Args:
            name (str): Имя процесса (может быть частичным)
            
        Returns:
            list: Список словарей с информацией о найденных процессах
        """
        result = []
        
        for process in psutil.process_iter(['pid', 'name', 'exe', 'cmdline']):
            try:
                process_info = process.info
                
                # Проверяем соответствие имени
                if name.lower() in process_info['name'].lower():
                    result.append({
                        "pid": process_info['pid'],
                        "name": process_info['name'],
                        "exe": process_info['exe'],
                        "cmdline": process_info['cmdline']
                    })
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                pass
        
        return result
    
    def wait_for_process_exit(self, pid, timeout=None):
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
            # Процесс уже завершен
            return True
        except Exception as e:
            print(f"Error waiting for process: {e}")
            return False
    
    def set_process_priority(self, pid, priority):
        """
        Устанавливает приоритет процесса.
        
        Args:
            pid (int): Идентификатор процесса
            priority (str): Приоритет ('high', 'above_normal', 'normal', 'below_normal', 'low')
            
        Returns:
            bool: True в случае успешной установки приоритета
        """
        try:
            # Словарь соответствия строковых приоритетов и констант Windows
            priority_map = {
                'high': win32process.HIGH_PRIORITY_CLASS,
                'above_normal': win32process.ABOVE_NORMAL_PRIORITY_CLASS,
                'normal': win32process.NORMAL_PRIORITY_CLASS,
                'below_normal': win32process.BELOW_NORMAL_PRIORITY_CLASS,
                'low': win32process.IDLE_PRIORITY_CLASS
            }
            
            # Проверяем, что указан допустимый приоритет
            if priority not in priority_map:
                print(f"Invalid priority: {priority}")
                return False
            
            # Получаем хэндл процесса
            handle = win32process.OpenProcess(win32con.PROCESS_ALL_ACCESS, False, pid)
            
            # Устанавливаем приоритет
            win32process.SetPriorityClass(handle, priority_map[priority])
            
            return True
        except Exception as e:
            print(f"Error setting process priority: {e}")
            return False
    
    def get_all_processes(self):
        """
        Получает список всех запущенных процессов.
        
        Returns:
            list: Список словарей с информацией о процессах
        """
        result = []
        
        for process in psutil.process_iter(['pid', 'name', 'exe', 'cmdline', 'username']):
            try:
                process_info = process.info
                result.append({
                    "pid": process_info['pid'],
                    "name": process_info['name'],
                    "exe": process_info.get('exe', ''),
                    "cmdline": process_info.get('cmdline', []),
                    "username": process_info.get('username', '')
                })
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                pass
        
        return result

    def terminate_process_by_name(self, name):
        """
        Завершает процесс по его имени.
        
        Args:
            name (str): Имя процесса
        
        Returns:
            bool: True в случае успешного завершения хотя бы одного процесса
        """
        processes = self.find_process_by_name(name)
        if not processes:
            print(f"No processes found with name {name}")
            return False
        
        success = False
        for process_info in processes:
            if self.terminate_process(process_info["pid"]):
                success = True
        
        return success

    def is_process_running(self, pid=None, name=None):
        """
        Проверяет, запущен ли процесс.
        
        Args:
            pid (int, optional): Идентификатор процесса
            name (str, optional): Имя процесса
        
        Returns:
            bool: True, если процесс запущен
        """
        if pid is not None:
            try:
                process = psutil.Process(pid)
                return process.is_running()
            except psutil.NoSuchProcess:
                return False
        elif name is not None:
            processes = self.find_process_by_name(name)
            return len(processes) > 0
        else:
            print("Either pid or name must be specified")
            return False