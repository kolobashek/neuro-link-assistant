class ComponentRegistry:
    """
    Реестр компонентов системы.
    Предоставляет функционал для регистрации и получения компонентов.
    """
    
    def __init__(self):
        self._components = {}
    
    def register(self, name, component):
        """Регистрирует компонент в реестре"""
        self._components[name] = component
        return component
    
    def get(self, name):
        """Получает компонент из реестра"""
        return self._components.get(name)
    
    def has(self, name):
        """Проверяет наличие компонента в реестре"""
        return name in self._components