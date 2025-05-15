# Модуль управления процессами
import platform


def get_process_manager():
    """Возвращает платформо-зависимый менеджер процессов"""
    system = platform.system().lower()

    if system == "windows":
        from core.windows.process_manager import ProcessManager

        return ProcessManager()
    else:
        raise NotImplementedError(f"Платформа {system} не поддерживается")
