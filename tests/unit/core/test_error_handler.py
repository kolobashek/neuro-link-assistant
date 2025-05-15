from unittest.mock import MagicMock

import pytest

from core.common.error_handler import ErrorHandler


class TestErrorHandler:
    """Тесты для обработчика ошибок"""

    @pytest.fixture
    def error_handler(self):
        """Фикстура для создания экземпляра ErrorHandler"""
        handler = ErrorHandler()
        # Заменяем логгер на мок
        handler.logger = MagicMock()
        return handler

    def test_handle_error(self, error_handler):
        """Тест обработки ошибки"""
        # Создаем тестовое исключение
        test_exception = ValueError("Test error")

        # Обрабатываем ошибку
        error_handler.handle_error(test_exception, "Test context")

        # Проверяем, что ошибка была залогирована
        error_handler.logger.error.assert_called_once()

    def test_handle_warning(self, error_handler):
        """Тест обработки предупреждения"""
        # Обрабатываем предупреждение
        error_handler.handle_warning("Test warning message", "Test context")

        # Проверяем, что предупреждение было залогировано
        error_handler.logger.warning.assert_called_once()

    def test_log_info(self, error_handler):
        """Тест логирования информационного сообщения"""
        # Логируем информационное сообщение
        error_handler.log_info("Test info message")

        # Проверяем, что сообщение было залогировано
        error_handler.logger.info.assert_called_once_with("Test info message")

    def test_log_debug(self, error_handler):
        """Тест логирования отладочного сообщения"""
        # Логируем отладочное сообщение
        error_handler.log_debug("Test debug message")

        # Проверяем, что сообщение было залогировано
        error_handler.logger.debug.assert_called_once_with("Test debug message")

    def test_handle_error_with_callback(self, error_handler):
        """Тест обработки ошибки с обратным вызовом"""
        # Создаем тестовое исключение
        test_exception = ValueError("Test error")

        # Создаем мок-функцию обратного вызова
        callback = MagicMock()

        # Обрабатываем ошибку с обратным вызовом
        error_handler.handle_error(test_exception, "Test context", callback=callback)

        # Проверяем, что ошибка была залогирована
        error_handler.logger.error.assert_called_once()

        # Проверяем, что callback был вызван
        callback.assert_called_once_with(test_exception, "Test context")

    def test_format_exception(self, error_handler):
        """Тест форматирования исключения"""
        # Создаем тестовое исключение
        try:
            # Генерируем исключение с трассировкой стека
            raise ValueError("Test error")
        except ValueError as e:
            # Форматируем исключение
            formatted = error_handler.format_exception(e)

            # Проверяем, что форматированное исключение содержит ожидаемую информацию
            assert "ValueError: Test error" in formatted
            assert "test_format_exception" in formatted
