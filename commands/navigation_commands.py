import logging

import pyautogui

logger = logging.getLogger("neuro_assistant")


# Перемещение по приложениям
def switch_to_application(app_name):
    """Переключиться на указанное приложение"""
    pyautogui.hotkey("alt", "tab")
    pyautogui.write(app_name)
    pyautogui.press("enter")


def switch_to_next_window():
    """Переключиться на следующее окно (Alt+Tab)"""


def switch_to_previous_window():
    """Переключиться на предыдущее окно (Alt+Shift+Tab)"""


def list_open_windows():
    """Показать список открытых окон"""


# Навигация по рабочим столам
def switch_to_desktop(desktop_number):
    """Переключиться на виртуальный рабочий стол"""


def create_virtual_desktop():
    """Создать новый виртуальный рабочий стол"""


def close_virtual_desktop():
    """Закрыть текущий виртуальный рабочий стол"""


# Навигация по веб-страницам
def open_tab(url=None):
    """Открыть новую вкладку в браузере"""


def close_tab():
    """Закрыть текущую вкладку"""


def switch_to_tab(tab_number):
    """Переключиться на вкладку по номеру"""


def switch_to_next_tab():
    """Переключиться на следующую вкладку"""


def switch_to_previous_tab():
    """Переключиться на предыдущую вкладку"""
