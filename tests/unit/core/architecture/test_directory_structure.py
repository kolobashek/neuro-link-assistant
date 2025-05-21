"""
Тесты для проверки соответствия структуры каталогов архитектурным принципам.
Эти тесты являются частью процесса рефакторинга и помогают контролировать
трансформацию кодовой базы к новой архитектуре.
"""

import os

import pytest


class TestDirectoryStructure:
    """Тесты для проверки структуры каталогов."""

    def test_core_directory_exists(self):
        """Проверка существования базовой директории core."""
        assert os.path.isdir("core"), "Директория core не существует"

    def test_common_directory_exists(self):
        """Проверка существования директории core/common."""
        common_dir = os.path.join("core", "common")
        assert os.path.isdir(common_dir), "Директория core/common не существует"

    def test_platform_directory_exists(self):
        """Проверка существования директории core/platform."""
        platform_dir = os.path.join("core", "platform")
        assert os.path.isdir(platform_dir), "Директория core/platform не существует"

    def test_common_subdirectories_exist(self):
        """Проверка существования основных поддиректорий в core/common."""
        common_dir = os.path.join("core", "common")
        expected_subdirs = ["input", "filesystem", "window", "registry", "system", "process"]

        for subdir in expected_subdirs:
            dir_path = os.path.join(common_dir, subdir)
            assert os.path.isdir(dir_path), f"Директория {dir_path} не существует"

    def test_platform_windows_exists(self):
        """Проверка существования директории для Windows-зависимого кода."""
        windows_dir = os.path.join("core", "platform", "windows")
        assert os.path.isdir(windows_dir), "Директория core/platform/windows не существует"

    def test_windows_subdirectories_exist(self):
        """Проверка существования основных поддиректорий в core/platform/windows."""
        windows_dir = os.path.join("core", "platform", "windows")
        expected_subdirs = ["input", "filesystem", "window", "system", "process"]

        for subdir in expected_subdirs:
            dir_path = os.path.join(windows_dir, subdir)
            assert os.path.isdir(dir_path), f"Директория {dir_path} не существует"

    def test_core_modules_exist(self):
        """Проверка существования основных модулей в корне core."""
        core_dir = "core"
        expected_modules = ["component_registry.py", "plugin_manager.py", "system_initializer.py"]

        for module in expected_modules:
            module_path = os.path.join(core_dir, module)
            assert os.path.isfile(module_path), f"Файл {module_path} не существует"

    def test_subsystem_directories_exist(self):
        """Проверка существования директорий для основных подсистем."""
        core_dir = "core"
        expected_subsystems = ["llm", "vision", "web", "db", "utils"]

        for subsystem in expected_subsystems:
            dir_path = os.path.join(core_dir, subsystem)
            assert os.path.isdir(dir_path), f"Директория {dir_path} не существует"

    def test_input_base_classes_exist(self):
        """Проверка существования файлов базовых классов для ввода (высший приоритет)."""
        input_dir = os.path.join("core", "common", "input")
        expected_files = ["base.py", "factory.py", "registry.py", "__init__.py"]

        for file in expected_files:
            file_path = os.path.join(input_dir, file)
            assert os.path.isfile(file_path), f"Файл {file_path} не существует"

    def test_input_implementation_exists(self):
        """Проверка существования реализаций контроллеров ввода для Windows."""
        windows_input_dir = os.path.join("core", "platform", "windows", "input")
        expected_files = ["keyboard.py", "mouse.py", "__init__.py"]

        for file in expected_files:
            file_path = os.path.join(windows_input_dir, file)
            assert os.path.isfile(file_path), f"Файл {file_path} не существует"

    def test_deprecated_directories_dont_exist(self):
        """Проверка отсутствия устаревших директорий после рефакторинга."""
        deprecated_dirs = [
            os.path.join("core", "input"),
            os.path.join("core", "windows"),
            os.path.join("core", "window"),
        ]

        for dir_path in deprecated_dirs:
            assert not os.path.isdir(
                dir_path
            ), f"Устаревшая директория {dir_path} все еще существует"


if __name__ == "__main__":
    pytest.main(["-v", __file__])
