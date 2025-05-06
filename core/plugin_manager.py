import os
import importlib.util
import inspect

class PluginManager:
    """
    Менеджер плагинов.
    Предоставляет функции для загрузки и управления плагинами.
    """
    
    def __init__(self, plugin_dir="plugins"):
        """
        Инициализация менеджера плагинов.
        
        Args:
            plugin_dir (str): Директория с плагинами
        """
        self.plugin_dir = plugin_dir
        self.plugins = {}
        self.active_plugins = {}
        
        # Создаем директорию для плагинов, если она не существует
        if not os.path.exists(plugin_dir):
            os.makedirs(plugin_dir)
    
    def discover_plugins(self):
        """
        Обнаруживает доступные плагины в директории плагинов.
        
        Returns:
            list: Список обнаруженных плагинов
        """
        discovered_plugins = []
        
        # Проверяем, что директория существует
        if not os.path.exists(self.plugin_dir):
            return discovered_plugins
        
        # Ищем Python-файлы в директории плагинов
        for filename in os.listdir(self.plugin_dir):
            if filename.endswith(".py") and not filename.startswith("__"):
                plugin_path = os.path.join(self.plugin_dir, filename)
                plugin_name = os.path.splitext(filename)[0]
                
                discovered_plugins.append({
                    "name": plugin_name,
                    "path": plugin_path
                })
        
        return discovered_plugins
    
    def load_plugin(self, plugin_info):
        """
        Загружает плагин.
        
        Args:
            plugin_info (dict): Информация о плагине (name, path)
            
        Returns:
            bool: True в случае успешной загрузки
        """
        try:
            plugin_name = plugin_info["name"]
            plugin_path = plugin_info["path"]
            
            # Проверяем, не загружен ли уже плагин
            if plugin_name in self.plugins:
                print(f"Plugin {plugin_name} is already loaded")
                return False
            
            # Загружаем модуль плагина
            spec = importlib.util.spec_from_file_location(plugin_name, plugin_path)
            plugin_module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(plugin_module)
            
            # Ищем класс плагина
            plugin_class = None
            for name, obj in inspect.getmembers(plugin_module):
                if inspect.isclass(obj) and hasattr(obj, "plugin_info"):
                    plugin_class = obj
                    break
            
            if plugin_class is None:
                print(f"No valid plugin class found in {plugin_name}")
                return False
            
            # Создаем экземпляр плагина
            plugin_instance = plugin_class()
            
            # Сохраняем информацию о плагине
            self.plugins[plugin_name] = {
                "instance": plugin_instance,
                "info": plugin_instance.plugin_info,
                "module": plugin_module
            }
            
            print(f"Plugin {plugin_name} loaded successfully")
            return True
        except Exception as e:
            print(f"Error loading plugin {plugin_info['name']}: {e}")
            return False
    
    def load_all_plugins(self):
        """
        Загружает все доступные плагины.
        
        Returns:
            int: Количество успешно загруженных плагинов
        """
        discovered_plugins = self.discover_plugins()
        loaded_count = 0
        
        for plugin_info in discovered_plugins:
            if self.load_plugin(plugin_info):
                loaded_count += 1
        
        return loaded_count
    
    def activate_plugin(self, plugin_name):
        """
        Активирует плагин.
        
        Args:
            plugin_name (str): Имя плагина
            
        Returns:
            bool: True в случае успешной активации
        """
        if plugin_name not in self.plugins:
            print(f"Plugin {plugin_name} is not loaded")
            return False
        
        if plugin_name in self.active_plugins:
            print(f"Plugin {plugin_name} is already active")
            return True
        
        plugin = self.plugins[plugin_name]
        
        try:
            # Вызываем метод активации плагина
            if hasattr(plugin["instance"], "activate"):
                plugin["instance"].activate()
            
            # Отмечаем плагин как активный
            self.active_plugins[plugin_name] = plugin
            
            print(f"Plugin {plugin_name} activated successfully")
            return True
        except Exception as e:
            print(f"Error activating plugin {plugin_name}: {e}")
            return False
    
    def deactivate_plugin(self, plugin_name):
        """
        Деактивирует плагин.
        
        Args:
            plugin_name (str): Имя плагина
            
        Returns:
            bool: True в случае успешной деактивации
        """
        if plugin_name not in self.active_plugins:
            print(f"Plugin {plugin_name} is not active")
            return False
        
        plugin = self.active_plugins[plugin_name]
        
        try:
            # Вызываем метод деактивации плагина
            if hasattr(plugin["instance"], "deactivate"):
                plugin["instance"].deactivate()
            
            # Удаляем плагин из списка активных
            del self.active_plugins[plugin_name]
            
            print(f"Plugin {plugin_name} deactivated successfully")
            return True
        except Exception as e:
            print(f"Error deactivating plugin {plugin_name}: {e}")
            return False
    
    def get_plugin_info(self, plugin_name):
        """
        Получает информацию о плагине.
        
        Args:
            plugin_name (str): Имя плагина
            
        Returns:
            dict: Информация о плагине или None, если плагин не найден
        """
        if plugin_name not in self.plugins:
            return None
        
        return self.plugins[plugin_name]["info"]
    
    def get_all_plugins(self):
        """
        Получает информацию о всех загруженных плагинах.
        
        Returns:
            dict: Словарь с информацией о плагинах
        """
        result = {}
        
        for plugin_name, plugin_data in self.plugins.items():
            result[plugin_name] = {
                "info": plugin_data["info"],
                "active": plugin_name in self.active_plugins
            }
        
        return result
    
    def unload_plugin(self, plugin_name):
        """
        Выгружает плагин.
        
        Args:
            plugin_name (str): Имя плагина
            
        Returns:
            bool: True в случае успешной выгрузки
        """
        if plugin_name not in self.plugins:
            print(f"Plugin {plugin_name} is not loaded")
            return False
        
        # Деактивируем плагин, если он активен
        if plugin_name in self.active_plugins:
            self.deactivate_plugin(plugin_name)
        
        # Удаляем плагин из списка загруженных
        del self.plugins[plugin_name]
        
        print(f"Plugin {plugin_name} unloaded successfully")
        return True