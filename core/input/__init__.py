# 2025. All rights reserved.
"""
Модуль для работы с устройствами ввода (клавиатура и мышь).
Предоставляет унифицированный интерфейс для управления клавиатурой и мышью.
"""

from core.common.input.base import AbstractKeyboard, AbstractMouse, InputController
from core.input.factory import get_keyboard, get_mouse


# Переопределяем документацию функции get_input_controller для лучшей читаемости
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
    from core.input.factory import get_input_controller as factory_get_input_controller

    return factory_get_input_controller(human_like, new_instance)


__all__ = [
    "AbstractKeyboard",
    "AbstractMouse",
    "InputController",
    "get_keyboard",
    "get_mouse",
    "get_input_controller",
]
