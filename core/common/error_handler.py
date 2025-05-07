
# Объединенный обработчик ошибок
import logging
import traceback
import sys

# Настройка логирования
logger = logging.getLogger('error_handler')

def handle_error(message, exception=None, module='general', log_level='error'):
    """
    Обработка ошибок с логированием
    
    Args:
        message (str): Сообщение об ошибке
        exception (Exception, optional): Исключение, вызвавшее ошибку
        module (str, optional): Модуль, в котором произошла ошибка
        log_level (str, optional): Уровень логирования ('error', 'warning', 'critical')
    
    Returns:
        bool: True, если ошибка обработана, False в противном случае
    """
    # Формируем полное сообщение
    full_message = f"[{module}] {message}"
    
    # Если предоставлено исключение, добавляем трассировку
    if exception:
        trace = ''.join(traceback.format_exception(
            type(exception), exception, exception.__traceback__
        ))
        full_message += f"\nException: {str(exception)}\nTraceback: {trace}"
    
    # Логируем в зависимости от уровня
    if log_level.lower() == 'warning':
        logger.warning(full_message)
    elif log_level.lower() == 'critical':
        logger.critical(full_message)
    else:
        logger.error(full_message)
    
    return True

def handle_llm_error(message, exception=None, model=None, prompt=None):
    """
    Специализированный обработчик ошибок для LLM
    
    Args:
        message (str): Сообщение об ошибке
        exception (Exception, optional): Исключение, вызвавшее ошибку
        model (str, optional): Модель LLM, вызвавшая ошибку
        prompt (str, optional): Промпт, вызвавший ошибку
    
    Returns:
        bool: True, если ошибка обработана, False в противном случае
    """
    # Формируем детали ошибки
    details = f"LLM Error"
    if model:
        details += f" in model {model}"
    if prompt:
        # Обрезаем длинные промпты
        max_prompt_length = 100
        short_prompt = prompt[:max_prompt_length] + "..." if len(prompt) > max_prompt_length else prompt
        details += f"\nPrompt: {short_prompt}"
    
    # Используем общий обработчик с модулем 'llm'
    return handle_error(f"{message}\n{details}", exception, module='llm')
