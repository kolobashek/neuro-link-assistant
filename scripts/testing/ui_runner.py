"""Объединенный UI Test Runner с полным функционалом"""

import json
import os
import platform
import subprocess
import sys
import time
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional

import psutil
import requests
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from scripts.app.manager import AppConfig, AppManager, AppMode
from scripts.network.port_manager import PortManager  # ← Добавить импорт

from .base_runner import BaseTestRunner


class UITestMode(Enum):
    """Режимы UI тестирования"""

    HEADLESS = "headless"
    PARALLEL = "parallel"
    GENTLE = "gentle"
    DIRECT = "direct"
    NORMAL = "normal"


@dataclass
class UITestConfig:
    """Конфигурация UI тестов"""

    mode: UITestMode = UITestMode.HEADLESS
    parallel_workers: int = 2
    timeout: int = 30
    app_port: Optional[int] = None  # ← Изменили на None для автопоиска
    headless: bool = True
    test_path: str = "tests/ui/e2e/"
    save_screenshots: bool = True
    detailed_logging: bool = True
    use_external_app: bool = False


class UITestRunner(BaseTestRunner):
    """Универсальный UI Test Runner"""

    def __init__(self, config: Optional[UITestConfig] = None):
        super().__init__("ui_tests")
        self.config = config if config is not None else UITestConfig()

        # Автоматический поиск свободного порта
        if self.config.app_port is None:
            try:
                self.config.app_port = PortManager.find_any_free_port(
                    5000
                )  # ← Теперь PortManager доступен
                print(f"🔍 [UI] Используем свободный порт: {self.config.app_port}")
            except Exception:
                self.config.app_port = 5000  # Fallback

        self.app_manager: Optional[AppManager] = None
        self.driver: Optional[webdriver.Chrome] = None
        self.test_results: Dict[str, Any] = {}

    def setup(self) -> bool:
        """Настройка перед UI тестами"""
        self._log(
            "🚀 Настройка UI тестов",
            {
                "mode": self.config.mode.value,
                "parallel_workers": self.config.parallel_workers,
                "headless": self.config.headless,
                "app_port": self.config.app_port,
            },
        )

        # Настройка окружения
        if self.config.headless:
            os.environ["HEADLESS"] = "true"
        else:
            os.environ.pop("HEADLESS", None)

        # Настройка приложения
        if not self.config.use_external_app:
            app_config = AppConfig(port=self.config.app_port or 5000, mode=AppMode.TESTING)
            self.app_manager = AppManager(app_config)

            if not self.app_manager.start_app():
                self._log("❌ Не удалось запустить приложение")
                return False
        else:
            # Проверяем внешнее приложение
            if not self._check_external_app():
                self._log("❌ Внешнее приложение недоступно")
                return False

        return True

    def cleanup(self) -> None:
        """Очистка после тестов"""
        self._log("🧹 Очистка после UI тестов")

        # Закрываем WebDriver
        if self.driver:
            try:
                self.driver.quit()
            except:
                pass
            self.driver = None

        # Останавливаем приложение
        if self.app_manager and not self.config.use_external_app:
            self.app_manager.stop_app()

    def run_tests(self) -> bool:
        """Запускает UI тесты согласно конфигурации"""
        if not self.setup():
            return False

        try:
            if self.config.mode == UITestMode.DIRECT:
                return self._run_direct_test()
            elif self.config.mode == UITestMode.GENTLE:
                return self._run_gentle_tests()
            elif self.config.mode == UITestMode.PARALLEL:
                return self._run_parallel_tests()
            elif self.config.mode == UITestMode.NORMAL:
                return self._run_normal_tests()
            else:  # HEADLESS
                return self._run_headless_tests()

        finally:
            self.cleanup()

    # === РЕЖИМЫ ТЕСТИРОВАНИЯ ===

    def _run_direct_test(self) -> bool:
        """Прямой тест без фикстур"""
        self._log("🧪 Запуск прямого теста")

        # Проверяем приложение
        if not self._verify_app_running():
            return False

        # Настройка Chrome
        chrome_options = self._get_chrome_options()

        try:
            self.driver = webdriver.Chrome(options=chrome_options)
            self._log("✅ Chrome WebDriver инициализирован")

            # Открываем страницу
            app_url = f"http://localhost:{self.config.app_port}"
            self.driver.get(app_url)
            self._log("✅ Страница загружена", {"title": self.driver.title})

            # Основные проверки
            return self._run_basic_checks()

        except Exception as e:
            self._log("❌ Ошибка прямого теста", {"error": str(e)})
            return False

    def _run_gentle_tests(self) -> bool:
        """Щадящий режим - один тест за раз"""
        self._log("🧪 Запуск тестов в щадящем режиме")

        cmd = [
            "poetry",
            "run",
            "pytest",
            "tests/ui/e2e/ui/test_ai_models.py",  # Начинаем с исправленного теста
            "-v",
            "--tb=short",
            "-x",  # Останавливаем на первой ошибке
            f"--timeout={self.config.timeout}",
        ]

        return self._execute_pytest(cmd)

    def _run_parallel_tests(self) -> bool:
        """Параллельное выполнение тестов"""
        self._log("🧪 Запуск параллельных тестов", {"workers": self.config.parallel_workers})

        # Создаем детальные логи
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        log_file = self.logs_dir / f"ui_parallel_{timestamp}.log"
        json_file = self.logs_dir / f"ui_parallel_{timestamp}.json"
        junit_file = self.logs_dir / f"ui_parallel_{timestamp}_junit.xml"

        cmd = [
            "poetry",
            "run",
            "pytest",
            self.config.test_path,
            "-v",
            "-n",
            str(self.config.parallel_workers),
            "--tb=short",
            "--color=yes",
            f"--junit-xml={junit_file}",
            "--durations=10",
        ]

        success = self._execute_pytest_with_logging(cmd, log_file, json_file)

        # Сохраняем метаданные
        self._save_session_metadata(
            json_file,
            {
                "mode": "parallel",
                "workers": self.config.parallel_workers,
                "files": {"log": str(log_file), "json": str(json_file), "junit": str(junit_file)},
            },
        )

        return success

    def _run_headless_tests(self) -> bool:
        """Обычные headless тесты"""
        self._log("🧪 Запуск headless тестов")

        cmd = ["poetry", "run", "pytest", self.config.test_path, "-v", "--tb=short"]

        return self._execute_pytest(cmd)

    def _run_normal_tests(self) -> bool:
        """Обычные тесты с UI"""
        self._log("🧪 Запуск обычных UI тестов")

        cmd = ["poetry", "run", "pytest", self.config.test_path, "-v"]

        return self._execute_pytest(cmd)

    # === ВСПОМОГАТЕЛЬНЫЕ МЕТОДЫ ===

    def _check_external_app(self) -> bool:
        """Проверка внешнего приложения"""
        try:
            app_url = f"http://localhost:{self.config.app_port}"
            response = requests.get(app_url, timeout=3)
            return 200 <= response.status_code < 500
        except:
            return False

    def _verify_app_running(self) -> bool:
        """Проверяет что приложение работает"""
        app_url = f"http://localhost:{self.config.app_port}"
        try:
            response = requests.get(app_url, timeout=3)
            if 200 <= response.status_code < 500:
                self._log("✅ Приложение доступно", {"status": response.status_code})
                return True
            else:
                self._log("❌ Приложение недоступно", {"status": response.status_code})
                return False
        except Exception as e:
            self._log("❌ Приложение недоступно", {"error": str(e)})
            return False

    def _get_chrome_options(self) -> Options:
        """Настройки Chrome для тестов"""
        chrome_options = Options()

        if self.config.headless:
            chrome_options.add_argument("--headless=new")

        # Базовые настройки
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--window-size=1280,720")
        chrome_options.add_argument("--disable-extensions")
        chrome_options.add_argument("--disable-background-timer-throttling")
        chrome_options.add_argument("--disable-renderer-backgrounding")

        return chrome_options

    def _run_basic_checks(self) -> bool:
        """Базовые проверки UI элементов"""
        assert self.driver is not None, "WebDriver должен быть инициализирован"

        try:
            wait = WebDriverWait(self.driver, 10)

            # Проверяем контейнер AI моделей
            models_container = wait.until(
                EC.presence_of_element_located((By.CLASS_NAME, "ai-models-container"))
            )
            self._log("✅ Найден ai-models-container")

            # Проверяем заголовок
            models_header = models_container.find_element(By.CLASS_NAME, "section-header")
            header_text = models_header.text

            if "Модели ИИ" in header_text:
                self._log("✅ Заголовок корректен", {"text": header_text})
            else:
                self._log("⚠️ Заголовок некорректен", {"text": header_text})

            # Проверяем список моделей
            models_list = models_container.find_element(By.CLASS_NAME, "ai-models-list")

            # Ищем элементы моделей
            model_items = models_list.find_elements(
                By.CSS_SELECTOR, "div.model-item, div.ai-model-item"
            )

            if len(model_items) > 0:
                self._log("✅ Найдены элементы моделей", {"count": len(model_items)})
                return True
            else:
                self._log("❌ Элементы моделей не найдены")
                if self.config.save_screenshots:
                    self._save_screenshot("no_models_found")
                return False

        except Exception as e:
            self._log("❌ Ошибка базовых проверок", {"error": str(e)})
            if self.config.save_screenshots:
                self._save_screenshot("basic_checks_error")
            return False

    def _execute_pytest(self, cmd: List[str]) -> bool:
        """Выполняет pytest команду"""
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8")

            # Выводим результат
            if result.stdout:
                print(result.stdout)
            if result.stderr:
                print(result.stderr)

            return result.returncode == 0

        except Exception as e:
            self._log("❌ Ошибка выполнения pytest", {"error": str(e)})
            return False

    def _execute_pytest_with_logging(self, cmd: List[str], log_file: Path, json_file: Path) -> bool:
        """Выполняет pytest с детальным логированием"""
        start_time = time.time()

        try:
            with open(log_file, "w", encoding="utf-8") as f:
                # Записываем заголовок
                self._write_session_header(f)

                result = subprocess.run(
                    cmd,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.STDOUT,
                    text=True,
                    encoding="utf-8",
                )

                # Записываем результат
                f.write("PYTEST OUTPUT:\n")
                f.write("-" * 40 + "\n")
                f.write(result.stdout)
                f.write("\n" + "-" * 40 + "\n")

                # Записываем сводку
                duration = time.time() - start_time
                self._write_session_summary(f, duration, result.returncode)

                # Консольный вывод с категоризацией
                self._print_categorized_output(result.stdout)

            return result.returncode == 0

        except Exception as e:
            self._log("❌ Ошибка выполнения с логированием", {"error": str(e)})
            return False

    def _write_session_header(self, f):
        """Записывает заголовок сессии"""
        f.write(f"{'='*80}\n")
        f.write(f"NEURO-LINK ASSISTANT - UI TESTS\n")
        f.write(f"{'='*80}\n")
        f.write(f"Session ID: {self.session_id}\n")
        f.write(f"Started: {datetime.now().isoformat()}\n")
        f.write(f"Mode: {self.config.mode.value}\n")
        f.write(f"Platform: {platform.system()} {platform.version()}\n")
        f.write(f"Python: {sys.version.split()[0]}\n")
        f.write(f"{'='*80}\n\n")

    def _write_session_summary(self, f, duration: float, exit_code: int):
        """Zapisuje podsumowanie sesji"""
        f.write(f"\nSESSION SUMMARY:\n")
        f.write(f"{'='*80}\n")
        f.write(f"Ended: {datetime.now().isoformat()}\n")
        f.write(f"Duration: {duration:.2f} seconds\n")
        f.write(f"Exit Code: {exit_code}\n")
        f.write(f"Status: {'PASSED' if exit_code == 0 else 'FAILED'}\n")
        f.write(f"{'='*80}\n")

    def _print_categorized_output(self, output: str):
        """Выводит категоризированный результат"""
        print(f"📋 [TEST OUTPUT]")

        for line in output.split("\n"):
            if line.strip():
                if "PASSED" in line:
                    print(f"   ✅ {line}")
                elif "FAILED" in line:
                    print(f"   ❌ {line}")
                elif "ERROR" in line:
                    print(f"   🔥 {line}")
                elif "WARNING" in line or "WARN" in line:
                    print(f"   ⚠️ {line}")
                elif "collecting" in line.lower():
                    print(f"   🔍 {line}")
                elif "session starts" in line:
                    print(f"   🎬 {line}")
                elif "=" in line and len(line) > 50:
                    print(f"   📏 {line}")
                else:
                    print(f"   📄 {line}")

    def _save_screenshot(self, name: str):
        """Сохраняет скриншот"""
        if not self.driver:
            return

        try:
            # Абсолютный путь от корня проекта
            project_root = Path(__file__).parent.parent.parent
            screenshots_dir = project_root / "static" / "screenshots"
            screenshots_dir.mkdir(parents=True, exist_ok=True)

            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = screenshots_dir / f"{name}_{timestamp}.png"

            self.driver.save_screenshot(str(filename))
            self._log("📸 Скриншот сохранен", {"file": str(filename)})

        except Exception as e:
            self._log("❌ Ошибка сохранения скриншота", {"error": str(e)})

    def _save_session_metadata(self, json_file: Path, additional_data: Dict[str, Any]):
        """Сохраняет метаданные сессии"""
        metadata = {
            "session_id": self.session_id,
            "timestamp": datetime.now().isoformat(),
            "config": {
                "mode": self.config.mode.value,
                "parallel_workers": self.config.parallel_workers,
                "headless": self.config.headless,
                "app_port": self.config.app_port,
            },
            "environment": {
                "platform": platform.system(),
                "python_version": sys.version.split()[0],
                "cpu_count": os.cpu_count(),
                "memory_gb": round(psutil.virtual_memory().total / (1024**3), 2),
            },
            **additional_data,
        }

        try:
            with open(json_file, "w", encoding="utf-8") as f:
                json.dump(metadata, f, indent=2, ensure_ascii=False)
        except Exception as e:
            self._log("❌ Ошибка сохранения метаданных", {"error": str(e)})

    def _log(self, message: str, data: Optional[Dict[str, Any]] = None):
        """Логирование UI тестов"""
        timestamp = time.strftime("%H:%M:%S")
        log_data = f" | {data}" if data else ""
        print(f"[{timestamp}] [UI] {message}{log_data}")


