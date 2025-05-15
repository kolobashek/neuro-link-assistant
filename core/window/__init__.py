# Модуль управления окнами
import platform


def get_window_manager():
    """Возвращает платформо-зависимый менеджер окон"""
    system = platform.system().lower()

    if system == "windows":
        from core.windows.window_manager import WindowManager

        return WindowManager()
    else:
        raise NotImplementedError(f"Платформа {system} не поддерживается")
