"""
Модуль для работы с вводом пользователя (клавиатура, мышь).
"""

from .base import AbstractKeyboard, AbstractMouse, InputController
from .factory import (
    get_input_controller,
    get_keyboard,
    get_mouse,
    register_keyboard,
    register_mouse,
)

__all__ = [
    "AbstractKeyboard",
    "AbstractMouse",
    "InputController",
    "get_keyboard",
    "get_mouse",
    "get_input_controller",
    "register_keyboard",
    "register_mouse",
]
