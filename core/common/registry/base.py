# -*- coding: utf-8 -*-
"""
Базовые абстрактные классы для работы с системным реестром.
"""
from abc import ABC, abstractmethod
from typing import Any, Dict, List


class AbstractRegistryManager(ABC):
    """
    Абстрактный класс для управления реестром.
    Определяет интерфейс для платформо-зависимых реализаций.
    """

    @abstractmethod
    def read_value(self, root_key: Any, key_path: str, value_name: str) -> Any:
        """
        Читает значение из реестра.

        Args:
            root_key (Any): Корневой ключ реестра
            key_path (str): Путь к ключу
            value_name (str): Имя значения

        Returns:
            Any: Значение из реестра или None, если значение не найдено
        """
        pass

    @abstractmethod
    def write_value(
        self, root_key: Any, key_path: str, value_name: str, value: Any, value_type: Any = None
    ) -> bool:
        """
        Записывает значение в реестр.

        Args:
            root_key (Any): Корневой ключ реестра
            key_path (str): Путь к ключу
            value_name (str): Имя значения
            value (Any): Значение для записи
            value_type (Any, optional): Тип значения

        Returns:
            bool: True в случае успешной записи
        """
        pass

    @abstractmethod
    def delete_value(self, root_key: Any, key_path: str, value_name: str) -> bool:
        """
        Удаляет значение из реестра.

        Args:
            root_key (Any): Корневой ключ реестра
            key_path (str): Путь к ключу
            value_name (str): Имя значения

        Returns:
            bool: True в случае успешного удаления
        """
        pass

    @abstractmethod
    def list_values(self, root_key: Any, key_path: str) -> List[Dict[str, Any]]:
        """
        Получает список всех значений в ключе реестра.

        Args:
            root_key (Any): Корневой ключ реестра
            key_path (str): Путь к ключу

        Returns:
            List[Dict[str, Any]]: Список словарей с информацией о значениях
        """
        pass

    @abstractmethod
    def list_keys(self, root_key: Any, key_path: str) -> List[str]:
        """
        Получает список всех подключей в ключе реестра.

        Args:
            root_key (Any): Корневой ключ реестра
            key_path (str): Путь к ключу

        Returns:
            List[str]: Список имен подключей
        """
        pass

    @abstractmethod
    def create_key(self, root_key: Any, key_path: str) -> bool:
        """
        Создает ключ реестра.

        Args:
            root_key (Any): Корневой ключ реестра
            key_path (str): Путь к ключу

        Returns:
            bool: True в случае успешного создания
        """
        pass

    @abstractmethod
    def delete_key(self, root_key: Any, key_path: str) -> bool:
        """
        Удаляет ключ реестра.

        Args:
            root_key (Any): Корневой ключ реестра
            key_path (str): Путь к ключу

        Returns:
            bool: True в случае успешного удаления
        """
        pass

    @abstractmethod
    def key_exists(self, root_key: Any, key_path: str) -> bool:
        """
        Проверяет существование ключа реестра.

        Args:
            root_key (Any): Корневой ключ реестра
            key_path (str): Путь к ключу

        Returns:
            bool: True, если ключ существует
        """
        pass

    @abstractmethod
    def value_exists(self, root_key: Any, key_path: str, value_name: str) -> bool:
        """
        Проверяет существование значения в реестре.

        Args:
            root_key (Any): Корневой ключ реестра
            key_path (str): Путь к ключу
            value_name (str): Имя значения

        Returns:
            bool: True, если значение существует
        """
        pass
