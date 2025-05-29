"""
Реализация клавиатуры для Windows.
"""

import ctypes
import random
import time
from typing import List, Optional

import win32api
import win32clipboard
import win32con

from core.common.error_handler import handle_error
from core.common.input.base import AbstractKeyboard

# Константы клавиш и словарь для преобразования строковых имён клавиш в коды
VK_CODES = {
    "backspace": 0x08,
    "tab": 0x09,
    "enter": 0x0D,
    "shift": 0x10,
    "ctrl": 0x11,
    "alt": 0x12,
    "pause": 0x13,
    "caps_lock": 0x14,
    "esc": 0x1B,
    "space": 0x20,
    "page_up": 0x21,
    "page_down": 0x22,
    "end": 0x23,
    "home": 0x24,
    "left": 0x25,
    "up": 0x26,
    "right": 0x27,
    "down": 0x28,
    "print_screen": 0x2C,
    "insert": 0x2D,
    "delete": 0x2E,
    "0": 0x30,
    "1": 0x31,
    "2": 0x32,
    "3": 0x33,
    "4": 0x34,
    "5": 0x35,
    "6": 0x36,
    "7": 0x37,
    "8": 0x38,
    "9": 0x39,
    "a": 0x41,
    "b": 0x42,
    "c": 0x43,
    "d": 0x44,
    "e": 0x45,
    "f": 0x46,
    "g": 0x47,
    "h": 0x48,
    "i": 0x49,
    "j": 0x4A,
    "k": 0x4B,
    "l": 0x4C,
    "m": 0x4D,
    "n": 0x4E,
    "o": 0x4F,
    "p": 0x50,
    "q": 0x51,
    "r": 0x52,
    "s": 0x53,
    "t": 0x54,
    "u": 0x55,
    "v": 0x56,
    "w": 0x57,
    "x": 0x58,
    "y": 0x59,
    "z": 0x5A,
    "win": 0x5B,
    "f1": 0x70,
    "f2": 0x71,
    "f3": 0x72,
    "f4": 0x73,
    "f5": 0x74,
    "f6": 0x75,
    "f7": 0x76,
    "f8": 0x77,
    "f9": 0x78,
    "f10": 0x79,
    "f11": 0x7A,
    "f12": 0x7B,
}


