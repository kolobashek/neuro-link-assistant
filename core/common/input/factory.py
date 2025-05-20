"""
Фабрика для создания контроллеров ввода.
Предоставляет методы для получения реализаций клавиатуры и мыши.
"""

import platform
from typing import Type

from core.common.input.base import AbstractKeyboard, AbstractMouse, InputController

# Словарь зарегистрированных реализаций клавиатуры
_keyboard_implementations = {}

# Словарь зарегистрированных реализаций мыши
_mouse_implementations = {}

# Глобальные экземпляры контроллеров
_keyboard_instance = None
_mouse_instance = None
_input_controller_instance = None


def register_keyboard(platform_name: str, implementation: Type[AbstractKeyboard]) -> None:
    """
    Регистрирует реализацию клавиатуры для указанной платформы.

    Args:
        platform_name (str): Имя платформы ("windows", "linux", "darwin").
        implementation (Type[AbstractKeyboard]): Класс реализации клавиатуры.
    """
    _keyboard_implementations[platform_name.lower()] = implementation


def register_mouse(platform_name: str, implementation: Type[AbstractMouse]) -> None:
    """
    Регистрирует реализацию мыши для указанной платформы.

    Args:
        platform_name (str): Имя платформы ("windows", "linux", "darwin").
        implementation (Type[AbstractMouse]): Класс реализации мыши.
    """
    _mouse_implementations[platform_name.lower()] = implementation


def get_keyboard(human_like: bool = True, new_instance: bool = False) -> AbstractKeyboard:
    """
    Получает экземпляр контроллера клавиатуры для текущей платформы.

    Args:
        human_like (bool): Флаг, указывающий, нужно ли эмулировать человеческое поведение.
        new_instance (bool): Флаг, указывающий, нужно ли создать новый экземпляр.

    Returns:
        AbstractKeyboard: Экземпляр контроллера клавиатуры.

    Raises:
        NotImplementedError: Если реализация для текущей платформы не найдена.
    """
    global _keyboard_instance

    # Если нужен новый экземпляр или экземпляр еще не создан
    if new_instance or _keyboard_instance is None:
        platform_name = platform.system().lower()

        # Получаем реализацию для текущей платформы
        keyboard_class = _keyboard_implementations.get(platform_name)
        if keyboard_class is None:
            raise NotImplementedError(
                f"Контроллер клавиатуры для платформы {platform_name} не реализован"
            )

        # Создаем новый экземпляр
        _keyboard_instance = keyboard_class(human_like=human_like)

    return _keyboard_instance


def get_mouse(human_like: bool = True, new_instance: bool = False) -> AbstractMouse:
    """
    Получает экземпляр контроллера мыши для текущей платформы.

    Args:
        human_like (bool): Флаг, указывающий, нужно ли эмулировать человеческое поведение.
        new_instance (bool): Флаг, указывающий, нужно ли создать новый экземпляр.

    Returns:
        AbstractMouse: Экземпляр контроллера мыши.

    Raises:
        NotImplementedError: Если реализация для текущей платформы не найдена.
    """
    global _mouse_instance

    # Если нужен новый экземпляр или экземпляр еще не создан
    if new_instance or _mouse_instance is None:
        platform_name = platform.system().lower()

        # Получаем реализацию для текущей платформы
        mouse_class = _mouse_implementations.get(platform_name)
        if mouse_class is None:
            raise NotImplementedError(
                f"Контроллер мыши для платформы {platform_name} не реализован"
            )

        # Создаем новый экземпляр
        _mouse_instance = mouse_class(human_like=human_like)

    return _mouse_instance


def get_input_controller(human_like: bool = True, new_instance: bool = False) -> InputController:
    """
    Получает экземпляр контроллера ввода для текущей платформы.

    Args:
        human_like (bool): Флаг, указывающий, нужно ли эмулировать человеческое поведение.
        new_instance (bool): Флаг, указывающий, нужно ли создать новый экземпляр.

    Returns:
        InputController: Экземпляр контроллера ввода.
    """
    global _input_controller_instance

    # Если нужен новый экземпляр или экземпляр еще не создан
    if new_instance or _input_controller_instance is None:
        keyboard = get_keyboard(human_like, new_instance)
        mouse = get_mouse(human_like, new_instance)
        _input_controller_instance = InputController(keyboard, mouse)

    return _input_controller_instance


# Автоматическая регистрация реализаций для Windows
try:
    from core.platform.windows.input.keyboard import WindowsKeyboard
    from core.platform.windows.input.mouse import WindowsMouse

    register_keyboard("windows", WindowsKeyboard)
    register_mouse("windows", WindowsMouse)
except ImportError:
    pass
