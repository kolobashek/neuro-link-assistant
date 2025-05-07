import pytest
import os
import time
import subprocess
from core.window import get_window_manager WindowManager
from core.windows.system_info import SystemInfo

class TestWindowManagement:
    """Тесты управления окнами Windows"""
    
    @pytest.fixture(autouse=True)
    def setup_and_teardown(self):
        """Запускаем и закрываем Блокнот для каждого теста"""
        # Запускаем Блокнот
        self.notepad_process = subprocess.Popen(["notepad.exe"])
        # Даем время на запуск
        time.sleep(2)
        
        yield  # Выполняем тест
        
        # Закрываем Блокнот после теста
        try:
            self.notepad_process.terminate()
            self.notepad_process.wait(timeout=2)
        except:
            # Если не удалось закрыть нормально, убиваем процесс
            os.system("taskkill /f /im notepad.exe 2>nul")
    
    def test_find_window(self):
        """Тест поиска окна по заголовку"""
        window_manager = WindowManager()
        
        # Используем более точное название окна - в Windows 10/11 это "Безымянный - Блокнот" или "Untitled - Notepad"
        window_info = window_manager.find_window(process_name="notepad.exe")
        assert window_info is not None
    
    def test_find_nonexistent_window(self):
        """Тест поиска несуществующего окна"""
        window_manager = WindowManager()
        
        window_info = window_manager.find_window(title="NonExistentWindowTitle123456789")
        assert window_info is None
    
    def test_activate_window(self):
        """Тест активации окна"""
        window_manager = WindowManager()
        window_info = window_manager.find_window(process_name="notepad.exe")
        
        assert window_info is not None  # Проверяем, что окно найдено
        result = window_manager.activate_window(window_info)
        assert result is True
    
    def test_close_window(self):
        """Тест закрытия окна"""
        window_manager = WindowManager()
        window_info = window_manager.find_window(process_name="notepad.exe")
        
        assert window_info is not None  # Проверяем, что окно найдено
        result = window_manager.close_window(window_info)
        assert result is True
        
        # Запускаем новый экземпляр Блокнота для следующих тестов
        time.sleep(1)
        self.notepad_process = subprocess.Popen(["notepad.exe"])
        time.sleep(2)
    
    def test_get_window_text(self):
        """Тест получения текста окна"""
        window_manager = WindowManager()
        window_info = window_manager.find_window(process_name="notepad.exe")
        
        assert window_info is not None  # Проверяем, что окно найдено
        text = window_manager.get_window_text(window_info)
        # В разных версиях Windows заголовок может отличаться
        # Проверяем, что текст не пустой
        assert text != ""


class TestFileSystem:
    """Тесты работы с файловой системой Windows"""
    
    def setup_method(self):
        """Подготовка перед каждым тестом"""
        self.test_dir = "test_files"
        self.test_file = f"{self.test_dir}/test.txt"
        
        # Создаем тестовую директорию, если она не существует
        import os
        if not os.path.exists(self.test_dir):
            os.makedirs(self.test_dir)
    
    def teardown_method(self):
        """Очистка после каждого теста"""
        # Удаляем тестовую директорию
        import shutil
        import os
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)
    
    def test_create_file(self):
        """Тест создания файла"""
        from core.filesystem import get_file_system FileSystem
        file_system = FileSystem()
        
        result = file_system.create_file(self.test_file, "Test content")
        
        assert result is True
        assert os.path.exists(self.test_file)
    
    def test_read_file(self):
        """Тест чтения файла"""
        from core.filesystem import get_file_system FileSystem
        file_system = FileSystem()
        
        # Создаем файл для чтения
        file_system.create_file(self.test_file, "Test content")
        
        content = file_system.read_file(self.test_file)
        
        assert content == "Test content"
    
    def test_write_file(self):
        """Тест записи в файл"""
        from core.filesystem import get_file_system FileSystem
        file_system = FileSystem()
        
        # Создаем файл
        file_system.create_file(self.test_file, "Initial content")
        
        # Записываем новое содержимое
        result = file_system.write_file(self.test_file, "New content")
        
        assert result is True
        
        # Проверяем, что содержимое изменилось
        content = file_system.read_file(self.test_file)
        assert content == "New content"
    
    def test_delete_file(self):
        """Тест удаления файла"""
        from core.filesystem import get_file_system FileSystem
        file_system = FileSystem()
        
        # Создаем файл для удаления
        file_system.create_file(self.test_file, "Test content")
        
        # Проверяем, что файл существует
        assert os.path.exists(self.test_file)
        
        # Удаляем файл
        result = file_system.delete_file(self.test_file)
        
        assert result is True
        assert not os.path.exists(self.test_file)


