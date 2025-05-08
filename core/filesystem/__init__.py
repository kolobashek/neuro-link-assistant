  # Модуль файловой системы
import platform

def get_file_system():
    """Возвращает платформо-зависимую реализацию файловой системы"""
    system = platform.system().lower()
    
    if system == 'windows':
        from core.windows.file_system import FileSystem
        return FileSystem()
    else:
        raise NotImplementedError(f"Платформа {system} не поддерживается")