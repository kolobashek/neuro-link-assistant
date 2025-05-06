import pytest
import os
import sys
from unittest.mock import patch, MagicMock, mock_open
from core.plugin_manager import PluginManager  # Добавьте эту строку

class TestPluginManager:
    """Тесты менеджера плагинов"""
    
    @pytest.fixture
    def registry(self):
        """Создает мок реестра компонентов"""
        registry = MagicMock()
        return registry
    
    @pytest.fixture
    def error_handler(self):
        """Создает мок обработчика ошибок"""
        error_handler = MagicMock()
        return error_handler
    
    @pytest.fixture
    def plugin_manager(self, registry, error_handler):
        """Создает экземпляр PluginManager с мок-зависимостями"""
        from core.plugin_manager import PluginManager
        
        # Настраиваем реестр для возврата мок-обработчика ошибок
        registry.get.return_value = error_handler
        
        return PluginManager(registry)
    
    @patch('os.path.exists', return_value=True)
    @patch('os.listdir')
    def test_discover_plugins(self, mock_listdir, mock_exists, plugin_manager):
        """Тест обнаружения плагинов"""
        # Настраиваем мок для имитации списка файлов в директории плагинов
        mock_listdir.return_value = [
            'plugin1.py',
            'plugin2.py',
            'not_a_plugin.txt',
            '__pycache__'
        ]
        
        # Обнаруживаем плагины
        plugins = plugin_manager.discover_plugins()
        
        # Проверяем, что найдены только файлы Python
        assert len(plugins) == 2
        assert 'plugin1.py' in plugins
        assert 'plugin2.py' in plugins
        assert 'not_a_plugin.txt' not in plugins
        assert '__pycache__' not in plugins
    
    @patch('os.path.exists', return_value=False)
    def test_discover_plugins_no_directory(self, mock_exists, plugin_manager):
        """Тест обнаружения плагинов при отсутствии директории"""
        # Обнаруживаем плагины
        plugins = plugin_manager.discover_plugins()
        
        # Проверяем, что список плагинов пуст
        assert len(plugins) == 0
    
    @patch('importlib.import_module')
    def test_load_plugin(self, mock_import, plugin_manager):
        """Тест загрузки плагина"""
        # Создаем мок-модуль плагина
        mock_plugin = MagicMock()
        mock_plugin.setup = MagicMock()
        mock_import.return_value = mock_plugin
        
        # Загружаем плагин
        result = plugin_manager.load_plugin('test_plugin')
        
        # Проверяем, что плагин был импортирован и инициализирован
        mock_import.assert_called_once_with('plugins.test_plugin')
        mock_plugin.setup.assert_called_once()
        assert result is True
    
    @patch('importlib.import_module')
    def test_load_plugin_error(self, mock_import, plugin_manager, error_handler):
        """Тест загрузки плагина с ошибкой"""
        # Настраиваем мок для генерации исключения
        mock_import.side_effect = ImportError("Test import error")
        
        # Загружаем плагин
        result = plugin_manager.load_plugin('test_plugin')
        
        # Проверяем, что ошибка была обработана
        error_handler.handle_error.assert_called_once()
        assert result is False
    
    @patch('importlib.import_module')
    def test_load_plugin_no_setup(self, mock_import, plugin_manager, error_handler):
        """Тест загрузки плагина без метода setup"""
        # Создаем мок-модуль плагина без метода setup
        mock_plugin = MagicMock(spec=[])
        mock_import.return_value = mock_plugin
        
        # Загружаем плагин
        result = plugin_manager.load_plugin('test_plugin')
        
        # Проверяем, что ошибка была обработана
        error_handler.handle_warning.assert_called_once()
        assert result is False
    
    @patch('os.path.exists', return_value=True)
    @patch('os.listdir')
    @patch.object(PluginManager, 'load_plugin')
    def test_load_plugins(self, mock_load_plugin, mock_listdir, mock_exists, plugin_manager):
        """Тест загрузки всех плагинов"""
        # Настраиваем мок для имитации списка файлов в директории плагинов
        mock_listdir.return_value = [
            'plugin1.py',
            'plugin2.py',
            'not_a_plugin.txt'
        ]
        
        # Настраиваем мок для имитации успешной загрузки плагинов
        mock_load_plugin.return_value = True
        
        # Загружаем все плагины
        plugin_manager.load_plugins()
        
        # Проверяем, что метод load_plugin был вызван для каждого плагина
        assert mock_load_plugin.call_count == 2
        mock_load_plugin.assert_any_call('plugin1')
        mock_load_plugin.assert_any_call('plugin2')
    
    @patch.dict(sys.modules, {'plugins.test_plugin': MagicMock()})
    def test_unload_plugin(self, plugin_manager):
        """Тест выгрузки плагина"""
        # Создаем мок-модуль плагина
        mock_plugin = MagicMock()
        mock_plugin.teardown = MagicMock()
        
        # Добавляем плагин в список загруженных плагинов
        plugin_manager.loaded_plugins['test_plugin'] = mock_plugin
        
        # Выгружаем плагин
        result = plugin_manager.unload_plugin('test_plugin')
        
        # Проверяем, что метод teardown был вызван
        mock_plugin.teardown.assert_called_once()
        assert result is True
        assert 'test_plugin' not in plugin_manager.loaded_plugins
    
    def test_unload_plugin_not_loaded(self, plugin_manager, error_handler):
        """Тест выгрузки незагруженного плагина"""
        # Выгружаем несуществующий плагин
        result = plugin_manager.unload_plugin('nonexistent_plugin')
        
        # Проверяем, что было сгенерировано предупреждение
        error_handler.handle_warning.assert_called_once()
        assert result is False
    
    def test_unload_plugins(self, plugin_manager):
        """Тест выгрузки всех плагинов"""
        # Создаем мок-плагины
        plugin1 = MagicMock()
        plugin1.teardown = MagicMock()
        
        plugin2 = MagicMock()
        plugin2.teardown = MagicMock()
        
        # Добавляем плагины в список загруженных плагинов
        plugin_manager.loaded_plugins = {
            'plugin1': plugin1,
            'plugin2': plugin2
        }
        
        # Выгружаем все плагины
        plugin_manager.unload_plugins()
        
        # Проверяем, что метод teardown был вызван для каждого плагина
        plugin1.teardown.assert_called_once()
        plugin2.teardown.assert_called_once()
        assert len(plugin_manager.loaded_plugins) == 0