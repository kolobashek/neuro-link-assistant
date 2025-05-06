import requests

class LLMErrorHandler:
    """
    Обработчик ошибок при работе с API языковой модели.
    """
    
    def handle_api_error(self, error):
        """
        Обрабатывает ошибки API языковой модели.
        
        Args:
            error (Exception): Объект исключения
            
        Returns:
            dict: Информация об ошибке в структурированном виде
        """
        error_type = type(error).__name__
        error_message = str(error)
        
        # Обрабатываем различные типы ошибок
        if isinstance(error, requests.exceptions.ConnectionError):
            return {
                "error": "connection_error",
                "message": error_message,
                "suggestion": "Check your internet connection and try again."
            }
        elif isinstance(error, requests.exceptions.Timeout):
            return {
                "error": "timeout_error",
                "message": error_message,
                "suggestion": "The server took too long to respond. Try again later."
            }
        elif isinstance(error, requests.exceptions.HTTPError):
            status_code = error.response.status_code if hasattr(error, 'response') else None
            
            if status_code == 401:
                return {
                    "error": "authentication_error",
                    "message": "Invalid API key or unauthorized access.",
                    "suggestion": "Check your API key and permissions."
                }
            elif status_code == 429:
                return {
                    "error": "rate_limit_error",
                    "message": "Too many requests. Rate limit exceeded.",
                    "suggestion": "Slow down your requests or upgrade your API plan."
                }
            else:
                return {
                    "error": "http_error",
                    "message": error_message,
                    "status_code": status_code
                }
        elif isinstance(error, requests.exceptions.RequestException):
            return {
                "error": "request_error",
                "message": error_message,
                "suggestion": "There was a problem with your request. Check the parameters."
            }
        else:
            # Общая обработка для других типов ошибок
            return {
                "error": error_type,
                "message": error_message
            }