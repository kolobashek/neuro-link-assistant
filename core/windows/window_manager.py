import psutil
import win32con
import win32gui
import win32process


class WindowManager:
    """
    Менеджер окон Windows.
    Предоставляет функции для поиска, активации и управления окнами.
    """

    def find_window(self, title=None, class_name=None, process_name=None):
        """
        Находит окно по заголовку, имени класса или имени процесса.

        Args:
            title (str, optional): Заголовок окна (может быть частичным)
            class_name (str, optional): Имя класса окна
            process_name (str, optional): Имя процесса

        Returns:
            dict: Информация о найденном окне или None, если окно не найдено
        """
        result = []

        def enum_windows_callback(hwnd, extra):
            if not win32gui.IsWindowVisible(hwnd):
                return

            window_title = win32gui.GetWindowText(hwnd)
            window_class = win32gui.GetClassName(hwnd)

            # Проверяем соответствие заголовка и класса
            title_match = title is None or (window_title and title.lower() in window_title.lower())
            class_match = class_name is None or (
                window_class and class_name.lower() == window_class.lower()
            )

            # Проверяем соответствие процесса, если указано
            process_match = True
            if process_name is not None:
                try:
                    _, pid = win32process.GetWindowThreadProcessId(hwnd)
                    process = psutil.Process(pid)
                    process_match = process_name.lower() in process.name().lower()
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    process_match = False

            if title_match and class_match and process_match:
                rect = win32gui.GetWindowRect(hwnd)
                result.append(
                    {"hwnd": hwnd, "title": window_title, "class": window_class, "rect": rect}
                )

        win32gui.EnumWindows(enum_windows_callback, None)

        # Возвращаем первое найденное окно или None
        return result[0] if result else None

    def activate_window(self, window_info):
        """
        Активирует окно (выводит на передний план).

        Args:
            window_info (dict): Информация об окне, полученная из find_window

        Returns:
            bool: True в случае успешной активации
        """
        if not window_info or "hwnd" not in window_info:
            return False

        hwnd = window_info["hwnd"]

        # Проверяем, свернуто ли окно
        if win32gui.IsIconic(hwnd):
            # Восстанавливаем свернутое окно
            win32gui.ShowWindow(hwnd, win32con.SW_RESTORE)

        # Активируем окно и выводим на передний план
        win32gui.SetForegroundWindow(hwnd)

        return True

    def close_window(self, window_info):
        """
        Закрывает окно.

        Args:
            window_info (dict): Информация об окне, полученная из find_window

        Returns:
            bool: True в случае успешного закрытия
        """
        if not window_info or "hwnd" not in window_info:
            return False

        hwnd = window_info["hwnd"]

        # Отправляем сообщение о закрытии окна
        win32gui.PostMessage(hwnd, win32con.WM_CLOSE, 0, 0)

        return True

    def get_window_text(self, window_info):
        """
        Получает текст заголовка окна.

        Args:
            window_info (dict): Информация об окне, полученная из find_window

        Returns:
            str: Текст заголовка окна
        """
        if not window_info or "hwnd" not in window_info:
            return ""

        hwnd = window_info["hwnd"]
        return win32gui.GetWindowText(hwnd)

    def get_all_windows(self):
        """
        Получает список всех видимых окон.

        Returns:
            list: Список словарей с информацией о каждом окне
        """
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
