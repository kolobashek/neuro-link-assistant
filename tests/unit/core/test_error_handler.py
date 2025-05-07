import pytest
import logging
from unittest.mock import patch, MagicMock

class TestErrorHandler:
    """Тесты обработчика ошибок"""
    
    @pytest.fixture
    def error_handler(self):
        """Создает экземпляр ErrorHandler"""
        from core.common.error_handler import ErrorHandler
        return ErrorHandler()
    
    @patch('logging.error')
    def test_handle_error(self, mock_log_error, error_handler):
        """Тест обработки ошибки"""
        # Создаем тестовое исключение
        test_exception = ValueError("Test error")
        
        # Обрабатываем ошибку
        error_handler.handle_error(test_exception, "Test context")
        
        # Проверяем, что ошибка была залогирована
        mock_log_error.assert_called_once()
        # Проверяем, что сообщение содержит контекст и текст ошибки
        assert "Test context" in mock_log_error.call_args[0][0]
        assert "Test error" in mock_log_error.call_args[0][0]
    
    @patch('logging.warning')
    def test_handle_warning(self, mock_log_warning, error_handler):
        """Тест обработки предупреждения"""
        # Обрабатываем предупреждение
        error_handler.handle_warning("Test warning message", "Test context")
        
        # Проверяем, что предупреждение было залогировано
        mock_log_warning.assert_called_once()
        # Проверяем, что сообщение содержит контекст и текст предупреждения
        assert "Test context" in mock_log_warning.call_args[0][0]
        assert "Test warning message" in mock_log_warning.call_args[0][0]
    
    @patch('logging.info')
    def test_log_info(self, mock_log_info, error_handler):
        """Тест логирования информационного сообщения"""
        # Логируем информационное сообщение
        error_handler.log_info("Test info message")
        
        # Проверяем, что сообщение было залогировано
        mock_log_info.assert_called_once_with("Test info message")
    
    @patch('logging.debug')
    def test_log_debug(self, mock_log_debug, error_handler):
        """Тест логирования отладочного сообщения"""
        # Логируем отладочное сообщение
        error_handler.log_debug("Test debug message")
        
        # Проверяем, что сообщение было залогировано
        mock_log_debug.assert_called_once_with("Test debug message")
    
    @patch('logging.error')
    def test_handle_error_with_callback(self, mock_log_error, error_handler):
        """Тест обработки ошибки с обратным вызовом"""
        # Создаем тестовое исключение
        test_exception = ValueError("Test error")
        
        # Создаем мок-функцию обратного вызова
        callback = MagicMock()
        
        # Обрабатываем ошибку с обратным вызовом
        error_handler.handle_error(test_exception, "Test context", callback=callback)
        
        # Проверяем, что ошибка была залогирована
        mock_log_error.assert_called_once()
        
        # Проверяем, что обратный вызов был выполнен
        callback.assert_called_once_with(test_exception)
    
    def test_format_exception(self, error_handler):
        """Тест форматирования исключения"""
        # Создаем тестовое исключение
        try:
            # Генерируем исключение с трассировкой стека
            raise ValueError("Test error")
        except ValueError as e:
            # Форматируем исключение
            formatted = error_handler.format_exception(e)
            
            # Проверяем, что форматированное исключение содержит нужную информацию
            assert "ValueError" in formatted
            assert "Test error" in formatted
            assert "Traceback" in formatted