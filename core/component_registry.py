class ComponentRegistry:
    """
    Реестр компонентов системы.
    Предоставляет централизованный доступ к компонентам по их именам.
    """
    
    def __init__(self):
        """Инициализация реестра компонентов."""
        self._components = {}
    
    def register(self, name, component):
        """
        Регистрирует компонент в реестре.
        
        Args:
            name (str): Имя компонента
            component (object): Объект компонента
        
        Returns:
            bool: True в случае успешной регистрации
        """
        if name in self._components:
            raise ValueError(f"Компонент с именем '{name}' уже зарегистрирован")
        
        self._components[name] = component
        return True
    
    def get(self, name, default=None):
        """
        Получает компонент из реестра по имени.
        
        Args:
            name (str): Имя компонента
            default (object, optional): Значение по умолчанию, если компонент не найден
            
        Returns:
            object: Экземпляр компонента или значение по умолчанию
        """
        if name in self._components:
            return self._components[name]
        
        return default  # Просто возвращаем значение по умолчанию
    
    def has(self, name):
        """
        Проверяет наличие компонента в реестре.
        
        Args:
            name (str): Имя компонента
            
        Returns:
            bool: True, если компонент зарегистрирован, иначе False
        """
        return name in self._components
    
    def remove(self, name):
        """
        Удаляет компонент из реестра.
        
        Args:
            name (str): Имя компонента
            
        Raises:
            KeyError: Если компонент с указанным именем не найден
        """
        if name not in self._components:
            raise KeyError(f"Компонент с именем '{name}' не зарегистрирован")
        
        del self._components[name]
    
    def get_all(self):
        """
        Получает все зарегистрированные компоненты.
        
        Returns:
            dict: Словарь всех компонентов {имя: компонент}
        """
        return self._components.copy()