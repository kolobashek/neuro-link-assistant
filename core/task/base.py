from core.common.error_handler import handle_error
from core.task.result import TaskResult


class BaseTask:
    """
    Базовая задача для выполнения системой.
    """

    def __init__(self, description, registry):
        """
        Инициализирует задачу.

        Args:
            description (str): Описание задачи
            registry: Реестр компонентов системы
        """
        self.description = description
        self._registry = registry

    def execute(self):
        """
        Выполняет задачу.

        Returns:
            TaskResult: Результат выполнения задачи
        """
        print(f"DEBUG: Выполняется задача: '{self.description}'")

        try:
            # Распознаем тип задачи и выполняем соответствующую операцию
            # Порядок важен: компьютерное зрение -> веб -> Windows -> файловые операции
            if self._is_computer_vision_operation():
                print("DEBUG: Определена как операция компьютерного зрения")
                return self._execute_computer_vision_operation()
            elif self._is_web_operation():
                print("DEBUG: Определена как веб-операция")
                return self._execute_web_operation()
            elif self._is_windows_operation():
                print("DEBUG: Определена как Windows-операция")
                return self._execute_windows_operation()
            elif self._is_file_operation():
                print("DEBUG: Определена как файловая операция")
                return self._execute_file_operation()
            else:
                print("DEBUG: Не распознана как специфичная операция")
                # Возвращаем успешный результат с упоминанием описания для других типов задач
                return TaskResult(True, f"Выполнена задача: {self.description}")
        except Exception as e:
            print(f"DEBUG: Ошибка выполнения: {e}")
            handle_error(f"Error executing task: {e}", e, module="task")
            return TaskResult(False, f"Ошибка выполнения задачи: {str(e)}")

    # Методы будут переопределены в миксинах
    def _is_computer_vision_operation(self):
        """Будет переопределен в VisionOperationsMixin"""
        return False

    def _is_web_operation(self):
        """Будет переопределен в WebOperationsMixin"""
        return False

    def _is_windows_operation(self):
        """Будет переопределен в WindowsOperationsMixin"""
        return False

    def _is_file_operation(self):
        """Будет переопределен в FileOperationsMixin"""
        return False

    def _execute_computer_vision_operation(self):
        """Будет переопределен в VisionOperationsMixin"""
        return TaskResult(False, "Операции компьютерного зрения не реализованы")

    def _execute_web_operation(self):
        """Будет переопределен в WebOperationsMixin"""
        return TaskResult(False, "Веб-операции не реализованы")

    def _execute_windows_operation(self):
        """Будет переопределен в WindowsOperationsMixin"""
        return TaskResult(False, "Windows-операции не реализованы")

    def _execute_file_operation(self):
        """Будет переопределен в FileOperationsMixin"""
        return TaskResult(False, "Файловые операции не реализованы")


# Импортируем миксины
from core.task.file_operations import FileOperationsMixin
from core.task.vision_operations import VisionOperationsMixin
from core.task.web_operations import WebOperationsMixin
from core.task.windows_operations import WindowsOperationsMixin


# Создаем финальный класс Task с миксинами
class Task(
    VisionOperationsMixin, WebOperationsMixin, WindowsOperationsMixin, FileOperationsMixin, BaseTask
):
    """
    Финальный класс Task со всеми миксинами.
    Порядок миксинов важен - VisionOperationsMixin первый для приоритета.
    """

    pass
