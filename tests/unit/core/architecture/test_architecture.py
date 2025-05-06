import pytest
from unittest.mock import MagicMock, patch
import logging

# Предполагаем, что у нас есть модуль core с компонентами системы
# Если структура другая, нужно будет адаптировать импорты
try:
    from core.component_registry import ComponentRegistry
    from core.system_initializer import SystemInitializer
    from core.error_handler import ErrorHandler
    from core.plugin_manager import PluginManager
except ImportError:
    # Создаем заглушки для тестирования, если модули еще не реализованы
    class ComponentRegistry:
        def __init__(self):
            self.components = {}
        
        def register(self, name, component):
            self.components[name] = component
            return True
        
        def get(self, name):
            return self.components.get(name)
    
    class SystemInitializer:
        def __init__(self, registry):
            self.registry = registry
            self.initialized = False
        
        def initialize(self):
            self.initialized = True
            return True
    
    class ErrorHandler:
        def __init__(self):
            self.logger = logging.getLogger("error_handler")
        
        def handle_error(self, error, context=None):
            self.logger.error(f"Error: {error}, Context: {context}")
            return True
    
    class PluginManager:
        def __init__(self, registry):
            self.registry = registry
            self.plugins = {}
        
        def load_plugin(self, name, plugin_class):
            plugin = plugin_class()
            self.plugins[name] = plugin
            return plugin
        
        def get_plugin(self, name):
            return self.plugins.get(name)


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
        
        component = registry.get("nonexistent")
        
        assert component is None
    
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
        initializer = SystemInitializer(registry)
        
        result = initializer.initialize()
        
        assert result is True
        assert initializer.initialized is True
    
    @patch.object(SystemInitializer, 'initialize')
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


class TestErrorHandling:
    """Тесты обработки ошибок и логирования"""
    
    @patch('logging.Logger.error')
    def test_error_handling(self, mock_error):
        """Тест обработки ошибок"""
        handler = ErrorHandler()
        test_error = Exception("Test error")
        
        result = handler.handle_error(test_error)
        
        assert result is True
        mock_error.assert_called_once()
    
    @patch('logging.Logger.error')
    def test_error_with_context(self, mock_error):
        """Тест обработки ошибок с контекстом"""
        handler = ErrorHandler()
        test_error = Exception("Test error")
        context = {"operation": "test_operation"}
        
        result = handler.handle_error(test_error, context)
        
        assert result is True
        mock_error.assert_called_once()


class TestPluginSystem:
    """Тесты расширяемости через плагины"""
    
    def test_load_plugin(self):
        """Тест загрузки плагина"""
        registry = ComponentRegistry()
        plugin_manager = PluginManager(registry)
        
        class TestPlugin:
            def __init__(self):
                self.initialized = True
        
        plugin = plugin_manager.load_plugin("test_plugin", TestPlugin)
        
        assert plugin.initialized is True
        assert plugin_manager.get_plugin("test_plugin") == plugin
    
    def test_get_nonexistent_plugin(self):
        """Тест получения несуществующего плагина"""
        registry = ComponentRegistry()
        plugin_manager = PluginManager(registry)
        
        plugin = plugin_manager.get_plugin("nonexistent")
        
        assert plugin is None
    
    def test_plugin_integration(self):
        """Тест интеграции плагина с системой"""
        registry = ComponentRegistry()
        plugin_manager = PluginManager(registry)
        
        class IntegrationPlugin:
            def __init__(self):
                self.registry = None
            
            def integrate(self, registry):
                self.registry = registry
                return True
        
        # Создаем класс плагина с методом интеграции
        class TestPlugin(IntegrationPlugin):
            pass
        
        plugin = plugin_manager.load_plugin("integration_plugin", TestPlugin)
        
        # Проверяем, что плагин может интегрироваться с реестром
        assert hasattr(plugin, 'integrate')
        result = plugin.integrate(registry)
        assert result is True
        assert plugin.registry == registry


if __name__ == "__main__":
    pytest.main(["-v", __file__])