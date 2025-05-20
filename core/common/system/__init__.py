# -*- coding: utf-8 -*-
"""
Модуль для получения системной информации.
"""

from .base import AbstractSystemInfo
from .factory import SystemInfoFactory

__all__ = ["AbstractSystemInfo", "SystemInfoFactory", "get_system_info"]


def get_system_info() -> AbstractSystemInfo:
    """
    Получить экземпляр объекта системной информации для текущей платформы.

    Returns:
        AbstractSystemInfo: Объект системной информации для текущей платформы
    """
    return SystemInfoFactory.create_system_info()
