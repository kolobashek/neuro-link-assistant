import os
import sys
import tempfile
import uuid
from unittest.mock import patch

import pytest
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

# Добавляем корневой каталог в путь поиска модулей
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# Унифицированный тестовый порт
TEST_PORT = 5100

print(f"🧪 [TESTS] Используем унифицированный тестовый порт: {TEST_PORT}")

# Устанавливаем в переменные окружения для других компонентов
os.environ["TEST_PORT"] = str(TEST_PORT)
os.environ["TESTING"] = "true"

# ===== БАЗОВЫЕ ФИКСТУРЫ =====


@pytest.fixture(scope="session")
def test_port():
    """Унифицированный тестовый порт для всех тестов."""
    return TEST_PORT


@pytest.fixture(scope="session")
def base_url(test_port):
    """Базовый URL для тестов."""
    return f"http://localhost:{test_port}"


# ===== ФИКСТУРЫ БАЗЫ ДАННЫХ =====


@pytest.fixture(scope="session")
def test_db_engine():
    """Создает тестовый движок базы данных."""
    # Создаем временный файл для SQLite
    db_fd, db_path = tempfile.mkstemp(suffix=".db")
    test_db_url = f"sqlite:///{db_path}"

    print(f"🔍 [DB] Создаем тестовую БД: {test_db_url}")

    # Патчим DATABASE_URL перед импортом
    with patch.dict(os.environ, {"DATABASE_URL": test_db_url}):
        try:
            # ✅ ИСПРАВЛЕНО: Импортируем после патчинга переменной окружения
            from core.db.connection import get_engine
            from core.db.models import Base

            engine = get_engine()

            # Создаем все таблицы
            print("🔍 [DB] Создаем таблицы...")
            Base.metadata.create_all(engine)
            print("✅ [DB] Таблицы созданы")

            yield engine

        except Exception as e:
            print(f"❌ [DB] Ошибка при создании тестовой БД: {e}")
            raise
        finally:
            # Очистка
            try:
                print("🔍 [DB] Очистка тестовой БД...")
                Base.metadata.drop_all(engine)
                engine.dispose()
                os.close(db_fd)
                os.unlink(db_path)
                print("✅ [DB] Тестовая БД очищена")
            except Exception as e:
                print(f"⚠️ [DB] Ошибка при очистке: {e}")


@pytest.fixture(scope="function")
def db_session(test_db_engine):
    """Создает изолированную сессию БД для каждого теста."""
    from sqlalchemy.orm import sessionmaker

    SessionLocal = sessionmaker(bind=test_db_engine)
    session = SessionLocal()

    try:
        yield session
    finally:
        session.rollback()
        session.close()


# ===== ФИКСТУРЫ FLASK ПРИЛОЖЕНИЯ =====


@pytest.fixture(scope="session")
def test_app(test_db_engine):
    """Создает тестовое Flask приложение."""
    # Патчим DATABASE_URL для приложения
    test_db_url = str(test_db_engine.url)

    print(f"🔍 [APP] Инициализируем тестовое приложение с БД: {test_db_url}")

    with patch.dict(os.environ, {"DATABASE_URL": test_db_url}):
        try:
            from app import init_app

            app = init_app()
            app.config.update(
                {
                    "TESTING": True,
                    "DEBUG": True,
                    "SECRET_KEY": "test-secret-key",
                    "WTF_CSRF_ENABLED": False,
                }
            )

            print("✅ [APP] Тестовое приложение инициализировано")
            yield app

        except Exception as e:
            print(f"❌ [APP] Ошибка при инициализации приложения: {e}")
            raise


@pytest.fixture(scope="function")
def app_client(test_app, db_session):
    """Создает тестовый клиент Flask для API тестирования."""

    # Патчим get_db для использования тестовой сессии
    def get_test_db():
        yield db_session

    import core.db.connection

    original_get_db = core.db.connection.get_db

    # ✅ ИСПРАВЛЕНО: Более надежное патчинг
    core.db.connection.get_db = get_test_db

    try:
        with test_app.test_client() as client:
            with test_app.app_context():
                print("🔍 [CLIENT] Тестовый клиент готов")
                yield client
    finally:
        # Восстанавливаем оригинальную функцию
        core.db.connection.get_db = original_get_db
        print("✅ [CLIENT] Тестовый клиент очищен")


# ===== ФИКСТУРЫ UI ТЕСТИРОВАНИЯ =====


