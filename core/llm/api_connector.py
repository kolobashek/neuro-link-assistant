from typing import Any, Dict, Optional

import requests


class APIConnector:
    """
    Коннектор для взаимодействия с API нейросетей.
    """

    def __init__(self, api_key: str, base_url: str, error_handler=None):
        """
        Инициализация коннектора API.

        Args:
            api_key (str): API-ключ для аутентификации
            base_url (str): Базовый URL API
            error_handler (object, optional): Обработчик ошибок
        """
        self.api_key = api_key
        self.base_url = base_url
        self.error_handler = error_handler

    def send_request(self, endpoint: str, payload: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Отправка запроса к API.

        Args:
            endpoint (str): Конечная точка API
            payload (Dict[str, Any]): Данные запроса

        Returns:
            Optional[Dict[str, Any]]: Ответ API или None в случае ошибки
        """
        try:
            # Формируем полный URL
            url = f"{self.base_url}{endpoint}"

            # Настраиваем заголовки
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.api_key}",
            }

            # Отправляем запрос
            response = requests.post(url, headers=headers, json=payload)

            # Проверяем статус ответа
            response.raise_for_status()

            # Возвращаем данные ответа
            return response.json()

        except requests.exceptions.RequestException as e:
            # Обрабатываем ошибку
            if self.error_handler:
                self.error_handler.handle_error(e, f"Error sending request to {endpoint}")
            else:
                print(f"Error sending request to {endpoint}: {e}")

            return None