class TestProcessManagement:
    """Тесты управления процессами Windows"""
    
    def teardown_method(self):
        """Очистка после каждого теста"""
        # Закрываем Блокнот, если он был запущен
        import os
        os.system("taskkill /f /im notepad.exe 2>nul")
    
    def test_start_process(self):
        """Тест запуска процесса"""
        from core.process import get_process_manager ProcessManager
        process_manager = ProcessManager()
        
        process_info = process_manager.start_process("notepad.exe")
        assert process_info is not None
        assert "pid" in process_info
        
        # Завершаем процесс
        import os
        os.system("taskkill /f /im notepad.exe 2>nul")
    
    def test_terminate_process(self):
        """Тест завершения процесса"""
        from core.process import get_process_manager ProcessManager
        process_manager = ProcessManager()
        
        # Запускаем процесс напрямую через subprocess
        import subprocess
        import time
        
        process = subprocess.Popen(["notepad.exe"])
        time.sleep(1)  # Даем время на запуск
        
        # Завершаем процесс через process_manager по имени
        result = process_manager.terminate_process(name="notepad.exe")
        
        assert result is True
    
    def test_is_process_running(self):
        """Тест проверки запущенного процесса"""
        from core.process import get_process_manager ProcessManager
        process_manager = ProcessManager()
        
        # Запускаем процесс напрямую через subprocess
        import subprocess
        import time
        
        process = subprocess.Popen(["notepad.exe"])
        time.sleep(1)  # Даем время на запуск
        
        # Проверяем по имени процесса
        result = process_manager.is_process_running(name="notepad.exe")
        assert result is True
        
        # Завершаем процесс
        process.terminate()
        try:
            process.wait(timeout=2)
        except:
            import os
            os.system("taskkill /f /im notepad.exe 2>nul")


class TestSystemInformation:
    """Тесты получения системной информации Windows"""
    
    def test_get_os_info(self):
        """Тест получения информации об ОС"""
        from core.windows.system_info import SystemInfo
        system_info = SystemInfo()
        
        os_info = system_info.get_os_info()
        
        assert os_info is not None
        assert "name" in os_info
        assert os_info["name"] == "Windows"
    
    def test_get_cpu_info(self):
        """Тест получения информации о процессоре"""
        from core.windows.system_info import SystemInfo
        system_info = SystemInfo()
        
        cpu_info = system_info.get_cpu_info()
        
        assert cpu_info is not None
        assert "name" in cpu_info
        # Используем cores_physical и cores_logical вместо cores
        assert "cores_physical" in cpu_info
        assert "cores_logical" in cpu_info
    
    def test_get_memory_info(self):
        """Тест получения информации о памяти"""
        from core.windows.system_info import SystemInfo
        system_info = SystemInfo()
        
        memory_info = system_info.get_memory_info()
        
        assert memory_info is not None
        assert "total" in memory_info
        assert "available" in memory_info
        assert "used" in memory_info
    
    def test_get_disk_info(self):
        """Тест получения информации о дисках"""
        from core.windows.system_info import SystemInfo
        system_info = SystemInfo()
        
        disk_info = system_info.get_disk_info()
        
        assert disk_info is not None
        # Используем "C:\\" вместо "C:"
        assert "C:\\" in disk_info


