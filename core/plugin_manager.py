import importlib
import inspect
import os
import sys


class PluginManager:
    """
    Менеджер плагинов.
    Предоставляет функции для обнаружения, загрузки и выгрузки плагинов.
    """

    def __init__(self, registry=None):
        """
        Инициализация менеджера плагинов.

        Args:
            registry (ComponentRegistry, optional): Реестр компонентов системы
        """
        self.registry = registry
        self.plugins = {}  # Словарь загруженных плагинов
        self.plugins_dir = os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "plugins"
        )

        # Получаем обработчик ошибок из реестра, если он доступен
        self.error_handler = registry.get("ErrorHandler") if registry else None

    def discover_plugins(self):
        """
        Обнаруживает доступные плагины в директории плагинов.

        Returns:
            list: Список имен файлов плагинов
        """
        plugins = []

        # Проверяем, существует ли директория плагинов
        if not os.path.exists(self.plugins_dir):
            return plugins

        # Получаем список файлов в директории плагинов
        for filename in os.listdir(self.plugins_dir):
            # Проверяем, что это файл Python и не начинается с "__"
            if filename.endswith(".py") and not filename.startswith("__"):
                # Добавляем имя файла в список плагинов
                plugins.append(filename)

        return plugins

    def load_plugin(self, plugin_name):
        """
        Загружает плагин.

        Args:
            plugin_name (str): Имя плагина

        Returns:
            object: Экземпляр плагина или None в случае ошибки
        """
        try:
            # Формируем путь к модулю плагина
            module_name = f"plugins.{plugin_name}"

            # Импортируем модуль плагина
            module = importlib.import_module(module_name)

            # Ищем класс плагина в модуле
            plugin_class = None
            for name, obj in inspect.getmembers(module):
                if inspect.isclass(obj) and hasattr(obj, "setup"):
                    plugin_class = obj
                    break

            if not plugin_class:
                if self.error_handler:
                    self.error_handler.handle_error(
                        Exception(f"Plugin class not found in {plugin_name}"),
                        f"Plugin class not found in {plugin_name}",
                    )
                return None

            # Создаем экземпляр плагина
            plugin = plugin_class()

            # Вызываем метод setup, если он существует
            if hasattr(plugin, "setup"):
                plugin.setup()

            # Сохраняем плагин в словаре загруженных плагинов
            self.plugins[plugin_name] = plugin

            return plugin
        except Exception as e:
            if self.error_handler:
                self.error_handler.handle_error(e, f"Error loading plugin {plugin_name}")
            else:
                print(f"Error loading plugin {plugin_name}: {e}")
            return None

    def load_plugins(self):
        """
        Загружает все доступные плагины.

        Returns:
            int: Количество успешно загруженных плагинов
        """
        plugin_files = self.discover_plugins()
        loaded_count = 0

        for plugin_file in plugin_files:
            plugin_name = plugin_file[:-3]  # Убираем расширение .py
            if self.load_plugin(plugin_name):
                loaded_count += 1

        return loaded_count

    @property
    def loaded_plugins(self):
        """
        Возвращает словарь загруженных плагинов.

        Returns:
            dict: Словарь загруженных плагинов
        """
        return self.plugins

    @loaded_plugins.setter
    def loaded_plugins(self, value):
        """
        Устанавливает словарь загруженных плагинов.

        Args:
            value (dict): Новый словарь загруженных плагинов
        """
        self.plugins = value

    def unload_plugin(self, plugin_name):
        """
        Выгружает плагин.

        Args:
            plugin_name (str): Имя плагина

        Returns:
            bool: True в случае успешной выгрузки
        """
        # Проверяем, загружен ли плагин
        if plugin_name not in self.plugins:
            print(f"Plugin {plugin_name} is not loaded")
            if self.error_handler:
                self.error_handler.handle_warning(f"Plugin {plugin_name} is not loaded")
            return False

        try:
            # Получаем модуль плагина
            plugin = self.plugins[plugin_name]

            # Вызываем метод teardown, если он существует
            if hasattr(plugin, "teardown"):
                plugin.teardown()

            # Удаляем плагин из словаря загруженных плагинов
            del self.plugins[plugin_name]

            # Удаляем модуль из sys.modules, если он там есть
            module_name = f"plugins.{plugin_name}"
            if module_name in sys.modules:
                del sys.modules[module_name]

            return True
        except Exception as e:
            if self.error_handler:
                self.error_handler.handle_error(e, f"Error unloading plugin {plugin_name}")
            else:
                print(f"Error unloading plugin {plugin_name}: {e}")
            return False

    def unload_plugins(self):
        """
        Выгружает все загруженные плагины.

        Returns:
            int: Количество успешно выгруженных плагинов
        """
        plugin_names = list(self.plugins.keys())
        unloaded_count = 0

        for plugin_name in plugin_names:
            if self.unload_plugin(plugin_name):
                unloaded_count += 1

        return unloaded_count

    def get_plugin(self, plugin_name):
        """
        Получает плагин по имени.

        Args:
            plugin_name (str): Имя плагина

        Returns:
            object: Экземпляр плагина или None, если плагин не найден
        """
        return self.plugins.get(plugin_name)
