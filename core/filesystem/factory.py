"""
Фабрика для создания экземпляров файловой системы.
Предоставляет единую точку доступа к функциональности файловой системы
в зависимости от текущей платформы.
"""

import os
import platform
from typing import Optional, Type

from core.common.file_system import AbstractFileSystem

# Глобальный экземпляр файловой системы для повторного использования
_file_system_instance: Optional[AbstractFileSystem] = None


def get_file_system(force_new: bool = False) -> AbstractFileSystem:
    """
    Возвращает экземпляр файловой системы для текущей платформы.

    Args:
        force_new (bool): Если True, будет создан новый экземпляр, даже если
                         уже существует глобальный экземпляр. По умолчанию False.

    Returns:
        AbstractFileSystem: Экземпляр файловой системы для текущей платформы.

    Raises:
        NotImplementedError: Если текущая платформа не поддерживается.
    """
    global _file_system_instance

    # Используем существующий экземпляр, если он есть и не требуется новый
    if _file_system_instance is not None and not force_new:
        return _file_system_instance

    # Определяем текущую операционную систему
    system = platform.system().lower()

    # Создаем экземпляр в зависимости от платформы
    if system == "windows":
        from core.platform.windows.file_system import WindowsFileSystem

        _file_system_instance = WindowsFileSystem()
    elif system == "linux":
        try:
            from core.platform.linux.file_system import LinuxFileSystem

            _file_system_instance = LinuxFileSystem()
        except ImportError:
            raise NotImplementedError("Поддержка Linux еще не реализована")
    elif system == "darwin":  # MacOS
        try:
            from core.platform.macos.file_system import MacOSFileSystem

            _file_system_instance = MacOSFileSystem()
        except ImportError:
            raise NotImplementedError("Поддержка MacOS еще не реализована")
    else:
        raise NotImplementedError(f"Операционная система '{system}' не поддерживается")

    return _file_system_instance


def register_file_system_implementation(
    os_name: str, implementation_class: Type[AbstractFileSystem]
) -> None:
    """
    Регистрирует пользовательскую реализацию файловой системы для указанной ОС.
    Используется для тестирования или для добавления поддержки новых платформ без
    изменения кода фабрики.

    Args:
        os_name (str): Название операционной системы (например, 'windows', 'linux').
        implementation_class (Type[AbstractFileSystem]): Класс, реализующий AbstractFileSystem.
    """
    setattr(get_file_system, f"_{os_name.lower()}_implementation", implementation_class)


def get_platform_specific_path(relative_path: str) -> str:
    """
    Преобразует относительный путь в абсолютный путь,
    учитывая особенности текущей операционной системы.

    Args:
        relative_path (str): Относительный путь.

    Returns:
        str: Абсолютный путь, адаптированный для текущей ОС.
    """
    # Нормализуем разделители пути в соответствии с текущей ОС
    normalized_path = os.path.normpath(relative_path)

    # Если путь абсолютный, возвращаем его как есть
    if os.path.isabs(normalized_path):
        return normalized_path

    # Иначе объединяем с базовым путем приложения
    base_path = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    return os.path.join(base_path, normalized_path)
