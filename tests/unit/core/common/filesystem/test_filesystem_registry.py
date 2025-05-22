import pytest

from core.common.filesystem.base import AbstractFileSystem
from core.common.filesystem.registry import (
    get_file_system_implementation,
    get_registered_file_systems,
    is_file_system_registered,
    register_file_system,
)


class TestMockFileSystem(AbstractFileSystem):
    """Мок-реализация файловой системы для тестов реестра"""

    # Минимальная заглушка для абстрактного класса
    def create_file(self, path, content="", encoding="utf-8"):
        return True


class TestMockFileSystem2(AbstractFileSystem):
    """Вторая мок-реализация файловой системы для тестов реестра"""

    # Минимальная заглушка для абстрактного класса
    def create_file(self, path, content="", encoding="utf-8"):
        return True


class TestFileSystemRegistry:
    """Тесты для реестра файловой системы"""

    @pytest.fixture(autouse=True)
    def cleanup(self):
        """Очистка после тестов"""
        original_registry = get_registered_file_systems()
        yield
        # Восстанавливаем оригинальное состояние реестра
        from core.common.filesystem.registry import _file_system_implementations

        _file_system_implementations.clear()
        for name, impl in original_registry.items():
            _file_system_implementations[name] = impl

    def test_register_file_system(self):
        """Тест регистрации реализации файловой системы"""
        # Регистрируем тестовую реализацию
        register_file_system("test_mock", TestMockFileSystem)

        # Проверяем, что реализация зарегистрирована
        assert is_file_system_registered("test_mock")

        # Проверяем, что можем получить зарегистрированную реализацию
        impl = get_file_system_implementation("test_mock")
        assert impl is TestMockFileSystem

    def test_register_multiple_file_systems(self):
        """Тест регистрации нескольких реализаций файловой системы"""
        # Регистрируем несколько реализаций
        register_file_system("test_mock1", TestMockFileSystem)
        register_file_system("test_mock2", TestMockFileSystem2)

        # Проверяем, что обе реализации зарегистрированы
        assert is_file_system_registered("test_mock1")
        assert is_file_system_registered("test_mock2")

        # Получаем список всех зарегистрированных реализаций
        implementations = get_registered_file_systems()

        # Проверяем, что наши реализации в списке
        assert implementations["test_mock1"] is TestMockFileSystem
        assert implementations["test_mock2"] is TestMockFileSystem2

    def test_case_insensitive_names(self):
        """Тест регистрации и получения с учетом регистра имен"""
        # Регистрируем реализацию с именем в смешанном регистре
        register_file_system("TestMock", TestMockFileSystem)

        # Проверяем, что можем получить её по имени в любом регистре
        assert is_file_system_registered("testmock")
        assert is_file_system_registered("TESTMOCK")
        assert is_file_system_registered("TestMock")

        # Получаем реализацию по имени в другом регистре
        impl1 = get_file_system_implementation("testmock")
        impl2 = get_file_system_implementation("TESTMOCK")

        assert impl1 is TestMockFileSystem
        assert impl2 is TestMockFileSystem

    def test_nonexistent_implementation(self):
        """Тест получения несуществующей реализации"""
        # Проверяем, что несуществующая реализация не зарегистрирована
        assert not is_file_system_registered("nonexistent")

        # Проверяем, что получение несуществующей реализации вызывает исключение
        with pytest.raises(KeyError):
            get_file_system_implementation("nonexistent")

    def test_overwrite_implementation(self):
        """Тест перезаписи существующей реализации"""
        # Регистрируем первую реализацию
        register_file_system("test_mock", TestMockFileSystem)

        # Проверяем, что она зарегистрирована
        assert get_file_system_implementation("test_mock") is TestMockFileSystem

        # Регистрируем вторую реализацию с тем же именем
        register_file_system("test_mock", TestMockFileSystem2)

        # Проверяем, что первая реализация была заменена на вторую
        assert get_file_system_implementation("test_mock") is TestMockFileSystem2

    def test_windows_implementation_registered(self):
        """Тест, что реализация для Windows автоматически зарегистрирована"""
        # Проверяем, что реализация для Windows зарегистрирована
        assert is_file_system_registered("windows")

        # Получаем реализацию
        impl = get_file_system_implementation("windows")

        # Проверяем, что это правильный класс
        from core.platform.windows.filesystem import Win32FileSystem

        assert impl is Win32FileSystem
