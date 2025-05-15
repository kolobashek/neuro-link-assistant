import logging
import os
import time

import pyautogui
import win32gui

logger = logging.getLogger("neuro_assistant")


def open_calculator():
    """Открыть калькулятор"""
    os.system("calc")
    return "Калькулятор открыт"


def calculate_expression(expression):
    """
    Вычисляет выражение с помощью калькулятора Windows

    Args:
        expression: Математическое выражение для вычисления

    Returns:
        Строка с результатом вычисления
    """
    # Открываем калькулятор
    os.system("calc")
    time.sleep(1)  # Ждем открытия калькулятора

    # Находим окно калькулятора и активируем его
    calc_window = win32gui.FindWindow(None, "Калькулятор")
    if calc_window == 0:  # Если не нашли по русскому названию
        calc_window = win32gui.FindWindow(None, "Calculator")

    if calc_window != 0:
        # Активируем окно калькулятора
        win32gui.SetForegroundWindow(calc_window)
        time.sleep(0.5)  # Даем время на активацию окна

        # Очищаем калькулятор
        pyautogui.press("escape")

        # Вводим выражение
        for char in expression:
            if char == "+":
                pyautogui.press("+")
            elif char == "-":
                pyautogui.press("-")
            elif char == "*":
                pyautogui.press("*")
            elif char == "/":
                pyautogui.press("/")
            else:
                pyautogui.press(char)

        # Нажимаем Enter для вычисления
        pyautogui.press("enter")

        # Даем время на вычисление
        time.sleep(0.5)

        return f"Вычислено выражение {expression} в калькуляторе"
    else:
        return "Не удалось найти окно калькулятора"


# Базовые приложения Windows
def open_notepad():
    """Открыть блокнот"""
    os.system("notepad")
    return "Блокнот открыт"


def open_explorer(path=None):
    """Открыть проводник"""
    if path:
        os.system(f'explorer "{path}"')
    else:
        os.system("explorer")
    return "Проводник открыт"


def open_control_panel():
    """Открыть панель управления"""
    os.system("control")
    return "Панель управления открыта"


def open_settings():
    """Открыть настройки Windows"""
    os.system("start ms-settings:")
    return "Настройки Windows открыты"


def open_task_manager():
    """Открыть диспетчер задач"""
    os.system("taskmgr")
    return "Диспетчер задач открыт"


def open_command_prompt(admin=False):
    """Открыть командную строку"""
    if admin:
        os.system("powershell Start-Process cmd -Verb RunAs")
    else:
        os.system("start cmd")
    return "Командная строка открыта"


def open_powershell(admin=False):
    """Открыть PowerShell"""
    if admin:
        os.system("powershell Start-Process powershell -Verb RunAs")
    else:
        os.system("start powershell")
    return "PowerShell открыт"


# Функции калькулятора
def convert_units(value, from_unit, to_unit):
    """Конвертировать величину из одних единиц в другие"""
    # Реализация конвертации единиц (упрощенно)
    return f"Конвертация {value} из {from_unit} в {to_unit}"


def calculate_date_difference(date1, date2):
    """Вычислить разницу между двумя датами"""
    # Реализация расчета разницы дат
    return f"Разница между {date1} и {date2}"


# Сторонние приложения
def open_word(file_path=None):
    """Открыть Microsoft Word"""
    if file_path:
        os.system(f'start winword.exe "{file_path}"')
    else:
        os.system("start winword.exe")
    return "Microsoft Word открыт"


def open_excel(file_path=None):
    """Открыть Microsoft Excel"""
    if file_path:
        os.system(f'start excel.exe "{file_path}"')
    else:
        os.system("start excel.exe")
    return "Microsoft Excel открыт"


def open_vlc(file_path=None):
    """Открыть VLC Media Player"""
    if file_path:
        os.system(f'start vlc.exe "{file_path}"')
    else:
        os.system("start vlc.exe")
    return "VLC Media Player открыт"


def open_custom_application(path, args=None):
    """Открыть произвольное приложение по пути"""
    if args:
        os.system(f'start "" "{path}" {args}')
    else:
        os.system(f'start "" "{path}"')
    return f"Приложение {path} открыто"


def get_commands():
    """
    Возвращает словарь команд модуля

    Returns:
        dict: Словарь с соответствием названий команд функциям
    """
    return {
        "открыть калькулятор": open_calculator,
        "вычислить": calculate_expression,
        "открыть блокнот": open_notepad,
        "открыть проводник": open_explorer,
        "открыть панель управления": open_control_panel,
        "открыть настройки": open_settings,
        "открыть диспетчер задач": open_task_manager,
        "открыть командную строку": open_command_prompt,
        "открыть powershell": open_powershell,
        "конвертировать единицы": convert_units,
        "разница между датами": calculate_date_difference,
        "открыть word": open_word,
        "открыть excel": open_excel,
        "открыть vlc": open_vlc,
        "открыть приложение": open_custom_application,
    }


def get_aliases():
    """
    Возвращает словарь псевдонимов команд модуля

    Returns:
        dict: Словарь с соответствием псевдонимов оригинальным командам
    """
    return {
        "калькулятор": "открыть калькулятор",
        "блокнот": "открыть блокнот",
        "проводник": "открыть проводник",
        "диспетчер задач": "открыть диспетчер задач",
        "cmd": "открыть командную строку",
        "word": "открыть word",
        "excel": "открыть excel",
    }


def get_intents():
    """
    Возвращает словарь намерений команд модуля

    Returns:
        dict: Словарь с группировкой команд по намерениям
    """
    return {
        "приложения": [
            "открыть калькулятор",
            "открыть блокнот",
            "открыть проводник",
            "открыть панель управления",
            "открыть настройки",
            "открыть диспетчер задач",
            "открыть командную строку",
            "открыть powershell",
            "открыть word",
            "открыть excel",
            "открыть vlc",
            "открыть приложение",
        ],
        "расчеты": [
            "вычислить",
            "конвертировать единицы",
            "разница между датами",
        ],
    }


def get_categories():
    """
    Возвращает словарь категорий команд модуля

    Returns:
        dict: Словарь с группировкой намерений по категориям
    """
    return {"Приложения": ["приложения", "расчеты"]}