@pytest.fixture(scope="session")
def ui_client(base_url):
    """Создает WebDriver для UI тестирования."""
    print("🔍 Настройка Chrome WebDriver...")

    chrome_options = Options()

    # Режим отладки через переменную окружения
    debug_mode = os.environ.get("UI_DEBUG", "false").lower() == "true"

    if not debug_mode:
        chrome_options.add_argument("--headless")

    # Стабильные опции для Windows
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--window-size=1280,720")
    chrome_options.add_argument("--disable-extensions")
    chrome_options.add_argument("--remote-debugging-port=0")
    chrome_options.add_argument("--disable-web-security")
    chrome_options.add_argument("--log-level=3")

    # Windows-специфичные опции
    if os.name == "nt":
        chrome_options.add_argument("--no-first-run")
        chrome_options.add_argument("--no-default-browser-check")
        chrome_options.add_argument("--disable-default-apps")

    # Экспериментальные опции
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
    chrome_options.add_experimental_option("useAutomationExtension", False)

    try:
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=chrome_options)
        driver.set_page_load_timeout(60)
        driver.implicitly_wait(10)

        print("✅ WebDriver инициализирован")

        # Тестируем базовую функциональность
        driver.get("data:text/html,<html><body><h1>Test OK</h1></body></html>")
        print("✅ WebDriver тест пройден")

        yield driver

    except Exception as e:
        print(f"❌ Ошибка инициализации WebDriver: {e}")
        pytest.skip(f"WebDriver недоступен: {e}")
    finally:
        try:
            driver.quit()
            print("✅ WebDriver закрыт")
        except:
            pass


# ===== ФИКСТУРЫ АУТЕНТИФИКАЦИИ =====


@pytest.fixture(scope="function")
def sample_user(db_session):
    """Создает тестового пользователя."""
    import secrets

    from core.db.models import User
    from core.security.password import hash_password

    # Генерируем уникальные данные для каждого теста
    user_id = str(uuid.uuid4())[:8]
    salt = secrets.token_hex(16)
    password_hash, _ = hash_password("testpassword123", salt)

    user = User(
        username=f"testuser_{user_id}",
        email=f"test_{user_id}@example.com",
        password_hash=password_hash,
        salt=salt,
        display_name=f"Test User {user_id}",
        role="user",
        is_active=True,
    )

    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)

    return user


@pytest.fixture(scope="function")
def authenticated_client(app_client, sample_user):
    """Клиент с аутентифицированным пользователем."""
    import json

    # Выполняем вход
    login_data = {"username": sample_user.username, "password": "testpassword123"}

    response = app_client.post(
        "/api/auth/login", data=json.dumps(login_data), content_type="application/json"
    )

    assert response.status_code == 200
    result = response.get_json()
    token = result["access_token"]

    # Создаем клиент-обертку с токеном
    class AuthenticatedClient:
        def __init__(self, client, token):
            self.client = client
            self.token = token
            self.headers = {"Authorization": f"Bearer {token}"}

        def get(self, *args, **kwargs):
            kwargs.setdefault("headers", {}).update(self.headers)
            return self.client.get(*args, **kwargs)

        def post(self, *args, **kwargs):
            kwargs.setdefault("headers", {}).update(self.headers)
            return self.client.post(*args, **kwargs)

        def put(self, *args, **kwargs):
            kwargs.setdefault("headers", {}).update(self.headers)
            return self.client.put(*args, **kwargs)

        def delete(self, *args, **kwargs):
            kwargs.setdefault("headers", {}).update(self.headers)
            return self.client.delete(*args, **kwargs)

    yield AuthenticatedClient(app_client, token)


# ===== УТИЛИТЫ =====


@pytest.fixture(scope="function")
def unique_test_id():
    """Генерирует уникальный ID для каждого теста."""
    return str(uuid.uuid4())[:8]


# ===== НАСТРОЙКИ PYTEST =====


def pytest_configure(config):
    """Конфигурация pytest."""
    # Добавляем маркеры
    config.addinivalue_line("markers", "ui: marks tests as UI tests")
    config.addinivalue_line("markers", "integration: marks tests as integration tests")
    config.addinivalue_line("markers", "auth: marks tests as authentication tests")
    config.addinivalue_line("markers", "slow: marks tests as slow running")


def pytest_collection_modifyitems(config, items):
    """Автоматически помечает тесты маркерами."""
    for item in items:
        # UI тесты
        if "ui" in item.nodeid.lower():
            item.add_marker(pytest.mark.ui)

        # Интеграционные тесты
        if "integration" in item.nodeid:
            item.add_marker(pytest.mark.integration)

        # Тесты аутентификации
        if "auth" in item.nodeid:
            item.add_marker(pytest.mark.auth)


# ===== АВТОМАТИЧЕСКАЯ ОЧИСТКА =====


@pytest.fixture(scope="session", autouse=True)
def cleanup_test_environment():
    """Автоматически очищает тестовую среду."""
    print("🔍 Подготовка тестовой среды...")

    # Очистка перед тестами
    yield

    print("✅ Завершение тестовой сессии")
    # Финальная очистка


# ===== ОТЛАДОЧНЫЕ ФИКСТУРЫ =====


@pytest.fixture(autouse=True)
def test_debug_info(request):
    """Автоматически выводит отладочную информацию для тестов."""
    test_name = request.node.name
    test_file = request.fspath.basename

    print(f"\n🧪 [TEST] Запуск: {test_file}::{test_name}")

    yield

    print(f"✅ [TEST] Завершен: {test_file}::{test_name}")


# ===== ДОПОЛНИТЕЛЬНЫЕ УТИЛИТЫ =====


