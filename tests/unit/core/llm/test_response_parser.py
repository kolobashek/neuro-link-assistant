import pytest
from unittest.mock import MagicMock, patch
import json

# Импортируем ResponseParser напрямую, без проверки
from core.llm.response_parser import ResponseParser

class TestResponseParser:
    """Тесты для парсера ответов нейросети"""
    
    @pytest.fixture
    def response_parser(self):
        """Фикстура для создания экземпляра ResponseParser"""
        # Создаем мок для обработчика ошибок
        error_handler = MagicMock()
        
        # Создаем парсер ответов
        parser = ResponseParser(error_handler=error_handler)
        
        return parser
    
    def test_parse_json_response(self, response_parser):
        """Тест парсинга JSON-ответа"""
        # Тестовый ответ в формате JSON
        json_response = '{"result": "success", "data": {"items": [1, 2, 3]}}'
        
        # Парсим ответ
        parsed = response_parser.parse_json_response(json_response)
        
        # Проверяем результат
        assert parsed == {"result": "success", "data": {"items": [1, 2, 3]}}
    
    def test_parse_json_response_invalid_json(self, response_parser):
        """Тест обработки невалидного JSON"""
        # Невалидный JSON
        invalid_json = '{"result": "success", "data": {"items": [1, 2, 3]'
        
        # Парсим ответ
        parsed = response_parser.parse_json_response(invalid_json)
        
        # Проверяем, что ошибка была обработана
        response_parser.error_handler.handle_error.assert_called_once()
        
        # Проверяем, что возвращается None при ошибке
        assert parsed is None
    
    def test_extract_code_blocks(self, response_parser):
        """Тест извлечения блоков кода из ответа"""
        # Тестовый ответ с блоками кода
        response = """
    Вот пример кода на Python:
    
    
    def hello_world():
        print("Hello, World!")
    
    
    А вот пример на JavaScript:
    
    
    function helloWorld() {
        console.log("Hello, World!");
    }
    
    """
    
        # Извлекаем блоки кода
        code_blocks = response_parser.extract_code_blocks(response)
        
        # Проверяем результат
        assert len(code_blocks) == 2
        assert code_blocks[0] == {"language": "python", "code": 'def hello_world():\n        print("Hello, World!")'}
        assert code_blocks[1] == {"language": "javascript", "code": 'function helloWorld() {\n        console.log("Hello, World!");\n    }'}    
        def test_extract_code_blocks_no_blocks(self, response_parser):
          """Тест извлечения блоков кода из ответа без блоков"""
        # Тестовый ответ без блоков кода
        response = "Это обычный текст без блоков кода."
        
        # Извлекаем блоки кода
        code_blocks = response_parser.extract_code_blocks(response)
        
        # Проверяем результат
        assert len(code_blocks) == 0