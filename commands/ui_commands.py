import logging

import pyautogui

logger = logging.getLogger("neuro_assistant")


# Управление мышью
def move_mouse(x, y):
    """Переместить курсор мыши в указанную позицию"""
    pyautogui.moveTo(x, y)


def click_mouse(x=None, y=None, button="left"):
    """Кликнуть мышью в текущей или указанной позиции"""


def double_click(x=None, y=None):
    """Двойной клик мышью"""


def right_click(x=None, y=None):
    """Клик правой кнопкой мыши"""


def drag_mouse(start_x, start_y, end_x, end_y):
    """Перетащить элемент мышью"""


def scroll_up(clicks=3):
    """Прокрутить колесо мыши вверх"""


def scroll_down(clicks=3):
    """Прокрутить колесо мыши вниз"""


# Управление клавиатурой
def type_text(text):
    """Ввести текст"""


def press_key(key):
    """Нажать клавишу"""


def hotkey(*keys):
    """Нажать комбинацию клавиш"""


def copy():
    """Копировать (Ctrl+C)"""


def cut():
    """Вырезать (Ctrl+X)"""


def paste():
    """Вставить (Ctrl+V)"""


def select_all():
    """Выделить всё (Ctrl+A)"""


# Элементы интерфейса
def find_element_by_image(image_path):
    """Найти элемент по изображению"""


def find_element_by_text(text):
    """Найти элемент по тексту"""


def wait_for_element(image_path, timeout=10):
    """Ожидать появления элемента"""


def interact_with_element(element, action="click"):
    """Взаимодействовать с элементом интерфейса"""


def get_commands():
    return {
        "переместить мышь": move_mouse,
        "кликнуть": click_mouse,
        "двойной клик": double_click,
        "правый клик": right_click,
        "перетащить": drag_mouse,
        "прокрутить вверх": scroll_up,
        "прокрутить вниз": scroll_down,
        "ввести текст": type_text,
        "нажать клавишу": press_key,
        "нажать комбинацию": hotkey,
        "копировать": copy,
        "вырезать": cut,
        "вставить": paste,
        "выделить всё": select_all,
        "найти элемент по изображению": find_element_by_image,
        "найти элемент по тексту": find_element_by_text,
        "дождаться элемент": wait_for_element,
    }


def get_aliases():
    return {
        "клик": "кликнуть",
        "нажать": "кликнуть",
        "двойной щелчок": "двойной клик",
        "щелкнуть правой кнопкой": "правый клик",
        "перетянуть": "перетащить",
        "напечатать": "ввести текст",
    }


def get_intents():
    return {
        "управление_мышью": [
            "переместить мышь",
            "кликнуть",
            "двойной клик",
            "правый клик",
            "перетащить",
            "прокрутить вверх",
            "прокрутить вниз",
        ],
        "управление_клавиатурой": [
            "ввести текст",
            "нажать клавишу",
            "нажать комбинацию",
            "копировать",
            "вырезать",
            "вставить",
            "выделить всё",
        ],
        "поиск_элементов": [
            "найти элемент по изображению",
            "найти элемент по тексту",
            "дождаться элемент",
        ],
    }


def get_categories():
    return {"Интерфейс": ["управление_мышью", "управление_клавиатурой", "поиск_элементов"]}
