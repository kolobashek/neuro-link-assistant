import requests
from requests.exceptions import RequestException

class LLMApiClient:
    """
    Клиент для взаимодействия с API языковой модели.
    """
    
    def __init__(self, api_key=None, base_url=None):
        """
        Инициализация клиента API.
        
        Args:
            api_key (str, optional): Ключ API для аутентификации
            base_url (str, optional): Базовый URL API
        """
        self.api_key = api_key
        self.base_url = base_url or "https://api.openai.com/v1"
        self.session = requests.Session()
        
        # Настройка заголовков для аутентификации
        if api_key:
            self.session.headers.update({
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json"
            })
    
    def connect(self):
        """
        Проверяет соединение с API.
        
        Returns:
            bool: True, если соединение установлено успешно
            
        Raises:
            requests.exceptions.RequestException: В случае ошибки соединения
        """
        try:
            # Проверяем соединение с API, используя простой запрос
            response = self.session.get(f"{self.base_url}/models")
            response.raise_for_status()  # Вызывает исключение при ошибке HTTP
            return True
        except RequestException as e:
            # Пробрасываем исключение дальше для обработки вызывающим кодом
            raise e
    
    def send_request(self, prompt, options=None):
        """
        Отправляет запрос к API языковой модели.
        
        Args:
            prompt (str): Текст промпта для модели
            options (dict, optional): Дополнительные параметры запроса
            
        Returns:
            dict: Ответ от API в формате JSON
            
        Raises:
            requests.exceptions.RequestException: В случае ошибки запроса
        """
        # Формируем данные запроса
        request_data = {
            "prompt": prompt,
            "max_tokens": 1000,
            "temperature": 0.7,
        }
        
        # Добавляем дополнительные параметры, если они предоставлены
        if options:
            request_data.update(options)
        
        try:
            # Отправляем POST-запрос к API
            response = self.session.post(
                f"{self.base_url}/completions",
                json=request_data
            )
            response.raise_for_status()
            
            # Возвращаем данные ответа в формате JSON
            return response.json()
        except RequestException as e:
            # Пробрасываем исключение дальше для обработки вызывающим кодом
            raise e