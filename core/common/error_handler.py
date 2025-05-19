# -*- coding: utf-8 -*-
"""
Модуль для обработки и логирования ошибок в системе.
Предоставляет как классы, так и глобальные функции для обработки различных типов ошибок.
"""

import logging
import traceback
from typing import Any, Callable, Dict, Optional

import requests


class ErrorHandler:
    """
    Обработчик ошибок.
    Предоставляет функции для обработки и логирования ошибок различных типов.
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

    def handle_api_error(self, exception: Exception, context: str) -> Dict[str, Any]:
        """
        Обработка ошибок API.

        Args:
            exception (Exception): Исключение
            context (str): Контекст, в котором произошла ошибка

        Returns:
            Dict[str, Any]: Информация об ошибке
        """
        error_info = {"status": "error", "message": str(exception), "context": context}

        # Извлекаем дополнительную информацию из исключения
        if isinstance(exception, requests.exceptions.HTTPError) and hasattr(exception, "response"):
            try:
                response_json = exception.response.json()
                if "error" in response_json and "message" in response_json["error"]:
                    error_info["message"] = response_json["error"]["message"]
                error_info["status_code"] = exception.response.status_code.__str__()
            except (ValueError, KeyError):
                pass

        # Логируем ошибку
        self.handle_error(exception, f"API Error in {context}: {error_info['message']}")

        return error_info

    def handle_rate_limit(self, exception: Exception, context: str) -> Dict[str, Any]:
        """
        Обработка ошибок превышения лимита запросов.

        Args:
            exception (Exception): Исключение
            context (str): Контекст, в котором произошла ошибка

        Returns:
            Dict[str, Any]: Информация об ошибке
        """
        error_info = {
            "status": "rate_limit",
            "message": "Rate limit exceeded",
            "context": context,
            "retry_after": 60,  # Значение по умолчанию
        }

        # Извлекаем дополнительную информацию из исключения
        if isinstance(exception, requests.exceptions.HTTPError) and hasattr(exception, "response"):
            try:
                response_json = exception.response.json()
                if "error" in response_json and "message" in response_json["error"]:
                    error_info["message"] = response_json["error"]["message"]

                # Извлекаем время до следующей попытки из заголовков
                if "Retry-After" in exception.response.headers:
                    error_info["retry_after"] = int(exception.response.headers["Retry-After"])
            except (ValueError, KeyError):
                pass

        # Логируем предупреждение
        self.handle_warning(
            f"Rate limit exceeded in {context}. Retry after {error_info['retry_after']} seconds.",
            "api_rate_limit",
        )

        return error_info

    def handle_timeout(self, exception: Exception, context: str) -> Dict[str, Any]:
        """
        Обработка ошибок таймаута.

        Args:
            exception (Exception): Исключение
            context (str): Контекст, в котором произошла ошибка

        Returns:
            Dict[str, Any]: Информация об ошибке
        """
        error_info = {
            "status": "timeout",
            "message": str(exception),
            "context": context,
            "retry_suggestion": "Попробуйте повторить запрос позже или уменьшить размер запроса.",
        }

        # Логируем предупреждение
        self.handle_warning(f"Timeout in {context}: {error_info['message']}", "api_timeout")

        return error_info

    def handle_llm_error(self, message, exception=None, model=None, prompt=None):
        """
        Специализированный обработчик ошибок для LLM.

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

        # Используем общий обработчик
        return self.handle_error(exception or Exception(message), f"{message}\n{details}")

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

    def add_error_handler(self, handler: Callable[[Exception, Optional[str]], None]):
        """
        Добавляет обработчик ошибок в список обработчиков.

        Args:
            handler (Callable): Функция обработчика, принимающая исключение и контекст
        """
        if callable(handler):
            self.error_handlers.append(handler)
            return True
        return False

    def remove_error_handler(self, handler: Callable[[Exception, Optional[str]], None]):
        """
        Удаляет обработчик ошибок из списка обработчиков.

        Args:
            handler (Callable): Функция обработчика, которую нужно удалить
        """
        if handler in self.error_handlers:
            self.error_handlers.remove(handler)
            return True
        return False


# Создаем глобальный экземпляр ErrorHandler
_error_handler = ErrorHandler()


# Глобальные функции для обратной совместимости и удобства
def handle_error(exception, context=None, callback=None, log_level="error"):
    """
    Глобальная функция для обработки ошибок с использованием глобального экземпляра ErrorHandler.

    Args:
        exception (Exception): Исключение, вызвавшее ошибку
        context (str, optional): Контекст, в котором произошла ошибка
        callback (callable, optional): Функция обратного вызова для обработки ошибки
        log_level (str, optional): Уровень логирования ('error', 'warning', 'critical')

    Returns:
        bool: True, если ошибка обработана, False в противном случае
    """
    return _error_handler.handle_error(exception, context, callback, log_level)


def handle_warning(message, context=None):
    """
    Глобальная функция для обработки предупреждений с использованием глобального экземпляра ErrorHandler.

    Args:
        message (str): Сообщение предупреждения
        context (str, optional): Контекст, в котором произошло предупреждение

    Returns:
        bool: True, если предупреждение обработано
    """
    return _error_handler.handle_warning(message, context)


def handle_llm_error(message, exception=None, model=None, prompt=None):
    """
    Глобальная функция для обработки ошибок LLM с использованием глобального экземпляра ErrorHandler.

    Args:
        message (str): Сообщение об ошибке
        exception (Exception, optional): Исключение, вызвавшее ошибку
        model (str, optional): Модель LLM, вызвавшая ошибку
        prompt (str, optional): Промпт, вызвавший ошибку

    Returns:
        bool: True, если ошибка обработана, False в противном случае
    """
    return _error_handler.handle_llm_error(message, exception, model, prompt)


def handle_api_error(exception: Exception, context: str) -> Dict[str, Any]:
    """
    Глобальная функция для обработки ошибок API с использованием глобального экземпляра ErrorHandler.

    Args:
        exception (Exception): Исключение
        context (str): Контекст, в котором произошла ошибка

    Returns:
        Dict[str, Any]: Информация об ошибке
    """
    return _error_handler.handle_api_error(exception, context)


def handle_rate_limit(exception: Exception, context: str) -> Dict[str, Any]:
    """
    Глобальная функция для обработки ошибок превышения лимита запросов
    с использованием глобального экземпляра ErrorHandler.

    Args:
        exception (Exception): Исключение
        context (str): Контекст, в котором произошла ошибка

    Returns:
        Dict[str, Any]: Информация об ошибке
    """
    return _error_handler.handle_rate_limit(exception, context)


def handle_timeout(exception: Exception, context: str) -> Dict[str, Any]:
    """
    Глобальная функция для обработки ошибок таймаута с использованием глобального экземпляра ErrorHandler.

    Args:
        exception (Exception): Исключение
        context (str): Контекст, в котором произошла ошибка

    Returns:
        Dict[str, Any]: Информация об ошибке
    """
    return _error_handler.handle_timeout(exception, context)


def get_error_handler() -> ErrorHandler:
    """
    Возвращает глобальный экземпляр ErrorHandler.

    Returns:
        ErrorHandler: Глобальный экземпляр ErrorHandler
    """
    return _error_handler
