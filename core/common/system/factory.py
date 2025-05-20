# -*- coding: utf-8 -*-
"""
Фабрика для создания объектов системной информации.
"""
import platform

from core.common.error_handler import handle_error
from core.common.system.base import AbstractSystemInfo


class SystemInfoFactory:
    """
    Фабрика для создания объектов системной информации.
    """

    @staticmethod
    def create_system_info() -> AbstractSystemInfo:
        """
        Создать объект системной информации для текущей платформы.

        Returns:
            AbstractSystemInfo: Объект системной информации для текущей платформы

        Raises:
            NotImplementedError: Если платформа не поддерживается
        """
        system = platform.system().lower()

        if system == "windows":
            try:
                from core.platform.windows.system.win32_system_info import Win32SystemInfo

                return Win32SystemInfo()
            except ImportError as e:
                handle_error(f"Не удалось импортировать Win32SystemInfo: {e}", e)
                raise ImportError("Не удалось создать объект системной информации для Windows")

        elif system == "darwin":  # macOS
            raise NotImplementedError("Объект системной информации для macOS пока не реализован")

        elif system == "linux":
            raise NotImplementedError("Объект системной информации для Linux пока не реализован")

        else:
            raise NotImplementedError(
                f"Объект системной информации для платформы {system} не поддерживается"
            )
