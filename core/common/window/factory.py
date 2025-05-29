# -*- coding: utf-8 -*-
"""
Фабрика для создания менеджеров окон в зависимости от платформы.
"""
import platform
from typing import Optional

from core.common.error_handler import handle_error
from core.common.window.base import AbstractWindowManager


class WindowManagerFactory:
    """
    Фабрика для создания менеджеров окон.
    """

    @staticmethod
    def create_window_manager(backend: Optional[str] = None) -> AbstractWindowManager:
        """
        Создать менеджер окон для текущей платформы.

        Args:
            backend (Optional[str]): Предпочтительный бэкенд
                ('win32' или 'pygetwindow' для Windows)

        Returns:
            AbstractWindowManager: Менеджер окон для текущей платформы

        Raises:
            NotImplementedError: Если платформа не поддерживается
        """
        system = platform.system().lower()

        if system == "windows":
            # Выбираем бэкенд для Windows
            if backend == "pygetwindow":
                try:
                    from core.platform.windows.window.pygetwindow_manager import PyGetWindowManager

                    return PyGetWindowManager()

                except ImportError as e:
                    handle_error(f"Не удалось импортировать PyGetWindowManager: {e}", e)
                    backend = "win32"  # Fallback на win32

            # По умолчанию используем Win32 API
            try:
                from core.platform.windows.window.win32_window_manager import Win32WindowManager

                return Win32WindowManager()
            except ImportError as e:
                handle_error(f"Не удалось импортировать Win32WindowManager: {e}", e)
                raise ImportError("Не удалось создать менеджер окон для Windows")

        elif system == "darwin":  # macOS
            raise NotImplementedError("Менеджер окон для macOS пока не реализован")

        elif system == "linux":
            raise NotImplementedError("Менеджер окон для Linux пока не реализован")

        else:
            raise NotImplementedError(f"Менеджер окон для платформы {system} не поддерживается")
