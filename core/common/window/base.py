# -*- coding: utf-8 -*-
"""
Базовые абстрактные классы для работы с окнами.
"""
from abc import ABC, abstractmethod
from typing import Any, List, Optional, Tuple


class AbstractWindowManager(ABC):
    """
    Абстрактный класс для управления окнами.
    Определяет интерфейс для платформо-зависимых реализаций.
    """

    @abstractmethod
    def get_all_windows(self) -> List[Any]:
        """
        Получение списка всех открытых окон.

        Returns:
            List[Any]: Список объектов окон
        """
        pass

    @abstractmethod
    def get_window_by_title(self, title: str) -> Optional[Any]:
        """
        Найти окно по заголовку (частичное совпадение).

        Args:
            title (str): Заголовок окна

        Returns:
            Optional[Any]: Объект окна или None, если окно не найдено
        """
        pass

    @abstractmethod
    def activate_window(self, window: Any) -> bool:
        """
        Активировать окно.

        Args:
            window: Объект окна

        Returns:
            bool: True, если окно успешно активировано
        """
        pass

    @abstractmethod
    def close_window(self, window: Any) -> bool:
        """
        Закрыть окно.

        Args:
            window: Объект окна

        Returns:
            bool: True, если окно успешно закрыто
        """
        pass

    @abstractmethod
    def minimize_window(self, window: Any) -> bool:
        """
        Свернуть окно.

        Args:
            window: Объект окна

        Returns:
            bool: True, если окно успешно свернуто
        """
        pass

    @abstractmethod
    def maximize_window(self, window: Any) -> bool:
        """
        Развернуть окно.

        Args:
            window: Объект окна

        Returns:
            bool: True, если окно успешно развернуто
        """
        pass

    @abstractmethod
    def wait_for_window(self, title: str, timeout: int = 10) -> Optional[Any]:
        """
        Ждать появления окна с заданным заголовком.

        Args:
            title (str): Заголовок окна
            timeout (int): Таймаут в секундах

        Returns:
            Optional[Any]: Объект окна или None, если окно не появилось за указанное время
        """
        pass

    @abstractmethod
    def find_window(
        self, title: Optional[str] = None, process_name: Optional[str] = None
    ) -> Optional[Any]:
        """
        Найти окно по заголовку или имени процесса.

        Args:
            title (str, optional): Заголовок окна
            process_name (str, optional): Имя процесса

        Returns:
            Optional[Any]: Объект окна или None, если окно не найдено
        """
        pass

    @abstractmethod
    def get_window_text(self, window: Any) -> str:
        """
        Получить текст окна.

        Args:
            window: Объект окна

        Returns:
            str: Текст окна или пустая строка в случае ошибки
        """
        pass

    @abstractmethod
    def get_window_rect(self, window: Any) -> Tuple[int, int, int, int]:
        """
        Получить координаты и размеры окна.

        Args:
            window: Объект окна

        Returns:
            Tuple[int, int, int, int]: Кортеж (x, y, width, height)
        """
        pass
