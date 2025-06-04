#!/usr/bin/env python3
"""Раннер для UI тестов с автоматическим запуском приложения"""

import os
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path

from .base_test_runner import BaseTestRunner
from .test_app_manager import TestAppManager


class UITestRunner(BaseTestRunner):
    def __init__(self):
        super().__init__("ui_parallel")
        self.app_manager = TestAppManager()

    def setup(self) -> bool:
        """Настройка и запуск приложения для тестов"""
        print(f"🔧 [SETUP] Подготовка приложения для UI тестов...")
        return self.app_manager.start_app()

    def cleanup(self) -> None:
        """Очистка после тестов"""
        print(f"🧹 [CLEANUP] Остановка приложения...")
        self.app_manager.stop_app()

    def run_tests(self, test_path="tests/ui/", parallel=True, workers=4):
        """Запуск UI тестов с правильной обработкой кодировки"""
        print(f"🚀 [UI TESTS] Starting {'parallel' if parallel else 'sequential'} execution...")
        print(f"🆔 [SESSION] ID: {self.session_id}")

        # Настройка логирования
        log_file = self.logs_dir / f"{self.session_id}.log"
        json_report = self.logs_dir / f"{self.session_id}.json"
        junit_xml = self.logs_dir / f"{self.session_id}_junit.xml"

        print(f"📝 [LOGGING] Text log: {log_file}")
        print(f"📊 [LOGGING] JSON report: {json_report}")
        print(f"📋 [LOGGING] JUnit XML: {junit_xml}")

        # Базовые аргументы pytest
        cmd = [
            "poetry",
            "run",
            "pytest",
            test_path,
            "-v",
            "--tb=short",
            f"--junitxml={junit_xml}",
        ]

        # Добавляем параллельность если нужно
        if parallel:
            cmd.extend(["-n", str(workers)])

        # Переменные окружения для подавления Chrome сообщений
        env = os.environ.copy()
        env.update(
            {
                "PYTHONIOENCODING": "utf-8",
                "PYTHONLEGACYWINDOWSSTDIO": "1" if os.name == "nt" else "",
                "CHROME_LOG_FILE": os.devnull,
                "WEBDRIVER_LOG_LEVEL": "SEVERE",
            }
        )

        try:
            print(f"⏱️  [EXECUTION] Starting pytest...")
            start_time = time.time()

            # ИСПРАВЛЯЕМ: запускаем с правильной кодировкой
            with open(log_file, "w", encoding="utf-8", errors="replace") as log_f:
                process = subprocess.Popen(
                    cmd,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.STDOUT,
                    env=env,
                    encoding="utf-8",  # Явная кодировка
                    errors="replace",  # Замена проблемных символов
                    universal_newlines=True,
                )

                # Проверяем что stdout доступен
                assert process.stdout is not None, "stdout должен быть доступен"

                # Читаем вывод построчно с обработкой ошибок
                while True:
                    try:
                        line = process.stdout.readline()
                        if not line:
                            break

                        # Фильтруем ненужные сообщения Chrome
                        if any(
                            skip in line
                            for skip in [
                                "DevTools listening",
                                "voice_transcription.cc",
                                "WARNING: All log messages before absl::InitializeLog()",
                                "Registering VoiceTranscriptionCapability",
                            ]
                        ):
                            continue

                        # Выводим и записываем
                        print(line.rstrip())
                        log_f.write(line)
                        log_f.flush()

                    except UnicodeDecodeError as e:
                        print(f"⚠️ [ENCODING] Skipping problematic line: {e}")
                        continue

                # Ждём завершения процесса
                return_code = process.wait()

            execution_time = time.time() - start_time

            if return_code == 0:
                print(f"✅ [SUCCESS] Tests completed in {execution_time:.1f}s")
            else:
                print(f"❌ [FAILED] Tests failed with code {return_code} in {execution_time:.1f}s")

            return return_code == 0

        except Exception as e:
            print(f"❌ [ERROR] Test execution failed: {e}")
            return False


def main():
    runner = UITestRunner()

    # Параметры из командной строки
    test_path = sys.argv[1] if len(sys.argv) > 1 else "tests/ui/"
    parallel = "--no-parallel" not in sys.argv
    workers = 4

    if "--workers" in sys.argv:
        idx = sys.argv.index("--workers")
        if idx + 1 < len(sys.argv):
            workers = int(sys.argv[idx + 1])

    success = runner.run_tests(test_path, parallel, workers)
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
