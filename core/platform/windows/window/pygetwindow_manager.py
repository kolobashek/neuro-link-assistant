# -*- coding: utf-8 -*-
"""
Реализация менеджера окон для Windows с использованием библиотеки pygetwindow.
"""
import time
from typing import Any, List, Optional, Tuple

import pygetwindow as gw

from core.common.error_handler import handle_error
from core.common.window.base import AbstractWindowManager


class PyGetWindowManager(AbstractWindowManager):
    """
    Менеджер окон Windows, использующий библиотеку pygetwindow.
    """

    def get_all_windows(self) -> List[Any]:
        """
        Получение списка всех открытых окон.

        Returns:
            List[Any]: Список объектов окон
        """
        try:
            return gw.getAllWindows()
        except Exception as e:
            handle_error(f"Ошибка при получении списка окон: {e}", e)
            return []

    def get_window_by_title(self, title: str) -> Optional[Any]:
        """
        Найти окно по заголовку (частичное совпадение).

        Args:
            title (str): Заголовок окна

        Returns:
            Optional[Any]: Объект окна или None, если окно не найдено
        """
        try:
            # Сначала ищем точное совпадение
            try:
                window = gw.getWindowsWithTitle(title)
                if window:
                    return window[0]
            except Exception:
                pass

            # Если не нашли, ищем частичное совпадение
            all_windows = gw.getAllWindows()
            for window in all_windows:
                if title.lower() in window.title.lower():
                    return window

            return None
        except Exception as e:
            handle_error(f"Ошибка при поиске окна '{title}': {e}", e)
            return None

    def activate_window(self, window: Any) -> bool:
        """
        Активировать окно.

        Args:
            window: Объект окна

        Returns:
            bool: True, если окно успешно активировано
        """
        try:
            window.activate()
            time.sleep(0.5)  # Даем время на активацию
            return True
        except Exception as e:
            handle_error(f"Ошибка при активации окна: {e}", e)
            return False

    def close_window(self, window: Any) -> bool:
        """
        Закрыть окно.

        Args:
            window: Объект окна

        Returns:
            bool: True, если окно успешно закрыто
        """
        try:
            window.close()
            return True
        except Exception as e:
            handle_error(f"Ошибка при закрытии окна: {e}", e)
            return False

    def minimize_window(self, window: Any) -> bool:
        """
        Свернуть окно.

        Args:
            window: Объект окна

        Returns:
            bool: True, если окно успешно свернуто
        """
        try:
            window.minimize()
            return True
        except Exception as e:
            handle_error(f"Ошибка при сворачивании окна: {e}", e)
            return False

    def maximize_window(self, window: Any) -> bool:
        """
        Развернуть окно.

        Args:
            window: Объект окна

        Returns:
            bool: True, если окно успешно развернуто
        """
        try:
            window.maximize()
            return True
        except Exception as e:
            handle_error(f"Ошибка при разворачивании окна: {e}", e)
            return False

    def wait_for_window(self, title: str, timeout: int = 10) -> Optional[Any]:
        """
        Ждать появления окна с заданным заголовком.

        Args:
            title (str): Заголовок окна
            timeout (int): Таймаут в секундах

        Returns:
            Optional[Any]: Объект окна или None, если окно не появилось за указанное время
        """
        try:
            start_time = time.time()
            while time.time() - start_time < timeout:
                window = self.get_window_by_title(title)
                if window:
                    return window
                time.sleep(0.5)
            return None
        except Exception as e:
            handle_error(f"Ошибка при ожидании окна '{title}': {e}", e)
            return None

    def find_window(
        self, title: Optional[str] = None, process_name: Optional[str] = None
    ) -> Optional[Any]:
        """
        Найти окно по заголовку или имени процесса.

        Примечание: pygetwindow не предоставляет прямого доступа к информации о процессе,
        поэтому поиск по process_name не реализован в этой версии.

        Args:
            title (str, optional): Заголовок окна
            process_name (str, optional): Имя процесса (игнорируется в этой реализации)

        Returns:
            Optional[Any]: Объект окна или None, если окно не найдено
        """
        if process_name:
            import logging

            logging.warning("Поиск по имени процесса не поддерживается в PyGetWindowManager")

        if title:
            return self.get_window_by_title(title)

        return None

    def get_window_text(self, window: Any) -> str:
        """
        Получить текст окна.

        Args:
            window: Объект окна

        Returns:
            str: Текст окна или пустая строка в случае ошибки
        """
        try:
            return window.title
        except Exception as e:
            handle_error(f"Ошибка при получении текста окна: {e}", e)
            return ""

    def get_window_rect(self, window: Any) -> Tuple[int, int, int, int]:
        """
        Получить координаты и размеры окна.

        Args:
            window: Объект окна

        Returns:
            Tuple[int, int, int, int]: Кортеж (x, y, width, height)
        """
        try:
            return (window.left, window.top, window.width, window.height)
        except Exception as e:
            handle_error(f"Ошибка при получении размеров окна: {e}", e)
            return (0, 0, 0, 0)

    def move_window(self, window: Any, x: int, y: int, width: int, height: int) -> bool:
        """
        Изменить положение и размер окна.

        Args:
            window: Объект окна
            x (int): Координата X левого верхнего угла
            y (int): Координата Y левого верхнего угла
            width (int): Ширина окна
            height (int): Высота окна

        Returns:
            bool: True, если окно успешно перемещено
        """
        try:
            window.moveTo(x, y)
            window.resizeTo(width, height)
            return True
        except Exception as e:
            handle_error(f"Ошибка при перемещении окна: {e}", e)
            return False
