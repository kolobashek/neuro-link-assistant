# 2025. All rights reserved.
import platform

from core.common.input.base import InputController
from core.input.input_factory import InputControllerFactory
from core.input.keyboard_controller import KeyboardController
from core.input.mouse_controller import MouseController

# Экспортируем методы фабрики для создания отдельных контроллеров
get_keyboard_controller = InputControllerFactory.get_keyboard_controller
get_mouse_controller = InputControllerFactory.get_mouse_controller


def get_input_controller(human_like: bool = True):
    """
    Возвращает объект контроллера ввода для текущей платформы.

    Args:
        human_like (bool, optional): Флаг, указывающий, должен ли контроллер
                                    имитировать человеческое поведение. По умолчанию True.

    Returns:
        InputController: Экземпляр комбинированного контроллера ввода.

    Raises:
        NotImplementedError: Если текущая платформа не поддерживается.
    """
    system = platform.system().lower()

    if system == "windows":
        # Создаем контроллеры клавиатуры и мыши
        keyboard = KeyboardController(human_like=human_like)
        mouse = MouseController(human_like=human_like)

        # Создаем и возвращаем комбинированный контроллер
        return InputController(keyboard, mouse)
    else:
        raise NotImplementedError(f"Система {system} не поддерживается")
