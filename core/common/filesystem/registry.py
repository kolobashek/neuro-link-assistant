"""
Реестр реализаций файловой системы.
Отвечает за регистрацию и хранение доступных реализаций файловой системы.
"""

from typing import Dict, Type

from core.common.filesystem.base import AbstractFileSystem

# Глобальный словарь для хранения всех зарегистрированных реализаций файловой системы
_file_system_implementations: Dict[str, Type[AbstractFileSystem]] = {}


def register_file_system(name: str, implementation: Type[AbstractFileSystem]) -> None:
    """
    Регистрирует реализацию файловой системы в глобальном реестре.

    Args:
        name (str): Имя реализации (например, "windows", "linux", "mac")
        implementation (Type[AbstractFileSystem]): Класс, реализующий AbstractFileSystem
    """
    global _file_system_implementations
    _file_system_implementations[name.lower()] = implementation


def get_registered_file_systems() -> Dict[str, Type[AbstractFileSystem]]:
    """
    Возвращает словарь всех зарегистрированных реализаций файловой системы.

    Returns:
        Dict[str, Type[AbstractFileSystem]]: Словарь с именами и классами реализаций
    """
    return _file_system_implementations.copy()


def get_file_system_implementation(name: str) -> Type[AbstractFileSystem]:
    """
    Возвращает класс реализации файловой системы по имени.

    Args:
        name (str): Имя реализации файловой системы

    Returns:
        Type[AbstractFileSystem]: Класс реализации файловой системы

    Raises:
        KeyError: Если реализация с указанным именем не зарегистрирована
    """
    name = name.lower()
    if name not in _file_system_implementations:
        raise KeyError(f"Реализация файловой системы '{name}' не зарегистрирована")

    return _file_system_implementations[name]


def is_file_system_registered(name: str) -> bool:
    """
    Проверяет, зарегистрирована ли реализация файловой системы с указанным именем.

    Args:
        name (str): Имя реализации файловой системы

    Returns:
        bool: True, если реализация зарегистрирована, иначе False
    """
    return name.lower() in _file_system_implementations


# Автоматическая регистрация доступных реализаций файловой системы
try:
    # Пытаемся импортировать и зарегистрировать реализацию для Windows
    from core.platform.windows.filesystem import Win32FileSystem

    register_file_system("windows", Win32FileSystem)
except ImportError:
    pass

# Другие реализации можно добавить здесь по мере их создания
