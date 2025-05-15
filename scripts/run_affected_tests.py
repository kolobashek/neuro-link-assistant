#!/usr/bin/env python
"""
Скрипт для запуска тестов только для измененных файлов.
"""
import os
import subprocess
import sys


def get_test_path(changed_file):
    """Определяет путь к тестам для измененного файла."""

    # Убираем расширение и заменяем путь core на tests/unit
    if changed_file.startswith("core/"):
        test_path = changed_file.replace("core/", "tests/unit/core/")
        test_dir = os.path.dirname(test_path)
        return test_dir

    return None


def main():
    changed_files = sys.argv[1:]
    test_paths = set()

    for file_path in changed_files:
        # Обрабатываем только Python файлы
        if file_path.endswith(".py") and "core/" in file_path:
            test_path = get_test_path(file_path)
            if test_path:
                test_paths.add(test_path)

    if test_paths:
        cmd = ["python", "-m", "pytest"] + list(test_paths) + ["-v"]
        print(f"Запуск тестов для измененных файлов: {' '.join(cmd)}")
        subprocess.run(cmd)
    else:
        print("Нет тестов для запуска")


if __name__ == "__main__":
    main()
