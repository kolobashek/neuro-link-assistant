# -*- coding: utf-8 -*-
"""
Модуль для управления окнами операционной системы.
"""
from .base import AbstractWindowManager
from .factory import WindowManagerFactory

__all__ = ["AbstractWindowManager", "WindowManagerFactory", "get_window_manager"]


def get_window_manager(backend=None) -> AbstractWindowManager:
    """
    Получить экземпляр менеджера окон для текущей платформы.

    Args:
        backend (Optional[str]): Предпочтительный бэкенд
            ('win32' или 'pygetwindow' для Windows)

    Returns:
        AbstractWindowManager: Менеджер окон для текущей платформы
    """
    return WindowManagerFactory.create_window_manager(backend)
