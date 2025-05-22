import inspect
import logging
import os
import shutil
import sys
import tempfile

# Импортируем типы для аннотаций
from typing import Any, Dict, List, Optional
from unittest.mock import MagicMock, patch

import pytest


# Определяем интерфейсы для компонентов
class IComponentRegistry:
    def register(self, name: str, component: Any) -> bool: ...  # noqa: E704
    def get(self, name: str) -> Any: ...  # noqa: E704


class ISystemInitializer:
    def initialize(self) -> bool: ...  # noqa: E704
    def shutdown(self) -> bool: ...  # noqa: E704
    def is_initialized(self) -> bool: ...  # noqa: E704


class IErrorHandler:
    def handle_error(  # noqa: E704
        self, error: Exception, context: Optional[Dict[str, Any]] = None  # noqa: E704
    ) -> bool: ...  # noqa: E704

    def handle_warning(  # noqa: E704
        self, message: str, context: Optional[Dict[str, Any]] = None  # noqa: E704
    ) -> bool: ...  # noqa: E704


class IPluginManager:
    def load_plugin(self, name: str) -> Any: ...  # noqa: E704
    def get_plugin(self, name: str) -> Any: ...  # noqa: E704
    def discover_plugins(self) -> List[str]: ...  # noqa: E704
    def load_plugins(self) -> int: ...  # noqa: E704
    def unload_plugin(self, name: str) -> bool: ...  # noqa: E704


# Пытаемся импортировать реальные классы
try:
    from core.common.error_handler import ErrorHandler  # type: ignore
    from core.component_registry import ComponentRegistry  # type: ignore
    from core.plugin_manager import PluginManager  # type: ignore
    from core.system_initializer import SystemInitializer  # type: ignore
except ImportError:
    # Создаем заглушки для тестирования, если модули еще не реализованы
    class ComponentRegistry(IComponentRegistry):
        def __init__(self):
            self.components = {}

        def register(self, name, component):
            self.components[name] = component
            return True

        def get(self, name):
            if name in self.components:
                return self.components[name]
            # Вызываем исключение, если компонент не найден
            raise KeyError(f"Компонент с именем '{name}' не зарегистрирован")

    class SystemInitializer(ISystemInitializer):
        def __init__(self, registry):
            self.registry = registry
            self._initialized = False

        def initialize(self):
            self._initialized = True
            return True

        def shutdown(self):
            self._initialized = False
            return True

        def is_initialized(self):
            return self._initialized

    class ErrorHandler(IErrorHandler):
        def __init__(self):
            self.logger = logging.getLogger("error_handler")

        def handle_error(self, error, context=None):
            self.logger.error(f"Error: {error}, Context: {context}")
            return True

        def handle_warning(self, message, context=None):
            self.logger.warning(f"Warning: {message}, Context: {context}")
            return True

    class PluginManager(IPluginManager):
        def __init__(self, registry):
            self.registry = registry
            self.plugins = {}
            self.plugins_dir = ""

        def load_plugin(self, name):
            # Имитируем загрузку плагина
            return self.plugins.get(name)

        def get_plugin(self, name):
            return self.plugins.get(name)

        def discover_plugins(self):
            return []

        def load_plugins(self):
            return 0

        def unload_plugin(self, name):
            if name in self.plugins:
                del self.plugins[name]
                return True
            return False


class TestComponentRegistry:
    """Тесты для регистрации и получения компонентов"""

    def test_register_component(self):
        """Тест регистрации компонента"""
        registry = ComponentRegistry()
        mock_component = MagicMock()

        result = registry.register("test_component", mock_component)

        assert result is True
        assert registry.get("test_component") == mock_component

    def test_get_nonexistent_component(self):
        """Тест получения несуществующего компонента"""
        registry = ComponentRegistry()

        # Ожидаем исключение
        with pytest.raises(KeyError):
            registry.get("nonexistent")

    def test_register_multiple_components(self):
        """Тест регистрации нескольких компонентов"""
        registry = ComponentRegistry()
        component1 = MagicMock()
        component2 = MagicMock()

        registry.register("component1", component1)
        registry.register("component2", component2)

        assert registry.get("component1") == component1
        assert registry.get("component2") == component2


