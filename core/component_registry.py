class ComponentRegistry:
    """
    Реестр компонентов.
    Предоставляет централизованный механизм регистрации и получения компонентов.
    """
    
    def __init__(self):
        """Инициализация реестра компонентов."""
        self._components = {}
    
    def register(self, name, component):
        """
        Регистрирует компонент в реестре.
        
        Args:
            name (str): Имя компонента
            component (object): Экземпляр компонента
            
        Returns:
            bool: True в случае успешной регистрации, False если компонент уже зарегистрирован
        """
        if name in self._components:
            return False
        
        self._components[name] = component
        return True
    
    def unregister(self, name):
        """
        Удаляет компонент из реестра.
        
        Args:
            name (str): Имя компонента
            
        Returns:
            bool: True в случае успешного удаления, False если компонент не найден
        """
        if name not in self._components:
            return False
        
        del self._components[name]
        return True
    
    def get(self, name):
        """
        Получает компонент из реестра.
        
        Args:
            name (str): Имя компонента
            
        Returns:
            object: Экземпляр компонента или None, если компонент не найден
        """
        return self._components.get(name)
    
    def has(self, name):
        """
        Проверяет наличие компонента в реестре.
        
        Args:
            name (str): Имя компонента
            
        Returns:
            bool: True, если компонент зарегистрирован, иначе False
        """
        return name in self._components
    
    def get_all(self):
        """
        Получает все зарегистрированные компоненты.
        
        Returns:
            dict: Словарь всех зарегистрированных компонентов
        """
        return self._components.copy()