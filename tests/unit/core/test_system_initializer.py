import pytest
from unittest.mock import MagicMock, patch

class TestSystemInitializer:
    """Тесты инициализатора системы"""
    
    @pytest.fixture
    def registry(self):
        """Создает мок реестра компонентов"""
        registry = MagicMock()
        registry.get.return_value = MagicMock()
        registry.has.return_value = True
        return registry
    
    @pytest.fixture
    def initializer(self, registry):
        """Создает экземпляр SystemInitializer с мок-реестром"""
        from core.system_initializer import SystemInitializer
        return SystemInitializer(registry)
    
    def test_initialize_system(self, initializer, registry):
        """Тест инициализации системы"""
        # Создаем мок-компоненты
        error_handler = MagicMock()
        plugin_manager = MagicMock()
        
        # Настраиваем реестр для возврата мок-компонентов
        registry.get.side_effect = lambda name, default=None: {
            "error_handler": error_handler,
            "plugin_manager": plugin_manager
        }.get(name, default)
        
        # Инициализируем систему
        result = initializer.initialize()
        
        assert result is True
        
        # Проверяем, что компоненты были получены из реестра
        registry.get.assert_any_call("error_handler")
        registry.get.assert_any_call("plugin_manager")
        
        # Проверяем, что плагины были загружены
        plugin_manager.load_plugins.assert_called_once()
    
    def test_initialize_system_with_missing_components(self, initializer, registry):
        """Тест инициализации системы с отсутствующими компонентами"""
        # Настраиваем реестр для имитации отсутствия компонентов
        registry.has.return_value = False
        
        # Инициализируем систему
        result = initializer.initialize()
        
        assert result is False
    
    def test_initialize_system_with_error(self, initializer, registry):
        """Тест инициализации системы с ошибкой"""
        # Создаем мок-компоненты
        error_handler = MagicMock()
        plugin_manager = MagicMock()
        
        # Настраиваем реестр для возврата мок-компонентов
        registry.get.side_effect = lambda name, default=None: {
            "error_handler": error_handler,
            "plugin_manager": plugin_manager
        }.get(name, default)
        
        # Настраиваем плагин-менеджер для генерации исключения
        plugin_manager.load_plugins.side_effect = Exception("Test error")
        
        # Инициализируем систему
        result = initializer.initialize()
        
        assert result is False
        
        # Проверяем, что ошибка была обработана
        error_handler.handle_error.assert_called_once()
    
    def test_shutdown_system(self, initializer, registry):
        """Тест завершения работы системы"""
        # Создаем мок-компоненты
        plugin_manager = MagicMock()
        
        # Настраиваем реестр для возврата мок-компонентов
        registry.get.side_effect = lambda name, default=None: {
            "plugin_manager": plugin_manager
        }.get(name, default)
        
        # Завершаем работу системы
        result = initializer.shutdown()
        
        assert result is True
        
        # Проверяем, что плагины были выгружены
        plugin_manager.unload_plugins.assert_called_once()
    
    def test_shutdown_system_with_error(self, initializer, registry):
        """Тест завершения работы системы с ошибкой"""
        # Создаем мок-компоненты
        error_handler = MagicMock()
        plugin_manager = MagicMock()
        
        # Настраиваем реестр для возврата мок-компонентов
        registry.get.side_effect = lambda name, default=None: {
            "error_handler": error_handler,
            "plugin_manager": plugin_manager
        }.get(name, default)
        
        # Настраиваем плагин-менеджер для генерации исключения
        plugin_manager.unload_plugins.side_effect = Exception("Test error")
        
        # Завершаем работу системы
        result = initializer.shutdown()
        
        assert result is False
        
        # Проверяем, что ошибка была обработана
        error_handler.handle_error.assert_called_once()