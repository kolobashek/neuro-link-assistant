"""
Фабрика для создания экземпляров файловой системы.
Отвечает за создание и кэширование экземпляров файловой системы.
"""

import platform
from typing import Dict, Optional, Type

from core.common.filesystem.base import AbstractFileSystem
from core.common.filesystem.registry import (
    get_file_system_implementation,
    is_file_system_registered,
    register_file_system,
)

# Кэш созданных экземпляров файловой системы
_file_system_instances: Dict[str, AbstractFileSystem] = {}


def create_file_system(name: str, **kwargs) -> AbstractFileSystem:
    """
    Создает новый экземпляр файловой системы с указанным именем.

    Args:
        name (str): Имя реализации файловой системы
        **kwargs: Дополнительные параметры для конструктора

    Returns:
        AbstractFileSystem: Экземпляр файловой системы

    Raises:
        KeyError: Если реализация с указанным именем не зарегистрирована
    """
    file_system_class = get_file_system_implementation(name)
    return file_system_class(**kwargs)


def get_file_system(name: Optional[str] = None) -> AbstractFileSystem:
    """
    Возвращает экземпляр файловой системы с указанным именем.
    Если экземпляр уже был создан ранее, возвращает его из кэша.
    Если имя не указано, определяет текущую операционную систему и возвращает соответствующую реализацию.

    Args:
        name (Optional[str]): Имя реализации файловой системы или None для автоопределения

    Returns:
        AbstractFileSystem: Экземпляр файловой системы

    Raises:
        RuntimeError: Если не удалось определить или создать файловую систему
    """
    global _file_system_instances

    # Если имя не указано, определяем его на основе текущей ОС
    if name is None:
        current_os = platform.system().lower()
        if current_os == "windows":
            name = "windows"
        elif current_os == "linux":
            name = "linux"
        elif current_os == "darwin":
            name = "mac"
        else:
            raise RuntimeError(f"Неподдерживаемая операционная система: {platform.system()}")

    # Нормализуем имя
    name = name.lower()

    # Проверяем, есть ли уже созданный экземпляр
    if name in _file_system_instances:
        return _file_system_instances[name]

    # Проверяем, зарегистрирована ли реализация
    if not is_file_system_registered(name):
        raise RuntimeError(f"Реализация файловой системы '{name}' не зарегистрирована")

    # Создаем новый экземпляр
    file_system = create_file_system(name)

    # Сохраняем в кэш
    _file_system_instances[name] = file_system

    return file_system


# Экспортируем функцию регистрации для удобства использования
# Это позволяет клиентскому коду регистрировать свои реализации без прямого импорта из registry
def register_file_system_implementation(
    name: str, implementation: Type[AbstractFileSystem]
) -> None:
    """
    Регистрирует реализацию файловой системы.
    Перенаправляет вызов к функции в registry.py для обратной совместимости.

    Args:
        name (str): Имя реализации
        implementation (Type[AbstractFileSystem]): Класс реализации
    """
    register_file_system(name, implementation)