# === ФАБРИЧНЫЕ МЕТОДЫ ===


def create_headless_runner(app_port: int = 5001) -> UITestRunner:
    """Создает headless runner"""
    config = UITestConfig(mode=UITestMode.HEADLESS, app_port=app_port, headless=True)
    return UITestRunner(config)


def create_parallel_runner(workers: int = 2, app_port: int = 5001) -> UITestRunner:
    """Создает параллельный runner"""
    config = UITestConfig(
        mode=UITestMode.PARALLEL,
        parallel_workers=workers,
        app_port=app_port,
        headless=True,
        detailed_logging=True,
    )
    return UITestRunner(config)


def create_gentle_runner(app_port: int = 5001) -> UITestRunner:
    """Создает щадящий runner"""
    config = UITestConfig(mode=UITestMode.GENTLE, app_port=app_port, headless=True, timeout=30)
    return UITestRunner(config)


def create_direct_runner(app_port: int = 5001, headless: bool = True) -> UITestRunner:
    """Создает прямой runner"""
    config = UITestConfig(
        mode=UITestMode.DIRECT, app_port=app_port, headless=headless, use_external_app=True
    )
    return UITestRunner(config)


# === CLI ===


def main():
    """CLI для UI тестов"""
    import argparse

    parser = argparse.ArgumentParser(description="UI Test Runner")
    parser.add_argument("mode", choices=["headless", "parallel", "gentle", "direct", "normal"])
    parser.add_argument("--port", type=int, default=5001, help="Порт приложения")
    parser.add_argument("--workers", type=int, default=2, help="Параллельные воркеры")
    parser.add_argument("--timeout", type=int, default=30, help="Таймаут тестов")
    parser.add_argument(
        "--external-app", action="store_true", help="Использовать внешнее приложение"
    )
    parser.add_argument("--no-headless", action="store_true", help="Отключить headless режим")

    args = parser.parse_args()

    config = UITestConfig(
        mode=UITestMode(args.mode),
        app_port=args.port,
        parallel_workers=args.workers,
        timeout=args.timeout,
        use_external_app=args.external_app,
        headless=not args.no_headless,
    )

    runner = UITestRunner(config)
    success = runner.run_tests()

    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
