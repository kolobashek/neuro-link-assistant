import pytest
from unittest.mock import MagicMock, patch
import os
import sys
from core.plugin_manager import PluginManager

class TestPluginManager:
    """Тесты для менеджера плагинов"""
    
    @pytest.fixture
    def plugin_manager(self):
        """Фикстура для создания экземпляра PluginManager"""
        # Создаем мок для реестра компонентов
        registry = MagicMock()
        
        # Создаем мок для обработчика ошибок
        error_handler = MagicMock()
        
        # Настраиваем реестр для возврата обработчика ошибок
        registry.get.return_value = error_handler
        
        # Создаем менеджер плагинов с моком реестра
        manager = PluginManager(registry)
        
        # Заменяем директорию плагинов на временную
        manager.plugins_dir = os.path.join(os.path.dirname(__file__), 'test_plugins')
        
        # Создаем временную директорию для тестов, если она не существует
        os.makedirs(manager.plugins_dir, exist_ok=True)
        
        # Возвращаем менеджер плагинов
        yield manager
        
        # Удаляем временную директорию после тестов
        if os.path.exists(manager.plugins_dir):
            for file in os.listdir(manager.plugins_dir):
                os.remove(os.path.join(manager.plugins_dir, file))
            os.rmdir(manager.plugins_dir)
    
    @pytest.fixture
    def error_handler(self, plugin_manager):
        """Фикстура для получения мока обработчика ошибок"""
        return plugin_manager.error_handler
    
    def test_discover_plugins(self, plugin_manager):
        """Тест обнаружения плагинов"""
        # Создаем тестовые файлы плагинов
        with open(os.path.join(plugin_manager.plugins_dir, 'test_plugin1.py'), 'w') as f:
            f.write('# Test plugin 1')
        
        with open(os.path.join(plugin_manager.plugins_dir, 'test_plugin2.py'), 'w') as f:
            f.write('# Test plugin 2')
        
        # Создаем файл, который не должен быть обнаружен
        with open(os.path.join(plugin_manager.plugins_dir, '__init__.py'), 'w') as f:
            f.write('# Init file')
        
        # Обнаруживаем плагины
        plugins = plugin_manager.discover_plugins()
        
        # Проверяем, что обнаружены только плагины
        assert len(plugins) == 2
        assert 'test_plugin1.py' in plugins
        assert 'test_plugin2.py' in plugins
        assert '__init__.py' not in plugins
    
    def test_discover_plugins_no_directory(self, plugin_manager):
        """Тест обнаружения плагинов при отсутствии директории"""
        # Удаляем директорию плагинов
        if os.path.exists(plugin_manager.plugins_dir):
            for file in os.listdir(plugin_manager.plugins_dir):
                os.remove(os.path.join(plugin_manager.plugins_dir, file))
            os.rmdir(plugin_manager.plugins_dir)
        
        # Обнаруживаем плагины
        plugins = plugin_manager.discover_plugins()
        
        # Проверяем, что список плагинов пуст
        assert len(plugins) == 0
    
    @patch('importlib.import_module')
    def test_load_plugin(self, mock_import, plugin_manager):
        """Тест загрузки плагина"""
        # Создаем класс плагина
        class TestPlugin:
            def setup(self):
                pass
        
        # Создаем мок-модуль плагина
        mock_module = MagicMock()
        mock_module.TestPlugin = TestPlugin
        mock_import.return_value = mock_module
        
        # Загружаем плагин
        result = plugin_manager.load_plugin('test_plugin')
        
        # Проверяем, что плагин был импортирован
        mock_import.assert_called_once_with('plugins.test_plugin')
        
        # Проверяем, что плагин был загружен
        assert result is not None
        assert isinstance(result, TestPlugin)
        assert 'test_plugin' in plugin_manager.plugins
    
    @patch('importlib.import_module')
    def test_load_plugin_error(self, mock_import, plugin_manager, error_handler):
        """Тест загрузки плагина с ошибкой"""
        # Настраиваем мок для генерации исключения
        mock_import.side_effect = ImportError("Test import error")
        
        # Загружаем плагин
        result = plugin_manager.load_plugin('test_plugin')
        
        # Проверяем, что ошибка была обработана
        error_handler.handle_error.assert_called_once()
        
        # Проверяем, что результат None
        assert result is None
    
    @patch('importlib.import_module')
    def test_load_plugin_no_setup(self, mock_import, plugin_manager, error_handler):
        """Тест загрузки плагина без метода setup"""
        # Создаем мок-модуль плагина без метода setup
        mock_module = MagicMock()
        mock_import.return_value = mock_module
        
        # Загружаем плагин
        result = plugin_manager.load_plugin('test_plugin')
        
        # Проверяем, что ошибка была обработана
        error_handler.handle_error.assert_called_once()
        
        # Проверяем, что результат None
        assert result is None
    
    def test_load_plugins(self, plugin_manager):
        """Тест загрузки всех плагинов"""
        # Создаем тестовые файлы плагинов
        with open(os.path.join(plugin_manager.plugins_dir, 'test_plugin1.py'), 'w') as f:
            f.write('# Test plugin 1')
        
        with open(os.path.join(plugin_manager.plugins_dir, 'test_plugin2.py'), 'w') as f:
            f.write('# Test plugin 2')
        
        # Заменяем метод load_plugin на мок
        plugin_manager.load_plugin = MagicMock(return_value=True)
        
        # Загружаем все плагины
        loaded_count = plugin_manager.load_plugins()
        
        # Проверяем, что все плагины были загружены
        assert loaded_count == 2
        assert plugin_manager.load_plugin.call_count == 2
    
    def test_unload_plugin(self, plugin_manager):
        """Тест выгрузки плагина"""
        # Создаем тестовый плагин
        plugin = MagicMock()
        plugin.teardown = MagicMock()
        
        # Добавляем плагин в словарь загруженных плагинов
        plugin_manager.plugins['test_plugin'] = plugin
        
        # Выгружаем плагин
        result = plugin_manager.unload_plugin('test_plugin')
        
        # Проверяем, что плагин был выгружен
        assert result is True
        assert 'test_plugin' not in plugin_manager.plugins
        plugin.teardown.assert_called_once()
    
    def test_unload_plugin_not_loaded(self, plugin_manager, error_handler):
        """Тест выгрузки незагруженного плагина"""
        # Выгружаем несуществующий плагин
        result = plugin_manager.unload_plugin('nonexistent_plugin')
        
        # Проверяем, что результат False
        assert result is False
        
        # Проверяем, что было залогировано предупреждение
        error_handler.handle_warning.assert_called_once()
    
    def test_unload_plugins(self, plugin_manager):
        """Тест выгрузки всех плагинов"""
        # Создаем тестовые плагины
        plugin1 = MagicMock()
        plugin2 = MagicMock()
        
        # Добавляем плагины в словарь загруженных плагинов
        plugin_manager.plugins['test_plugin1'] = plugin1
        plugin_manager.plugins['test_plugin2'] = plugin2
        
        # Заменяем метод unload_plugin на мок
        plugin_manager.unload_plugin = MagicMock(return_value=True)
        
        # Выгружаем все плагины
        unloaded_count = plugin_manager.unload_plugins()
        
        # Проверяем, что все плагины были выгружены
        assert unloaded_count == 2
        assert plugin_manager.unload_plugin.call_count == 2