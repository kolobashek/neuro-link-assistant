"""
Фабрика контроллеров ввода.
"""

import platform
from typing import Any, Optional

from core.common.input.base import AbstractKeyboard, AbstractMouse, InputController
from core.common.input.registry import InputRegistry

# Получаем глобальный экземпляр реестра
registry = InputRegistry()


# Кэш для хранения экземпляров контроллеров
_keyboard_instances = {}
_mouse_instances = {}


def get_keyboard(
    human_like=True, platform_name=None, new_instance=False
) -> Optional[AbstractKeyboard]:
    """
    Возвращает экземпляр контроллера клавиатуры для текущей или указанной платформы.

    Args:
        human_like (bool, optional): Признак человекоподобного поведения.
        platform_name (str, optional): Имя платформы (если None, используется текущая платформа).
        new_instance (bool, optional): Признак создания нового экземпляра (не использовать кэш).

    Returns:
        AbstractKeyboard: Экземпляр контроллера клавиатуры или None, если не найден.
    """
    # Определяем имя платформы, если не указано
    if platform_name is None:
        platform_name = platform.system().lower()

    # Используем кэш, если не требуется новый экземпляр
    cache_key = f"{platform_name}_{human_like}"
    if not new_instance and cache_key in _keyboard_instances:
        return _keyboard_instances[cache_key]

    # Получаем класс контроллера клавиатуры для указанной платформы
    keyboard_class = registry.get_keyboard(platform_name)
    if not keyboard_class:
        return None

    # Создаем экземпляр контроллера
    keyboard = keyboard_class(human_like=human_like)

    # Сохраняем в кэш, если не требуется новый экземпляр
    if not new_instance:
        _keyboard_instances[cache_key] = keyboard

    return keyboard


def get_mouse(human_like=True, platform_name=None, new_instance=False) -> Optional[AbstractMouse]:
    """
    Возвращает экземпляр контроллера мыши для текущей или указанной платформы.

    Args:
        human_like (bool, optional): Признак человекоподобного поведения.
        platform_name (str, optional): Имя платформы (если None, используется текущая платформа).
        new_instance (bool, optional): Признак создания нового экземпляра (не использовать кэш).

    Returns:
        AbstractMouse: Экземпляр контроллера мыши или None, если не найден.
    """
    # Определяем имя платформы, если не указано
    if platform_name is None:
        platform_name = platform.system().lower()

    # Используем кэш, если не требуется новый экземпляр
    cache_key = f"{platform_name}_{human_like}"
    if not new_instance and cache_key in _mouse_instances:
        return _mouse_instances[cache_key]

    # Получаем класс контроллера мыши для указанной платформы
    mouse_class = registry.get_mouse(platform_name)
    if not mouse_class:
        return None

    # Создаем экземпляр контроллера
    mouse = mouse_class(human_like=human_like)

    # Сохраняем в кэш, если не требуется новый экземпляр
    if not new_instance:
        _mouse_instances[cache_key] = mouse

    return mouse


def get_input_controller(
    human_like=True, platform_name=None, new_instance=False
) -> Optional[InputController]:
    """
    Возвращает комбинированный контроллер ввода для текущей или указанной платформы.

    Args:
        human_like (bool, optional): Признак человекоподобного поведения.
        platform_name (str, optional): Имя платформы (если None, используется текущая платформа).
        new_instance (bool, optional): Признак создания нового экземпляра (не использовать кэш).

    Returns:
        InputController: Экземпляр контроллера ввода или None, если не найдены контроллеры.
    """

    # Получаем контроллеры клавиатуры и мыши
    keyboard = get_keyboard(human_like, platform_name, new_instance)
    mouse = get_mouse(human_like, platform_name, new_instance)

    # Если один из контроллеров не найден, возвращаем None
    if not keyboard or not mouse:
        return None

    # Создаем и возвращаем комбинированный контроллер
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