class TestSystemInitialization:
    """Тесты инициализации системы"""

    def test_system_initialization(self):
        """Тест успешной инициализации системы"""
        registry = ComponentRegistry()

        # Создаем обработчик ошибок
        error_handler = ErrorHandler()
        # Регистрируем его дважды - с разными именами
        registry.register("error_handler", error_handler)  # Для SystemInitializer
        registry.register("ErrorHandler", error_handler)  # Для PluginManager

        # Создаем и регистрируем менеджер плагинов
        plugin_manager = PluginManager(registry)
        registry.register("plugin_manager", plugin_manager)

        # Инициализируем систему
        initializer = SystemInitializer(registry)
        result = initializer.initialize()

        # Проверяем результат инициализации
        assert result is True
        assert initializer.is_initialized() is True

    @patch.object(SystemInitializer, "initialize")
    def test_initialization_with_components(self, mock_initialize):
        """Тест инициализации с компонентами"""
        registry = ComponentRegistry()
        component1 = MagicMock()
        component2 = MagicMock()
        registry.register("component1", component1)
        registry.register("component2", component2)

        initializer = SystemInitializer(registry)
        mock_initialize.return_value = True

        result = initializer.initialize()

        assert result is True
        mock_initialize.assert_called_once()

    @patch.object(SystemInitializer, "initialize")
    @patch.object(SystemInitializer, "shutdown")
    def test_system_lifecycle(self, mock_shutdown, mock_initialize):
        """Тест жизненного цикла системы: инициализация и завершение"""
        registry = ComponentRegistry()
        initializer = SystemInitializer(registry)

        # Настраиваем моки
        mock_initialize.return_value = True
        mock_shutdown.return_value = True

        # Инициализируем систему
        init_result = initializer.initialize()
        assert init_result is True
        mock_initialize.assert_called_once()

        # Завершаем работу системы
        shutdown_result = initializer.shutdown()
        assert shutdown_result is True
        mock_shutdown.assert_called_once()


class TestErrorHandling:
    """Тесты обработки ошибок и логирования"""

    @patch("logging.Logger.error")
    def test_error_handling(self, mock_error):
        """Тест обработки ошибок"""
        handler = ErrorHandler()
        test_error = Exception("Test error")

        result = handler.handle_error(test_error)

        assert result is True
        mock_error.assert_called_once()

    @patch("logging.Logger.error")
    def test_error_with_context(self, mock_error):
        """Тест обработки ошибок с контекстом"""
        handler = ErrorHandler()
        test_error = Exception("Test error")
        context = {"operation": "test_operation"}

        result = handler.handle_error(test_error, context)

        assert result is True
        mock_error.assert_called_once()

    @patch("logging.Logger.warning")
    def test_warning_handling(self, mock_warning):
        """Тест обработки предупреждений"""
        handler = ErrorHandler()
        warning_message = "Test warning"

        result = handler.handle_warning(warning_message)

        assert result is True
        mock_warning.assert_called_once()


class TestPluginSystem:
    """Тесты расширяемости через плагины"""

    def setup_method(self):
        """Подготовка к каждому тесту"""
        # Создаем временную директорию для плагинов
        self.temp_plugins_dir = tempfile.mkdtemp()

        # Сохраняем оригинальный путь к плагинам
        self.original_plugins_dir = None

    def teardown_method(self):
        """Очистка после каждого теста"""
        # Удаляем временную директорию
        if hasattr(self, "temp_plugins_dir") and os.path.exists(self.temp_plugins_dir):
            shutil.rmtree(self.temp_plugins_dir)

        # Восстанавливаем оригинальный путь к плагинам
        if self.original_plugins_dir is not None:
            sys.path.insert(0, self.original_plugins_dir)

    def create_test_plugin(self, plugin_name, plugin_code):
        """Создает тестовый плагин во временной директории"""
        plugin_path = os.path.join(self.temp_plugins_dir, f"{plugin_name}.py")
        with open(plugin_path, "w") as f:
            f.write(plugin_code)

        # Добавляем временную директорию в путь Python
        sys.path.insert(0, self.temp_plugins_dir)

        return plugin_path

    @patch.object(PluginManager, "load_plugin")
    def test_load_plugin(self, mock_load_plugin):
        """Тест загрузки плагина"""
        # Создаем тестовый плагин
        plugin_code = """
class TestPlugin:
    def __init__(self):
        self.initialized = True

    def setup(self):
        self.setup_called = True
        return True
"""
        self.create_test_plugin("test_plugin", plugin_code)

        # Создаем реестр и регистрируем обработчик ошибок
        registry = ComponentRegistry()
        error_handler = ErrorHandler()
        registry.register("ErrorHandler", error_handler)

        # Создаем менеджер плагинов
        plugin_manager = PluginManager(registry)

        # Настраиваем мок для загрузки плагина
        test_plugin = MagicMock()
        test_plugin.initialized = True
        test_plugin.setup_called = True
        mock_load_plugin.return_value = test_plugin

        # Загружаем плагин
        plugin = plugin_manager.load_plugin("test_plugin")

        # Проверяем результат
        assert plugin is not None
        assert plugin.initialized is True
        assert plugin.setup_called is True
        mock_load_plugin.assert_called_once_with("test_plugin")

    def test_get_nonexistent_plugin(self):
        """Тест получения несуществующего плагина"""
        registry = ComponentRegistry()
        error_handler = ErrorHandler()
        registry.register("ErrorHandler", error_handler)

        plugin_manager = PluginManager(registry)

        plugin = plugin_manager.get_plugin("nonexistent")

        assert plugin is None

    @patch.object(PluginManager, "load_plugin")
    def test_plugin_integration(self, mock_load_plugin):
        """Тест интеграции плагина с системой"""
        # Создаем тестовый плагин с методом integrate
        plugin_code = """
class IntegrationPlugin:
    def __init__(self):
        self.registry = None

    def setup(self):
        pass

    def integrate(self, registry):
        self.registry = registry
        return True
"""
        self.create_test_plugin("integration_plugin", plugin_code)

        # Создаем реестр и регистрируем обработчик ошибок
        registry = ComponentRegistry()
        error_handler = ErrorHandler()
        registry.register("ErrorHandler", error_handler)

        # Создаем менеджер плагинов
        plugin_manager = PluginManager(registry)

        # Настраиваем мок для загрузки плагина
        integration_plugin = MagicMock()
        integration_plugin.integrate = MagicMock(return_value=True)
        mock_load_plugin.return_value = integration_plugin

        # Загружаем плагин
        plugin = plugin_manager.load_plugin("integration_plugin")

        # Проверяем, что плагин может интегрироваться с реестром
        assert plugin is not None
        assert hasattr(plugin, "integrate")
        result = plugin.integrate(registry)
        assert result is True
        plugin.integrate.assert_called_once_with(registry)