class WindowsKeyboard(AbstractKeyboard):
    """Реализация клавиатуры для операционной системы Windows."""

    def __init__(self, human_like: bool = True):
        """
        Инициализирует контроллер клавиатуры.

        Args:
            human_like (bool): Флаг, указывающий, нужно ли эмулировать человеческое поведение.
        """
        self.human_like = human_like
        self.controller = None  # Для тестирования будет заменено моком

        # Настройки для эмуляции поведения человека
        self.min_press_delay = 0.05  # минимальная задержка между нажатиями
        self.max_press_delay = 0.2  # максимальная задержка между нажатиями

        # Константы для SendInput
        self.PUL = ctypes.POINTER(ctypes.c_ulong)
        self.INPUT_KEYBOARD = 1

    def _get_code(self, key: str) -> int:
        """
        Возвращает код клавиши для Windows.

        Args:
            key (str): Имя клавиши.

        Returns:
            int: Код клавиши.

        Raises:
            ValueError: Если клавиша не найдена.
        """
        key = key.lower()

        if key in VK_CODES:
            return VK_CODES[key]
        else:
            # Если это одиночный символ, попробуем получить его виртуальный код
            if len(key) == 1:
                try:
                    return ord(key.upper())
                except Exception:
                    pass

            raise ValueError(f"Неизвестная клавиша: {key}")

    def _human_delay(self) -> None:
        """
        Создает задержку для имитации человеческого поведения.
        """
        if self.human_like:
            delay = random.uniform(self.min_press_delay, self.max_press_delay)
            time.sleep(delay)

    def _send_input(self, input_structure) -> None:
        """
        Отправляет ввод с клавиатуры через SendInput API.

        Args:
            input_structure: Структура ввода для SendInput.
        """
        # Отправляем ввод
        ctypes.windll.user32.SendInput(
            1, ctypes.pointer(input_structure), ctypes.sizeof(input_structure)
        )

    def press_key(self, key: str) -> bool:
        """
        Нажимает клавишу и сразу отпускает её.

        Args:
            key (str): Клавиша для нажатия.

        Returns:
            bool: True если успешно, иначе False.
        """
        try:
            # Получаем код клавиши
            key_code = self._get_code(key)

            # Нажимаем клавишу
            win32api.keybd_event(key_code, 0, 0, 0)

            # Небольшая задержка для правдоподобности
            self._human_delay()

            # Отпускаем клавишу
            win32api.keybd_event(key_code, 0, win32con.KEYEVENTF_KEYUP, 0)

            return True
        except Exception as e:
            handle_error(f"Ошибка при нажатии клавиши {key}: {e}", e)
            return False

    def press_keys(self, keys: List[str]) -> bool:
        """
        Нажимает комбинацию клавиш.

        Args:
            keys (List[str]): Список клавиш для нажатия.

        Returns:
            bool: True если успешно, иначе False.
        """
        try:
            # Получаем коды клавиш
            key_codes = [self._get_code(key) for key in keys]

            # Нажимаем все клавиши
            for key_code in key_codes:
                win32api.keybd_event(key_code, 0, 0, 0)
                self._human_delay()

            # Небольшая задержка для правдоподобности
            time.sleep(0.1)

            # Отпускаем клавиши в обратном порядке
            for key_code in reversed(key_codes):
                win32api.keybd_event(key_code, 0, win32con.KEYEVENTF_KEYUP, 0)
                self._human_delay()

            return True
        except Exception as e:
            handle_error(f"Ошибка при нажатии комбинации клавиш {keys}: {e}", e)
            return False

    def key_down(self, key: str) -> bool:
        """
        Удерживает клавишу нажатой.

        Args:
            key (str): Клавиша для удержания.

        Returns:
            bool: True если успешно, иначе False.
        """
        try:
            # Получаем код клавиши
            key_code = self._get_code(key)

            # Нажимаем клавишу
            win32api.keybd_event(key_code, 0, 0, 0)

            return True
        except Exception as e:
            handle_error(f"Ошибка при удержании клавиши {key}: {e}", e)
            return False

    def key_up(self, key: str) -> bool:
        """
        Отпускает удерживаемую клавишу.

        Args:
            key (str): Клавиша для отпускания.

        Returns:
            bool: True если успешно, иначе False.
        """
        try:
            # Получаем код клавиши
            key_code = self._get_code(key)

            # Отпускаем клавишу
            win32api.keybd_event(key_code, 0, win32con.KEYEVENTF_KEYUP, 0)

            return True
        except Exception as e:
            handle_error(f"Ошибка при отпускании клавиши {key}: {e}", e)
            return False

    def type_text(self, text: str, interval: Optional[float] = None) -> bool:
        """
        Вводит текст с указанным интервалом между нажатиями.

        Args:
            text (str): Текст для ввода.
            interval (Optional[float]): Интервал между нажатиями в секундах.

        Returns:
            bool: True если успешно, иначе False.
        """
        try:
            for char in text:
                # Определяем, нужна ли клавиша Shift для верхнего регистра или специальных символов
                if char.isupper() or char in '~!@#$%^&*()_+{}|:"<>?':
                    self.key_down("shift")
                    self._human_delay()

                    # Для специальных символов с Shift нужно преобразовать их в нижний регистр
                    if char in '~!@#$%^&*()_+{}|:"<>?':
                        char_map = {
                            "~": "`",
                            "!": "1",
                            "@": "2",
                            "#": "3",
                            "$": "4",
                            "%": "5",
                            "^": "6",
                            "&": "7",
                            "*": "8",
                            "(": "9",
                            ")": "0",
                            "_": "-",
                            "+": "=",
                            "{": "[",
                            "}": "]",
                            "|": "\\",
                            ":": ";",
                            '"': "'",
                            "<": ",",
                            ">": ".",
                            "?": "/",
                        }
                        char = char_map.get(char, char)
                    else:
                        char = char.lower()

                    self.press_key(char)
                    self.key_up("shift")
                else:
                    # Для пробела используем специальную клавишу
                    if char == " ":
                        self.press_key("space")
                    else:
                        self.press_key(char)

                # Ждем указанный интервал или используем человекоподобную задержку
                if interval:
                    time.sleep(interval)
                elif self.human_like:
                    self._human_delay()

            return True
        except Exception as e:
            handle_error(f"Ошибка при вводе текста: {e}", e)
            return False

    def paste_text(self, text: str) -> bool:
        """
        Вставляет текст через буфер обмена.

        Args:
            text (str): Текст для вставки.

        Returns:
            bool: True если успешно, иначе False.
        """
        try:
            # Открываем буфер обмена и очищаем его
            win32clipboard.OpenClipboard()
            win32clipboard.EmptyClipboard()

            # Устанавливаем новый текст в буфер обмена
            win32clipboard.SetClipboardText(text, win32clipboard.CF_UNICODETEXT)
            win32clipboard.CloseClipboard()

            # Нажимаем Ctrl+V для вставки
            self.press_keys(["ctrl", "v"])

            return True
        except Exception as e:
            handle_error(f"Ошибка при вставке текста через буфер обмена: {e}", e)

            # Убедимся, что буфер обмена закрыт
            try:
                win32clipboard.CloseClipboard()
            except Exception:
                pass

            return False

    def press_enter(self) -> bool:
        """
        Нажимает клавишу Enter.

        Returns:
            bool: True если успешно, иначе False.
        """
        return self.press_key("enter")

    def press_ctrl_c(self) -> bool:
        """
        Нажимает комбинацию клавиш Ctrl+C.

        Returns:
            bool: True если успешно, иначе False.
        """
        return self.press_keys(["ctrl", "c"])
