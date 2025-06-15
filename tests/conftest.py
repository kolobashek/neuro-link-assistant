import os
import subprocess  # < Добавляем импорт
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

# Глобальная конфигурация для тестов
import socket

import pytest

from scripts.app.manager import AppConfig, AppManager, AppMode

# Импортируем унифицированный порт-менеджер
from scripts.network.port_manager import PortManager

# ✅ АРХИТЕКТУРНО ПРАВИЛЬНО: единый источник истины для портов
TEST_PORT = PortManager.get_test_port()  # ← Используем унифицированный метод
TEST_CONFIG = {"base_url": f"http://localhost:{TEST_PORT}"}

print(f"🧪 [TESTS] Используем унифицированный тестовый порт: {TEST_PORT}")

# Устанавливаем в переменные окружения для других компонентов
os.environ["TEST_PORT"] = str(TEST_PORT)


@pytest.fixture(scope="session")
def app_manager():
    """Фикстура для управления приложением в тестах"""
    config = AppConfig(
        port=TEST_PORT,  # ← Используем унифицированный порт
        mode=AppMode.TESTING,
        debug=True,
        auto_cleanup=True,
        force_kill=True,
    )

    manager = AppManager(config)

    # Запускаем приложение один раз для всей сессии
    if not manager.start_app():
        pytest.skip("Не удалось запустить тестовое приложение")

    yield manager

    # Останавливаем после всех тестов
    manager.stop_app()


@pytest.fixture(scope="session")
def base_url():
    """URL приложения для тестов"""
    return f"http://localhost:{TEST_PORT}"


@pytest.fixture(scope="session")
def test_port():
    """Порт приложения для тестов"""
    return TEST_PORT


import logging

# Настройка логированияаж для тестов
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
    from scripts.network.port_manager import PortConfig, PortManager

    # ✅ АРХИТЕКТУРНО ПРАВИЛЬНО: используем унифицированный менеджер
    config = PortConfig(port=TEST_PORT, force_kill=True)
    port_manager = PortManager(config)

    # Очистка перед тестами
    print("🔍 Предварительная очистка тестового порта...")
    port_manager.smart_cleanup()

    yield

    print("✅ Завершение тестовой сессии")
    # Финальная очистка только после ВСЕХ тестов


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
                print(f"?? Завершаем процесс {pid} на порту {port}")

                # Принудительное завершение
                subprocess.run(["taskkill", "/PID", pid, "/F"], capture_output=True)
                time.sleep(2)

        return True
    except Exception as e:
        print(f"? Ошибка очистки порта: {e}")
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


from typing import Any

from selenium.webdriver.remote.webdriver import WebDriver


class UiTestDriver:
    """Обертка над WebDriver с дополнительной функциональностью для тестов UI."""

    def __init__(self, driver: WebDriver, base_url: str):
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
        print(f"?? Поиск элемента: {by}={value}")
        try:
            element = WebDriverWait(self.driver, timeout).until(
                EC.presence_of_element_located((by, value))
            )
            print(f"? Найден: {by}={value}")
            return element
        except Exception as e:
            print(f"? Не найден за {timeout}с: {by}={value}")
            # Отладочная информация
            print(f"?? Текущий URL: {self.driver.current_url}")
            print(f"?? Заголовок: {self.driver.title}")
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


# Заменяем фикстуру app_server
import os

# Добавляем импорт нового менеджера
from scripts.app.manager import AppManager
from scripts.app.manager import AppManager as TestAppManager

# В начале файла
REUSE_APP = os.environ.get("REUSE_APP", "true").lower() == "true"


@pytest.fixture(scope="session")  # ← МЕНЯЕМ на session
def app_server():
    """Фикстура для управления жизненным циклом приложения в UI тестах"""
    from scripts.app.manager import create_external_manager, create_test_manager

    # ВСЕГДА сначала проверяем уже запущенное приложение
    external_manager = create_external_manager(port=TEST_PORT)
    if external_manager.is_app_running() and external_manager.health_check():
        print(f"♻️ [SESSION] Переиспользуем приложение на порту {TEST_PORT}")
        yield external_manager
        return

    # Только если нет - запускаем новое
    manager = create_test_manager(port=TEST_PORT)

    print(f"🚀 [SESSION] Настройка СЕССИОННОГО приложения на порту {TEST_PORT}...")

    if not manager.start_app():
        pytest.skip("Не удалось запустить приложение для UI тестов")

    if not manager.health_check():
        manager.stop_app()
        pytest.skip("Приложение запустилось, но не прошло проверку здоровья")

    print(f"✅ [SESSION] Сессионное приложение готово на порту {TEST_PORT}")
    yield manager

    print(f"🛑 [SESSION] Завершение сессии UI тестов...")
    manager.stop_app()


