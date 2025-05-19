# -*- coding: utf-8 -*-
"""
Базовые интерфейсы для системы ввода.
Предоставляет абстрактные классы для клавиатуры и мыши.
"""

from .base import AbstractKeyboard, AbstractMouse, InputController

__all__ = ["AbstractKeyboard", "AbstractMouse", "InputController"]
