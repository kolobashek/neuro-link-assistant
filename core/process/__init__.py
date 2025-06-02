# -*- coding: utf-8 -*-
"""
Модуль для управления процессами - публичный API.
Переэкспортирует функциональность из core.common.process.
"""

from core.common.process import AbstractProcessManager, ProcessManagerFactory, get_process_manager

__all__ = ["get_process_manager", "AbstractProcessManager", "ProcessManagerFactory"]