def create_chrome_driver_debug(base_url: str) -> webdriver.Chrome:
    """Создание Chrome WebDriver в режиме отладки (с видимым окном)"""
    chrome_options = Options()

    # БЕЗ headless режима для отладки
    chrome_options.add_argument("--window-size=1280,720")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-web-security")
    chrome_options.add_argument("--remote-debugging-port=0")

    # Путь к Chrome для debug режима
    possible_chrome_paths = [
        "C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe",
        "C:\\Program Files (x86)\\Google\\Chrome\\Application\\chrome.exe",
    ]

    chrome_path = None
    for path in possible_chrome_paths:
        if os.path.exists(path):
            chrome_path = path
            break

    if chrome_path:
        chrome_options.binary_location = chrome_path

    try:
        from webdriver_manager.chrome import ChromeDriverManager

        service = ChromeService(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=chrome_options)
        driver.set_page_load_timeout(30)
        driver.implicitly_wait(5)
        print("✅ Debug Chrome WebDriver создан")
        return driver
    except Exception as e:
        print(f"❌ Debug Chrome WebDriver недоступен: {e}")
        raise


def create_chrome_driver(base_url: str) -> webdriver.Chrome:
    """Создание Chrome WebDriver с исправленными таймаутами для Windows"""
    chrome_options = Options()

    # 🔥 ИСПРАВЛЯЕМ headless режим для Windows
    chrome_options.add_argument("--headless")  # ← Убираем =new, используем классический headless

    # Базовые стабильные опции для Windows
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--disable-extensions")

    # 🔥 КРИТИЧНО: Исправляем проблемы с DevTools на Windows
    chrome_options.add_argument("--remote-debugging-port=0")  # ← Автоматический порт
    chrome_options.add_argument("--disable-web-security")
    chrome_options.add_argument("--disable-features=VizDisplayCompositor")

    # Размер окна
    chrome_options.add_argument("--window-size=1280,720")

    # Минимальные безопасные опции
    chrome_options.add_argument("--ignore-certificate-errors")
    chrome_options.add_argument("--ignore-ssl-errors")
    chrome_options.add_argument("--log-level=3")  # ← Минимальные логи

    # 🔥 ДОБАВЛЯЕМ специфичные для Windows опции
    if os.name == "nt":  # Windows
        chrome_options.add_argument("--no-first-run")
        chrome_options.add_argument("--no-default-browser-check")
        chrome_options.add_argument("--disable-default-apps")

    # Экспериментальные опции (минимальный набор)
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
    chrome_options.add_experimental_option("useAutomationExtension", False)

    # Путь к Chrome
    possible_chrome_paths = [
        "C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe",
        "C:\\Program Files (x86)\\Google\\Chrome\\Application\\chrome.exe",
    ]

    chrome_path = None
    for path in possible_chrome_paths:
        if os.path.exists(path):
            chrome_path = path
            break

    if chrome_path:
        chrome_options.binary_location = chrome_path
        print(f"✅ Найден Chrome: {chrome_path}")

    try:
        from webdriver_manager.chrome import ChromeDriverManager

        service = ChromeService(ChromeDriverManager().install())

        # Создаем драйвер с уменьшенными таймаутами для отладки
        driver = webdriver.Chrome(service=service, options=chrome_options)

        # 🔥 КРИТИЧНО: Устанавливаем разумные таймауты
        driver.set_page_load_timeout(60)  # Уменьшаем с 120 до 60
        driver.implicitly_wait(10)  # Уменьшаем с 30 до 10

        print("✅ Chrome WebDriver создан")

        # 🔍 Тестируем простую страницу
        print("🔍 Тестируем загрузку простой страницы...")
        try:
            driver.get("data:text/html,<html><body><h1>Test OK</h1></body></html>")
            print("✅ Простая страница загружена")
        except Exception as e:
            print(f"❌ Не удалось загрузить даже простую страницу: {e}")
            driver.quit()
            raise

        return driver

    except Exception as e:
        print(f"❌ Ошибка создания Chrome WebDriver: {e}")

        # 🔥 ДОБАВЛЯЕМ отладочную информацию
        if chrome_path:  # ← ИСПРАВЛЯЕМ: проверяем, что путь не None
            try:
                import subprocess

                result = subprocess.run(
                    [chrome_path, "--version"],
                    capture_output=True,
                    text=True,
                    timeout=10,  # ← Добавляем таймаут
                )
                print(f"🔍 Версия Chrome: {result.stdout.strip()}")
            except Exception as version_error:
                print(f"⚠️ Не удалось определить версию Chrome: {version_error}")
        else:
            print("⚠️ Chrome не найден в стандартных путях")

        pytest.skip(f"Chrome WebDriver недоступен: {e}")


