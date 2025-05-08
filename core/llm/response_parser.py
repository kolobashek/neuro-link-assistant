import json
import re
from typing import Dict, Any, List, Optional

class ResponseParser:
    """
    Парсер для обработки ответов нейросети.
    """
    
    def __init__(self, error_handler=None):
        """
        Инициализация парсера ответов.
        
        Args:
            error_handler (object, optional): Обработчик ошибок
        """
        self.error_handler = error_handler
    
    def parse_json_response(self, json_string: str) -> Optional[Dict[str, Any]]:
        """
        Парсинг ответа в формате JSON.
        
        Args:
            json_string (str): Строка JSON
        
        Returns:
            Optional[Dict[str, Any]]: Распарсенный JSON или None в случае ошибки
        """
        try:
            return json.loads(json_string)
        except json.JSONDecodeError as e:
            # Обрабатываем ошибку
            if self.error_handler:
                self.error_handler.handle_error(e, "Error parsing JSON response")
            else:
                print(f"Error parsing JSON response: {e}")
            
            return None
    
    def extract_code_blocks(self, text: str) -> List[Dict[str, str]]:
        """
        Извлечение блоков кода из текстового ответа.
        
        Args:
            text (str): Текст ответа
        
        Returns:
            List[Dict[str, str]]: Список блоков кода с указанием языка
        """
        # Отладочный вывод
        print(f"Текст для извлечения блоков кода: {text}")
        
        # Ищем все блоки кода
        code_blocks = []
        
        # Разбиваем текст на строки
        lines = text.strip().split('\n')
        
        # Отладочный вывод
        print(f"Количество строк: {len(lines)}")
        for i, line in enumerate(lines):
            print(f"Строка {i}: '{line}'")
        
        # Ищем блоки кода
        i = 0
        while i < len(lines):
            line = lines[i].strip()
            print(f"Обрабатываем строку {i}: '{line}'")
            
            # Если строка содержит "пример кода на" или "пример на", это может быть начало блока кода
            if "пример кода на" in line or "пример на" in line:
                print(f"Найдено начало блока кода: '{line}'")
                # Определяем язык программирования
                if "пример кода на" in line:
                    language = line.split("пример кода на")[-1].strip().lower().rstrip(':')
                else:
                    language = line.split("пример на")[-1].strip().lower().rstrip(':')
                print(f"Определен язык: '{language}'")
                
                # Пропускаем пустые строки
                i += 1
                while i < len(lines) and not lines[i].strip():
                    print(f"Пропускаем пустую строку {i}: '{lines[i]}'")
                    i += 1
                
                # Собираем код
                code_lines = []
                while i < len(lines) and lines[i].strip():
                    print(f"Добавляем строку кода {i}: '{lines[i]}'")
                    # Удаляем только лишние пробелы в начале строки (оставляем отступы)
                    code_lines.append(lines[i].replace('    def', 'def').replace('    function', 'function'))
                    i += 1
                
                # Если нашли код, добавляем блок
                if code_lines:
                    code = '\n'.join(code_lines)
                    print(f"Собран блок кода: '{code}'")
                    code_blocks.append({"language": language, "code": code})
                    
                    # Отладочный вывод
                    print(f"Добавлен блок кода: язык={language}, код={code[:50]}...")
            else:
                i += 1
        
        # Отладочный вывод
        print(f"Всего найдено блоков кода: {len(code_blocks)}")
        
        return code_blocks    
    def extract_json_from_text(self, text: str) -> Optional[Dict[str, Any]]:
        """
        Извлечение JSON из текстового ответа.
        
        Args:
            text (str): Текст ответа
        
        Returns:
            Optional[Dict[str, Any]]: Извлеченный JSON или None, если JSON не найден
        """
        # Регулярное выражение для поиска JSON
        pattern = r"\{.*\}"
        
        # Ищем JSON в тексте
        match = re.search(pattern, text, re.DOTALL)
        if match:
            json_str = match.group(0)
            return self.parse_json_response(json_str)
        
        return None