import os
import importlib
import sys

class PluginManager:
    """
    Менеджер плагинов.
    Предоставляет функционал для загрузки и управления плагинами.
    """
    
    def __init__(self, registry, plugins_dir='plugins'):
        self.registry = registry
        self.plugins_dir = plugins_dir
        self.error_handler = registry.get('error_handler')
        self.plugins = {}
    
    def discover_plugins(self):
        """Обнаруживает доступные плагины"""
        try:
            if not os.path.exists(self.plugins_dir):
                os.makedirs(self.plugins_dir)
                
            plugin_names = []
            
            # Ищем все директории в plugins_dir, содержащие __init__.py
            for item in os.listdir(self.plugins_dir):
                plugin_path = os.path.join(self.plugins_dir, item)
                if os.path.isdir(plugin_path) and os.path.exists(os.path.join(plugin_path, '__init__.py')):
                    plugin_names.append(item)
            
            return plugin_names
        except Exception as e:
            if self.error_handler:
                self.error_handler.log_error("Ошибка при обнаружении плагинов", e)
            return []
    
    def load_plugin(self, plugin_name):
        """Загружает плагин"""
        try:
            if plugin_name in self.plugins:
                return self.plugins[plugin_name]
            
            # Добавляем директорию плагинов в sys.path, если её там нет
            plugins_abs_path = os.path.abspath(self.plugins_dir)
            if plugins_abs_path not in sys.path:
                sys.path.append(plugins_abs_path)
            
            # Импортируем модуль плагина
            plugin_module = importlib.import_module(f"{plugin_name}")
            
            # Создаем экземпляр плагина
            plugin_class = getattr(plugin_module, plugin_name.capitalize())
            plugin_instance = plugin_class(self.registry)
            
            # Регистрируем плагин
            self.plugins[plugin_name] = plugin_instance
            self.registry.register(f"plugin_{plugin_name}", plugin_instance)
            
            if self.error_handler:
                self.error_handler.log_info(f"Плагин {plugin_name} успешно загружен")
            return plugin_instance
        except Exception as e:
            if self.error_handler:
                self.error_handler.log_error(f"Ошибка при загрузке плагина {plugin_name}", e)
            return None