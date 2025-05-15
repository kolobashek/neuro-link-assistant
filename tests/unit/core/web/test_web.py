from unittest.mock import MagicMock, patch

import pytest


class TestBrowserController:
    """Тесты контроллера браузера"""

    @pytest.fixture
    def mock_webdriver(self):
        """Мок для Selenium WebDriver"""
        with patch("core.web.browser_controller.webdriver") as mock_webdriver:
            # Настраиваем мок драйвера
            mock_driver = MagicMock()
            mock_webdriver.Chrome.return_value = mock_driver

            yield mock_webdriver

    @pytest.fixture
    def mock_service(self):
        """Мок для Service"""
        with patch("core.web.browser_controller.ChromeService") as mock_service:
            yield mock_service

    @pytest.fixture
    def mock_chrome_driver_manager(self):
        """Мок для ChromeDriverManager"""
        with patch("core.web.browser_controller.ChromeDriverManager") as mock_manager:
            mock_manager.return_value.install.return_value = "/path/to/chromedriver"
            yield mock_manager

    def test_initialize_chrome(self, mock_webdriver, mock_service, mock_chrome_driver_manager):
        """Тест инициализации Chrome"""
        from core.web.browser_controller import BrowserController

        browser = BrowserController(browser_type="chrome", headless=True)
        result = browser.initialize()

        assert result is True
        mock_webdriver.Chrome.assert_called_once()

    def test_navigate(self, mock_webdriver, mock_service, mock_chrome_driver_manager):
        """Тест навигации по URL"""
        from core.web.browser_controller import BrowserController

        # Создаем экземпляр браузера с моком драйвера
        browser = BrowserController(browser_type="chrome", headless=True)
        mock_driver = MagicMock()
        browser.driver = mock_driver

        result = browser.navigate("https://example.com")

        assert result is True
        mock_driver.get.assert_called_once_with("https://example.com")

    def test_get_current_url(self, mock_webdriver, mock_service, mock_chrome_driver_manager):
        """Тест получения текущего URL"""
        from core.web.browser_controller import BrowserController

        # Создаем экземпляр браузера с моком драйвера
        browser = BrowserController(browser_type="chrome", headless=True)
        mock_driver = MagicMock()
        # Устанавливаем свойство через атрибут типа данных
        type(mock_driver).current_url = property(lambda self: "https://example.com")
        browser.driver = mock_driver

        url = browser.get_current_url()

        assert url == "https://example.com"

    def test_get_page_title(self, mock_webdriver, mock_service, mock_chrome_driver_manager):
        """Тест получения заголовка страницы"""
        from core.web.browser_controller import BrowserController

        # Создаем экземпляр браузера с моком драйвера
        browser = BrowserController(browser_type="chrome", headless=True)
        mock_driver = MagicMock()
        # Устанавливаем свойство через атрибут типа данных
        type(mock_driver).title = property(lambda self: "Example Domain")
        browser.driver = mock_driver

        title = browser.get_page_title()

        assert title == "Example Domain"

    def test_refresh_page(self, mock_webdriver, mock_service, mock_chrome_driver_manager):
        """Тест обновления страницы"""
        from core.web.browser_controller import BrowserController

        # Создаем экземпляр браузера с моком драйвера
        browser = BrowserController(browser_type="chrome", headless=True)
        mock_driver = MagicMock()
        browser.driver = mock_driver

        result = browser.refresh_page()

        assert result is True
        mock_driver.refresh.assert_called_once()

    def test_execute_script(self, mock_webdriver, mock_service, mock_chrome_driver_manager):
        """Тест выполнения JavaScript"""
        from core.web.browser_controller import BrowserController

        # Создаем экземпляр браузера с моком драйвера
        browser = BrowserController(browser_type="chrome", headless=True)
        mock_driver = MagicMock()
        mock_driver.execute_script.return_value = "result"
        browser.driver = mock_driver

        result = browser.execute_script("return document.title;")

        assert result == "result"
        mock_driver.execute_script.assert_called_once_with("return document.title;")

    def test_quit(self, mock_webdriver, mock_service, mock_chrome_driver_manager):
        """Тест закрытия браузера"""
        from core.web.browser_controller import BrowserController

        # Создаем экземпляр браузера с моком драйвера
        browser = BrowserController(browser_type="chrome", headless=True)
        mock_driver = MagicMock()
        browser.driver = mock_driver

        result = browser.quit()

        assert result is True
        mock_driver.quit.assert_called_once()


