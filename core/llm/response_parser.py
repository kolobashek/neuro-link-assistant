import json
import re

class ResponseParser:
    """
    Парсер ответов от языковой модели.
    Извлекает полезную информацию из ответов модели.
    """
    
    def parse_response(self, response):
        """
        Парсит ответ от API языковой модели.
        
        Args:
            response (dict): Ответ от API в формате JSON
            
        Returns:
            str: Текст ответа или None, если ответ не содержит текста
        """
        if "choices" in response and len(response["choices"]) > 0:
            # Извлекаем текст из первого выбора модели
            return response["choices"][0]["text"]
        return None
    
    def extract_json(self, text):
        """
        Извлекает JSON-объект из текста ответа.
        
        Args:
            text (str): Текст, который может содержать JSON
            
        Returns:
            dict: Извлеченный JSON-объект или None, если JSON не найден
        """
        try:
            # Ищем JSON в тексте между фигурными скобками
            # Используем регулярное выражение для поиска наиболее внешних фигурных скобок
            json_pattern = r'\{(?:[^{}]|(?:\{(?:[^{}]|(?:\{[^{}]*\}))*\}))*\}'
            match = re.search(json_pattern, text)
            
            if match:
                json_str = match.group(0)
                return json.loads(json_str)
            
            # Если регулярное выражение не сработало, пробуем простой поиск
            start = text.find('{')
            end = text.rfind('}') + 1
            
            if start >= 0 and end > start:
                json_str = text[start:end]
                return json.loads(json_str)
                
            return None
        except json.JSONDecodeError:
            # В случае ошибки декодирования JSON возвращаем None
            return None
    
    def extract_list(self, text):
        """
        Извлекает список элементов из текста ответа.
        
        Args:
            text (str): Текст, который может содержать список
            
        Returns:
            list: Извлеченный список элементов или пустой список
        """
        # Ищем элементы списка, начинающиеся с цифры или маркера
        list_pattern = r'(?:^|\n)(?:\d+\.|\*|\-)\s+(.+?)(?=\n(?:\d+\.|\*|\-|$)|$)'
        matches = re.findall(list_pattern, text)
        
        return matches if matches else []