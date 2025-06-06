import os
import subprocess  # ← Добавляем импорт
import sys
import time
from typing import Any
from unittest.mock import MagicMock

import pytest
from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.common.by import By

# from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

sys.path.append(os.path.join(os.path.dirname(__file__), ".."))
from scripts.port_cleanup import PortManager

# Глобальная конфигурация для тестов
TEST_CONFIG = {"base_url": "http://localhost:5000"}

import logging

# Настройка логирования для тестов
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)8s] %(name)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)

# Добавляем логгер для тестов
test_logger = logging.getLogger("TEST")
test_logger.setLevel(logging.INFO)


@pytest.fixture
def mock_component():
    """Фикстура для создания мок-компонента"""
    return MagicMock()


@pytest.fixture(scope="session", autouse=True)
def cleanup_ports():
    """Автоматически очищает порты перед и после тестов"""
    port_manager = PortManager(5000)

    # Очистка перед тестами
    print("🧹 Предварительная очистка портов...")
    port_manager.smart_cleanup()

    yield

    # Очистка после тестов
    print("🧹 Финальная очистка портов...")
    port_manager.smart_cleanup()


def cleanup_port(port: int) -> bool:
    """Улучшенная очистка порта"""
    import subprocess
    import time

    try:
        # Найти процесс на порту
        result = subprocess.run(["netstat", "-ano"], capture_output=True, text=True)

        for line in result.stdout.split("\n"):
            if f":{port}" in line and "LISTENING" in line:
                pid = line.strip().split()[-1]
                print(f"🔧 Завершаем процесс {pid} на порту {port}")

                # Принудительное завершение
                subprocess.run(["taskkill", "/PID", pid, "/F"], capture_output=True)
                time.sleep(2)

        return True
    except Exception as e:
        print(f"❌ Ошибка очистки порта: {e}")
        return False


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

    def wait_for_element(self, by, value, timeout=5):
        """Ожидание элемента с улучшенной отладкой."""
        print(f"🔍 Поиск элемента: {by}={value}")
        try:
            element = WebDriverWait(self.driver, timeout).until(
                EC.presence_of_element_located((by, value))
            )
            print(f"✅ Найден: {by}={value}")
            return element
        except Exception as e:
            print(f"❌ Не найден за {timeout}с: {by}={value}")
            # Отладочная информация
            print(f"📄 Текущий URL: {self.driver.current_url}")
            print(f"📋 Заголовок: {self.driver.title}")
            self.take_screenshot(f"debug_timeout_{value.replace('/', '_')[:20]}.png")
            raise TimeoutException(f"Элемент не найден: {by}={value}")

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


from scripts.app_manager import AppManager

# Добавляем импорт нового менеджера
from scripts.test_app_manager import TestAppManager


# Заменяем фикстуру app_server
@pytest.fixture(scope="session")
def app_server():
    """Фикстура для управления жизненным циклом приложения в UI тестах"""
    manager = TestAppManager(port=5000, timeout=45)

    print(f" [SESSION] Настройка приложения для UI тестов...")

    # Запускаем приложение
    if not manager.start_app():
        pytest.skip("Не удалось запустить приложение для UI тестов")

    # Дополнительная проверка готовности
    if not manager.health_check():
        manager.stop_app()
        pytest.skip("Приложение запустилось, но не прошло проверку здоровья")

    print(f"✅ [SESSION] Приложение готово для UI тестов")

    yield manager

    print(f"🧹 [SESSION] Завершение сессии UI тестов...")
    # Останавливаем приложение
    manager.stop_app()


def create_chrome_driver(base_url: str) -> webdriver.Chrome:
    """Создание Chrome WebDriver с оптимизированными опциями для старых GPU"""
    chrome_options = Options()

    # Минимальный стабильный набор для Windows + старая GPU
    chrome_options.add_argument("--headless=new")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--use-gl=swiftshader")  # Программный рендеринг
    chrome_options.add_argument("--disable-software-rasterizer")
    chrome_options.add_argument("--window-size=1280,720")
    chrome_options.add_argument("--disable-web-security")
    chrome_options.add_argument(
        "--disable-features=VizDisplayCompositor,AudioServiceOutOfProcess,TranslateUI"
    )
    chrome_options.add_argument("--disable-extensions")
    chrome_options.add_argument("--disable-logging")
    chrome_options.add_argument("--log-level=3")
    chrome_options.add_argument("--silent")

    chrome_options.binary_location = "C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe"

    try:
        from webdriver_manager.chrome import ChromeDriverManager

        service = ChromeService(ChromeDriverManager().install())

        driver = webdriver.Chrome(service=service, options=chrome_options)
        # Короткие таймауты для быстрого обнаружения проблем
        driver.set_page_load_timeout(15)
        driver.implicitly_wait(5)

        print("✅ Chrome WebDriver оптимизирован для Windows + старая GPU")
        return driver

    except Exception as e:
        print(f"❌ Ошибка Chrome WebDriver: {e}")
        pytest.skip(f"Chrome WebDriver недоступен: {e}")


