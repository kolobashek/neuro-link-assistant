import os
import platform

import pytest

from core.platform.windows.filesystem import Win32FileSystem
from tests.unit.core.common.filesystem.test_base_filesystem import BaseFileSystemTest


class TestWin32FileSystem(BaseFileSystemTest):
    """
    Тесты для Windows-реализации файловой системы.
    Наследует общие тесты из BaseFileSystemTest и добавляет специфичные для Windows.
    """

    file_system_class = Win32FileSystem

    @pytest.fixture(autouse=True)
    def check_platform(self):
        """Пропускаем тесты, если не Windows"""
        if platform.system().lower() != "windows":
            pytest.skip("Тесты Win32FileSystem запускаются только на Windows")

    def test_get_drive_info(self, file_system):
        """Тест получения информации о дисках (Windows-специфичная функция)"""
        drives = file_system.get_drive_info()

        # Проверяем результат
        assert isinstance(drives, dict)

        # На Windows должен быть хотя бы один диск (C:)
        assert len(drives) > 0

        # Проверяем структуру данных для одного из дисков
        for drive, info in drives.items():
            assert isinstance(drive, str)
            assert isinstance(info, dict)
            assert "mountpoint" in info
            assert "total" in info
            assert "used" in info
            assert "free" in info
            assert "percent" in info
            break  # Достаточно проверить один диск

    def test_windows_paths(self, file_system, temp_dir):
        """Тест работы с Windows-путями"""
        # Создаем вложенную структуру каталогов
        nested_dir = os.path.join(temp_dir, "level1", "level2")
        file_system.create_directory(nested_dir)

        # Проверяем, что директория создана
        assert os.path.exists(nested_dir)

        # Создаем файл в этой директории с Windows-путем (обратные слеши)
        win_path = nested_dir.replace("/", "\\") + "\\test.txt"
        result = file_system.create_file(win_path, "Windows path test")

        assert result is True
        assert os.path.exists(os.path.join(nested_dir, "test.txt"))

    def test_long_paths_support(self, file_system, temp_dir):
        """Тест поддержки длинных путей (Windows-специфично)"""
        # Пропускаем тест, если это старая версия Windows без поддержки длинных путей
        try:
            # Создаем очень длинный путь (более 260 символов)
            long_dir = os.path.join(temp_dir, "a" * 250)
            file_system.create_directory(long_dir)

            # Проверяем, что директория создана
            assert os.path.exists(long_dir)

            # Создаем файл в этой директории
            long_file = os.path.join(long_dir, "test.txt")
            result = file_system.create_file(long_file, "Long path test")

            assert result is True
            assert os.path.exists(long_file)

            # Проверяем чтение из файла
            content = file_system.read_file(long_file)
            assert content == "Long path test"
        except (OSError, PermissionError):
            # На некоторых системах длинные пути могут не поддерживаться
            pytest.skip("Система не поддерживает длинные пути")
