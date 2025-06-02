from unittest.mock import MagicMock

import pytest
import requests

# Предполагаем, что у нас есть модуль error_handling в core/llm/error_handling.py
# Если его нет, нужно будет создать этот файл
try:
    from core.llm.error_handling import handle_api_error, handle_rate_limit, handle_timeout

    HAS_ERROR_HANDLING = True
except ImportError:
    HAS_ERROR_HANDLING = False

# Пропускаем тесты, если модуль не найден
pytestmark = pytest.mark.skipif(
    not HAS_ERROR_HANDLING, reason="LLM error handling not implemented yet"
)


class TestErrorHandling:
    """Тесты для обработки ошибок LLM API"""

    @pytest.fixture
    def error_handler(self):
        """Фикстура для создания мока обработчика ошибок"""
        return MagicMock()

    def test_handle_api_error(self, error_handler):
        """Тест обработки ошибки API"""
        # Создаем тестовое исключение
        response = MagicMock()
        response.status_code = 400
        response.json.return_value = {"error": {"message": "Invalid request"}}
        exception = requests.exceptions.HTTPError("400 Client Error", response=response)

        # Обрабатываем ошибку
        result = handle_api_error(exception, "Test API call", error_handler)

        # Проверяем, что ошибка была обработана
        error_handler.handle_error.assert_called_once()

        # Проверяем, что возвращается словарь с информацией об ошибке
        assert result["status"] == "error"
        assert "Invalid request" in result["message"]

    def test_handle_rate_limit(self, error_handler):
        """Тест обработки ошибки превышения лимита запросов"""
        # Создаем тестовое исключение
        response = MagicMock()
        response.status_code = 429
        response.json.return_value = {"error": {"message": "Rate limit exceeded"}}
        exception = requests.exceptions.HTTPError("429 Too Many Requests", response=response)

        # Обрабатываем ошибку
        result = handle_rate_limit(exception, "Test API call", error_handler)

        # Проверяем, что ошибка была обработана
        error_handler.handle_warning.assert_called_once()

        # Проверяем, что возвращается словарь с информацией об ошибке
        assert result["status"] == "rate_limit"
        assert "Rate limit exceeded" in result["message"]
        assert "retry_after" in result

    def test_handle_timeout(self, error_handler):
        """Тест обработки ошибки таймаута"""
        # Создаем тестовое исключение
        exception = requests.exceptions.Timeout("Connection timed out")

        # Обрабатываем ошибку
        result = handle_timeout(exception, "Test API call", error_handler)

        # Проверяем, что ошибка была обработана
        error_handler.handle_warning.assert_called_once()

        # Проверяем, что возвращается словарь с информацией об ошибке
        assert result["status"] == "timeout"
        assert "Connection timed out" in result["message"]
        assert "retry_suggestion" in result
