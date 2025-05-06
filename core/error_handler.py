import logging
import traceback

class ErrorHandler:
    """
    Обработчик ошибок системы.
    Предоставляет функционал для обработки и логирования ошибок.
    """
    
    def __init__(self, log_file=None):
        self.logger = logging.getLogger('neuro_link_assistant')
        self.logger.setLevel(logging.INFO)
        
        # Добавляем обработчик для вывода в консоль
        console_handler = logging.StreamHandler()
        console_formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        console_handler.setFormatter(console_formatter)
        self.logger.addHandler(console_handler)
        
        # Если указан файл логов, добавляем обработчик для записи в файл
        if log_file:
            file_handler = logging.FileHandler(log_file)
            file_formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
            file_handler.setFormatter(file_formatter)
            self.logger.addHandler(file_handler)
    
    def log_error(self, message, exception=None):
        """Логирует ошибку"""
        if exception:
            self.logger.error(f"{message}: {str(exception)}")
            self.logger.error(traceback.format_exc())
        else:
            self.logger.error(message)
    
    def log_warning(self, message):
        """Логирует предупреждение"""
        self.logger.warning(message)
    
    def log_info(self, message):
        """Логирует информационное сообщение"""
        self.logger.info(message)