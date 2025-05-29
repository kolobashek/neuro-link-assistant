import re
from typing import TYPE_CHECKING

from core.task.result import TaskResult

if TYPE_CHECKING:
    from core.task.base import Task


class FileOperationsMixin:
    """
    Миксин для файловых операций.
    """

    def _is_file_operation(self: "Task") -> bool:
        """
        Проверяет, является ли задача файловой операцией.

        Returns:
            bool: True если это файловая операция
        """
        file_keywords = [
            "создать файл",
            "создать",
            "записать",
            "написать",
            "прочитать",
            "читать",
            "удалить файл",
            "удалить",
            "стереть",
            "файл",
            ".txt",
            ".json",
            ".csv",
        ]

        description_lower = self.description.lower()
        is_file_op = any(keyword in description_lower for keyword in file_keywords)
        print(f"DEBUG: Проверка файловой операции: {is_file_op}")
        return is_file_op

    def _execute_file_operation(self: "Task") -> TaskResult:
        """
        Выполняет файловую операцию.

        Returns:
            TaskResult: Результат выполнения файловой операции
        """
        filesystem = self._registry.get("filesystem")
        if not filesystem:
            return TaskResult(False, "Файловая система не доступна")

        description_lower = self.description.lower()

        try:
            # Создание файла
            if any(keyword in description_lower for keyword in ["создать файл", "создать"]):
                return self._create_file(filesystem)

            # Чтение файла
            elif any(keyword in description_lower for keyword in ["прочитать", "читать"]):
                return self._read_file(filesystem)

            # Удаление файла
            elif any(
                keyword in description_lower for keyword in ["удалить файл", "удалить", "стереть"]
            ):
                return self._delete_file(filesystem)

            else:
                return TaskResult(False, f"Неизвестная файловая операция: {self.description}")

        except Exception as e:
            return TaskResult(False, f"Ошибка файловой операции: {str(e)}")

    def _create_file(self: "Task", filesystem) -> TaskResult:
        """Создает файл с содержимым."""
        # Извлекаем имя файла из описания
        filename = self._extract_filename()
        if not filename:
            return TaskResult(False, "Не удалось определить имя файла")

        # Извлекаем содержимое из описания
        content = self._extract_content()

        # Создаем файл
        success = filesystem.create_file(filename, content)

        if success:
            return TaskResult(True, f"Файл {filename} успешно создан с содержимым: {content}")
        else:
            return TaskResult(False, f"Не удалось создать файл {filename}")

    def _read_file(self: "Task", filesystem) -> TaskResult:
        """Читает содержимое файла."""
        filename = self._extract_filename()
        if not filename:
            return TaskResult(False, "Не удалось определить имя файла")

        content = filesystem.read_file(filename)

        if content is not None:
            return TaskResult(True, content)
        else:
            return TaskResult(False, f"Не удалось прочитать файл {filename}")

    def _delete_file(self: "Task", filesystem) -> TaskResult:
        """Удаляет файл."""
        filename = self._extract_filename()
        if not filename:
            return TaskResult(False, "Не удалось определить имя файла")

        success = filesystem.delete_file(filename)

        if success:
            return TaskResult(True, f"Файл {filename} успешно удален")
        else:
            return TaskResult(False, f"Не удалось удалить файл {filename}")

    def _extract_filename(self: "Task") -> str:
        """
        Извлекает имя файла из описания задачи.

        Returns:
            str: Имя файла или None
        """
        # Ищем файлы с расширениями
        patterns = [
            r"(\w+\.\w+)",  # filename.ext
            r"файл\s+(\S+)",  # "файл filename"
            r"файла\s+(\S+)",  # "файла filename"
        ]

        for pattern in patterns:
            match = re.search(pattern, self.description, re.IGNORECASE)
            if match:
                return match.group(1)

        return None

    def _extract_content(self: "Task") -> str:
        """
        Извлекает содержимое для записи в файл из описания задачи.

        Returns:
            str: Содержимое для записи
        """
        # Ищем содержимое в кавычках
        patterns = [
            r"'([^']*)'",  # содержимое в одинарных кавычках
            r'"([^"]*)"',  # содержимое в двойных кавычках
            r'текстом\s+["\']?([^"\']*)["\']?',  # "с текстом ..."
        ]

        for pattern in patterns:
            match = re.search(pattern, self.description, re.IGNORECASE)
            if match:
                return match.group(1)

        # Если не найдено в кавычках, возвращаем пустую строку
        return ""
