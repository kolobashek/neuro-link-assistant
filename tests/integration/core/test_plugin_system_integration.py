import os
import tempfile
from unittest.mock import patch

import pytest

from core.common.error_handler import ErrorHandler
from core.component_registry import ComponentRegistry
from core.plugin_manager import PluginManager


class TestPluginSystemIntegration:
    """Интеграционные тесты для проверки взаимодействия системы плагинов с другими компонентами."""

    @pytest.fixture
    def setup_plugin_system(self):
        """
        Создает и настраивает компоненты для тестирования системы плагинов.
        """
        # Создаем компоненты
        registry = ComponentRegistry()
        error_handler = ErrorHandler()
        plugin_manager = PluginManager(registry)

        # Регистрируем компоненты в реестре
        registry.register("error_handler", error_handler)
        registry.register("plugin_manager", plugin_manager)

        # Создаем временную директорию для тестовых плагинов
        temp_dir = tempfile.mkdtemp()

        # Сохраняем оригинальную директорию плагинов
        original_plugins_dir = plugin_manager.plugins_dir
        plugin_manager.plugins_dir = temp_dir

        yield {
            "registry": registry,
            "error_handler": error_handler,
            "plugin_manager": plugin_manager,
            "temp_dir": temp_dir,
            "original_plugins_dir": original_plugins_dir,
        }

        # Очистка после теста
        plugin_manager.plugins_dir = original_plugins_dir
        try:
            import shutil

            shutil.rmtree(temp_dir)
        except (PermissionError, FileNotFoundError):
            pass

    def create_test_plugin(self, temp_dir, plugin_name, plugin_code):
        """
        Создает тестовый плагин в указанной директории.

        Args:
            temp_dir (str): Путь к временной директории
            plugin_name (str): Имя плагина (без расширения .py)
            plugin_code (str): Код плагина

        Returns:
            str: Полный путь к созданному файлу плагина
        """
        plugin_path = os.path.join(temp_dir, f"{plugin_name}.py")
        with open(plugin_path, "w") as f:
            f.write(plugin_code)
        return plugin_path

    def test_plugin_loading_and_initialization(self, setup_plugin_system):
        """
        Тест загрузки и инициализации плагина.
        """
        system = setup_plugin_system
        plugin_manager = system["plugin_manager"]
        temp_dir = system["temp_dir"]

        # Создаем тестовый плагин
        plugin_code = """
class TestPlugin:
    def __init__(self):
        self.initialized = False
        self.registry = None

    def setup(self):
        self.initialized = True
        return True
"""
        self.create_test_plugin(temp_dir, "test_plugin", plugin_code)

        # Загружаем плагин
        plugin = plugin_manager.load_plugin("test_plugin")

        # Проверяем результат загрузки
        assert plugin is not None
        assert hasattr(plugin, "initialized")
        assert plugin.initialized is True

        # Проверяем, что плагин добавлен в словарь плагинов
        assert "test_plugin" in plugin_manager.plugins
        assert plugin_manager.get_plugin("test_plugin") == plugin

    def test_plugin_with_registry_integration(self, setup_plugin_system):
        """
        Тест взаимодействия плагина с реестром компонентов.
        """
        system = setup_plugin_system
        plugin_manager = system["plugin_manager"]
        registry = system["registry"]
        temp_dir = system["temp_dir"]

        # Создаем тестовый плагин, который будет использовать реестр
        plugin_code = """
class RegistryPlugin:
    def __init__(self):
        self.registry = None
        self.error_handler = None

    def setup(self):
        # Ничего не делаем в setup
        pass

    def integrate(self, registry):
        self.registry = registry
        self.error_handler = registry.get("error_handler")
        return True
"""
        self.create_test_plugin(temp_dir, "registry_plugin", plugin_code)

        # Загружаем плагин
        plugin = plugin_manager.load_plugin("registry_plugin")

        # Проверяем, что плагин был загружен
        assert plugin is not None

        # Интегрируем плагин с реестром
        result = plugin.integrate(registry)
        assert result is True

        # Проверяем, что плагин получил доступ к реестру и его компонентам
        assert plugin.registry == registry
        assert plugin.error_handler == registry.get("error_handler")

    def test_plugin_error_handling(self, setup_plugin_system):
        """
        Тест обработки ошибок при загрузке и использовании плагинов.
        """
        system = setup_plugin_system
        plugin_manager = system["plugin_manager"]
        error_handler = system["error_handler"]
        temp_dir = system["temp_dir"]

        # Создаем плагин с ошибкой в методе setup
        plugin_code = """
class BrokenPlugin:
    def __init__(self):
        self.initialized = False

    def setup(self):
        raise Exception("Test error in plugin setup")
"""
        self.create_test_plugin(temp_dir, "broken_plugin", plugin_code)

        # Патчим метод handle_error для перехвата вызовов
        with patch.object(error_handler, "handle_error") as mock_handle_error:
            # Загружаем плагин с ошибкой
            plugin = plugin_manager.load_plugin("broken_plugin")

            # Проверяем, что плагин не был загружен
            assert plugin is None

            # Проверяем, что метод handle_error был вызван
            mock_handle_error.assert_called_once()
            assert "Test error in plugin setup" in str(mock_handle_error.call_args[0][0])

    def test_plugin_discovery_and_bulk_loading(self, setup_plugin_system):
        """
        Тест обнаружения и массовой загрузки плагинов.
        """
        system = setup_plugin_system
        plugin_manager = system["plugin_manager"]
        temp_dir = system["temp_dir"]

        # Создаем несколько тестовых плагинов
        plugin1_code = """
class Plugin1:
    def __init__(self):
        self.name = "Plugin1"

    def setup(self):
        pass
"""
        plugin2_code = """
class Plugin2:
    def __init__(self):
        self.name = "Plugin2"

    def setup(self):
        pass
"""
        self.create_test_plugin(temp_dir, "plugin1", plugin1_code)
        self.create_test_plugin(temp_dir, "plugin2", plugin2_code)

        # Обнаруживаем плагины
        discovered_plugins = plugin_manager.discover_plugins()
        assert len(discovered_plugins) == 2
        assert "plugin1.py" in discovered_plugins
        assert "plugin2.py" in discovered_plugins

        # Загружаем все плагины
        loaded_count = plugin_manager.load_plugins()
        assert loaded_count == 2

        # Проверяем, что плагины были загружены
        plugin1 = plugin_manager.get_plugin("plugin1")
        plugin2 = plugin_manager.get_plugin("plugin2")
        assert plugin1 is not None
        assert plugin2 is not None
        assert plugin1.name == "Plugin1"
        assert plugin2.name == "Plugin2"

    def test_plugin_unloading(self, setup_plugin_system):
        """
        Тест выгрузки плагинов.
        """
        system = setup_plugin_system
        plugin_manager = system["plugin_manager"]
        temp_dir = system["temp_dir"]

        # Создаем тестовый плагин с методом teardown
        plugin_code = """
class UnloadablePlugin:
    def __init__(self):
        self.torn_down = False

    def setup(self):
        pass

    def teardown(self):
        self.torn_down = True
"""
        self.create_test_plugin(temp_dir, "unloadable_plugin", plugin_code)

        # Загружаем плагин
        plugin = plugin_manager.load_plugin("unloadable_plugin")
        assert plugin is not None

        # Выгружаем плагин
        result = plugin_manager.unload_plugin("unloadable_plugin")
        assert result is True

        # Проверяем, что плагин был выгружен
        assert "unloadable_plugin" not in plugin_manager.plugins
        assert plugin_manager.get_plugin("unloadable_plugin") is None

        # Проверяем, что метод teardown был вызван
        assert plugin.torn_down is True
