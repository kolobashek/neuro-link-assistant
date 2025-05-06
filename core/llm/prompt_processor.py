class PromptProcessor:
    """
    Процессор промптов для языковой модели.
    Позволяет создавать и обрабатывать шаблоны промптов.
    """
    
    def __init__(self):
        """Инициализация процессора промптов."""
        self.templates = {}
    
    def add_template(self, name, template):
        """
        Добавляет шаблон промпта.
        
        Args:
            name (str): Имя шаблона
            template (str): Текст шаблона с плейсхолдерами в формате {variable}
            
        Returns:
            bool: True в случае успешного добавления
        """
        self.templates[name] = template
        return True
    
    def process_prompt(self, template_name, variables=None):
        """
        Обрабатывает шаблон промпта, подставляя переменные.
        
        Args:
            template_name (str): Имя шаблона
            variables (dict, optional): Словарь с переменными для подстановки
            
        Returns:
            str: Обработанный текст промпта
            
        Raises:
            ValueError: Если шаблон с указанным именем не найден
        """
        if template_name not in self.templates:
            raise ValueError(f"Template {template_name} not found")
        
        template = self.templates[template_name]
        
        # Если переменные предоставлены, подставляем их в шаблон
        if variables:
            for key, value in variables.items():
                placeholder = f"{{{key}}}"
                template = template.replace(placeholder, str(value))
        
        return template
    
    def load_templates_from_file(self, file_path):
        """
        Загружает шаблоны из JSON-файла.
        
        Args:
            file_path (str): Путь к файлу с шаблонами
            
        Returns:
            bool: True в случае успешной загрузки
            
        Raises:
            FileNotFoundError: Если файл не найден
            json.JSONDecodeError: Если файл содержит некорректный JSON
        """
        import json
        
        with open(file_path, 'r', encoding='utf-8') as file:
            templates = json.load(file)
            
            for name, template in templates.items():
                self.add_template(name, template)
                
        return True