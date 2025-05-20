# -*- coding: utf-8 -*-
"""
Фабрика для создания менеджеров реестра в зависимости от платформы.
"""
import platform

from core.common.error_handler import handle_error
from core.common.registry.base import AbstractRegistryManager


class RegistryManagerFactory:
    """
    Фабрика для создания менеджеров реестра.
    """

    @staticmethod
    def create_registry_manager() -> AbstractRegistryManager:
        """
        Создать менеджер реестра для текущей платформы.

        Returns:
            AbstractRegistryManager: Менеджер реестра для текущей платформы

        Raises:
            NotImplementedError: Если платформа не поддерживается
        """
        system = platform.system().lower()

        if system == "windows":
            try:
                from core.platform.windows.registry.win32_registry_manager import (
                    Win32RegistryManager,
                )

                return Win32RegistryManager()
            except ImportError as e:
                handle_error(f"Не удалось импортировать Win32RegistryManager: {e}", e)
                raise ImportError("Не удалось создать менеджер реестра для Windows")

        elif system == "darwin":  # macOS
            raise NotImplementedError("Менеджер реестра для macOS пока не реализован")

        elif system == "linux":
            raise NotImplementedError("Менеджер реестра для Linux пока не реализован")

        else:
            raise NotImplementedError(f"Менеджер реестра для платформы {system} не поддерживается")
