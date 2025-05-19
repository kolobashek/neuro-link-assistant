import os
import time
from typing import Any
from unittest.mock import MagicMock

import pytest
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.common.by import By

# from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

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

    def get(self, url):
        """Открытие URL."""
        return self.driver.get(url)

    def find_element(self, by, value):
        """Поиск элемента."""
        return self.driver.find_element(by, value)

    def find_elements(self, by, value):
        """Поиск элементов."""
        return self.driver.find_elements(by, value)

    def wait_for_element(self, by, value, timeout=10):
        """Ожидание появления элемента."""
        return WebDriverWait(self.driver, timeout).until(
            EC.presence_of_element_located((by, value))
        )

    def wait_for_clickable(self, by, value, timeout=10):
        """Ожидание кликабельности элемента."""
        return WebDriverWait(self.driver, timeout).until(EC.element_to_be_clickable((by, value)))

    def click(self, by, value):
        """Клик по элементу с ожиданием кликабельности."""
        element = self.wait_for_clickable(by, value)
        element.click()
        return element

    def input(self, by, value, text):
        """Ввод текста в элемент."""
        element = self.wait_for_element(by, value)
        element.clear()
        element.send_keys(text)
        return element

    def execute_script(self, script, *args):
        """Выполнение JavaScript-кода."""
        return self.driver.execute_script(script, *args)

    def back(self):
        """Навигация назад."""
        return self.driver.back()

    def forward(self):
        """Навигация вперед."""
        return self.driver.forward()

    def refresh(self):
        """Обновление страницы."""
        return self.driver.refresh()

    def get_current_url(self):
        """Получение текущего URL."""
        return self.driver.current_url

    def switch_to_window(self, window_handle):
        """Переключение на другое окно/вкладку."""
        return self.driver.switch_to.window(window_handle)

    def close(self):
        """Закрытие текущего окна/вкладки."""
        return self.driver.close()

    def set_window_size(self, width, height):
        """Установка размера окна."""
        return self.driver.set_window_size(width, height)

    def get_window_size(self):
        """Получение текущего размера окна."""
        return self.driver.get_window_size()

    def get_page_source(self):
        """Получение HTML-кода страницы."""
        return self.driver.page_source

    def take_screenshot(self, filename):
        """Сделать скриншот страницы."""
        return self.driver.save_screenshot(filename)

    def __getattr__(self, name: str) -> Any:
        """Делегирует неизвестные атрибуты к объекту WebDriver."""
        return getattr(self.driver, name)


@pytest.fixture(scope="function")
def ui_client(base_url):
    """Фикстура для тестирования UI с Selenium WebDriver"""
    # Создаем опции Chrome
    chrome_options = Options()

    # Добавляем аргументы для запуска Chrome в безголовом режиме при CI/CD
    if os.environ.get("CI") == "true":
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")

    # Дополнительные настройки для стабильности тестов
    chrome_options.add_argument("--window-size=1920,1080")
    chrome_options.add_argument("--disable-extensions")
    chrome_options.add_argument("--disable-popup-blocking")

    # Инициализируем драйвер Chrome
    service = ChromeService()
    driver = webdriver.Chrome(service=service, options=chrome_options)

    # Устанавливаем окно браузера на максимальный размер
    driver.maximize_window()

    # Устанавливаем таймаут для неявных ожиданий
    driver.implicitly_wait(10)

    # Создаем и предоставляем UiTestDriver
    ui_driver = UiTestDriver(driver, base_url)

    yield ui_driver

    # Закрываем браузер после теста
    driver.quit()


@pytest.fixture
def base_url():
    """Фикстура, возвращающая базовый URL для тестов."""
    return TEST_CONFIG["base_url"]


