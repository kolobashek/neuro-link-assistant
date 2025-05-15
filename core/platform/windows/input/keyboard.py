# Windows-специфичная реализация эмуляции клавиатуры

try:
    import pyautogui
except ImportError:
    pyautogui = None

from core.common.error_handler import handle_error
from core.common.input.base import AbstractKeyboard


class WindowsKeyboard(AbstractKeyboard):
    """Реализация эмуляции клавиатуры для Windows с использованием PyAutoGUI"""

    def __init__(self):
        if pyautogui is None:
            handle_error(
                "PyAutoGUI не установлен. Установите его: pip install pyautogui", module="keyboard"
            )

    def press_key(self, key):
        """Нажать клавишу"""
        try:
            if pyautogui:
                pyautogui.keyDown(key)
            return True
        except Exception as e:
            handle_error(f"Ошибка при нажатии клавиши {key}: {e}", e, module="keyboard")
            return False

    def release_key(self, key):
        """Отпустить клавишу"""
        try:
            if pyautogui:
                pyautogui.keyUp(key)
            return True
        except Exception as e:
            handle_error(f"Ошибка при отпускании клавиши {key}: {e}", e, module="keyboard")
            return False

    def type_text(self, text):
        """Напечатать текст"""
        try:
            if pyautogui:
                pyautogui.write(text)
            return True
        except Exception as e:
            handle_error(f"Ошибка при вводе текста: {e}", e, module="keyboard")
            return False

    def hotkey(self, *keys):
        """Нажать комбинацию клавиш"""
        try:
            if pyautogui:
                pyautogui.hotkey(*keys)
            return True
        except Exception as e:
            handle_error(f"Ошибка при нажатии комбинации клавиш {keys}: {e}", e, module="keyboard")
            return False
