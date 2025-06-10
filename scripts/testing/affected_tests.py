"""Запуск тестов для измененных файлов"""

import os
import subprocess
import sys
from pathlib import Path
from typing import List, Optional, Set


def get_test_path_for_file(changed_file: str) -> Optional[str]:
    """Определяет путь к тестам для измененного файла"""
    if changed_file.startswith("core/"):
        return changed_file.replace("core/", "tests/unit/core/")
    elif changed_file.startswith("routes/"):
        return "tests/integration/"
    elif changed_file.startswith("scripts/"):
        return "tests/unit/"
    return None


def collect_affected_tests(changed_files: List[str]) -> Set[str]:
    """Собирает пути тестов для измененных файлов"""
    test_paths = set()

    for file_path in changed_files:
        if file_path.endswith(".py"):
            test_path = get_test_path_for_file(file_path)
            if test_path and Path(test_path).exists():
                test_paths.add(test_path)

    return test_paths


def run_affected_tests(changed_files: Optional[List[str]] = None) -> bool:
    """Запускает тесты только для измененных файлов"""
    if changed_files is None:
        changed_files = sys.argv[1:] if len(sys.argv) > 1 else []

    if not changed_files:
        print("❌ Не указаны измененные файлы")
        return False

    test_paths = collect_affected_tests(changed_files)

    if not test_paths:
        print("ℹ️ Нет тестов для измененных файлов")
        return True

    print(f"🧪 Запуск тестов для измененных файлов:")
    for path in sorted(test_paths):
        print(f"  📁 {path}")

    cmd = ["poetry", "run", "pytest"] + list(test_paths) + ["-v"]

    try:
        result = subprocess.run(cmd)
        return result.returncode == 0
    except Exception as e:
        print(f"❌ Ошибка запуска тестов: {e}")
        return False


def main():
    """CLI для affected tests"""
    success = run_affected_tests()
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