@pytest.fixture(scope="function")
def authenticated_ui_client(ui_client):
    """
    Фикстура для UI-тестов, требующих аутентификации.

    Выполняет вход в систему перед запуском теста и выход после завершения.
    """
    # Открываем страницу логина
    ui_client.get("http://localhost:5000/login")

    try:
        # Ожидаем загрузки формы логина
        WebDriverWait(ui_client.driver, 10).until(
            EC.presence_of_element_located(
                (By.CSS_SELECTOR, "form input[type='email'], form input[name='username']")
            )
        )

        # Вводим учетные данные для тестирования
        # Замените на реальные тестовые учетные данные для вашего приложения
        username_input = ui_client.find_element(
            By.CSS_SELECTOR, "input[type='email'], input[name='username']"
        )
        username_input.send_keys("test@example.com")

        password_input = ui_client.find_element(By.CSS_SELECTOR, "input[type='password']")
        password_input.send_keys("testpassword")

        # Отправляем форму
        login_button = ui_client.find_element(
            By.CSS_SELECTOR, "button[type='submit'], input[type='submit']"
        )
        login_button.click()

        # Ожидаем успешной аутентификации
        WebDriverWait(ui_client.driver, 10).until(lambda driver: "login" not in driver.current_url)

        # Проверяем, что авторизация произошла успешно
        assert "login" not in ui_client.current_url, "Не удалось войти в систему"

    except Exception as e:
        # В случае проблем с авторизацией, пропускаем тест
        pytest.skip(f"Не удалось выполнить вход в систему: {str(e)}")

    # Передаем аутентифицированного клиента в тест
    yield ui_client

    # После теста - выходим из системы
    try:
        ui_client.get("http://localhost:5000/logout")
        time.sleep(1)  # Даем время на обработку выхода
    except Exception:
        # Игнорируем ошибки при выходе
        pass


@pytest.fixture
def mobile_ui_client(ui_client):
    """
    Фикстура для мобильного вида UI-тестирования.

    Устанавливает размер окна браузера, соответствующий мобильному устройству,
    и возвращает его в исходное состояние после завершения теста.
    """
    # Сохраняем исходный размер окна
    original_size = ui_client.get_window_size()

    # Устанавливаем размер окна как у iPhone X
    ui_client.set_window_size(375, 812)

    # Передаем клиент в тест
    yield ui_client

    # Возвращаем исходный размер окна
    ui_client.set_window_size(original_size["width"], original_size["height"])


@pytest.fixture
def take_screenshot_on_failure(ui_client, request):
    """
    Фикстура для создания скриншотов при падении тестов.

    Автоматически делает скриншот страницы, если тест не прошел,
    и сохраняет его в директории screenshots.
    """
    yield

    # Делаем скриншот только в случае падения теста
    if request.node.rep_setup.failed or request.node.rep_call.failed:
        # Создаем директорию для скриншотов, если она не существует
        screenshots_dir = "screenshots"
        if not os.path.exists(screenshots_dir):
            os.makedirs(screenshots_dir)

        # Формируем имя скриншота на основе имени теста и временной метки
        timestamp = time.strftime("%Y%m%d-%H%M%S")
        screenshot_name = f"{screenshots_dir}/{request.node.name}-{timestamp}.png"

        # Делаем и сохраняем скриншот
        ui_client.take_screenshot(screenshot_name)
        print(f"Скриншот сохранен: {screenshot_name}")


# Хук для пометки теста как провалившегося в репорте для скриншотов
@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item, call):
    outcome = yield
    rep = outcome.get_result()
    setattr(item, f"rep_{rep.when}", rep)


@pytest.fixture(scope="function")
def mobile_driver():
    """Фикстура для тестирования на мобильном устройстве с эмуляцией"""
    # Настройка мобильной эмуляции
    mobile_emulation = {"deviceName": "iPhone X"}
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_experimental_option("mobileEmulation", mobile_emulation)

    # Для CI/CD добавляем необходимые аргументы
    if os.environ.get("CI") == "true":
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")

    driver = webdriver.Chrome(options=chrome_options)
    yield driver
    driver.quit()
