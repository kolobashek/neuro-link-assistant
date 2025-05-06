import pytest
from unittest.mock import patch, MagicMock

class TestProcessManager:
    """Тесты менеджера процессов Windows"""
    
    @pytest.fixture
    def process_manager(self):
        """Создает экземпляр ProcessManager"""
        from core.windows.process_manager import ProcessManager
        return ProcessManager()
    
    @patch('subprocess.Popen')
    def test_start_process(self, mock_popen, process_manager):
        """Тест запуска процесса"""
        # Настраиваем мок для Popen
        mock_process = MagicMock()
        mock_process.pid = 12345
        mock_popen.return_value = mock_process
        
        # Запускаем процесс без ожидания
        result = process_manager.start_process("notepad.exe", wait=False)
        
        # Проверяем результат
        assert result is not None
        assert result["pid"] == 12345
        assert result["process"] == mock_process
        
        # Проверяем вызов Popen
        mock_popen.assert_called_once()
        args, kwargs = mock_popen.call_args
        assert args[0] == "notepad.exe"
        assert kwargs["shell"] is False
        assert kwargs["stdout"] is not None
        assert kwargs["stderr"] is not None
    
    @patch('subprocess.Popen')
    def test_start_process_with_args(self, mock_popen, process_manager):
        """Тест запуска процесса с аргументами"""
        # Настраиваем мок для Popen
        mock_process = MagicMock()
        mock_process.pid = 12345
        mock_popen.return_value = mock_process
        
        # Запускаем процесс с аргументами
        result = process_manager.start_process("python", args=["-m", "pip", "list"], wait=False)
        
        # Проверяем результат
        assert result is not None
        assert result["pid"] == 12345
        
        # Проверяем вызов Popen
        mock_popen.assert_called_once()
        args, kwargs = mock_popen.call_args
        assert args[0] == ["python", "-m", "pip", "list"]
    
    @patch('subprocess.Popen')
    def test_start_process_with_wait(self, mock_popen, process_manager):
        """Тест запуска процесса с ожиданием завершения"""
        # Настраиваем мок для Popen
        mock_process = MagicMock()
        mock_process.pid = 12345
        mock_process.returncode = 0
        mock_process.communicate.return_value = ("stdout output", "stderr output")
        mock_popen.return_value = mock_process
        
        # Запускаем процесс с ожиданием
        result = process_manager.start_process("echo", args=["Hello"], wait=True)
        
        # Проверяем результат
        assert result is not None
        assert result["pid"] == 12345
        assert result["returncode"] == 0
        assert result["stdout"] == "stdout output"
        assert result["stderr"] == "stderr output"
        
        # Проверяем вызов communicate
        mock_process.communicate.assert_called_once()
    
    @patch('subprocess.Popen')
    def test_run_command(self, mock_popen, process_manager):
        """Тест выполнения команды"""
        # Настраиваем мок для Popen
        mock_process = MagicMock()
        mock_process.pid = 12345
        mock_process.returncode = 0
        mock_process.communicate.return_value = ("stdout output", "stderr output")
        mock_popen.return_value = mock_process
        
        # Выполняем команду
        result = process_manager.run_command("echo Hello")
        
        # Проверяем результат
        assert result is not None
        assert result["pid"] == 12345
        assert result["returncode"] == 0
        assert result["stdout"] == "stdout output"
        assert result["stderr"] == "stderr output"
        
        # Проверяем вызов Popen
        mock_popen.assert_called_once()
        args, kwargs = mock_popen.call_args
        assert args[0] == "echo Hello"
        assert kwargs["shell"] is True
    
    @patch('psutil.Process')
    def test_terminate_process(self, mock_process_class, process_manager):
        """Тест завершения процесса"""
        # Настраиваем мок для Process
        mock_process = MagicMock()
        mock_process_class.return_value = mock_process
        
        # Завершаем процесс
        result = process_manager.terminate_process(12345)
        
        # Проверяем результат
        assert result is True
        
        # Проверяем вызов terminate
        mock_process.terminate.assert_called_once()
        
        # Проверяем создание объекта Process
        mock_process_class.assert_called_once_with(12345)
    
    @patch('psutil.Process')
    def test_terminate_process_no_such_process(self, mock_process_class, process_manager):
        """Тест завершения несуществующего процесса"""
        # Настраиваем мок для генерации исключения
        import psutil
        mock_process_class.side_effect = psutil.NoSuchProcess(12345)
        
        # Завершаем несуществующий процесс
        result = process_manager.terminate_process(12345)
        
        # Проверяем результат
        assert result is False
    
    @patch('psutil.Process')
    def test_kill_process(self, mock_process_class, process_manager):
        """Тест принудительного завершения процесса"""
        # Настраиваем мок для Process
        mock_process = MagicMock()
        mock_process_class.return_value = mock_process
        
        # Завершаем процесс
        result = process_manager.kill_process(12345)
        
        # Проверяем результат
        assert result is True
        
        # Проверяем вызов kill
        mock_process.kill.assert_called_once()
    
    @patch('psutil.Process')
    def test_get_process_info(self, mock_process_class, process_manager):
        """Тест получения информации о процессе"""
        # Настраиваем мок для Process
        mock_process = MagicMock()
        mock_process.pid = 12345
        mock_process.name.return_value = "test_process.exe"
        mock_process.exe.return_value = "C:\\test_process.exe"
        mock_process.status.return_value = "running"
        mock_process.cpu_percent.return_value = 5.0
        mock_process.memory_percent.return_value = 2.5
        mock_process.create_time.return_value = 1600000000.0
        mock_process.username.return_value = "USER"
        mock_process.cmdline.return_value = ["C:\\test_process.exe", "--arg1", "--arg2"]
        mock_process_class.return_value = mock_process
        
        # Получаем информацию о процессе
        info = process_manager.get_process_info(12345)
        
        # Проверяем результат
        assert info is not None
        assert info["pid"] == 12345
        assert info["name"] == "test_process.exe"
        assert info["exe"] == "C:\\test_process.exe"
        assert info["status"] == "running"
        assert info["cpu_percent"] == 5.0
        assert info["memory_percent"] == 2.5
        assert info["create_time"] == 1600000000.0
        assert info["username"] == "USER"
        assert info["cmdline"] == ["C:\\test_process.exe", "--arg1", "--arg2"]
    
    @patch('psutil.process_iter')
    def test_find_process_by_name(self, mock_process_iter, process_manager):
        """Тест поиска процессов по имени"""
        # Создаем мок-процессы
        mock_process1 = MagicMock()
        mock_process1.info = {
            'pid': 1001,
            'name': 'test_process.exe',
            'exe': 'C:\\test_process.exe',
            'cmdline': ['C:\\test_process.exe', '--arg1']
        }
        
        mock_process2 = MagicMock()
        mock_process2.info = {
            'pid': 1002,
            'name': 'another_test_process.exe',
            'exe': 'C:\\another_test_process.exe',
            'cmdline': ['C:\\another_test_process.exe']
        }
        
        mock_process3 = MagicMock()
        mock_process3.info = {
            'pid': 1003,
            'name': 'not_matching.exe',
            'exe': 'C:\\not_matching.exe',
            'cmdline': ['C:\\not_matching.exe']
        }
        
        # Настраиваем мок для process_iter
        mock_process_iter.return_value = [mock_process1, mock_process2, mock_process3]
        
        # Ищем процессы по имени
        processes = process_manager.find_process_by_name("test_process")
        
        # Проверяем результат
        assert len(processes) == 2
        assert processes[0]["pid"] == 1001
        assert processes[0]["name"] == "test_process.exe"
        assert processes[1]["pid"] == 1002
        assert processes[1]["name"] == "another_test_process.exe"
    
    @patch('psutil.Process')
    def test_wait_for_process_exit(self, mock_process_class, process_manager):
        """Тест ожидания завершения процесса"""
        # Настраиваем мок для Process
        mock_process = MagicMock()
        mock_process_class.return_value = mock_process
        
        # Ожидаем завершения процесса
        result = process_manager.wait_for_process_exit(12345, timeout=5)
        
        # Проверяем результат
        assert result is True
        
        # Проверяем вызов wait
        mock_process.wait.assert_called_once_with(timeout=5)
    
    @patch('psutil.Process')
    def test_wait_for_process_exit_timeout(self, mock_process_class, process_manager):
        """Тест ожидания завершения процесса с таймаутом"""
        # Настраиваем мок для Process
        import psutil
        mock_process = MagicMock()
        mock_process.wait.side_effect = psutil.TimeoutExpired(5)
        mock_process_class.return_value = mock_process
        
        # Ожидаем завершения процесса с таймаутом
        result = process_manager.wait_for_process_exit(12345, timeout=5)
        
        # Проверяем результат
        assert result is False
    
    @patch('win32process.OpenProcess')
    @patch('win32process.SetPriorityClass')
    def test_set_process_priority(self, mock_set_priority, mock_open_process, process_manager):
        """Тест установки приоритета процесса"""
        # Настраиваем моки
        mock_handle = MagicMock()
        mock_open_process.return_value = mock_handle
        
        # Устанавливаем приоритет
        result = process_manager.set_process_priority(12345, "high")
        
        # Проверяем результат
        assert result is True
        
        # Проверяем вызовы функций
        import win32con
        import win32process
        mock_open_process.assert_called_once_with(win32con.PROCESS_ALL_ACCESS, False, 12345)
        mock_set_priority.assert_called_once_with(mock_handle, win32process.HIGH_PRIORITY_CLASS)
    
    def test_set_process_priority_invalid(self, process_manager):
        """Тест установки недопустимого приоритета процесса"""
        # Устанавливаем недопустимый приоритет
        result = process_manager.set_process_priority(12345, "invalid_priority")
        
        # Проверяем результат
        assert result is False
    
    @patch('psutil.process_iter')
    def test_get_all_processes(self, mock_process_iter, process_manager):
        """Тест получения списка всех процессов"""
        # Создаем мок-процессы
        mock_process1 = MagicMock()
        mock_process1.info = {
            'pid': 1001,
            'name': 'process1.exe',
            'exe': 'C:\\process1.exe',
            'cmdline': ['C:\\process1.exe', '--arg1'],
            'username': 'USER'
        }
        
        mock_process2 = MagicMock()
        mock_process2.info = {
            'pid': 1002,
            'name': 'process2.exe',
            'exe': 'C:\\process2.exe',
            'cmdline': ['C:\\process2.exe'],
            'username': 'USER'
        }
        
        # Настраиваем мок для process_iter
        mock_process_iter.return_value = [mock_process1, mock_process2]
        
        # Получаем список всех процессов
        processes = process_manager.get_all_processes()
        
        # Проверяем результат
        assert len(processes) == 2
        assert processes[0]["pid"] == 1001
        assert processes[0]["name"] == "process1.exe"
        assert processes[0]["exe"] == "C:\\process1.exe"
        assert processes[1]["pid"] == 1002
        assert processes[1]["name"] == "process2.exe"