class TestElementFinder:
    """Тесты искателя элементов"""

    @pytest.fixture
    def mock_browser_controller(self):
        """Мок для BrowserController"""
        mock_browser = MagicMock()
        mock_browser.driver = MagicMock()
        return mock_browser

    @pytest.fixture
    def element_finder(self, mock_browser_controller):
        """Создает экземпляр ElementFinder с моком BrowserController"""
        from core.web.element_finder import ElementFinder

        return ElementFinder(mock_browser_controller)

    def test_find_element(self, element_finder, mock_browser_controller):
        """Тест поиска элемента"""
        # Настраиваем мок WebDriverWait
        with patch("core.web.element_finder.WebDriverWait") as mock_wait:
            mock_wait.return_value.until.return_value = MagicMock()

            element = element_finder.find_element("id", "test-id")

            assert element is not None
            mock_wait.assert_called_once()

    def test_find_elements(self, element_finder, mock_browser_controller):
        """Тест поиска нескольких элементов"""
        # Настраиваем мок WebDriverWait и find_elements
        with patch("core.web.element_finder.WebDriverWait") as mock_wait:
            mock_elements = [MagicMock(), MagicMock()]
            mock_browser_controller.driver.find_elements.return_value = mock_elements

            elements = element_finder.find_elements("class", "test-class")

            assert len(elements) == 2
            mock_wait.assert_called_once()
            mock_browser_controller.driver.find_elements.assert_called_once()

    def test_find_element_by_id(self, element_finder):
        """Тест поиска элемента по ID"""
        # Мокаем метод find_element
        element_finder.find_element = MagicMock(return_value=MagicMock())

        element = element_finder.find_element_by_id("test-id")

        assert element is not None
        element_finder.find_element.assert_called_once_with("id", "test-id", 10)

    def test_find_element_by_xpath(self, element_finder):
        """Тест поиска элемента по XPath"""
        # Мокаем метод find_element
        element_finder.find_element = MagicMock(return_value=MagicMock())

        element = element_finder.find_element_by_xpath('//div[@id="test"]')

        assert element is not None
        element_finder.find_element.assert_called_once_with("xpath", '//div[@id="test"]', 10)

    def test_wait_for_element(self, element_finder, mock_browser_controller):
        """Тест ожидания элемента"""
        # Настраиваем мок WebDriverWait
        with patch("core.web.element_finder.WebDriverWait") as mock_wait:
            mock_wait.return_value.until.return_value = MagicMock()

            element = element_finder.wait_for_element("id", "test-id", condition="visibility")

            assert element is not None
            mock_wait.assert_called_once()

    def test_is_element_present(self, element_finder, mock_browser_controller):
        """Тест проверки наличия элемента"""
        # Настраиваем мок find_element
        mock_browser_controller.driver.find_element.return_value = MagicMock()

        result = element_finder.is_element_present("id", "test-id")

        assert result is True
        mock_browser_controller.driver.find_element.assert_called_once()

    def test_get_element_text(self, element_finder):
        """Тест получения текста элемента"""
        # Создаем мок элемента
        mock_element = MagicMock()
        mock_element.text = "Test Text"

        text = element_finder.get_element_text(mock_element)

        assert text == "Test Text"

    def test_get_element_attribute(self, element_finder):
        """Тест получения атрибута элемента"""
        # Создаем мок элемента
        mock_element = MagicMock()
        mock_element.get_attribute.return_value = "attribute-value"

        value = element_finder.get_element_attribute(mock_element, "data-test")

        assert value == "attribute-value"
        mock_element.get_attribute.assert_called_once_with("data-test")

    def test_click_element(self, element_finder):
        """Тест клика по элементу"""
        # Создаем мок элемента
        mock_element = MagicMock()

        result = element_finder.click_element(mock_element)

        assert result is True
        mock_element.click.assert_called_once()

    def test_send_keys(self, element_finder):
        """Тест ввода текста в элемент"""
        # Создаем мок элемента
        mock_element = MagicMock()

        result = element_finder.send_keys(mock_element, "test input")

        assert result is True
        mock_element.clear.assert_called_once()
        mock_element.send_keys.assert_called_once_with("test input")