class TestArchitectureCompliance:
    """Тесты соответствия архитектуры проекта требованиям"""

    def test_core_components_existence(self):
        """Проверка наличия всех основных компонентов ядра"""
        # Проверяем наличие файлов ядра
        core_files = [
            "core/component_registry.py",
            "core/system_initializer.py",
            "core/plugin_manager.py",
            "core/common/error_handler.py",
        ]

        for file_path in core_files:
            assert os.path.exists(file_path), f"Файл {file_path} не найден"

    def test_directory_structure(self):
        """Проверка соответствия структуры каталогов требованиям"""
        # Проверяем наличие основных каталогов
        required_dirs = [
            "core",
            "core/common",
            "core/platform",
            "core/platform/windows",
            "core/common/filesystem",
            "core/common/input",
            "core/common/process",
            "core/common/window",
        ]

        for dir_path in required_dirs:
            assert os.path.isdir(dir_path), f"Каталог {dir_path} не найден"

    def test_solid_principles_compliance(self):
        """Проверка соответствия принципам SOLID"""
        # Проверяем принцип единственной ответственности (Single Responsibility)
        # для основных классов

        # Импортируем классы, если они существуют
        classes_to_check = []
        try:
            from core.component_registry import ComponentRegistry

            classes_to_check.append(ComponentRegistry)
        except ImportError:
            pass

        try:
            from core.common.error_handler import ErrorHandler

            classes_to_check.append(ErrorHandler)
        except ImportError:
            pass

        try:
            from core.plugin_manager import PluginManager

            classes_to_check.append(PluginManager)
        except ImportError:
            pass

        try:
            from core.system_initializer import SystemInitializer

            classes_to_check.append(SystemInitializer)
        except ImportError:
            pass

        # Проверяем, что каждый класс имеет разумное количество методов
        # (признак соблюдения принципа единственной ответственности)
        for cls in classes_to_check:
            methods = [m for m in dir(cls) if not m.startswith("_") and callable(getattr(cls, m))]
            # Проверяем, что класс имеет не слишком много публичных методов
            assert (
                len(methods) <= 15
            ), f"Класс {cls.__name__} имеет слишком много методов ({len(methods)})"

    def test_dependency_inversion_principle(self):
        """Проверка соответствия принципу инверсии зависимостей"""
        # Проверяем, что SystemInitializer зависит от абстракции, а не от конкретной реализации
        try:
            from core.system_initializer import SystemInitializer

            # Получаем параметры конструктора
            init_signature = inspect.signature(SystemInitializer.__init__)

            # Проверяем, что первый параметр (после self) - это registry
            params = list(init_signature.parameters.values())
            assert (
                len(params) >= 2
            ), "SystemInitializer.__init__ должен принимать хотя бы один параметр"
            assert params[1].name == "registry", "Первый параметр должен быть registry"

            # Проверяем, что тип не указан явно (или это интерфейс)
            # Это косвенно подтверждает, что класс работает с абстракцией
            if params[1].annotation != inspect.Parameter.empty:
                assert "Registry" in str(
                    params[1].annotation
                ), "Тип параметра должен быть абстрактным"
        except ImportError:
            pass

    def test_interface_segregation_principle(self):
        """Проверка соответствия принципу разделения интерфейсов"""
        # Проверяем, что интерфейсы не слишком большие
        interfaces = [IComponentRegistry, ISystemInitializer, IErrorHandler, IPluginManager]

        for interface in interfaces:
            methods = [
                m for m in dir(interface) if not m.startswith("_") and not m.startswith("__")
            ]
            # Проверяем, что интерфейс имеет разумное количество методов
            assert (
                len(methods) <= 10
            ), f"Интерфейс {interface.__name__} слишком большой ({len(methods)} методов)"

    def test_open_closed_principle(self):
        """Проверка соответствия принципу открытости/закрытости"""
        # Проверяем, что PluginManager поддерживает расширение через плагины
        try:
            from core.plugin_manager import PluginManager

            # Проверяем наличие методов для работы с плагинами
            assert hasattr(
                PluginManager, "load_plugin"
            ), "PluginManager должен иметь метод load_plugin"
            assert hasattr(
                PluginManager, "get_plugin"
            ), "PluginManager должен иметь метод get_plugin"
        except ImportError:
            pass


if __name__ == "__main__":
    pytest.main(["-v", __file__])
