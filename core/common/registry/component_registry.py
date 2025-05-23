class ComponentRegistry:
    """
    Реестр компонентов системы.
    Обеспечивает регистрацию, поиск и управление компонентами.
    """

    def __init__(self):
        self._components = {}

    def register(self, name, component):
        """
        Регистрирует компонент в реестре.

        Args:
            name (str): Имя компонента
            component: Экземпляр компонента

        Returns:
            bool: True в случае успешной регистрации
        """
        self._components[name] = component
        return True

    def get(self, name, default=None):
        """
        Возвращает компонент по имени.

        Args:
            name (str): Имя компонента
            default: Значение по умолчанию, если компонент не найден

        Returns:
            Компонент или значение по умолчанию
        """
        return self._components.get(name, default)

    def has(self, name):
        """
        Проверяет наличие компонента в реестре.

        Args:
            name (str): Имя компонента

        Returns:
            bool: True, если компонент существует, иначе False
        """
        return name in self._components

    def remove(self, name):
        """
        Удаляет компонент из реестра.

        Args:
            name (str): Имя компонента

        Returns:
            bool: True в случае успешного удаления
        """
        if name in self._components:
            del self._components[name]
            return True
        return False

    def get_all(self):
        """
        Возвращает все зарегистрированные компоненты.

        Returns:
            dict: Словарь компонентов
        """
        return self._components.copy()
