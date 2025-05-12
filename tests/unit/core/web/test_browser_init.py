import pytest
from unittest.mock import patch, MagicMock

class TestBrowserInitialization:
    """Тесты инициализации различных браузеров"""
    
    @patch('core.web.browser_controller.webdriver.Chrome')
    @patch('core.web.browser_controller.Service')
    @patch('core.web.browser_controller.ChromeDriverManager')
    def test_initialize_chrome(self, mock_chrome_driver_manager, mock_service, mock_webdriver):
        """Тест инициализации Chrome браузера"""
        from core.web.browser_controller import BrowserController
        
        # Настраиваем моки
        mock_instance = MagicMock()
        mock_chrome_driver_manager.return_value = mock_instance
        mock_instance.install.return_value = "/path/to/chromedriver"
        mock_service.return_value = "chrome_service"
        mock_webdriver.return_value = MagicMock()
        
        # Инициализируем браузер
        browser = BrowserController(browser_type="chrome", headless=True)
        result = browser.initialize()
        
        # Проверяем результат
        assert result is True
        assert browser.driver is not None
        
        # Проверяем, что Chrome был создан
        mock_chrome_driver_manager.assert_called_once()
        mock_instance.install.assert_called_once()
        mock_service.assert_called_once()
        mock_webdriver.assert_called_once()
    
    @patch('core.web.browser_controller.webdriver.Firefox')
    @patch('core.web.browser_controller.Service')
    @patch('core.web.browser_controller.webdriver.firefox.options.Options')
    @patch('webdriver_manager.firefox.GeckoDriverManager')
    def test_initialize_firefox(self, mock_gecko_driver_manager, mock_firefox_options, mock_service, mock_webdriver):
        """Тест инициализации Firefox браузера"""
        from core.web.browser_controller import BrowserController
        
        # Настраиваем моки
        mock_instance = MagicMock()
        mock_gecko_driver_manager.return_value = mock_instance
        mock_instance.install.return_value = "/path/to/geckodriver"
        mock_service.return_value = "firefox_service"
        mock_webdriver.return_value = MagicMock()
        mock_firefox_options.return_value = MagicMock()
        
        # Инициализируем браузер
        browser = BrowserController(browser_type="firefox", headless=True)
        result = browser.initialize()
        
        # Проверяем результат
        assert result is True
        assert browser.driver is not None
        
        # Проверяем, что Firefox был создан
        mock_gecko_driver_manager.assert_called_once()
        mock_instance.install.assert_called_once()
        mock_service.assert_called_once()
        mock_webdriver.assert_called_once()
    
    @patch('core.web.browser_controller.webdriver.Edge')
    @patch('core.web.browser_controller.Service')
    @patch('core.web.browser_controller.webdriver.edge.options.Options')
    @patch('webdriver_manager.microsoft.EdgeChromiumDriverManager')
    def test_initialize_edge(self, mock_edge_driver_manager, mock_edge_options, mock_service, mock_webdriver):
        """Тест инициализации Edge браузера"""
        from core.web.browser_controller import BrowserController
        
        # Настраиваем моки
        mock_instance = MagicMock()
        mock_edge_driver_manager.return_value = mock_instance
        mock_instance.install.return_value = "/path/to/msedgedriver"
        mock_service.return_value = "edge_service"
        mock_webdriver.return_value = MagicMock()
        mock_edge_options.return_value = MagicMock()
        
        # Инициализируем браузер
        browser = BrowserController(browser_type="edge", headless=True)
        result = browser.initialize()
        
        # Проверяем результат
        assert result is True
        assert browser.driver is not None
        
        # Проверяем, что Edge был создан
        mock_edge_driver_manager.assert_called_once()
        mock_instance.install.assert_called_once()
        mock_service.assert_called_once()
        mock_webdriver.assert_called_once()
    
    def test_initialize_unsupported_browser(self):
        """Тест инициализации неподдерживаемого браузера"""
        from core.web.browser_controller import BrowserController
        
        # Инициализируем браузер с неподдерживаемым типом
        browser = BrowserController(browser_type="unsupported", headless=True)
        result = browser.initialize()
        
        # Проверяем результат
        assert result is False
        assert browser.driver is None
    
    @patch('core.web.browser_controller.webdriver.Chrome')
    @patch('core.web.browser_controller.Service')
    @patch('core.web.browser_controller.ChromeDriverManager')
    def test_initialize_with_exception(self, mock_chrome_driver_manager, mock_service, mock_webdriver):
        """Тест обработки исключений при инициализации браузера"""
        from core.web.browser_controller import BrowserController
        
        # Настраиваем моки для имитации ошибки
        mock_instance = MagicMock()
        mock_chrome_driver_manager.return_value = mock_instance
        mock_instance.install.return_value = "/path/to/chromedriver"
        mock_service.return_value = "chrome_service"
        mock_webdriver.side_effect = Exception("Test error")
        
        # Инициализируем браузер
        browser = BrowserController(browser_type="chrome", headless=True)
        result = browser.initialize()
        
        # Проверяем результат
        assert result is False
        assert browser.driver is None