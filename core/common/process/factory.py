# -*- coding: utf-8 -*-
"""
Фабрика для создания менеджеров процессов в зависимости от платформы.
"""
import platform

from core.common.error_handler import handle_error
from core.common.process.base import AbstractProcessManager


class ProcessManagerFactory:
    """
    Фабрика для создания менеджеров процессов.
    """

    @staticmethod
    def create_process_manager() -> AbstractProcessManager:
        """
        Создать менеджер процессов для текущей платформы.

        Returns:
            AbstractProcessManager: Менеджер процессов для текущей платформы

        Raises:
            NotImplementedError: Если платформа не поддерживается
        """
        system = platform.system().lower()

        if system == "windows":
            try:
                from core.platform.windows.process.win32_process_manager import Win32ProcessManager

                return Win32ProcessManager()
            except ImportError as e:
                handle_error(f"Не удалось импортировать Win32ProcessManager: {e}", e)
                raise ImportError("Не удалось создать менеджер процессов для Windows")

        elif system == "darwin":  # macOS
            raise NotImplementedError("Менеджер процессов для macOS пока не реализован")

        elif system == "linux":
            raise NotImplementedError("Менеджер процессов для Linux пока не реализован")

        else:
            raise NotImplementedError(
                f"Менеджер процессов для платформы {system} не поддерживается"
            )
