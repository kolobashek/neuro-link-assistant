# -*- coding: utf-8 -*-
"""
Фабрика для создания объектов файловой системы.
"""
import platform
from typing import Dict, Optional, Type

from core.common.error_handler import handle_error
from core.common.filesystem.base import AbstractFileSystem

# Словарь зарегистрированных реализаций файловой системы
_file_system_implementations: Dict[str, Type[AbstractFileSystem]] = {}

# Глобальный экземпляр файловой системы
_file_system_instance = None


def register_file_system(platform_name: str, implementation: Type[AbstractFileSystem]) -> None:
    """
    Регистрирует реализацию файловой системы для указанной платформы.

    Args:
        platform_name (str): Имя платформы ("windows", "linux", "darwin").
        implementation (Type[AbstractFileSystem]): Класс реализации файловой системы.
    """
    _file_system_implementations[platform_name.lower()] = implementation


def create_file_system(platform_name: Optional[str] = None) -> AbstractFileSystem:
    """
    Создает экземпляр файловой системы для указанной платформы.

    Args:
        platform_name (Optional[str], optional): Имя платформы. Если None, используется текущая платформа.

    Returns:
        AbstractFileSystem: Экземпляр файловой системы.

    Raises:
        NotImplementedError: Если реализация для указанной платформы не найдена.
    """
    if platform_name is None:
        platform_name = platform.system().lower()

    # Получаем реализацию для указанной платформы
    file_system_class = _file_system_implementations.get(platform_name)
    if file_system_class is None:
        error_msg = f"Реализация файловой системы для платформы {platform_name} не найдена"
        handle_error(error_msg, module="filesystem")
        raise NotImplementedError(error_msg)

    try:
        # Создаем экземпляр
        return file_system_class()
    except Exception as e:
        handle_error(f"Ошибка создания файловой системы: {e}", e, module="filesystem")
        raise


def get_file_system(new_instance: bool = False) -> AbstractFileSystem:
    """
    Получает экземпляр файловой системы для текущей платформы.

    Args:
        new_instance (bool, optional): Флаг, указывающий, нужно ли создать новый экземпляр.
                                      По умолчанию False.

    Returns:
        AbstractFileSystem: Экземпляр файловой системы.
    """
    global _file_system_instance

    # Если нужен новый экземпляр или экземпляр еще не создан
    if new_instance or _file_system_instance is None:
        _file_system_instance = create_file_system()

    return _file_system_instance


# Автоматическая регистрация реализаций
try:
    from core.platform.windows.filesystem.win32_file_system import Win32FileSystem

    register_file_system("windows", Win32FileSystem)
except ImportError:
    pass
