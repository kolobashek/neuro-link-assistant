class TaskResult:
    """
    Результат выполнения задачи.
    """

    def __init__(self, success, details=""):
        """
        Инициализирует результат задачи.

        Args:
            success (bool): Успешность выполнения
            details (str): Подробности выполнения
        """
        self.success = success
        self.details = details
