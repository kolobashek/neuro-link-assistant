"""
Обработчик ошибок для LLM модуля.
"""

from core.common.error_handler import handle_error as base_handle_error
from core.common.error_handler import handle_llm_error as base_handle_llm_error


def handle_error(exception, context=None, callback=None, log_level="error"):
    """
    Обработка ошибок для LLM модуля.

    Args:
        exception: Исключение
        context: Контекст ошибки
        callback: Функция обратного вызова
        log_level: Уровень логирования

    Returns:
        bool: True если ошибка обработана
    """
    return base_handle_error(exception, context, callback, log_level, module="llm")


def handle_llm_error(message, exception=None, model=None, prompt=None):
    """
    Специализированный обработчик ошибок LLM.

    Args:
        message: Сообщение об ошибке
        exception: Исключение
        model: Модель LLM
        prompt: Промпт

    Returns:
        bool: True если ошибка обработана
    """
    return base_handle_llm_error(message, exception, model, prompt)
