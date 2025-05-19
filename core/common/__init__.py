# -*- coding: utf-8 -*-
"""
Модуль общих компонентов системы.
Содержит базовые классы и утилиты, используемые в различных частях приложения.
"""

# Импорт из модуля обработки ошибок
from .error_handler import (
    ErrorHandler,
    get_error_handler,
    handle_api_error,
    handle_error,
    handle_llm_error,
    handle_rate_limit,
    handle_timeout,
    handle_warning,
)

# Импорт из модуля файловой системы
from .file_system import AbstractFileSystem

# Импорт из модуля ввода
from .input import AbstractKeyboard, AbstractMouse, InputController

__all__ = [
    # Компоненты обработки ошибок
    "ErrorHandler",
    "handle_error",
    "handle_warning",
    "handle_llm_error",
    "handle_api_error",
    "handle_rate_limit",
    "handle_timeout",
    "get_error_handler",
    # Компоненты файловой системы
    "AbstractFileSystem",
    # Компоненты ввода
    "AbstractKeyboard",
    "AbstractMouse",
    "InputController",
]
