
# Модуль файловой системы
import platform

def get_file_system():
    """Возвращает платформо-зависимую реализацию файловой системы"""
    system = platform.system().lower()
    
    if system == 'windows':
        from core.platform.windows.file_system import WindowsFileSystem
        return WindowsFileSystem()
    else:
        raise NotImplementedError(f"Платформа {system} не поддерживается")
