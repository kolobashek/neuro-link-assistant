import logging
import traceback
import sys
import os
from datetime import datetime

class ErrorHandler:
    """
    Обработчик ошибок.
    Предоставляет функции для логирования и обработки ошибок.
    """
    
    def __init__(self, log_dir="logs"):
        """
        Инициализация обработчика ошибок.
        
        Args:
            log_dir (str): Директория для хранения логов
        """
        self.log_dir = log_dir
        
        # Создаем директорию для логов, если она не существует
        if not os.path.exists(log_dir):
            os.makedirs(log_dir)
        
        # Настраиваем логгер
        self.logger = logging.getLogger("neuro-link-assistant")
        self.logger.setLevel(logging.DEBUG)
        
        # Обработчик для консоли
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        console_format = logging.Formatter('%(levelname)s: %(message)s')
        console_handler.setFormatter(console_format)
        
        # Обработчик для файла
        log_file = os.path.join(log_dir, f"app_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log")
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(logging.DEBUG)
        file_format = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        file_handler.setFormatter(file_format)
        
        # Добавляем обработчики к логгеру
        self.logger.addHandler(console_handler)
        self.logger.addHandler(file_handler)
        
        # Устанавливаем обработчик исключений
        sys.excepthook = self.handle_exception
    
    def log_info(self, message):
        """
        Логирует информационное сообщение.
        
        Args:
            message (str): Сообщение для логирования
        """
        self.logger.info(message)
    
    def log_warning(self, message):
        """
        Логирует предупреждение.
        
        Args:
            message (str): Сообщение для логирования
        """
        self.logger.warning(message)
    
    def log_error(self, message, exc_info=None):
        """
        Логирует ошибку.
        
        Args:
            message (str): Сообщение для логирования
            exc_info (Exception, optional): Информация об исключении
        """
        if exc_info:
            self.logger.error(f"{message}: {exc_info}", exc_info=True)
        else:
            self.logger.error(message)
    
    def log_debug(self, message):
        """
        Логирует отладочное сообщение.
        
        Args:
            message (str): Сообщение для логирования
        """
        self.logger.debug(message)
    
    def handle_exception(self, exc_type, exc_value, exc_traceback):
        """
        Обрабатывает необработанное исключение.
        
        Args:
            exc_type: Тип исключения
            exc_value: Значение исключения
            exc_traceback: Трассировка исключения
        """
        if issubclass(exc_type, KeyboardInterrupt):
            # Стандартная обработка для KeyboardInterrupt
            sys.__excepthook__(exc_type, exc_value, exc_traceback)
            return
        
        # Логируем исключение
        self.logger.critical("Необработанное исключение", exc_info=(exc_type, exc_value, exc_traceback))
    
    def handle_error(self, error, message=None):
        """
        Обрабатывает ошибку.
        
        Args:
            error (Exception): Объект исключения
            message (str, optional): Дополнительное сообщение
        """
        if message:
            self.log_error(f"{message}: {error}", exc_info=error)
        else:
            self.log_error(str(error), exc_info=error)
    
    def handle_warning(self, message):
        """
        Обрабатывает предупреждение.
        
        Args:
            message (str): Сообщение предупреждения
        """
        self.log_warning(message)