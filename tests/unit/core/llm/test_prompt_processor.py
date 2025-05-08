import pytest
from unittest.mock import MagicMock, patch

# Предполагаем, что у нас есть класс PromptProcessor в core/llm/prompt_processor.py
# Если его нет, нужно будет создать этот файл
try:
    from core.llm.prompt_processor import PromptProcessor
    HAS_PROMPT_PROCESSOR = True
except ImportError:
    HAS_PROMPT_PROCESSOR = False

# Пропускаем тесты, если модуль не найден
pytestmark = pytest.mark.skipif(not HAS_PROMPT_PROCESSOR, reason="PromptProcessor not implemented yet")

class TestPromptProcessor:
    """Тесты для процессора промптов"""
    
    @pytest.fixture
    def prompt_processor(self):
        """Фикстура для создания экземпляра PromptProcessor"""
        # Создаем мок для обработчика ошибок
        error_handler = MagicMock()
        
        # Создаем процессор промптов
        processor = PromptProcessor(error_handler=error_handler)
        
        return processor
    
    def test_format_prompt(self, prompt_processor):
        """Тест форматирования промпта с переменными"""
        # Тестовый шаблон промпта
        template = "Привет, {name}! Сегодня {day_of_week}."
        
        # Переменные для подстановки
        variables = {
            "name": "Иван",
            "day_of_week": "понедельник"
        }
        
        # Форматируем промпт
        formatted = prompt_processor.format_prompt(template, variables)
        
        # Проверяем результат
        assert formatted == "Привет, Иван! Сегодня понедельник."
    
    def test_format_prompt_missing_variable(self, prompt_processor):
        """Тест обработки отсутствующей переменной"""
        # Тестовый шаблон промпта
        template = "Привет, {name}! Сегодня {day_of_week}."
        
        # Переменные для подстановки (отсутствует day_of_week)
        variables = {
            "name": "Иван"
        }
        
        # Форматируем промпт
        formatted = prompt_processor.format_prompt(template, variables)
        
        # Проверяем, что ошибка была обработана
        prompt_processor.error_handler.handle_warning.assert_called_once()
        
        # Проверяем, что в результате отсутствующая переменная заменена на пустую строку
        assert formatted == "Привет, Иван! Сегодня ."
    
    def test_load_prompt_template(self, prompt_processor):
        """Тест загрузки шаблона промпта из файла"""
        # Создаем мок для open
        mock_open = MagicMock()
        mock_open.return_value.__enter__.return_value.read.return_value = "Привет, {name}! Сегодня {day_of_week}."
        
        # Патчим встроенную функцию open
        with patch('builtins.open', mock_open):
            # Загружаем шаблон промпта
            template = prompt_processor.load_prompt_template("test_template.txt")
            
            # Проверяем, что шаблон был загружен
            assert template == "Привет, {name}! Сегодня {day_of_week}."
            
            # Проверяем, что файл был открыт с правильными параметрами
            mock_open.assert_called_once()
            args, kwargs = mock_open.call_args
            assert args[0] == "test_template.txt"
            assert kwargs["mode"] == "r"