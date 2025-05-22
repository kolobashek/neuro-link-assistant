import platform
from datetime import datetime

import pytest

from core.common.filesystem import get_file_system
from core.common.filesystem.base import AbstractFileSystem
from core.common.filesystem.factory import create_file_system, register_file_system_implementation


class MockFileSystem(AbstractFileSystem):
    """Мок-реализация файловой системы для тестирования"""

    def __init__(self, **kwargs):
        self.test_param = kwargs.get("test_param", None)

    # Реализация абстрактных методов
    def create_file(self, path, content="", encoding="utf-8"):
        return True

    def read_file(self, path, encoding="utf-8"):
        return "Mock content"

    def append_to_file(self, path, content, encoding="utf-8"):
        return True

    def delete_file(self, path):
        return True

    def create_directory(self, path):
        return True

    def delete_directory(self, path):
        return True

    def list_directory(self, path, pattern="*"):
        return ["mock_file.txt"]

    def copy_file(self, source, destination):
        return True

    def move_file(self, source, destination):
        return True

    def rename_file(self, path, new_name):
        return True

    def get_file_info(self, path):
        return {"name": "mock_file.txt", "size": 0, "is_file": True, "is_directory": False}

    def zip_files(self, file_paths, zip_path):
        return True

    def unzip_file(self, zip_path, extract_to):
        return True

    def read_json(self, path):
        return {}

    def write_json(self, path, data, indent=4):
        return True

    def read_csv(self, path, delimiter=","):
        return []

    def write_csv(self, path, data, delimiter=","):
        return True

    def read_binary(self, path):
        return b""

    def write_binary(self, path, data):
        return True

    def read_pickle(self, path):
        return {}

    def write_pickle(self, path, data):
        return True

    def search_files(self, directory, pattern="*", recursive=False):
        return []

    def is_file_exists(self, path):
        return True

    def is_directory_exists(self, path):
        return True

    def get_file_size(self, path):
        return 0

    def get_file_extension(self, path):
        return ".txt"

    # Недостающие абстрактные методы
    def file_exists(self, path):
        """Реализация недостающего метода для тестов"""
        return True

    def get_file_modification_time(self, path):
        """Реализация недостающего метода для тестов"""
        return datetime.now()

    def list_directory_names(self, path, pattern="*"):
        """Реализация недостающего метода для тестов"""
        return ["mock_dir"]

    def write_file(self, path, content, encoding="utf-8"):
        """Реализация недостающего метода для тестов"""
        return True


class TestFileSystemFactory:
    """Тесты для фабрики файловой системы"""

    @pytest.fixture(autouse=True)
    def cleanup(self):
        """Очистка после тестов"""
        yield
        # Удаляем тестовую реализацию из реестра
        from core.common.filesystem.registry import _file_system_implementations

        if "mock" in _file_system_implementations:
            del _file_system_implementations["mock"]
        if "mock_params" in _file_system_implementations:
            del _file_system_implementations["mock_params"]

    def test_get_file_system_auto(self):
        """Тест автоматического определения файловой системы"""
        fs = get_file_system()
        assert fs is not None

        # Проверяем, что получаем правильную реализацию для текущей ОС
        current_os = platform.system().lower()
        if current_os == "windows":
            from core.platform.windows.filesystem import Win32FileSystem

            assert isinstance(fs, Win32FileSystem)

    def test_register_and_get_custom_file_system(self):
        """Тест регистрации и получения пользовательской реализации"""
        # Регистрируем мок-реализацию
        register_file_system_implementation("mock", MockFileSystem)

        # Получаем экземпляр
        fs = get_file_system("mock")

        # Проверяем, что получили нужную реализацию
        assert isinstance(fs, MockFileSystem)

        # Проверяем базовую функциональность
        assert fs.read_file("any_path") == "Mock content"

    def test_file_system_with_parameters(self):
        """Тест создания файловой системы с параметрами"""
        # Регистрируем мок-реализацию
        register_file_system_implementation("mock_params", MockFileSystem)

        # Создаем экземпляр с параметрами
        fs = create_file_system("mock_params", test_param="test_value")

        # Проверяем, что получили нужную реализацию
        assert isinstance(fs, MockFileSystem)

        # Проверяем, что параметры переданы правильно
        assert fs.test_param == "test_value"

    def test_file_system_caching(self):
        """Тест кэширования экземпляров файловой системы"""
        # Регистрируем мок-реализацию
        register_file_system_implementation("mock", MockFileSystem)

        # Получаем экземпляр дважды
        fs1 = get_file_system("mock")
        fs2 = get_file_system("mock")

        # Проверяем, что это один и тот же объект (кэширование)
        assert fs1 is fs2

    def test_nonexistent_file_system(self):
        """Тест получения несуществующей реализации"""
        # Пытаемся получить несуществующую реализацию
        with pytest.raises(RuntimeError):
            get_file_system("nonexistent")
