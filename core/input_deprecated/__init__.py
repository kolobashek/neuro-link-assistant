# 2025. All rights reserved.
"""
Модуль для работы с устройствами ввода (клавиатура и мышь).
Предоставляет унифицированный интерфейс для управления клавиатурой и мышью.
"""

# Импортируем все необходимые классы и функции из core.common.input
from core.common.input.base import AbstractKeyboard, AbstractMouse, InputController
from core.common.input.factory import get_input_controller as common_get_input_controller
from core.common.input.factory import get_keyboard, get_mouse

# Для обратной совместимости с существующим кодом
from core.platform.windows.input.keyboard import WindowsKeyboard as KeyboardController
from core.platform.windows.input.mouse import WindowsMouse as MouseController


# Переопределяем функцию get_input_controller для сохранения обратной совместимости
def get_input_controller(human_like: bool = True, new_instance: bool = False):
    """
    Возвращает объект контроллера ввода для текущей платформы.

    Args:
        human_like (bool, optional): Флаг, указывающий, должен ли контроллер
                                    имитировать человеческое поведение. По умолчанию True.
        new_instance (bool, optional): Флаг, указывающий, нужно ли создать новый
                                      экземпляр. По умолчанию False.

    Returns:
        InputController: Экземпляр комбинированного контроллера ввода.

    Raises:
        NotImplementedError: Если текущая платформа не поддерживается.
    """
    return common_get_input_controller(human_like, new_instance)


__all__ = [
    "AbstractKeyboard",
    "AbstractMouse",
    "InputController",
    "KeyboardController",
    "MouseController",
    "get_keyboard",
    "get_mouse",
    "get_input_controller",
]
