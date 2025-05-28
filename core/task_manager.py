class TaskManager:
    """
    Менеджер задач для управления жизненным циклом задач.
    """

    def __init__(self):
        """
        Инициализация менеджера задач.
        """
        self._tasks = {}
        self._task_counter = 0
        self._task_history = []

    def save_task(self, task):
        """
        Сохраняет задачу и возвращает её ID.

        Args:
            task (Task): Задача для сохранения

        Returns:
            int: ID сохраненной задачи
        """
        self._task_counter += 1
        task.id = self._task_counter
        self._tasks[self._task_counter] = task
        self._task_history.append(task)
        return self._task_counter

    def get_task(self, task_id):
        """
        Возвращает задачу по ID.

        Args:
            task_id (int): ID задачи

        Returns:
            Task: Задача или None, если задача не найдена
        """
        return self._tasks.get(task_id)

    def get_task_history(self):
        """
        Возвращает историю задач.

        Returns:
            list: Список всех задач в истории
        """
        return self._task_history.copy()

    def get_all_tasks(self):
        """
        Возвращает все задачи.

        Returns:
            dict: Словарь всех задач {id: task}
        """
        return self._tasks.copy()

    def delete_task(self, task_id):
        """
        Удаляет задачу по ID.

        Args:
            task_id (int): ID задачи для удаления

        Returns:
            bool: True если задача была удалена, False если не найдена
        """
        if task_id in self._tasks:
            del self._tasks[task_id]
            return True
        return False
