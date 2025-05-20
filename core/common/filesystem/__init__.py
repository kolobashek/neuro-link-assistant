# -*- coding: utf-8 -*-
"""
Предоставляет общие интерфейсы и фабрику для работы с файловой системой.
"""

from core.common.filesystem.base import AbstractFileSystem
from core.common.filesystem.factory import get_file_system, register_file_system

__all__ = ["AbstractFileSystem", "get_file_system", "register_file_system"]
