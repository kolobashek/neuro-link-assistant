"""Базовый класс для всех test runners"""

import subprocess
from abc import ABC, abstractmethod
from datetime import datetime
from pathlib import Path
from typing import Optional


class BaseTestRunner(ABC):
    """Базовый класс для всех test runners"""

    def __init__(self, test_type: str = "generic"):
        self.test_type = test_type
        self.session_id = f"{test_type}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        self.logs_dir = Path("logs")
        self.logs_dir.mkdir(exist_ok=True)

    @abstractmethod
    def setup(self) -> bool:
        """Настройка перед запуском тестов"""
        pass

    @abstractmethod
    def cleanup(self) -> None:
        """Очистка после тестов"""
        pass

    def _create_subprocess_safely(self, cmd: list, **kwargs) -> subprocess.Popen:
        """Безопасное создание subprocess с проверкой типов"""
        process = subprocess.Popen(cmd, **kwargs)

        # Проверяем что stdout доступен если нужен
        if kwargs.get("stdout") == subprocess.PIPE and process.stdout is None:
            raise RuntimeError("Не удалось получить stdout процесса")

        return process
