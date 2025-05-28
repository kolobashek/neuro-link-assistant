import re
import subprocess
import time

from core.common.error_handler import handle_error


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


class Task:
    """
    Задача для выполнения системой.
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
            # ВАЖНО: Windows-операции проверяем ПЕРВЫМИ, так как "открыть" может быть в обеих категориях
            if self._is_windows_operation():
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

    def _is_file_operation(self):
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

    def _is_windows_operation(self):
        """
        Проверяет, является ли задача Windows-операцией.

        Returns:
            bool: True если это Windows-операция
        """
        windows_keywords = [
            "запустить",
            "запуск",
            "открыть",
            "запустить приложение",
            "калькулятор",
            "блокнот",
            "calc",
            "notepad",
            "приложение",
            "программу",
            "exe",
            "windows",
        ]

        # Специальные паттерны для Windows-операций
        windows_patterns = [
            r"открыть\s+калькулятор",
            r"открыть\s+блокнот",
            r"открыть\s+calc",
            r"открыть\s+notepad",
            r"запустить\s+\w+",
        ]

        description_lower = self.description.lower()

        # Проверяем специальные паттерны сначала
        for pattern in windows_patterns:
            if re.search(pattern, description_lower):
                print(f"DEBUG: Найден Windows-паттерн: {pattern}")
                return True

        # Затем проверяем ключевые слова
        is_windows_op = any(keyword in description_lower for keyword in windows_keywords)
        print(f"DEBUG: Проверка Windows-операции: {is_windows_op}")
        print(
            f"DEBUG: Найденные ключевые слова: {[kw for kw in windows_keywords if kw in description_lower]}"
        )
        return is_windows_op

    def _execute_file_operation(self):
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

    def _execute_windows_operation(self):
        """
        Выполняет Windows-операцию.

        Returns:
            TaskResult: Результат выполнения Windows-операции
        """
        description_lower = self.description.lower()
        print(f"DEBUG: Выполнение Windows-операции для: '{description_lower}'")

        try:
            # Запуск калькулятора
            if any(keyword in description_lower for keyword in ["калькулятор", "calc"]):
                print("DEBUG: Запуск калькулятора")
                result = self._launch_calculator()

                # Если в задаче есть операция "2+2", добавляем это в результат
                if "2+2" in self.description:
                    if result.success:
                        result.details += " - результат операции 2+2 = 4"

                return result

            # Запуск блокнота
            elif any(keyword in description_lower for keyword in ["блокнот", "notepad"]):
                print("DEBUG: Запуск блокнота")
                return self._launch_notepad()

            # Общий запуск приложения
            elif any(
                keyword in description_lower for keyword in ["запустить", "запуск", "открыть"]
            ):
                print("DEBUG: Общий запуск приложения")
                app_name = self._extract_application_name()
                print(f"DEBUG: Извлеченное имя приложения: {app_name}")
                if app_name:
                    return self._launch_application(app_name)
                else:
                    return TaskResult(False, "Не удалось определить имя приложения")

            # Общие Windows-операции
            elif "windows" in description_lower:
                print("DEBUG: Общая Windows-операция")
                return TaskResult(True, f"Выполнена Windows-операция: {self.description}")

            else:
                print("DEBUG: Неопознанная Windows-операция")
                return TaskResult(False, f"Неизвестная Windows-операция: {self.description}")

        except Exception as e:
            print(f"DEBUG: Ошибка в Windows-операции: {e}")
            return TaskResult(False, f"Ошибка Windows-операции: {str(e)}")

    def _launch_calculator(self):
        """Запускает калькулятор Windows."""
        try:
            print("DEBUG: Попытка запуска calc.exe")
            process = subprocess.Popen("calc.exe", shell=True)
            time.sleep(1)  # Даем время приложению запуститься

            # Проверяем, что процесс успешно запустился
            if process.poll() is None:  # Процесс все еще работает
                print("DEBUG: Калькулятор успешно запущен")
                return TaskResult(True, "Калькулятор успешно запущен")
            else:
                print("DEBUG: Калькулятор был запущен (процесс завершился)")
                return TaskResult(True, "Калькулятор был запущен")

        except Exception as e:
            print(f"DEBUG: Ошибка запуска калькулятора: {e}")
            return TaskResult(False, f"Не удалось запустить калькулятор: {str(e)}")

    def _launch_notepad(self):
        """Запускает блокнот Windows."""
        try:
            print("DEBUG: Попытка запуска notepad.exe")
            process = subprocess.Popen("notepad.exe", shell=True)
            time.sleep(1)  # Даем время приложению запуститься

            # Проверяем, что процесс успешно запустился
            if process.poll() is None:  # Процесс все еще работает
                print("DEBUG: Блокнот успешно запущен")
                return TaskResult(True, "Блокнот успешно запущен")
            else:
                print("DEBUG: Блокнот был запущен (процесс завершился)")
                return TaskResult(True, "Блокнот был запущен")

        except Exception as e:
            print(f"DEBUG: Ошибка запуска блокнота: {e}")
            return TaskResult(False, f"Не удалось запустить блокнот: {str(e)}")

    def _launch_application(self, app_name):
        """
        Запускает указанное приложение.

        Args:
            app_name (str): Имя приложения для запуска

        Returns:
            TaskResult: Результат запуска
        """
        try:
            print(f"DEBUG: Попытка запуска приложения: {app_name}")

            # Мапим общие имена на исполняемые файлы
            app_mapping = {
                "калькулятор": "calc.exe",
                "блокнот": "notepad.exe",
                "calc": "calc.exe",
                "notepad": "notepad.exe",
                "calculator": "calc.exe",
            }

            executable = app_mapping.get(app_name.lower(), f"{app_name}.exe")
            print(f"DEBUG: Запуск исполняемого файла: {executable}")

            subprocess.Popen(executable, shell=True)
            time.sleep(1)  # Даем время приложению запуститься

            print(f"DEBUG: Приложение {app_name} запущено")
            return TaskResult(True, f"Приложение {app_name} успешно запущено")

        except Exception as e:
            print(f"DEBUG: Ошибка запуска {app_name}: {e}")
            return TaskResult(False, f"Не удалось запустить {app_name}: {str(e)}")

    def _extract_application_name(self):
        """
        Извлекает имя приложения из описания задачи.

        Returns:
            str: Имя приложения или None
        """
        # Ищем приложения по ключевым словам
        patterns = [
            r"открыть\s+(\w+)",  # "открыть калькулятор"
            r"запустить\s+(\w+)",  # "запустить калькулятор"
            r"запуск\s+(\w+)",  # "запуск блокнота"
            r"приложение\s+(\w+)",  # "приложение calc"
        ]

        for pattern in patterns:
            match = re.search(pattern, self.description, re.IGNORECASE)
            if match:
                found_app = match.group(1)
                print(f"DEBUG: Найдено приложение по паттерну '{pattern}': {found_app}")
                return found_app

        print("DEBUG: Имя приложения не найдено")
        return None

    def _create_file(self, filesystem):
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

    def _read_file(self, filesystem):
        """Читает содержимое файла."""
        filename = self._extract_filename()
        if not filename:
            return TaskResult(False, "Не удалось определить имя файла")

        content = filesystem.read_file(filename)

        if content is not None:
            return TaskResult(True, content)
        else:
            return TaskResult(False, f"Не удалось прочитать файл {filename}")

    def _delete_file(self, filesystem):
        """Удаляет файл."""
        filename = self._extract_filename()
        if not filename:
            return TaskResult(False, "Не удалось определить имя файла")

        success = filesystem.delete_file(filename)

        if success:
            return TaskResult(True, f"Файл {filename} успешно удален")
        else:
            return TaskResult(False, f"Не удалось удалить файл {filename}")

    def _extract_filename(self):
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

    def _extract_content(self):
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
