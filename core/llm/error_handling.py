from typing import Dict, Any
import requests

def handle_api_error(exception: Exception, context: str, error_handler=None) -> Dict[str, Any]:
    """
    Обработка ошибок API.
    
    Args:
        exception (Exception): Исключение
        context (str): Контекст, в котором произошла ошибка
        error_handler (object, optional): Обработчик ошибок
    
    Returns:
        Dict[str, Any]: Информация об ошибке
    """
    error_info = {
        "status": "error",
        "message": str(exception),
        "context": context
    }
    
    # Извлекаем дополнительную информацию из исключения
    if isinstance(exception, requests.exceptions.HTTPError) and hasattr(exception, 'response'):
        try:
            response_json = exception.response.json()
            if "error" in response_json and "message" in response_json["error"]:
                error_info["message"] = response_json["error"]["message"]
            error_info["status_code"] = exception.response.status_code
        except (ValueError, KeyError):
            pass
    
    # Логируем ошибку
    if error_handler:
        error_handler.handle_error(exception, f"API Error in {context}: {error_info['message']}")
    else:
        print(f"API Error in {context}: {error_info['message']}")
    
    return error_info

def handle_rate_limit(exception: Exception, context: str, error_handler=None) -> Dict[str, Any]:
    """
    Обработка ошибок превышения лимита запросов.
    
    Args:
        exception (Exception): Исключение
        context (str): Контекст, в котором произошла ошибка
        error_handler (object, optional): Обработчик ошибок
    
    Returns:
        Dict[str, Any]: Информация об ошибке
    """
    error_info = {
        "status": "rate_limit",
        "message": "Rate limit exceeded",
        "context": context,
        "retry_after": 60  # Значение по умолчанию
    }
    
    # Извлекаем дополнительную информацию из исключения
    if isinstance(exception, requests.exceptions.HTTPError) and hasattr(exception, 'response'):
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
    if error_handler:
        error_handler.handle_warning(
            f"Rate limit exceeded in {context}. Retry after {error_info['retry_after']} seconds.",
            "api_rate_limit"
        )
    else:
        print(f"Rate limit exceeded in {context}. Retry after {error_info['retry_after']} seconds.")
    
    return error_info

def handle_timeout(exception: Exception, context: str, error_handler=None) -> Dict[str, Any]:
    """
    Обработка ошибок таймаута.
    
    Args:
        exception (Exception): Исключение
        context (str): Контекст, в котором произошла ошибка
        error_handler (object, optional): Обработчик ошибок
    
    Returns:
        Dict[str, Any]: Информация об ошибке
    """
    error_info = {
        "status": "timeout",
        "message": str(exception),
        "context": context,
        "retry_suggestion": "Попробуйте повторить запрос позже или уменьшить размер запроса."
    }
    
    # Логируем предупреждение
    if error_handler:
        error_handler.handle_warning(
            f"Timeout in {context}: {error_info['message']}",
            "api_timeout"
        )
    else:
        print(f"Timeout in {context}: {error_info['message']}")
    
    return error_info