@pytest.fixture
def temp_file():
    """Создает временный файл для тестов."""
    import tempfile

    fd, path = tempfile.mkstemp()
    yield path

    try:
        os.close(fd)
        os.unlink(path)
    except OSError:
        pass


@pytest.fixture
def temp_dir():
    """Создает временную директорию для тестов."""
    import shutil
    import tempfile

    temp_dir = tempfile.mkdtemp()
    yield temp_dir

    try:
        shutil.rmtree(temp_dir)
    except OSError:
        pass


# ===== MOCK ФИКСТУРЫ =====


@pytest.fixture
def mock_huggingface_api():
    """Мокает API HuggingFace для тестов."""
    with patch("services.huggingface_service.requests.post") as mock_post:
        mock_post.return_value.json.return_value = {
            "generated_text": "Mock response from HuggingFace"
        }
        mock_post.return_value.status_code = 200
        yield mock_post


@pytest.fixture
def mock_openai_api():
    """Мокает API OpenAI для тестов."""
    with patch("services.ai_service.openai") as mock_openai:
        mock_openai.Completion.create.return_value = {
            "choices": [{"text": "Mock response from OpenAI"}]
        }
        yield mock_openai


# ===== ТЕСТОВЫЕ ДАННЫЕ =====


@pytest.fixture
def sample_ai_model():
    """Создает пример AI модели для тестов."""
    return {
        "id": "test-model-1",
        "name": "Test Model",
        "provider": "test",
        "is_api": True,
        "base_url": "https://api.test.com",
        "api_key_name": "TEST_API_KEY",
        "is_active": True,
        "configuration": {"max_tokens": 100, "temperature": 0.7},
    }


@pytest.fixture
def sample_task():
    """Создает пример задачи для тестов."""
    return {
        "id": "test-task-1",
        "title": "Test Task",
        "description": "Test task description",
        "status": "created",
        "priority": 1,
    }


@pytest.fixture
def sample_workflow():
    """Создает пример workflow для тестов."""
    return {
        "id": "test-workflow-1",
        "name": "Test Workflow",
        "description": "Test workflow description",
        "is_active": True,
        "steps": [
            {"name": "Step 1", "description": "First step", "order": 1, "configuration": {}},
            {"name": "Step 2", "description": "Second step", "order": 2, "configuration": {}},
        ],
    }


# ===== СПЕЦИАЛЬНЫЕ ФИКСТУРЫ ДЛЯ WINDOWS =====


@pytest.fixture
def windows_environment():
    """Проверяет, что тесты запускаются на Windows."""
    if os.name != "nt":
        pytest.skip("Тест предназначен только для Windows")

    return {"platform": "windows", "powershell_available": True, "cmd_available": True}


# ===== ПРОИЗВОДИТЕЛЬНОСТЬ =====


@pytest.fixture
def performance_monitor():
    """Монитор производительности для тестов."""
    import time

    import psutil

    start_time = time.time()
    start_memory = psutil.Process().memory_info().rss

    yield

    end_time = time.time()
    end_memory = psutil.Process().memory_info().rss

    duration = end_time - start_time
    memory_diff = end_memory - start_memory

    print(f"📊 [PERF] Время выполнения: {duration:.2f}s")
    print(f"📊 [PERF] Изменение памяти: {memory_diff / 1024 / 1024:.2f}MB")


# ===== СЕТЕВЫЕ ТЕСТЫ =====


@pytest.fixture
def mock_requests():
    """Мокает HTTP запросы для тестов."""
    with patch("requests.get") as mock_get, patch("requests.post") as mock_post:
        # Настройка стандартных ответов
        mock_get.return_value.status_code = 200
        mock_get.return_value.json.return_value = {"status": "ok"}

        mock_post.return_value.status_code = 200
        mock_post.return_value.json.return_value = {"success": True}

        yield {"get": mock_get, "post": mock_post}


# ===== ЛОГИРОВАНИЕ В ТЕСТАХ =====


@pytest.fixture
def capture_logs():
    """Захватывает логи для анализа в тестах."""
    import logging
    from io import StringIO

    log_capture = StringIO()
    handler = logging.StreamHandler(log_capture)

    # Добавляем обработчик к корневому логгеру
    root_logger = logging.getLogger()
    root_logger.addHandler(handler)

    yield log_capture

    # Убираем обработчик
    root_logger.removeHandler(handler)


# ===== ФИНАЛЬНЫЕ НАСТРОЙКИ =====


# Автоматически применяемые настройки для всех тестов
def pytest_runtest_setup(item):
    """Настройки, применяемые перед каждым тестом."""
    # Устанавливаем тестовую среду
    os.environ["TESTING"] = "true"

    # Отключаем внешние API в тестах по умолчанию
    os.environ["DISABLE_EXTERNAL_APIS"] = "true"


def pytest_runtest_teardown(item):
    """Очистка после каждого теста."""
    # Очищаем временные переменные окружения
    test_vars = [k for k in os.environ.keys() if k.startswith("TEST_")]
    for var in test_vars:
        if var not in ["TEST_PORT", "TESTING"]:  # Сохраняем основные переменные
            os.environ.pop(var, None)
