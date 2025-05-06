import logging
import traceback
import sys

class ErrorHandler:
    """
    Обработчик ошибок и логирования.
    Предоставляет функции для обработки ошибок и логирования сообщений.
    """
    
    def __init__(self, log_level=logging.INFO, log_file=None):
        """
        Инициализация обработчика ошибок.
        
        Args:
            log_level (int, optional): Уровень логирования
            log_file (str, optional): Путь к файлу логов
        """
        # Настраиваем логирование
        self.logger = logging.getLogger('neuro-link-assistant')
        self.logger.setLevel(log_level)
        
        # Создаем форматтер для логов
        formatter = logging.Formatter('%(levelname)-8s %(name)s:%(filename)s:%(lineno)d %(message)s')
        
        # Добавляем обработчик для вывода в консоль
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        self.logger.addHandler(console_handler)
        
        # Если указан файл логов, добавляем обработчик для записи в файл
        if log_file:
            file_handler = logging.FileHandler(log_file)
            file_handler.setFormatter(formatter)
            self.logger.addHandler(file_handler)
    
    def handle_error(self, exception, context=None, callback=None):
        """
        Обрабатывает исключение.
        
        Args:
            exception (Exception): Исключение для обработки
            context (str, optional): Контекст, в котором произошла ошибка
            callback (callable, optional): Функция обратного вызова для дополнительной обработки
            
        Returns:
            bool: False, так как произошла ошибка
        """
        # Форматируем сообщение об ошибке
        error_message = self.format_error_message(exception, context)
        
        # Логируем ошибку
        self.logger.error(error_message)
        logging.error(error_message)
        
        # Выводим ошибку в stderr
        print(f"ERROR: {error_message}", file=sys.stderr)
        
        # Если указан callback, вызываем его только с аргументом exception
        if callback:
            try:
                callback(exception)  # Изменено: передаем только exception
            except Exception as callback_error:
                self.logger.error(f"Error in error callback: {callback_error}")
        
        return False
    
    def handle_warning(self, message, context=None):
        """
        Обрабатывает предупреждение.
        
        Args:
            message (str): Сообщение предупреждения
            context (str, optional): Контекст, в котором произошло предупреждение
            
        Returns:
            bool: True, так как это только предупреждение
        """
        # Форматируем сообщение предупреждения
        if context:
            warning_message = f"{context}: {message}"
        else:
            warning_message = message
        
        # Логируем предупреждение
        self.logger.warning(warning_message)
        logging.warning(warning_message)
        
        # Выводим предупреждение в stderr
        print(f"WARNING: {warning_message}", file=sys.stderr)
        
        return True
    
    def log_info(self, message):
        """
        Логирует информационное сообщение.
        
        Args:
            message (str): Информационное сообщение
        """
        self.logger.info(message)
        logging.info(message)
        
        # Выводим информацию в stderr (для наглядности в тестах)
        print(f"INFO: {message}", file=sys.stderr)
    
    def log_debug(self, message):
        """
        Логирует отладочное сообщение.
        
        Args:
            message (str): Отладочное сообщение
        """
        self.logger.debug(message)
        logging.debug(message)
    
    def format_exception(self, exception):
        """
        Форматирует исключение в строку с трассировкой стека.
        
        Args:
            exception (Exception): Исключение для форматирования
            
        Returns:
            str: Отформатированная строка с трассировкой стека
        """
        return ''.join(traceback.format_exception(type(exception), exception, exception.__traceback__))
    
    def format_error_message(self, exception, context=None):
        """
        Форматирует сообщение об ошибке.
        
        Args:
            exception (Exception): Исключение
            context (str, optional): Контекст, в котором произошла ошибка
            
        Returns:
            str: Отформатированное сообщение об ошибке
        """
        if context:
            return f"{context}: {type(exception).__name__}: {str(exception)}"
        else:
            return f"{type(exception).__name__}: {str(exception)}"