# -*- coding: utf-8 -*-
"""
Менеджеры окон для Windows.
"""

from core.platform.windows.window.pygetwindow_manager import PyGetWindowManager
from core.platform.windows.window.win32_window_manager import Win32WindowManager

__all__ = ["Win32WindowManager", "PyGetWindowManager"]
