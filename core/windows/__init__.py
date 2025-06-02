"""
Модуль для работы с Windows API.
"""

from core.platform.windows.window.pygetwindow_manager import PyGetWindowManager
from core.platform.windows.window.win32_window_manager import Win32WindowManager

# Выбираем реализацию по умолчанию
try:
    # Пытаемся использовать Win32 API (более функциональный)
    WindowManager = Win32WindowManager
except ImportError:
    # Если Win32 недоступен, используем PyGetWindow
    WindowManager = PyGetWindowManager

__all__ = ["WindowManager", "Win32WindowManager", "PyGetWindowManager"]
