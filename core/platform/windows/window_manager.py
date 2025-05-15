# Windows-специфичная реализация управления окнами
import time

try:
    import pygetwindow as gw
except ImportError:
    gw = None

from core.common.error_handler import handle_error


class WindowsWindowManager:
    """Управление окнами в Windows"""

    def __init__(self):
        if gw is None:
            handle_error(
                "PyGetWindow не установлен. Установите его: pip install pygetwindow",
                module="window",
            )

    def get_all_windows(self):
        """
        Получить список всех окон

        Returns:
            list: Список объектов окон
        """
        try:
            if gw:
                return gw.getAllWindows()
            return []
        except Exception as e:
            handle_error(f"Ошибка при получении списка окон: {e}", e, module="window")
            return []

    def get_window_by_title(self, title):
        """
        Найти окно по заголовку (частичное совпадение)

        Args:
            title (str): Заголовок окна

        Returns:
            object: Объект окна или None, если окно не найдено
        """
        try:
            if gw:
                matching_windows = gw.getWindowsWithTitle(title)
                if matching_windows:
                    return matching_windows[0]
            return None
        except Exception as e:
            handle_error(f"Ошибка при поиске окна '{title}': {e}", e, module="window")
            return None

    def activate_window(self, window):
        """
        Активировать окно

        Args:
            window: Объект окна

        Returns:
            bool: True, если окно успешно активировано
        """
        try:
            if window:
                window.activate()
                # Даем время на активацию окна
                time.sleep(0.5)
                return True
            return False
        except Exception as e:
            handle_error(f"Ошибка при активации окна: {e}", e, module="window")
            return False

    def close_window(self, window):
        """
        Закрыть окно

        Args:
            window: Объект окна

        Returns:
            bool: True, если окно успешно закрыто
        """
        try:
            if window:
                window.close()
                return True
            return False
        except Exception as e:
            handle_error(f"Ошибка при закрытии окна: {e}", e, module="window")
            return False

    def minimize_window(self, window):
        """
        Свернуть окно

        Args:
            window: Объект окна

        Returns:
            bool: True, если окно успешно свернуто
        """
        try:
            if window:
                window.minimize()
                return True
            return False
        except Exception as e:
            handle_error(f"Ошибка при сворачивании окна: {e}", e, module="window")
            return False

    def maximize_window(self, window):
        """
        Развернуть окно

        Args:
            window: Объект окна

        Returns:
            bool: True, если окно успешно развернуто
        """
        try:
            if window:
                window.maximize()
                return True
            return False
        except Exception as e:
            handle_error(f"Ошибка при разворачивании окна: {e}", e, module="window")
            return False

    def wait_for_window(self, title, timeout=10):
        """
        Ждать появления окна с заданным заголовком

        Args:
            title (str): Заголовок окна
            timeout (int): Таймаут в секундах

        Returns:
            object: Объект окна или None, если окно не появилось за указанное время
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

    def find_window(self, title=None, process_name=None):
        """
        Найти окно по заголовку или имени процесса

        Args:
            title (str, optional): Заголовок окна
            process_name (str, optional): Имя процесса

        Returns:
            object: Объект окна или None, если окно не найдено
        """
        try:
            if title:
                return self.get_window_by_title(title)
            elif process_name:
                # Здесь мы ищем окно по имени процесса
                # Это упрощенная реализация, в реальности нужно использовать
                # более сложную логику для поиска окна по имени процесса
                import psutil

                for proc in psutil.process_iter(["pid", "name"]):
                    if process_name.lower() in proc.info["name"].lower():
                        # Получаем все окна
                        all_windows = self.get_all_windows()
                        # Ищем окно, принадлежащее этому процессу
                        for window in all_windows:
                            try:
                                if window._hWnd:  # Проверяем, что окно существует
                                    return window
                            except Exception:
                                pass
            return None
        except Exception as e:
            handle_error(f"Ошибка при поиске окна: {e}", e, module="window")
            return None

    def get_window_text(self, window):
        """
        Получить текст окна

        Args:
            window: Объект окна

        Returns:
            str: Текст окна или пустая строка в случае ошибки
        """
        try:
            if window:
                return window.title
            return ""
        except Exception as e:
            handle_error(f"Ошибка при получении текста окна: {e}", e, module="window")
            return ""
