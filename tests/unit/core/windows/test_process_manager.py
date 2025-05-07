import pytest
import time
from unittest.mock import patch, MagicMock

class TestProcessManager:
    """Тесты класса управления процессами Windows"""
    
    @pytest.fixture
    def process_manager(self):
        """Создает экземпляр ProcessManager"""
        from core.process import get_process_manager ProcessManager
        return ProcessManager()
    
    @patch('subprocess.Popen')
    def test_start_process(self, mock_popen, process_manager):
        """Тест запуска процесса"""
        # Настраиваем мок для Popen
        mock_process = MagicMock()
        mock_process.pid = 12345
        mock_popen.return_value = mock_process
        
        # Запускаем процесс
        process = process_manager.start_process("notepad.exe")
        
        # Проверяем результат
        assert process is not None
        assert process["pid"] == 12345
        assert process["name"] == "notepad.exe"
        mock_popen.assert_called_once()
    
    @patch('subprocess.Popen')
    def test_start_process_with_args(self, mock_popen, process_manager):
        """Тест запуска процесса с аргументами"""
        # Настраиваем мок для Popen
        mock_process = MagicMock()
        mock_process.pid = 12345
        mock_popen.return_value = mock_process
        
        # Запускаем процесс с аргументами
        process = process_manager.start_process("python.exe", args=["-c", "print('Hello')"])
        
        # Проверяем результат
        assert process is not None
        assert process["pid"] == 12345
        assert process["name"] == "python.exe"
        mock_popen.assert_called_once()
        
        # Проверяем, что аргументы были переданы правильно
        args, kwargs = mock_popen.call_args
        assert args[0] == ["python.exe", "-c", "print('Hello')"]
    
    @patch('subprocess.Popen')
    def test_start_process_with_wait(self, mock_popen, process_manager):
        """Тест запуска процесса с ожиданием завершения"""
        # Настраиваем мок для Popen
        mock_process = MagicMock()
        mock_process.pid = 12345
        mock_process.wait.return_value = 0
        mock_popen.return_value = mock_process
        
        # Запускаем процесс с ожиданием
        process = process_manager.start_process("notepad.exe", wait=True)
        
        # Проверяем результат
        assert process is not None
        assert process["pid"] == 12345
        assert process["exit_code"] == 0
        mock_process.wait.assert_called_once()
    
    @patch('subprocess.run')
    def test_run_command(self, mock_run, process_manager):
        """Тест выполнения команды"""
        # Настраиваем мок для run
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = "Command output"
        mock_run.return_value = mock_result
        
        # Выполняем команду
        result = process_manager.run_command("echo Hello")
        
        # Проверяем результат
        assert result is not None
        assert result["exit_code"] == 0
        assert result["output"] == "Command output"
        mock_run.assert_called_once()
    
    @patch('psutil.Process')
    def test_terminate_process(self, mock_process_class, process_manager):
        """Тест завершения процесса"""
        # Настраиваем мок для Process
        mock_process = MagicMock()
        mock_process.terminate.return_value = None
        mock_process.wait.return_value = None
        mock_process_class.return_value = mock_process
        
        # Завершаем процесс
        result = process_manager.terminate_process(12345)
        
        # Проверяем результат
        assert result is True
        mock_process.terminate.assert_called_once()
        mock_process.wait.assert_called_once()
    
    @patch('psutil.Process')
    def test_terminate_process_no_such_process(self, mock_process_class, process_manager):
        """Тест завершения несуществующего процесса"""
        # Настраиваем мок для Process, чтобы он вызывал исключение
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
        mock_process.kill.return_value = None
        mock_process_class.return_value = mock_process
        
        # Принудительно завершаем процесс
        result = process_manager.kill_process(12345)
        
        # Проверяем результат
        assert result is True
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
        """Тест поиска процесса по имени"""
        # Создаем мок-процессы
        mock_process1 = MagicMock()
        mock_process1.name.return_value = "test_process.exe"
        mock_process1.pid = 12345
        
        mock_process2 = MagicMock()
        mock_process2.name.return_value = "other_process.exe"
        mock_process2.pid = 67890
        
        # Настраиваем мок для process_iter
        mock_process_iter.return_value = [mock_process1, mock_process2]
        
        # Ищем процесс по имени
        processes = process_manager.find_process_by_name("test_process.exe")
        
        # Проверяем результат
        assert len(processes) == 1
        assert processes[0]["pid"] == 12345
        assert processes[0]["name"] == "test_process.exe"
    
    @patch('psutil.Process')
    @patch('time.sleep')
    def test_wait_for_process_exit(self, mock_sleep, mock_process_class, process_manager):
        """Тест ожидания завершения процесса"""
        # Настраиваем мок для Process
        mock_process = MagicMock()
        mock_process.is_running.side_effect = [True, True, False]  # Процесс завершается после третьей проверки
        mock_process_class.return_value = mock_process
        
        # Ожидаем завершения процесса
        result = process_manager.wait_for_process_exit(12345, timeout=5)
        
        # Проверяем результат
        assert result is True
        assert mock_sleep.call_count == 2  # Две паузы между тремя проверками
    
    @patch('psutil.Process')
    @patch('time.sleep')
    def test_wait_for_process_exit_timeout(self, mock_sleep, mock_process_class, process_manager):
        """Тест ожидания завершения процесса с таймаутом"""
        # Настраиваем мок для Process
        mock_process = MagicMock()
        mock_process.is_running.return_value = True  # Процесс никогда не завершается
        mock_process_class.return_value = mock_process
        
        # Настраиваем мок для time.sleep, чтобы имитировать истечение времени
        mock_sleep.side_effect = lambda x: None
        
        # Ожидаем завершения процесса с таймаутом
        result = process_manager.wait_for_process_exit(12345, timeout=2, check_interval=1)
        
        # Проверяем результат
        assert result is False
        assert mock_sleep.call_count == 2  # Две паузы по 1 секунде
    
    @patch('psutil.Process')
    def test_set_process_priority(self, mock_process_class, process_manager):
        """Тест установки приоритета процесса"""
        # Настраиваем мок для Process
        mock_process = MagicMock()
        mock_process.nice = MagicMock()
        mock_process_class.return_value = mock_process
        
        # Устанавливаем приоритет процесса
        result = process_manager.set_process_priority(12345, "high")
        
        # Проверяем результат
        assert result is True
        mock_process.nice.assert_called_once()
    
    @patch('psutil.Process')
    def test_set_process_priority_invalid(self, mock_process_class, process_manager):
        """Тест установки недопустимого приоритета процесса"""
        # Настраиваем мок для Process
        mock_process = MagicMock()
        mock_process.nice = MagicMock()
        mock_process_class.return_value = mock_process
        
        # Устанавливаем недопустимый приоритет процесса
        result = process_manager.set_process_priority(12345, "invalid_priority")
        
        # Проверяем результат
        assert result is False
        assert not mock_process.nice.called
    
    @patch('psutil.process_iter')
    def test_get_all_processes(self, mock_process_iter, process_manager):
        """Тест получения списка всех процессов"""
        # Создаем мок-процессы
        mock_process1 = MagicMock()
        mock_process1.name.return_value = "process1.exe"
        mock_process1.pid = 12345
        mock_process1.info = {"name": "process1.exe", "pid": 12345}
        
        mock_process2 = MagicMock()
        mock_process2.name.return_value = "process2.exe"
        mock_process2.pid = 67890
        mock_process2.info = {"name": "process2.exe", "pid": 67890}
        
        # Настраиваем мок для process_iter
        mock_process_iter.return_value = [mock_process1, mock_process2]
        
        # Получаем список всех процессов
        processes = process_manager.get_all_processes()
        
        # Проверяем результат
        assert len(processes) == 2
        assert any(p["pid"] == 12345 and p["name"] == "process1.exe" for p in processes)
        assert any(p["pid"] == 67890 and p["name"] == "process2.exe" for p in processes)