import os
import tempfile
from unittest.mock import MagicMock, patch

import pytest

from core.common.error_handler import ErrorHandler
from core.component_registry import ComponentRegistry
from core.plugin_manager import PluginManager
from core.system_initializer import SystemInitializer


@pytest.fixture
def setup_core_components():
    """
    Создает и настраивает основные компоненты ядра для тестирования.
    """
    # Создаем компоненты
    registry = ComponentRegistry()
    error_handler = ErrorHandler()

    # СНАЧАЛА регистрируем ErrorHandler
    registry.register("error_handler", error_handler)

    # ПОТОМ создаем PluginManager (который ищет error_handler в конструкторе)
    plugin_manager = PluginManager(registry)
    system_initializer = SystemInitializer(registry)

    # Регистрируем остальные компоненты в реестре
    registry.register("plugin_manager", plugin_manager)

    # Возвращаем созданные компоненты
    return {
        "registry": registry,
        "error_handler": error_handler,
        "plugin_manager": plugin_manager,
        "system_initializer": system_initializer,
    }


class TestCoreComponentsIntegration:
    """Интеграционные тесты для проверки взаимодействия компонентов ядра системы."""

    def test_system_initialization_with_all_components(self, setup_core_components):
        """
        Тест полной инициализации системы со всеми компонентами.
        """
        components = setup_core_components
        registry = components["registry"]
        system_initializer = components["system_initializer"]

        # Создаем и регистрируем тестовый компонент
        test_component = MagicMock()
        test_component.initialize = MagicMock(return_value=True)
        registry.register("test_component", test_component)

        # Инициализируем систему
        result = system_initializer.initialize()

        # Проверяем результат инициализации - должен вернуться объект System
        from core.system import System

        assert isinstance(result, System), f"Expected System object, got {type(result)}"
        assert system_initializer.is_initialized() is True

        # Проверяем, что система имеет доступ к реестру
        assert result._registry == registry

        # Проверяем, что метод initialize тестового компонента был вызван
        test_component.initialize.assert_called_once()

    def test_error_handling_during_initialization(self, setup_core_components):
        """
        Тест обработки ошибок во время инициализации системы.
        """
        components = setup_core_components
        registry = components["registry"]
        system_initializer = components["system_initializer"]
        error_handler = components["error_handler"]

        # Создаем компонент, который будет вызывать ошибку
        failing_component = MagicMock()
        failing_component.initialize = MagicMock(side_effect=Exception("Test error"))
        registry.register("failing_component", failing_component)

        # Патчим метод handle_error обработчика ошибок
        with patch.object(error_handler, "handle_error") as mock_handle_error:
            # Инициализируем систему
            result = system_initializer.initialize()

            # Проверяем, что инициализация завершилась неудачно
            assert result is False

            # Проверяем, что метод handle_error был вызван
            mock_handle_error.assert_called_once()
            assert "Test error" in str(mock_handle_error.call_args[0][0])

    def test_plugin_loading_with_error_handling(self, setup_core_components):
        """
        Тест загрузки плагинов с обработкой ошибок.
        """
        components = setup_core_components
        plugin_manager = components["plugin_manager"]
        error_handler = components["error_handler"]

        # Создаем временную директорию для тестового плагина
        with tempfile.TemporaryDirectory() as temp_dir:
            # Сохраняем оригинальную директорию плагинов
            original_plugins_dir = plugin_manager.plugins_dir
            plugin_manager.plugins_dir = temp_dir

            # Создаем тестовый плагин
            plugin_code = """
class TestPlugin:
    def __init__(self):
        self.initialized = False

    def setup(self):
        self.initialized = True
        return True
"""
            plugin_path = os.path.join(temp_dir, "test_plugin.py")
            with open(plugin_path, "w") as f:
                f.write(plugin_code)

            # Патчим метод для обработки ошибок
            with patch.object(error_handler, "handle_error") as mock_handle_error:
                # Загружаем плагин
                plugin = plugin_manager.load_plugin("test_plugin")

                # Проверяем результат загрузки
                assert plugin is not None
                assert hasattr(plugin, "initialized")
                assert plugin.initialized is True

                # Проверяем, что метод handle_error не был вызван
                mock_handle_error.assert_not_called()

            # Восстанавливаем оригинальную директорию плагинов
            plugin_manager.plugins_dir = original_plugins_dir

    def test_component_registry_integration(self, setup_core_components):
        """
        Тест интеграции реестра компонентов с другими компонентами.
        """
        components = setup_core_components
        registry = components["registry"]
        error_handler = components["error_handler"]

        # Добавляем тестовый компонент в реестр
        test_component = MagicMock()
        registry.register("test_component", test_component)

        # Проверяем, что компонент был добавлен
        assert registry.get("test_component") == test_component

        # Проверяем получение обработчика ошибок
        assert registry.get("error_handler") == error_handler

        # Проверяем обработку ошибки при получении несуществующего компонента
        with pytest.raises(KeyError):
            registry.get("non_existent_component")

    def test_full_system_lifecycle(self, setup_core_components):
        """
        Тест полного жизненного цикла системы: инициализация, работа, завершение.
        """
        components = setup_core_components
        registry = components["registry"]
        system_initializer = components["system_initializer"]

        # Создаем компоненты с методами инициализации и завершения
        component1 = MagicMock()
        component1.initialize = MagicMock(return_value=True)
        component1.shutdown = MagicMock(return_value=True)

        component2 = MagicMock()
        component2.initialize = MagicMock(return_value=True)
        component2.shutdown = MagicMock(return_value=True)

        # Регистрируем компоненты
        registry.register("component1", component1)
        registry.register("component2", component2)

        # Инициализируем систему
        init_result = system_initializer.initialize()
        assert init_result is not False  # Не должно быть False
        assert system_initializer.is_initialized() is True

        # Проверяем, что методы initialize были вызваны
        component1.initialize.assert_called_once()
        component2.initialize.assert_called_once()

        # Завершаем работу системы
        shutdown_result = system_initializer.shutdown()
        assert shutdown_result is True
        assert system_initializer.is_initialized() is False

        # Проверяем, что методы shutdown были вызваны
        component1.shutdown.assert_called_once()
        component2.shutdown.assert_called_once()
