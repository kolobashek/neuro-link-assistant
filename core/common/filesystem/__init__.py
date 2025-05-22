"""
Экспортирует основные компоненты подсистемы файловой системы.
"""

from core.common.filesystem.base import AbstractFileSystem
from core.common.filesystem.factory import get_file_system
from core.common.filesystem.factory import (
    register_file_system_implementation as register_file_system,
)

__all__ = ["AbstractFileSystem", "get_file_system", "register_file_system"]
