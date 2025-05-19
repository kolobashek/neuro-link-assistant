# -*- coding: utf-8 -*-
"""
Реализация менеджера окон для Windows с использованием Win32 API.
"""
import time
from typing import Any, Dict, List, Optional, Tuple

import psutil
import win32con
import win32gui
import win32process

from core.common.error_handler import handle_error
from core.common.window.base import AbstractWindowManager


class Win32WindowManager(AbstractWindowManager):
    """
    Менеджер окон Windows, использующий Win32 API.
    """

    def get_all_windows(self) -> List[Dict[str, Any]]:
        """
        Получение списка всех открытых окон.

        Returns:
            List[Dict[str, Any]]: Список словарей с информацией о каждом окне
        """
        try:
            result = []

            def enum_windows_callback(hwnd, extra):
                if not win32gui.IsWindowVisible(hwnd):
                    return

                window_title = win32gui.GetWindowText(hwnd)
                window_class = win32gui.GetClassName(hwnd)

                # Пропускаем пустые заголовки
                if not window_title:
                    return

                rect = win32gui.GetWindowRect(hwnd)
                result.append(
                    {"hwnd": hwnd, "title": window_title, "class": window_class, "rect": rect}
                )

            win32gui.EnumWindows(enum_windows_callback, None)
            return result
        except Exception as e:
            handle_error(f"Ошибка при получении списка окон: {e}", e, module="window")
            return []

    def get_window_by_title(self, title: str) -> Optional[Dict[str, Any]]:
        """
        Найти окно по заголовку (частичное совпадение).

        Args:
            title (str): Заголовок окна

        Returns:
            Optional[Dict[str, Any]]: Информация об окне или None, если окно не найдено
        """
        try:
            result = []

            def enum_windows_callback(hwnd, extra):
                if not win32gui.IsWindowVisible(hwnd):
                    return

                window_title = win32gui.GetWindowText(hwnd)
                if window_title and title.lower() in window_title.lower():
                    window_class = win32gui.GetClassName(hwnd)
                    rect = win32gui.GetWindowRect(hwnd)
                    result.append(
                        {"hwnd": hwnd, "title": window_title, "class": window_class, "rect": rect}
                    )

            win32gui.EnumWindows(enum_windows_callback, None)
            return result[0] if result else None
        except Exception as e:
            handle_error(f"Ошибка при поиске окна '{title}': {e}", e, module="window")
            return None

    def activate_window(self, window: Dict[str, Any]) -> bool:
        """
        Активировать окно.

        Args:
            window (Dict[str, Any]): Информация об окне

        Returns:
            bool: True, если окно успешно активировано
        """
        try:
            if not window or "hwnd" not in window:
                return False

            hwnd = window["hwnd"]

            # Проверяем, свернуто ли окно
            if win32gui.IsIconic(hwnd):
                # Восстанавливаем свернутое окно
                win32gui.ShowWindow(hwnd, win32con.SW_RESTORE)

            # Активируем окно и выводим на передний план
            win32gui.SetForegroundWindow(hwnd)

            # Даем время на активацию окна
            time.sleep(0.5)

            return True
        except Exception as e:
            handle_error(f"Ошибка при активации окна: {e}", e, module="window")
            return False

    def close_window(self, window: Dict[str, Any]) -> bool:
        """
        Закрыть окно.

        Args:
            window (Dict[str, Any]): Информация об окне

        Returns:
            bool: True, если окно успешно закрыто
        """
        try:
            if not window or "hwnd" not in window:
                return False

            hwnd = window["hwnd"]

            # Отправляем сообщение о закрытии окна
            win32gui.PostMessage(hwnd, win32con.WM_CLOSE, 0, 0)

            return True
        except Exception as e:
            handle_error(f"Ошибка при закрытии окна: {e}", e, module="window")
            return False

    def minimize_window(self, window: Dict[str, Any]) -> bool:
        """
        Свернуть окно.

        Args:
            window (Dict[str, Any]): Информация об окне

        Returns:
            bool: True, если окно успешно свернуто
        """
        try:
            if not window or "hwnd" not in window:
                return False

            hwnd = window["hwnd"]
            win32gui.ShowWindow(hwnd, win32con.SW_MINIMIZE)
            return True
        except Exception as e:
            handle_error(f"Ошибка при сворачивании окна: {e}", e, module="window")
            return False

    def maximize_window(self, window: Dict[str, Any]) -> bool:
        """
        Развернуть окно.

        Args:
            window (Dict[str, Any]): Информация об окне

        Returns:
            bool: True, если окно успешно развернуто
        """
        try:
            if not window or "hwnd" not in window:
                return False

            hwnd = window["hwnd"]
            win32gui.ShowWindow(hwnd, win32con.SW_MAXIMIZE)
            return True
        except Exception as e:
            handle_error(f"Ошибка при разворачивании окна: {e}", e, module="window")
            return False

    def wait_for_window(self, title: str, timeout: int = 10) -> Optional[Dict[str, Any]]:
        """
        Ждать появления окна с заданным заголовком.

        Args:
            title (str): Заголовок окна
            timeout (int): Таймаут в секундах

        Returns:
            Optional[Dict[str, Any]]: Информация об окне или None, если окно не появилось за указанное время
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
            handle_error(f"Ошибка при ожидании окна '{title}': {e}", e, module="window")
            return None

    def find_window(
        self, title: Optional[str] = None, process_name: Optional[str] = None
    ) -> Optional[Dict[str, Any]]:
        """
        Найти окно по заголовку или имени процесса.

        Args:
            title (str, optional): Заголовок окна
            process_name (str, optional): Имя процесса

        Returns:
            Optional[Dict[str, Any]]: Информация об окне или None, если окно не найдено
        """
        try:
            result = []

            def enum_windows_callback(hwnd, extra):
                if not win32gui.IsWindowVisible(hwnd):
                    return

                window_title = win32gui.GetWindowText(hwnd)
                window_class = win32gui.GetClassName(hwnd)

                # Пропускаем пустые заголовки и системные окна
                if not window_title:
                    return

                if title and title.lower() not in window_title.lower():
                    return

                # Получаем PID процесса
                _, pid = win32process.GetWindowThreadProcessId(hwnd)

                # Проверяем имя процесса, если указано
                if process_name:
                    try:
                        process = psutil.Process(pid)
                        if process_name.lower() not in process.name().lower():
                            return
                    except (psutil.NoSuchProcess, psutil.AccessDenied):
                        return

                rect = win32gui.GetWindowRect(hwnd)
                result.append(
                    {
                        "hwnd": hwnd,
                        "title": window_title,
                        "class": window_class,
                        "rect": rect,
                        "pid": pid,
                    }
                )

            win32gui.EnumWindows(enum_windows_callback, None)
            return result[0] if result else None
        except Exception as e:
            handle_error(f"Ошибка при поиске окна: {e}", e)
            return None

    def get_window_text(self, window: Dict[str, Any]) -> str:
        """
        Получить текст окна.

        Args:
            window (Dict[str, Any]): Информация об окне

        Returns:
            str: Текст окна или пустая строка в случае ошибки
        """
        try:
            if not window or "hwnd" not in window:
                return ""

            hwnd = window["hwnd"]
            return win32gui.GetWindowText(hwnd)
        except Exception as e:
            handle_error(f"Ошибка при получении текста окна: {e}", e)
            return ""

    def get_window_rect(self, window: Dict[str, Any]) -> Tuple[int, int, int, int]:
        """
        Получить координаты и размеры окна.

        Args:
            window (Dict[str, Any]): Информация об окне

        Returns:
            Tuple[int, int, int, int]: Кортеж (x, y, width, height)
        """
        try:
            if not window or "hwnd" not in window:
                return (0, 0, 0, 0)

            hwnd = window["hwnd"]
            left, top, right, bottom = win32gui.GetWindowRect(hwnd)
            return (left, top, right - left, bottom - top)
        except Exception as e:
            handle_error(f"Ошибка при получении размеров окна: {e}", e)
            return (0, 0, 0, 0)

    def move_window(self, window: Dict[str, Any], x: int, y: int, width: int, height: int) -> bool:
        """
        Изменить положение и размер окна.

        Args:
            window (Dict[str, Any]): Информация об окне
            x (int): Координата X левого верхнего угла
            y (int): Координата Y левого верхнего угла
            width (int): Ширина окна
            height (int): Высота окна

        Returns:
            bool: True, если окно успешно перемещено
        """
        try:
            if not window or "hwnd" not in window:
                return False

            hwnd = window["hwnd"]
            win32gui.MoveWindow(hwnd, x, y, width, height, True)
            return True
        except Exception as e:
            handle_error(f"Ошибка при перемещении окна: {e}", e)
            return False

    def get_window_process_info(self, window: Dict[str, Any]) -> Dict[str, Any]:
        """
        Получить информацию о процессе окна.

        Args:
            window (Dict[str, Any]): Информация об окне

        Returns:
            Dict[str, Any]: Информация о процессе или пустой словарь в случае ошибки
        """
        try:
            if not window or "hwnd" not in window:
                return {}

            hwnd = window["hwnd"]
            _, pid = win32process.GetWindowThreadProcessId(hwnd)

            try:
                process = psutil.Process(pid)
                return {
                    "pid": pid,
                    "name": process.name(),
                    "exe": process.exe(),
                    "cmdline": process.cmdline(),
                    "create_time": process.create_time(),
                    "username": process.username(),
                    "status": process.status(),
                }
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                return {"pid": pid}

        except Exception as e:
            handle_error(f"Ошибка при получении информации о процессе: {e}", e)
            return {}

    def screenshot_window(self, window: Dict[str, Any], save_path: str) -> bool:
        """
        Сделать скриншот окна.

        Args:
            window (Dict[str, Any]): Информация об окне
            save_path (str): Путь для сохранения скриншота

        Returns:
            bool: True, если скриншот успешно сделан
        """
        try:
            if not window or "hwnd" not in window:
                return False

            # Использование PIL для создания скриншота
            from PIL import ImageGrab

            hwnd = window["hwnd"]
            left, top, right, bottom = win32gui.GetWindowRect(hwnd)

            # Сделать скриншот указанной области
            screenshot = ImageGrab.grab((left, top, right, bottom))
            screenshot.save(save_path)

            return True
        except Exception as e:
            handle_error(f"Ошибка при создании скриншота окна: {e}", e)
            return False
