"""
Фабрика для создания и регистрации контроллеров ввода.
"""

import platform
from typing import Any, Dict

from core.common.input.base import AbstractKeyboard, AbstractMouse, InputController
from core.common.input.registry import InputRegistry

# Глобальный экземпляр реестра
registry = InputRegistry()

# Глобальные экземпляры контроллеров для кэширования
_keyboard_instances: Dict[str, AbstractKeyboard] = {}
_mouse_instances: Dict[str, AbstractMouse] = {}


def get_keyboard(human_like: bool = True, new_instance: bool = False) -> AbstractKeyboard:
    """
    Возвращает контроллер клавиатуры для текущей платформы.

    Args:
        human_like: Флаг, указывающий, должен ли контроллер имитировать человеческое поведение.
        new_instance: Флаг, указывающий, нужно ли создать новый экземпляр
                      контроллера вместо использования кэшированного.

    Returns:
        Экземпляр контроллера клавиатуры.
    """
    key = f"keyboard_{human_like}"

    if key in _keyboard_instances and not new_instance:
        return _keyboard_instances[key]

    system = platform.system().lower()

    if system == "windows":

        # Важно: импортируем непосредственно из модуля для тестов
        from core.platform.windows.input.keyboard import WindowsKeyboard

        keyboard = WindowsKeyboard(human_like=human_like)
    else:
        raise NotImplementedError(f"Система {system} не поддерживается")

    if not new_instance:
        _keyboard_instances[key] = keyboard

    return keyboard


def get_mouse(human_like: bool = True, new_instance: bool = False) -> AbstractMouse:
    """
    Возвращает контроллер мыши для текущей платформы.

    Args:
        human_like: Флаг, указывающий, должен ли контроллер имитировать человеческое поведение.
        new_instance: Флаг, указывающий, нужно ли создать новый экземпляр
                     контроллера вместо использования кэшированного.

    Returns:
        Экземпляр контроллера мыши.
    """
    key = f"mouse_{human_like}"

    if key in _mouse_instances and not new_instance:
        return _mouse_instances[key]

    system = platform.system().lower()

    if system == "windows":

        # Важно: импортируем непосредственно из модуля для тестов
        from core.platform.windows.input.mouse import WindowsMouse

        mouse = WindowsMouse(human_like=human_like)
    else:
        raise NotImplementedError(f"Система {system} не поддерживается")

    if not new_instance:
        _mouse_instances[key] = mouse

    return mouse


def get_input_controller(human_like: bool = True) -> InputController:
    """
    Возвращает комбинированный контроллер ввода для текущей платформы.

    Args:
        human_like: Флаг, указывающий, должен ли контроллер имитировать человеческое поведение.

    Returns:
        Экземпляр комбинированного контроллера ввода.
    """
    # Важно использовать именованные аргументы для соответствия тестам
    keyboard = get_keyboard(human_like=human_like)
    mouse = get_mouse(human_like=human_like)
    # Импортируем здесь, чтобы избежать циклических зависимостей
    from core.common.input.base import InputController

    return InputController(keyboard, mouse)


# Функции регистрации контроллеров для системы плагинов
def register_keyboard(name: str, keyboard_class: Any) -> bool:
    """
    Регистрирует класс контроллера клавиатуры в реестре.

    Args:
        name: Уникальное имя контроллера.
        keyboard_class: Класс контроллера клавиатуры.

    Returns:
        True если регистрация успешна, иначе False.
    """
    return registry.register_keyboard(name, keyboard_class)


def register_mouse(name: str, mouse_class: Any) -> bool:
    """
    Регистрирует класс контроллера мыши в реестре.

    Args:
        name: Уникальное имя контроллера.
        mouse_class: Класс контроллера мыши.

    Returns:
        True если регистрация успешна, иначе False.
    """
    return registry.register_mouse(name, mouse_class)
