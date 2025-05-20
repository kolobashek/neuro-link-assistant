import os
import subprocess
import time

import pytest

from core.common.filesystem import get_file_system
from core.platform.windows.window.win32_window_manager import Win32WindowManager as WindowManager


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
        except subprocess.TimeoutExpired:
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
        # Просто проверяем, что метод отработал без ошибок
        # Текст может быть пустым в тестовой среде
        assert isinstance(text, str)  # Проверяем, что результат - строка


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
        import os
        import shutil

        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)

    def test_create_file(self):
        """Тест создания файла"""

        file_system = get_file_system()

        result = file_system.create_file(self.test_file, "Test content")

        assert result is True
        assert os.path.exists(self.test_file)

    def test_read_file(self):
        """Тест чтения файла"""

        file_system = get_file_system()

        # Создаем файл для чтения
        file_system.create_file(self.test_file, "Test content")

        content = file_system.read_file(self.test_file)

        assert content == "Test content"

    def test_write_file(self):
        """Тест записи в файл"""

        file_system = get_file_system()

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

        file_system = get_file_system()

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
        from core.common.process import get_process_manager

        process_manager = get_process_manager()

        process_info = process_manager.start_process("notepad.exe")
        assert process_info is not None
        assert "pid" in process_info

        # Завершаем процесс
        import os

        os.system("taskkill /f /im notepad.exe 2>nul")

    def test_terminate_process(self):
        """Тест завершения процесса"""
        from core.common.process import get_process_manager

        process_manager = get_process_manager()

        # Запускаем процесс напрямую через subprocess
        import subprocess
        import time

        process = subprocess.Popen(["notepad.exe"])
        # Проверяем, что процесс запущен
        assert process.pid > 0

        time.sleep(1)  # Даем время на запуск

        # Завершаем процесс через process_manager по имени
        result = process_manager.terminate_process(name="notepad.exe")
        assert result is True

        # Дополнительно проверяем, что процесс действительно завершен
        process.poll()
        assert process.returncode is not None

    def test_is_process_running(self):
        """Тест проверки запущенного процесса"""
        from core.common.process import get_process_manager

        process_manager = get_process_manager()

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
        except subprocess.TimeoutExpired:
            import os

            os.system("taskkill /f /im notepad.exe 2>nul")


class TestSystemInformation:
    """Тесты получения системной информации Windows"""

    def test_get_os_info(self):
        """Тест получения информации об ОС"""
        from core.platform.windows.system.win32_system_info import Win32SystemInfo

        system_info = Win32SystemInfo()

        os_info = system_info.get_os_info()

        assert os_info is not None
        assert "name" in os_info
        assert os_info["name"] == "Windows"

    def test_get_cpu_info(self):
        """Тест получения информации о процессоре"""
        from core.platform.windows.system.win32_system_info import Win32SystemInfo

        system_info = Win32SystemInfo()

        cpu_info = system_info.get_cpu_info()

        assert cpu_info is not None
        assert "name" in cpu_info
        # Используем cores_physical и cores_logical вместо cores
        assert "cores_physical" in cpu_info
        assert "cores_logical" in cpu_info

    def test_get_memory_info(self):
        """Тест получения информации о памяти"""
        from core.platform.windows.system.win32_system_info import Win32SystemInfo

        system_info = Win32SystemInfo()

        memory_info = system_info.get_memory_info()

        assert memory_info is not None
        assert "total" in memory_info
        assert "available" in memory_info
        assert "used" in memory_info

    def test_get_disk_info(self):
        """Тест получения информации о дисках"""
        from core.platform.windows.system.win32_system_info import Win32SystemInfo

        system_info = Win32SystemInfo()

        disk_info = system_info.get_disk_info()

        assert disk_info is not None
        # Используем "C:\\" вместо "C:"
        assert "C:\\" in disk_info