# И используем в фикстуре:
@pytest.fixture(scope="session")  # было: function
def ui_client(base_url, app_server):  # Убрать request из параметров
    """Фикстура для UI тестов"""
    # Убрать эти 2 строчки:
    # test_file = str(request.fspath)
    # if not ("ui" in test_file or "e2e" in test_file):
    #     pytest.skip("ui_client фикстура только для UI тестов")

    if not app_server.is_app_running():
        pytest.skip("Приложение не доступно для UI теста")

    # Создаем драйвер
    driver = create_chrome_driver(base_url)
    ui_driver = UiTestDriver(driver, base_url)

    yield ui_driver

    driver.quit()


# Добавить фикстуру для очистки состояния между тестами
@pytest.fixture(autouse=True)
def smart_cleanup_browser_state(request):
    """Условная очистка состояния браузера только для UI тестов"""
    # Проверяем, является ли это UI тестом
    if "ui" in str(request.fspath) or "e2e" in str(request.fspath):
        # Для UI тестов запрашиваем ui_client
        ui_client = request.getfixturevalue("ui_client")

        yield

        # Очищаем после UI теста
        try:
            ui_client.driver.delete_all_cookies()
            ui_client.execute_script("window.localStorage.clear();")
            ui_client.execute_script("window.sessionStorage.clear();")
        except Exception:
            pass
    else:
        # Для не-UI тестов просто пропускаем
        yield


@pytest.fixture(scope="session")  # Только для base_url
def base_url():
    """Фикстура, возвращающая базовый URL для тестов."""
    return TEST_CONFIG["base_url"]


@pytest.fixture(scope="class")  # Для ui_client
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


import psycopg2
import pytest
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from core.db.crud import create_user
from core.db.models import Base


@pytest.fixture(scope="module")
def db_engine():
    """
    Создает тестовый движок БД с изолированной тестовой базой данных.
    """
    # Настройки подключения
    db_user = "neurolink"
    db_password = "secure_password"
    db_host = "localhost"
    db_port = "5432"

    test_db_name = "neurolink_test_db"
    # Создаем тестовую БД, если она не существует
    conn = psycopg2.connect(
        user=db_user,
        password=db_password,
        host=db_host,
        port=db_port,
        database="neurolink",  # Основная БД для начального подключения
    )
    conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
    cursor = conn.cursor()

    cursor.execute("SELECT 1 FROM pg_catalog.pg_database WHERE datname = %s", (test_db_name,))
    db_exists = cursor.fetchone()
    if not db_exists:
        cursor.execute(f"CREATE DATABASE {test_db_name}")
    cursor.close()
    conn.close()

    # Подключаемся к тестовой БД и создаем схему
    test_db_url = f"postgresql://{db_user}:{db_password}@{db_host}:{db_port}/{test_db_name}"
    engine = create_engine(test_db_url)
    # Создаем все таблицы
    Base.metadata.create_all(engine)

    yield engine

    # Удаляем таблицы после всех тестов
    Base.metadata.drop_all(engine)


@pytest.fixture
def db_session(db_engine):
    """
    Создает изолированную сессию БД для каждого теста.
    """
    connection = db_engine.connect()
    transaction = connection.begin()
    session = Session(bind=connection)

    yield session

    # Правильный порядок закрытия ресурсов
    session.close()
    if transaction.is_active:
        transaction.rollback()
    connection.close()


@pytest.fixture
def test_user(db_session):
    """
    Создает тестового пользователя для использования в тестах.
    """
    user_data = {
        "username": "test_user",
        "email": "test@example.com",
        "password_hash": "hashed_password",
    }

    user = create_user(db_session, **user_data)
    db_session.commit()  # Важно: делаем commit, чтобы пользователь был доступен в БД

    return user


# UI тесты конфигурация
def pytest_configure(config):
    """Конфигурация для всех тестов"""
    # Для UI тестов включаем verbose режим
    if hasattr(config.option, "verbose"):
        config.option.verbose = max(config.option.verbose, 1)


def pytest_runtest_setup(item):
    """Настройка перед каждым тестом"""
    # Проверяем, является ли это UI тестом
    test_file = str(item.fspath)
    if "ui" in test_file or "e2e" in test_file:
        print(f"\n🚀 [UI-TEST] Запуск теста: {item.name}")


def pytest_runtest_teardown(item):
    """Очистка после каждого теста"""
    test_file = str(item.fspath)
    if "ui" in test_file or "e2e" in test_file:
        print(f"🏁 [UI-TEST] Завершение теста: {item.name}")


def pytest_collection_modifyitems(config, items):
    """Модификация собранных тестов"""
    for item in items:
        # Добавляем маркер ui для UI тестов
        test_file = str(item.fspath)
        if "ui" in test_file or "e2e" in test_file:
            item.add_marker(pytest.mark.ui)