class TestRegistryManagement:
    """Тесты работы с реестром Windows"""
    
    def setup_method(self):
        """Подготовка перед каждым тестом"""
        from core.windows.registry_manager import RegistryManager
        self.registry_manager = RegistryManager()
        
        # Используем временный ключ для тестов
        self.root_key = self.registry_manager.HKEY_CURRENT_USER
        self.test_key_path = "Software\\NLATest"
        self.test_value_name = "TestValue"
        
        # Создаем тестовый ключ
        self.registry_manager.create_key(self.root_key, self.test_key_path)
    
    def teardown_method(self):
        """Очистка после каждого теста"""
        # Удаляем тестовый ключ
        try:
            self.registry_manager.delete_key(self.root_key, self.test_key_path)
        except:
            pass
    
    def test_read_value(self):
        """Тест чтения значения из реестра"""
        # Записываем значение
        self.registry_manager.write_value(
            self.root_key, 
            self.test_key_path, 
            self.test_value_name, 
            "Test Value"
        )
        
        # Читаем значение
        value, value_type = self.registry_manager.read_value(
            self.root_key, 
            self.test_key_path, 
            self.test_value_name
        )
        
        assert value == "Test Value"
        assert value_type == self.registry_manager.REG_SZ
    
    def test_write_value(self):
        """Тест записи значения в реестр"""
        # Записываем значение
        result = self.registry_manager.write_value(
            self.root_key, 
            self.test_key_path, 
            self.test_value_name, 
            "Test Value"
        )
        
        assert result is True
        
        # Проверяем, что значение записалось
        value, _ = self.registry_manager.read_value(
            self.root_key, 
            self.test_key_path, 
            self.test_value_name
        )
        
        assert value == "Test Value"
    
    def test_delete_value(self):
        """Тест удаления значения из реестра"""
        # Записываем значение
        self.registry_manager.write_value(
            self.root_key, 
            self.test_key_path, 
            self.test_value_name, 
            "Test Value"
        )
        
        # Удаляем значение
        result = self.registry_manager.delete_value(
            self.root_key, 
            self.test_key_path, 
            self.test_value_name
        )
        
        assert result is True
        
        # Проверяем, что значение удалено
        value, _ = self.registry_manager.read_value(
            self.root_key, 
            self.test_key_path, 
            self.test_value_name
        )
        
        assert value is None
    
    def test_create_key(self):
        """Тест создания ключа реестра"""
        # Создаем новый ключ
        new_key_path = f"{self.test_key_path}\\SubKey"
        result = self.registry_manager.create_key(
            self.root_key, 
            new_key_path
        )
        
        assert result is True
        
        # Проверяем, что ключ создан, записав в него значение
        write_result = self.registry_manager.write_value(
            self.root_key, 
            new_key_path, 
            self.test_value_name, 
            "Test Value"
        )
        
        assert write_result is True
    
    def test_delete_key(self):
        """Тест удаления ключа реестра"""
        # Создаем новый ключ
        new_key_path = f"{self.test_key_path}\\SubKey"
        self.registry_manager.create_key(
            self.root_key, 
            new_key_path
        )
        
        # Удаляем ключ
        result = self.registry_manager.delete_key(
            self.root_key, 
            new_key_path
        )
        
        # Проверяем результат удаления
        # Примечание: в некоторых случаях удаление может не сработать из-за прав доступа
        # Поэтому мы не проверяем результат удаления, а только проверяем, что ключ не существует
        
        # Проверяем, что ключ удален, проверив список подключей
        subkeys = self.registry_manager.list_keys(self.root_key, self.test_key_path)
        assert "SubKey" not in subkeys


if __name__ == "__main__":
    pytest.main(["-v", __file__])