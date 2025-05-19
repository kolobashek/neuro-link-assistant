from typing import Any
from unittest.mock import MagicMock

import pytest
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service as ChromeService

# Глобальная конфигурация для тестов
TEST_CONFIG = {"base_url": "http://localhost:5000"}


@pytest.fixture
def mock_component():
    """Фикстура для создания мок-компонента"""
    return MagicMock()


@pytest.fixture
def empty_registry():
    """Фикстура для создания пустого реестра компонентов"""
    try:
        from core.component_registry import ComponentRegistry

        return ComponentRegistry()
    except ImportError:
        # Заглушка, если модуль еще не реализован
        class MockComponentRegistry:
            def __init__(self):
                self.components = {}

            def register(self, name, component):
                self.components[name] = component
                return True

            def get(self, name):
                return self.components.get(name)

        return MockComponentRegistry()


class UiTestDriver:
    """Обертка над WebDriver с дополнительной функциональностью для тестов UI."""

    def __init__(self, driver: webdriver.Chrome, base_url: str):
        self.driver = driver
        self.base_url = base_url

    def get_url(self, path: str) -> None:
        """Открывает относительный путь, используя базовый URL."""
        url = f"{self.base_url}{path}"
        self.driver.get(url)

    def __getattr__(self, name: str) -> Any:
        """Делегирует неизвестные атрибуты к объекту WebDriver."""
        return getattr(self.driver, name)


@pytest.fixture(scope="function")
def ui_client():
    """Фикстура для тестирования UI с Selenium WebDriver"""
    # Создаем опции Chrome
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")

    # Инициализируем драйвер Chrome
    service = ChromeService()
    driver = webdriver.Chrome(service=service, options=chrome_options)

    # Устанавливаем окно браузера на максимальный размер
    driver.maximize_window()

    # Предоставляем драйвер для теста
    yield driver

    # Закрываем браузер после теста
    driver.quit()


@pytest.fixture
def base_url():
    """Фикстура, возвращающая базовый URL для тестов."""
    return TEST_CONFIG["base_url"]
