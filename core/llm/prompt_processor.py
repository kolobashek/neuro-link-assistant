from typing import Dict, Any, Optional
import os

class PromptProcessor:
    """
    Процессор для работы с промптами.
    """
    
    def __init__(self, error_handler=None):
        """
        Инициализация процессора промптов.
        
        Args:
            error_handler (object, optional): Обработчик ошибок
        """
        self.error_handler = error_handler
    
    def format_prompt(self, template: str, variables: Dict[str, Any]) -> str:
        """
        Форматирование промпта с подстановкой переменных.
        
        Args:
            template (str): Шаблон промпта
            variables (Dict[str, Any]): Словарь переменных для подстановки
        
        Returns:
            str: Отформатированный промпт
        """
        try:
            return template.format(**variables)
        except KeyError as e:
            # Обрабатываем ошибку отсутствующей переменной
            if self.error_handler:
                self.error_handler.handle_warning(
                    f"Missing variable in prompt template: {e}",
                    "prompt_processor"
                )
            else:
                print(f"Warning: Missing variable in prompt template: {e}")
            
            # Заменяем отсутствующие переменные пустыми строками
            for key in e.args:
                if key not in variables:
                    variables[key] = ""
            
            return template.format(**variables)
    
    def load_prompt_template(self, template_path: str) -> Optional[str]:
        """
        Загрузка шаблона промпта из файла.
        
        Args:
            template_path (str): Путь к файлу шаблона
        
        Returns:
            Optional[str]: Содержимое шаблона или None в случае ошибки
        """
        try:
            with open(template_path, mode="r", encoding="utf-8") as file:
                return file.read()
        except Exception as e:
            # Обрабатываем ошибку
            if self.error_handler:
                self.error_handler.handle_error(e, f"Error loading prompt template from {template_path}")
            else:
                print(f"Error loading prompt template from {template_path}: {e}")
            
            return None