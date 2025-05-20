# -*- coding: utf-8 -*-
"""
Базовые абстрактные классы для получения системной информации.
"""
from abc import ABC, abstractmethod
from typing import Any, Dict, Optional


class AbstractSystemInfo(ABC):
    """
    Абстрактный класс для получения системной информации.
    Определяет интерфейс для платформо-зависимых реализаций.
    """

    @abstractmethod
    def get_os_info(self) -> Dict[str, Any]:
        """
        Получает информацию об операционной системе.

        Returns:
            Dict[str, Any]: Информация об ОС
        """
        pass

    @abstractmethod
    def get_cpu_info(self) -> Dict[str, Any]:
        """
        Получает информацию о процессоре.

        Returns:
            Dict[str, Any]: Информация о CPU
        """
        pass

    @abstractmethod
    def get_memory_info(self) -> Dict[str, Any]:
        """
        Получает информацию о памяти.

        Returns:
            Dict[str, Any]: Информация о памяти
        """
        pass

    @abstractmethod
    def get_disk_info(self) -> Dict[str, Any]:
        """
        Получает информацию о дисках.

        Returns:
            Dict[str, Any]: Информация о дисках
        """
        pass

    @abstractmethod
    def get_network_info(self) -> Dict[str, Any]:
        """
        Получает информацию о сетевых интерфейсах.

        Returns:
            Dict[str, Any]: Информация о сетевых интерфейсах
        """
        pass

    @abstractmethod
    def get_battery_info(self) -> Optional[Dict[str, Any]]:
        """
        Получает информацию о батарее (для ноутбуков).

        Returns:
            Optional[Dict[str, Any]]: Информация о батарее или None, если батарея отсутствует
        """
        pass

    @abstractmethod
    def get_system_uptime(self) -> float:
        """
        Получает время работы системы в секундах.

        Returns:
            float: Время работы системы в секундах
        """
        pass

    @abstractmethod
    def get_user_info(self) -> Dict[str, str]:
        """
        Получает информацию о текущем пользователе.

        Returns:
            Dict[str, str]: Информация о пользователе
        """
        pass

    @abstractmethod
    def get_full_system_info(self) -> Dict[str, Any]:
        """
        Получает полную информацию о системе.

        Returns:
            Dict[str, Any]: Вся системная информация
        """
        pass
