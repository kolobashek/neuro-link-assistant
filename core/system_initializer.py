class SystemInitializer:
    """
    Инициализатор системы.
    Отвечает за инициализацию и настройку компонентов системы.
    """
    
    def __init__(self, registry):
        """
        Инициализация инициализатора системы.
        
        Args:
            registry: Реестр компонентов
        """
        self.registry = registry
        self.initialized = False
    
    def initialize(self, config=None):
        """
        Инициализирует систему.
        
        Args:
            config (dict, optional): Конфигурация системы
            
        Returns:
            bool: True в случае успешной инициализации
        """
        if self.initialized:
            print("System is already initialized")
            return True
        
        try:
            # Проверяем наличие необходимых компонентов
            required_components = ["error_handler", "plugin_manager"]
            for component_name in required_components:
                if not self.registry.has(component_name):
                    print(f"Required component {component_name} is not registered")
                    return False
            
            # Получаем компоненты
            error_handler = self.registry.get("error_handler")
            plugin_manager = self.registry.get("plugin_manager")
            
            # Логируем начало инициализации
            error_handler.log_info("Starting system initialization")
            
            # Загружаем плагины
            plugin_count = plugin_manager.load_all_plugins()
            error_handler.log_info(f"Loaded {plugin_count} plugins")
            
            # Активируем основные плагины
            if config and "active_plugins" in config:
                for plugin_name in config["active_plugins"]:
                    if plugin_manager.activate_plugin(plugin_name):
                        error_handler.log_info(f"Activated plugin: {plugin_name}")
                    else:
                        error_handler.log_warning(f"Failed to activate plugin: {plugin_name}")
            
            # Отмечаем систему как инициализированную
            self.initialized = True
            
            error_handler.log_info("System initialization completed successfully")
            return True
        except Exception as e:
            if self.registry.has("error_handler"):
                error_handler = self.registry.get("error_handler")
                error_handler.log_error(f"Error during system initialization: {e}", exc_info=e)
            else:
                print(f"Error during system initialization: {e}")
            
            return False
    
    def shutdown(self):
        """
        Завершает работу системы.
        
        Returns:
            bool: True в случае успешного завершения
        """
        if not self.initialized:
            print("System is not initialized")
            return True
        
        try:
            # Проверяем наличие необходимых компонентов
            if not self.registry.has("error_handler") or not self.registry.has("plugin_manager"):
                print("Required components are not registered")
                return False
            
            # Получаем компоненты
            error_handler = self.registry.get("error_handler")
            plugin_manager = self.registry.get("plugin_manager")
            
            # Логируем начало завершения работы
            error_handler.log_info("Starting system shutdown")
            
            # Деактивируем все активные плагины
            active_plugins = list(plugin_manager.active_plugins.keys())
            for plugin_name in active_plugins:
                if plugin_manager.deactivate_plugin(plugin_name):
                    error_handler.log_info(f"Deactivated plugin: {plugin_name}")
                else:
                    error_handler.log_warning(f"Failed to deactivate plugin: {plugin_name}")
            
            # Отмечаем систему как не инициализированную
            self.initialized = False
            
            error_handler.log_info("System shutdown completed successfully")
            return True
        except Exception as e:
            if self.registry.has("error_handler"):
                error_handler = self.registry.get("error_handler")
                error_handler.log_error(f"Error during system shutdown: {e}", exc_info=e)
            else:
                print(f"Error during system shutdown: {e}")
            
            return False
    
    def is_initialized(self):
        """
        Проверяет, инициализирована ли система.
        
        Returns:
            bool: True, если система инициализирована
        """
        return self.initialized
    
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