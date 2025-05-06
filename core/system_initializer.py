from .component_registry import ComponentRegistry
from .error_handler import ErrorHandler

class SystemInitializer:
    """
    Инициализатор системы.
    Отвечает за инициализацию и настройку компонентов системы.
    """
    
    def __init__(self, config=None):
        self.config = config or {}
        self.registry = ComponentRegistry()
        
        # Создаем и регистрируем обработчик ошибок
        self.error_handler = ErrorHandler(log_file=self.config.get('log_file'))
        self.registry.register('error_handler', self.error_handler)
        
        # Регистрируем сам реестр компонентов
        self.registry.register('component_registry', self.registry)
    
    def initialize(self):
        """Инициализирует систему"""
        try:
            self.error_handler.log_info("Инициализация системы...")
            
            # Здесь будет код инициализации других компонентов
            
            self.error_handler.log_info("Система успешно инициализирована")
            return self.registry
        except Exception as e:
            self.error_handler.log_error("Ошибка при инициализации системы", e)
            raise