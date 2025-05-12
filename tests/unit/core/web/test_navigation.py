import pytest
from unittest.mock import patch, MagicMock

class TestNavigation:
    """Тесты навигации по веб-страницам"""
    
    def setup_method(self):
        """Настройка перед каждым тестом"""
        # Создаем мок-объект для драйвера
        self.mock_driver = MagicMock()
        
        # Импортируем класс BrowserController
        from core.web.browser_controller import BrowserController
        
        # Создаем экземпляр BrowserController
        self.browser = BrowserController(browser_type="chrome", headless=True)
        
        # Устанавливаем мок-драйвер
        self.browser.driver = self.mock_driver
    
    def test_navigate_to_url(self):
        """Тест навигации по URL"""
        # Тестовый URL
        test_url = "https://example.com"
        
        # Вызываем метод navigate
        result = self.browser.navigate(test_url)
        
        # Проверяем результат
        assert result is True
        
        # Проверяем, что метод get был вызван с правильным URL
        self.mock_driver.get.assert_called_once_with(test_url)
    
    def test_navigate_with_exception(self):
        """Тест обработки исключений при навигации"""
        # Тестовый URL
        test_url = "https://example.com"
        
        # Настраиваем мок для имитации ошибки
        self.mock_driver.get.side_effect = Exception("Test error")
        
        # Вызываем метод navigate
        result = self.browser.navigate(test_url)
        
        # Проверяем результат
        assert result is False
        
        # Проверяем, что метод get был вызван с правильным URL
        self.mock_driver.get.assert_called_once_with(test_url)
    
    def test_get_current_url(self):
        """Тест получения текущего URL"""
        # Настраиваем мок для возврата URL
        self.mock_driver.current_url = "https://example.com/page"
        
        # Вызываем метод get_current_url
        url = self.browser.get_current_url()
        
        # Проверяем результат
        assert url == "https://example.com/page"
    
    def test_get_current_url_with_exception(self):
        """Тест обработки исключений при получении текущего URL"""
        # Настраиваем мок для имитации ошибки
        type(self.mock_driver).current_url = property(side_effect=Exception("Test error"))
        
        # Вызываем метод get_current_url
        url = self.browser.get_current_url()
        
        # Проверяем результат
        assert url is None
    
    def test_refresh_page(self):
        """Тест обновления страницы"""
        # Вызываем метод refresh_page
        result = self.browser.refresh_page()
        
        # Проверяем результат
        assert result is True
        
        # Проверяем, что метод refresh был вызван
        self.mock_driver.refresh.assert_called_once()
    
    def test_refresh_page_with_exception(self):
        """Тест обработки исключений при обновлении страницы"""
        # Настраиваем мок для имитации ошибки
        self.mock_driver.refresh.side_effect = Exception("Test error")
        
        # Вызываем метод refresh_page
        result = self.browser.refresh_page()
        
        # Проверяем результат
        assert result is False
        
        # Проверяем, что метод refresh был вызван
        self.mock_driver.refresh.assert_called_once()
    
    def test_go_back(self):
        """Тест перехода назад в истории браузера"""
        # Вызываем метод go_back
        result = self.browser.go_back()
        
        # Проверяем результат
        assert result is True
        
        # Проверяем, что метод back был вызван
        self.mock_driver.back.assert_called_once()
    
    def test_go_back_with_exception(self):
        """Тест обработки исключений при переходе назад"""
        # Настраиваем мок для имитации ошибки
        self.mock_driver.back.side_effect = Exception("Test error")
        
        # Вызываем метод go_back
        result = self.browser.go_back()
        
        # Проверяем результат
        assert result is False
        
        # Проверяем, что метод back был вызван
        self.mock_driver.back.assert_called_once()
    
    def test_go_forward(self):
        """Тест перехода вперед в истории браузера"""
        # Вызываем метод go_forward
        result = self.browser.go_forward()
        
        # Проверяем результат
        assert result is True
        
        # Проверяем, что метод forward был вызван
        self.mock_driver.forward.assert_called_once()
    
    def test_go_forward_with_exception(self):
        """Тест обработки исключений при переходе вперед"""
        # Настраиваем мок для имитации ошибки
        self.mock_driver.forward.side_effect = Exception("Test error")
        
        # Вызываем метод go_forward
        result = self.browser.go_forward()
        
        # Проверяем результат
        assert result is False
        
        # Проверяем, что метод forward был вызван
        self.mock_driver.forward.assert_called_once()
    
    def test_get_page_title(self):
        """Тест получения заголовка страницы"""
        # Настраиваем мок для возврата заголовка
        self.mock_driver.title = "Example Page"
        
        # Вызываем метод get_page_title
        title = self.browser.get_page_title()
        
        # Проверяем результат
        assert title == "Example Page"
    
    def test_get_page_title_with_exception(self):
        """Тест обработки исключений при получении заголовка страницы"""
        # Настраиваем мок для имитации ошибки
        type(self.mock_driver).title = property(side_effect=Exception("Test error"))
        
        # Вызываем метод get_page_title
        title = self.browser.get_page_title()
        
        # Проверяем результат
        assert title is None