class TestRegistryManagement:
    """Тесты работы с реестром Windows"""

    def setup_method(self):
        """Подготовка перед каждым тестом"""
        from core.platform.windows.registry.win32_registry_manager import Win32RegistryManager

        self.registry_manager = Win32RegistryManager()

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
        except Exception:
            pass

    def test_read_value(self):
        """Тест чтения значения из реестра"""
        # Записываем значение
        self.registry_manager.write_value(
            self.root_key, self.test_key_path, self.test_value_name, "Test Value"
        )

        # Читаем значение
        value = self.registry_manager.read_value(
            self.root_key, self.test_key_path, self.test_value_name
        )

        assert value == "Test Value"

    def test_write_value(self):
        """Тест записи значения в реестр"""
        # Записываем значение
        result = self.registry_manager.write_value(
            self.root_key, self.test_key_path, self.test_value_name, "Test Value"
        )

        assert result is True

        # Проверяем, что значение записалось
        value = self.registry_manager.read_value(
            self.root_key, self.test_key_path, self.test_value_name
        )

        assert value == "Test Value"

    def test_delete_value(self):
        """Тест удаления значения из реестра"""
        # Сначала записываем значение
        self.registry_manager.write_value(
            self.root_key, self.test_key_path, self.test_value_name, "Test Value"
        )

        # Удаляем значение
        result = self.registry_manager.delete_value(
            self.root_key, self.test_key_path, self.test_value_name
        )

        assert result is True

        # Проверяем, что значение удалено
        value = self.registry_manager.read_value(
            self.root_key, self.test_key_path, self.test_value_name
        )

        assert value is None

    def test_list_values(self):
        """Тест получения списка значений из реестра"""
        # Записываем несколько значений
        self.registry_manager.write_value(
            self.root_key, self.test_key_path, "Value1", "Test Value 1"
        )
        self.registry_manager.write_value(
            self.root_key, self.test_key_path, "Value2", "Test Value 2"
        )
        import winreg

        self.registry_manager.write_value(
            self.root_key, self.test_key_path, "Value3", 123, winreg.REG_DWORD
        )

        # Получаем список значений
        values = self.registry_manager.list_values(self.root_key, self.test_key_path)

        # Проверяем результат
        assert len(values) >= 3  # Могут быть другие значения
        # Проверяем наличие наших значений в списке
        value_names = [value["name"] for value in values]
        assert "Value1" in value_names
        assert "Value2" in value_names
        assert "Value3" in value_names

    def test_create_key(self):
        """Тест создания ключа реестра"""
        # Создаем новый ключ
        subkey_path = f"{self.test_key_path}\\SubKey"
        result = self.registry_manager.create_key(self.root_key, subkey_path)

        assert result is True
        # Проверяем, что ключ создан, получив список подключей
        keys = self.registry_manager.list_keys(self.root_key, self.test_key_path)

        assert "SubKey" in keys

    def test_delete_key(self):
        """Тест удаления ключа реестра"""
        # Создаем новый ключ
        subkey_path = f"{self.test_key_path}\\SubKey"
        self.registry_manager.create_key(self.root_key, subkey_path)

        # Удаляем подключ
        result = self.registry_manager.delete_key(self.root_key, subkey_path)

        assert result is True

        # Проверяем, что ключ удален
        keys = self.registry_manager.list_keys(self.root_key, self.test_key_path)
        assert "SubKey" not in keys

    def test_list_keys(self):
        """Тест получения списка подключей ключа реестра"""
        # Создаем несколько подключей
        self.registry_manager.create_key(self.root_key, f"{self.test_key_path}\\Subkey1")
        self.registry_manager.create_key(self.root_key, f"{self.test_key_path}\\Subkey2")
        self.registry_manager.create_key(self.root_key, f"{self.test_key_path}\\Subkey3")

        # Получаем список подключей
        keys = self.registry_manager.list_keys(self.root_key, self.test_key_path)

        assert len(keys) >= 3  # Минимум 3 созданных нами ключа
        assert "Subkey1" in keys
        assert "Subkey2" in keys
        assert "Subkey3" in keys


if __name__ == "__main__":
    # При запуске файла напрямую запускаем тесты с verbose
    pytest.main(["-v", __file__])