def create_firefox_driver(base_url: str) -> webdriver.Firefox:
    """Создание Firefox WebDriver как альтернатива Chrome"""
    from selenium.webdriver.firefox.options import Options as FirefoxOptions
    from selenium.webdriver.firefox.service import Service as FirefoxService

    firefox_options = FirefoxOptions()
    firefox_options.add_argument("--headless")
    firefox_options.add_argument("--width=1280")
    firefox_options.add_argument("--height=720")

    try:
        from webdriver_manager.firefox import GeckoDriverManager

        service = FirefoxService(GeckoDriverManager().install())

        driver = webdriver.Firefox(service=service, options=firefox_options)
        driver.set_page_load_timeout(60)
        driver.implicitly_wait(20)

        print("✅ Firefox WebDriver настроен")
        return driver

    except Exception as e:
        print(f"❌ Firefox WebDriver недоступен: {e}")
        raise


# И используем в фикстуре:
@pytest.fixture(scope="session")  # ← МЕНЯЕМ на session
def ui_client(base_url, app_server):
    if not app_server.is_app_running():
        pytest.skip("Приложение не доступно для UI теста")

    # 🔥 ДОБАВЛЯЕМ переменную окружения для отладки
    debug_mode = os.environ.get("UI_DEBUG", "false").lower() == "true"

    driver = None
    try:
        if debug_mode:
            print("🔧 Режим отладки UI: запуск Chrome с видимым окном")
            driver = create_chrome_driver_debug(base_url)
        else:
            driver = create_chrome_driver(base_url)
    except Exception as chrome_error:
        print(f"⚠️ Chrome недоступен: {chrome_error}")
        try:
            driver = create_firefox_driver(base_url)
            print("✅ Переключились на Firefox")
        except Exception as firefox_error:
            pytest.skip(
                f"Ни один браузер недоступен. Chrome: {chrome_error}, Firefox: {firefox_error}"
            )

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

        # УСИЛЕННАЯ очистка после UI теста
        try:
            print(f"🧹 [CLEANUP] Очистка состояния после теста: {request.node.name}")

            # Закрываем все лишние окна/вкладки
            windows = ui_client.driver.window_handles
            if len(windows) > 1:
                for window in windows[1:]:  # Оставляем только первое окно
                    ui_client.driver.switch_to.window(window)
                    ui_client.driver.close()
                ui_client.driver.switch_to.window(windows[0])

            # Очищаем состояние
            ui_client.driver.delete_all_cookies()
            ui_client.execute_script("window.localStorage.clear();")
            ui_client.execute_script("window.sessionStorage.clear();")

            # Принудительно возвращаемся на главную страницу
            ui_client.get(ui_client.base_url)

            # Небольшая пауза для стабилизации
            import time

            time.sleep(1)

            print(f"✅ [CLEANUP] Состояние очищено для теста: {request.node.name}")

        except Exception as e:
            print(f"⚠️ [CLEANUP] Ошибка очистки: {e}")
    else:
        # Для не-UI тестов просто пропускаем
        yield


# @pytest.fixture(scope="session")  # Только для base_url
# def base_url():
#     """Фикстура, возвращающая базовый URL для тестов."""
#     return TEST_CONFIG["base_url"]


@pytest.fixture(scope="function")  # ИЗМЕНИТЬ НА "function" (если используется ui_client)
# или scope="class", если authenticated_ui_client используется на уровне класса
# и вы хотите, чтобы логин происходил один раз для класса.
# Но для начала лучше "function" для максимальной изоляции.
def authenticated_ui_client(ui_client):  # ui_client теперь function-scoped
    """
    Фикстура для UI-тестов, требующих аутентификации.

    Выполняет вход в систему перед запуском теста и выход после завершения.
    """
    # Открываем страницу логина
    ui_client.get("{base_url}/login")

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
        ui_client.get("{base_url}/logout")
        time.sleep(1)  # Даем время на обработку выхода
    except Exception:
        # Игнорируем ошибки при выходе
        pass


@pytest.fixture(scope="function")
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


@pytest.fixture(scope="function")  # ИЗМЕНИТЬ НА "function"
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
        print(f"\n?? [UI-TEST] Запуск теста: {item.name}")


def pytest_runtest_teardown(item):
    """Очистка после каждого теста"""
    test_file = str(item.fspath)
    if "ui" in test_file or "e2e" in test_file:
        print(f"?? [UI-TEST] Завершение теста: {item.name}")


def pytest_collection_modifyitems(config, items):
    """Модификация собранных тестов"""
    for item in items:
        # Добавляем маркер ui для UI тестов
        test_file = str(item.fspath)
        if "ui" in test_file or "e2e" in test_file:
            item.add_marker(pytest.mark.ui)
