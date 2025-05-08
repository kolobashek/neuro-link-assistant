# Модуль управления реестром Windows
import platform

def get_registry_manager():
    """Возвращает платформо-зависимый менеджер реестра"""
    system = platform.system().lower()
    
    if system == 'windows':
        from core.registry import get_registry_manager
        return get_registry_manager()
    else:
        raise NotImplementedError(f"Платформа {system} не поддерживается")