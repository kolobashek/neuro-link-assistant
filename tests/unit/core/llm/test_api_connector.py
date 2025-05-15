from unittest.mock import MagicMock, patch

import pytest
import requests

# Предполагаем, что у нас есть класс APIConnector в core/llm/api_connector.py
# Если его нет, нужно будет создать этот файл
try:
    from core.llm.api_connector import APIConnector

    HAS_API_CONNECTOR = True
except ImportError:
    HAS_API_CONNECTOR = False

# Пропускаем тесты, если модуль не найден
pytestmark = pytest.mark.skipif(not HAS_API_CONNECTOR, reason="APIConnector not implemented yet")


class TestAPIConnector:
    """Тесты для коннектора API нейросетей"""

    @pytest.fixture
    def api_connector(self):
        """Фикстура для создания экземпляра APIConnector"""
        # Создаем мок для обработчика ошибок
        error_handler = MagicMock()

        # Создаем коннектор с тестовыми настройками
        connector = APIConnector(
            api_key="test_key", base_url="https://api.example.com", error_handler=error_handler
        )

        return connector

    @patch("requests.post")
    def test_send_request(self, mock_post, api_connector):
        """Тест отправки запроса к API"""
        # Настраиваем мок для имитации успешного ответа
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"result": "success", "data": "test data"}
        mock_post.return_value = mock_response

        # Отправляем тестовый запрос
        endpoint = "/v1/completions"
        payload = {"prompt": "Test prompt", "max_tokens": 100}

        response = api_connector.send_request(endpoint, payload)

        # Проверяем, что запрос был отправлен с правильными параметрами
        mock_post.assert_called_once()
        args, kwargs = mock_post.call_args
        assert args[0] == "https://api.example.com/v1/completions"
        assert "headers" in kwargs
        assert "Authorization" in kwargs["headers"]
        assert kwargs["headers"]["Authorization"] == "Bearer test_key"
        assert "json" in kwargs
        assert kwargs["json"] == payload

        # Проверяем, что ответ был правильно обработан
        assert response == {"result": "success", "data": "test data"}

    @patch("requests.post")
    def test_send_request_error(self, mock_post, api_connector):
        """Тест обработки ошибки при отправке запроса"""
        # Настраиваем мок для имитации ошибки
        mock_post.side_effect = requests.exceptions.RequestException("Connection error")

        # Отправляем тестовый запрос
        endpoint = "/v1/completions"
        payload = {"prompt": "Test prompt", "max_tokens": 100}

        # Проверяем, что ошибка обрабатывается и возвращается None
        response = api_connector.send_request(endpoint, payload)
        assert response is None

        # Проверяем, что ошибка была обработана
        api_connector.error_handler.handle_error.assert_called_once()
