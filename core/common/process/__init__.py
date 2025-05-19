# -*- coding: utf-8 -*-
"""
Модуль для управления процессами операционной системы.
"""

from .base import AbstractProcessManager
from .factory import ProcessManagerFactory

__all__ = ["AbstractProcessManager", "ProcessManagerFactory", "get_process_manager"]


def get_process_manager() -> AbstractProcessManager:
    """
    Получить экземпляр менеджера процессов для текущей платформы.

    Returns:
        AbstractProcessManager: Менеджер процессов для текущей платформы
    """
    return ProcessManagerFactory.create_process_manager()
