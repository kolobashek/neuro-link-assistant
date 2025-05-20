# -*- coding: utf-8 -*-
"""
Модуль для управления системным реестром.
"""

from .base import AbstractRegistryManager
from .factory import RegistryManagerFactory

__all__ = ["AbstractRegistryManager", "RegistryManagerFactory", "get_registry_manager"]


def get_registry_manager() -> AbstractRegistryManager:
    """
    Получить экземпляр менеджера реестра для текущей платформы.

    Returns:
        AbstractRegistryManager: Менеджер реестра для текущей платформы
    """
    return RegistryManagerFactory.create_registry_manager()
