import logging

# import sys
import traceback


class ErrorHandler:
    """
    Обработчик ошибок.
    Предоставляет функции для обработки и логирования ошибок.
    """

    def __init__(self, logger_name="error_handler"):
        """
        Инициализация обработчика ошибок.

        Args:
            logger_name (str, optional): Имя логгера
        """
        # Настройка логирования
        self.logger = logging.getLogger(logger_name)
        if not self.logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)
            self.logger.setLevel(logging.INFO)

        # Список обработчиков ошибок
        self.error_handlers = []

    def handle_error(self, exception, context=None, callback=None, log_level="error"):
        """
        Обработка ошибок с логированием.

        Args:
            exception (Exception): Исключение, вызвавшее ошибку
            context (str, optional): Контекст, в котором произошла ошибка
            callback (callable, optional): Функция обратного вызова для обработки ошибки
            log_level (str, optional): Уровень логирования ('error', 'warning', 'critical')

        Returns:
            bool: True, если ошибка обработана, False в противном случае
        """
        # Формируем полное сообщение
        message = f"[general] {context}" if context else str(exception)

        # Добавляем информацию об исключении
        if isinstance(exception, Exception):
            formatted_exception = self.format_exception(exception)
            message += f"\nException: {str(exception)}\nTraceback: {formatted_exception}"

        # Логируем в зависимости от уровня
        if log_level.lower() == "warning":
            self.logger.warning(message)
        elif log_level.lower() == "critical":
            self.logger.critical(message)
        else:
            self.logger.error(message)

        # Вызываем callback, если он предоставлен
        if callback and callable(callback):
            callback(exception, context)

        # Вызываем все зарегистрированные обработчики ошибок
        for handler in self.error_handlers:
            if callable(handler):
                handler(exception, context)

        return True

    def handle_warning(self, message, context=None):
        """
        Обработка предупреждений.

        Args:
            message (str): Сообщение предупреждения
            context (str, optional): Контекст, в котором произошло предупреждение

        Returns:
            bool: True, если предупреждение обработано
        """
        # Формируем полное сообщение
        full_message = f"{context}: {message}" if context else message

        # Логируем предупреждение
        self.logger.warning(full_message)

        return True

    def log_info(self, message):
        """
        Логирование информационного сообщения.

        Args:
            message (str): Информационное сообщение
        """
        self.logger.info(message)

    def log_debug(self, message):
        """
        Логирование отладочного сообщения.

        Args:
            message (str): Отладочное сообщение
        """
        self.logger.debug(message)

    def format_exception(self, exception):
        """
        Форматирование исключения в строку.

        Args:
            exception (Exception): Исключение

        Returns:
            str: Отформатированная строка с трассировкой стека
        """
        if isinstance(exception, Exception):
            return "".join(
                traceback.format_exception(type(exception), exception, exception.__traceback__)
            )
        return str(exception)

    def register_error_handler(self, handler):
        """
        Регистрация обработчика ошибок.

        Args:
            handler (callable): Функция обработки ошибок
        """
        if callable(handler) and handler not in self.error_handlers:
            self.error_handlers.append(handler)

    def unregister_error_handler(self, handler):
        """
        Отмена регистрации обработчика ошибок.

        Args:
            handler (callable): Функция обработки ошибок
        """
        if handler in self.error_handlers:
            self.error_handlers.remove(handler)


# Создаем глобальный экземпляр обработчика ошибок
_error_handler = ErrorHandler()


def handle_error(message, exception=None, module="general", log_level="error"):
    """
    Обработка ошибок с логированием (глобальная функция).

    Args:
        message (str): Сообщение об ошибке
        exception (Exception, optional): Исключение, вызвавшее ошибку
        module (str, optional): Модуль, в котором произошла ошибка
        log_level (str, optional): Уровень логирования ('error', 'warning', 'critical')

    Returns:
        bool: True, если ошибка обработана, False в противном случае
    """
    context = f"[{module}] {message}"
    return _error_handler.handle_error(
        exception or Exception(message), context, log_level=log_level
    )


def handle_warning(message, module="general"):
    """
    Обработка предупреждений (глобальная функция).

    Args:
        message (str): Сообщение предупреждения
        module (str, optional): Модуль, в котором произошло предупреждение

    Returns:
        bool: True, если предупреждение обработано
    """
    return _error_handler.handle_warning(message, module)


def handle_llm_error(message, exception=None, model=None, prompt=None):
    """
    Специализированный обработчик ошибок для LLM (глобальная функция).

    Args:
        message (str): Сообщение об ошибке
        exception (Exception, optional): Исключение, вызвавшее ошибку
        model (str, optional): Модель LLM, вызвавшая ошибку
        prompt (str, optional): Промпт, вызвавший ошибку

    Returns:
        bool: True, если ошибка обработана, False в противном случае
    """
    # Формируем детали ошибки
    details = "LLM Error"
    if model:
        details += f" in model {model}"
    if prompt:
        # Обрезаем длинные промпты
        max_prompt_length = 100
        short_prompt = (
            prompt[:max_prompt_length] + "..." if len(prompt) > max_prompt_length else prompt
        )
        details += f"\nPrompt: {short_prompt}"

    # Используем общий обработчик с модулем 'llm'
    return handle_error(f"{message}\n{details}", exception, module="llm")
