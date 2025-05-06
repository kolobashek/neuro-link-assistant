class SystemInitializer:
    """
    Инициализатор системы.
    Отвечает за инициализацию и завершение работы системы.
    """
    
    def __init__(self, registry):
        """
        Инициализация инициализатора системы.
        
        Args:
            registry (ComponentRegistry): Реестр компонентов системы
        """
        self._registry = registry
        self._initialized = False
    
    def initialize(self):
        """
        Инициализирует систему.
        
        Returns:
            bool: True в случае успешной инициализации, иначе False
        """
        try:
            # Проверяем наличие необходимых компонентов
            required_components = ["error_handler", "plugin_manager"]
            for component_name in required_components:
                if not self._registry.has(component_name):
                    print(f"Missing required component: {component_name}")
                    return False
            
            # Получаем обработчик ошибок
            error_handler = self._registry.get("error_handler")
            
            # Получаем менеджер плагинов
            plugin_manager = self._registry.get("plugin_manager")
            
            # Загружаем плагины
            plugin_manager.load_plugins()
            
            # Отмечаем систему как инициализированную
            self._initialized = True
            
            return True
        except Exception as e:
            # Если есть обработчик ошибок, используем его
            try:
                error_handler = self._registry.get("error_handler", None)
                if error_handler:
                    error_handler.handle_error(e, "Error initializing system")
            except:
                # Если не удалось обработать ошибку, просто выводим ее
                print(f"Error initializing system: {e}")
            
            return False
    
    def shutdown(self):
        """
        Завершает работу системы.
        
        Returns:
            bool: True в случае успешного завершения, иначе False
        """
        try:
            # Получаем менеджер плагинов
            plugin_manager = self._registry.get("plugin_manager")
            
            # Выгружаем плагины
            plugin_manager.unload_plugins()
            
            # Отмечаем систему как неинициализированную
            self._initialized = False
            
            return True
        except Exception as e:
            # Если есть обработчик ошибок, используем его
            try:
                error_handler = self._registry.get("error_handler", None)
                if error_handler:
                    error_handler.handle_error(e, "Error shutting down system")
            except:
                # Если не удалось обработать ошибку, просто выводим ее
                print(f"Error shutting down system: {e}")
            
            return False
    
    def is_initialized(self):
        """
        Проверяет, инициализирована ли система.
        
        Returns:
            bool: True, если система инициализирована, иначе False
        """
        return self._initialized
    
    def register_core_components(self):
        """
        Регистрирует основные компоненты системы.
        
        Returns:
            bool: True в случае успешной регистрации
        """
        try:
            # Создаем и регистрируем обработчик ошибок
            from core.error_handler import ErrorHandler
            error_handler = ErrorHandler()
            self.registry.register("error_handler", error_handler)
            
            # Создаем и регистрируем менеджер плагинов
            from core.plugin_manager import PluginManager
            plugin_manager = PluginManager()
            self.registry.register("plugin_manager", plugin_manager)
            
            # Создаем и регистрируем менеджер окон
            from core.windows.window_manager import WindowManager
            window_manager = WindowManager()
            self.registry.register("window_manager", window_manager)
            
            # Создаем и регистрируем менеджер процессов
            from core.windows.process_manager import ProcessManager
            process_manager = ProcessManager()
            self.registry.register("process_manager", process_manager)
            
            # Создаем и регистрируем системную информацию
            from core.windows.system_info import SystemInfo
            system_info = SystemInfo()
            self.registry.register("system_info", system_info)
            
            return True
        except Exception as e:
            print(f"Error registering core components: {e}")
            return False