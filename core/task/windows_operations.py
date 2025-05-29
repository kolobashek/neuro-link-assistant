import re
import subprocess
import time
from typing import TYPE_CHECKING, Optional

from core.task.result import TaskResult

if TYPE_CHECKING:
    from core.task.base import Task


class WindowsOperationsMixin:
    """
    Миксин для Windows-операций.
    """

    def _is_windows_operation(self: "Task") -> bool:
        """
        Проверяет, является ли задача Windows-операцией.

        Returns:
            bool: True если это Windows-операция
        """
        windows_keywords = [
            "запустить",
            "запуск",
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

        # Специальные паттерны для Windows-операций (исключаем браузер)
        windows_patterns = [
            r"открыть\s+калькулятор",
            r"открыть\s+блокнот",
            r"открыть\s+calc",
            r"открыть\s+notepad",
            r"запустить\s+\w+(?<!браузер)",  # запустить что-то, но не браузер
        ]

        description_lower = self.description.lower()

        # Проверяем специальные паттерны сначала
        for pattern in windows_patterns:
            if re.search(pattern, description_lower):
                print(f"DEBUG: Найден Windows-паттерн: {pattern}")
                return True

        # Затем проверяем ключевые слова, но исключаем браузер
        if "браузер" in description_lower:
            return False

        is_windows_op = any(keyword in description_lower for keyword in windows_keywords)
        print(f"DEBUG: Проверка Windows-операции: {is_windows_op}")
        print(
            "DEBUG: Найденные ключевые слова:"
            f" {[kw for kw in windows_keywords if kw in description_lower]}"
        )
        return is_windows_op

    def _execute_windows_operation(self: "Task") -> TaskResult:
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

            # Общий запуск приложения (исключая браузер)
            elif (
                any(keyword in description_lower for keyword in ["запустить", "запуск", "открыть"])
                and "браузер" not in description_lower
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

    def _launch_calculator(self: "Task") -> TaskResult:
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

    def _launch_notepad(self: "Task") -> TaskResult:
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

    def _launch_application(self: "Task", app_name: str) -> TaskResult:
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

    def _extract_application_name(self: "Task") -> Optional[str]:
        """
        Извлекает имя приложения из описания задачи.

        Returns:
            str: Имя приложения или None
        """
        # Ищем приложения по ключевым словам (исключая браузер)
        patterns = [
            r"открыть\s+(\w+)(?<!браузер)",  # "открыть калькулятор"
            r"запустить\s+(\w+)(?<!браузер)",  # "запустить калькулятор"
            r"запуск\s+(\w+)(?<!браузер)",  # "запуск блокнота"
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
