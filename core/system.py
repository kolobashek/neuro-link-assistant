class System:
    """
    Основной класс системы, представляющий собой точку входа для взаимодействия с функциональностью.
    """

    def __init__(self, registry):
        """
        Инициализирует экземпляр системы.

        Args:
            registry: Реестр компонентов системы
        """
        self._registry = registry

    def is_component_registered(self, component_name):
        """
        Проверяет, зарегистрирован ли компонент в системе.

        Args:
            component_name (str): Имя компонента

        Returns:
            bool: True, если компонент зарегистрирован, иначе False
        """
        return self._registry.has(component_name)

    def create_task(self, task_description):
        """
        Создает новую задачу на основе описания.

        Args:
            task_description (str): Описание задачи

        Returns:
            Task: Экземпляр задачи
        """
        from core.task import Task

        return Task(task_description, self._registry)
