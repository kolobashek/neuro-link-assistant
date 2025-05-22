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
            except Exception as e:
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
            except Exception as e:
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
            try:
                from core.common.error_handler import ErrorHandler

                error_handler = ErrorHandler()
                self._registry.register("error_handler", error_handler)
            except ImportError:
                # Пробуем альтернативный путь импорта
                try:
                    from core.common.error_handler import ErrorHandler

                    error_handler = ErrorHandler()
                    self._registry.register("error_handler", error_handler)
                except ImportError:
                    print("Не удалось импортировать ErrorHandler")

            # Создаем и регистрируем менеджер плагинов
            try:
                from core.plugin_manager import PluginManager

                plugin_manager = PluginManager()
                self._registry.register("plugin_manager", plugin_manager)
            except ImportError:
                print("Не удалось импортировать PluginManager")

            # Регистрируем дополнительные компоненты, если они доступны
            self._register_optional_components()

            return True
        except Exception as e:
            print(f"Error registering core components: {e}")
            return False

    def _register_optional_components(self):
        """
        Регистрирует дополнительные компоненты, если они доступны.
        """
        # Список возможных компонентов для регистрации
        optional_components = [
            # (имя_импорта, имя_класса, имя_регистрации)
            ("core.windows.system_info", "SystemInfo", "system_info"),
        ]

        for import_path, class_name, register_name in optional_components:
            try:
                module = __import__(import_path, fromlist=[class_name])
                component_class = getattr(module, class_name)
                component = component_class()
                self._registry.register(register_name, component)
            except (ImportError, AttributeError) as e:
                print(f"Не удалось зарегистрировать компонент {register_name}: {e}")
