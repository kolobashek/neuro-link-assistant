# 2025. All rights reserved.
import platform

from core.common.input.base import InputController


def get_input_controller():
    """Возвращает объект контроллера ввода"""
    system = platform.system().lower()

    if system == "windows":
        from core.platform.windows.input.keyboard import WindowsKeyboard
        from core.platform.windows.input.mouse import WindowsMouse

        return InputController(WindowsKeyboard(), WindowsMouse())
    else:
        raise NotImplementedError(f"Система {system} не поддерживается")
