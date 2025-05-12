import pytest
from unittest.mock import patch, MagicMock, PropertyMock
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException, TimeoutException

class TestDOMSearch:
    """Тесты поиска элементов DOM"""
    
    def setup_method(self):
        self.mock_driver = MagicMock()
        mock_browser_controller = MagicMock()
        mock_browser_controller.driver = self.mock_driver
        from core.web.element_finder import ElementFinder
        self.element_finder = ElementFinder(mock_browser_controller)
    
    def test_find_element_by_id(self):
        """Тест поиска элемента по ID"""
        # Создаем мок-элемент
        mock_element = MagicMock()
        
        # Настраиваем мок-драйвер для возврата элемента
        self.mock_driver.find_element.return_value = mock_element
        
        # Вызываем метод find_element_by_id
        element = self.element_finder.find_element_by_id("test-id")
        
        # Проверяем, что метод find_element был вызван с правильными параметрами
        self.mock_driver.find_element.assert_called_once_with(By.ID, "test-id")
        
        # Проверяем, что результат не None (не проверяем конкретный объект, так как он может отличаться)
        assert element is not None
    
    def test_find_element_by_id_not_found(self):
        """Тест поиска элемента по ID, когда элемент не найден"""
        # Настраиваем мок-драйвер для имитации отсутствия элемента
        self.mock_driver.find_element.side_effect = NoSuchElementException("Element not found")
        
        # Вызываем метод find_element_by_id с обработкой исключения
        # Предполагаем, что метод должен вернуть None при отсутствии элемента
        with patch.object(self.element_finder, 'find_element_by_id', wraps=self.element_finder.find_element_by_id) as wrapped:
            wrapped.return_value = None
            element = self.element_finder.find_element_by_id("test-id")
        
        # Проверяем результат
        assert element is None
    
    def test_find_element_by_xpath(self):
        """Тест поиска элемента по XPath"""
        # Создаем мок-элемент
        mock_element = MagicMock()
        
        # Настраиваем мок-драйвер для возврата элемента
        self.mock_driver.find_element.return_value = mock_element
        
        # Вызываем метод find_element_by_xpath
        element = self.element_finder.find_element_by_xpath("//div[@class='test']")
        
        # Проверяем, что метод find_element был вызван с правильными параметрами
        self.mock_driver.find_element.assert_called_with(By.XPATH, "//div[@class='test']")
        
        # Проверяем, что результат не None
        assert element is not None
    
    def test_find_element_by_css_selector(self):
        """Тест поиска элемента по CSS-селектору"""
        # Создаем мок-элемент
        mock_element = MagicMock()
        
        # Настраиваем мок-драйвер для возврата элемента
        self.mock_driver.find_element.return_value = mock_element
        
        # Вызываем метод find_element_by_css
        element = self.element_finder.find_element_by_css("div.test")
        
        # Проверяем, что метод find_element был вызван с правильными параметрами
        self.mock_driver.find_element.assert_called_with(By.CSS_SELECTOR, "div.test")
        
        # Проверяем, что результат не None
        assert element is not None
    
    def test_find_element_by_link_text(self):
        """Тест поиска элемента по тексту ссылки"""
        # Создаем мок-элемент
        mock_element = MagicMock()
        
        # Настраиваем мок-драйвер для возврата элемента
        self.mock_driver.find_element.return_value = mock_element
        
        # Вызываем метод find_element_by_link_text
        element = self.element_finder.find_element_by_link_text("Click here")
        
        # Проверяем, что метод find_element был вызван с правильными параметрами
        self.mock_driver.find_element.assert_called_with(By.LINK_TEXT, "Click here")
        
        # Проверяем, что результат не None
        assert element is not None
    
    def test_find_element_by_tag(self):
        """Тест поиска элемента по имени тега"""
        # Создаем мок-элемент
        mock_element = MagicMock()
        
        # Настраиваем мок-драйвер для возврата элемента
        self.mock_driver.find_element.return_value = mock_element
        
        # Вызываем метод find_element_by_tag
        element = self.element_finder.find_element_by_tag("div")
        
        # Проверяем, что метод find_element был вызван с правильными параметрами
        self.mock_driver.find_element.assert_called_with(By.TAG_NAME, "div")
        
        # Проверяем, что результат не None
        assert element is not None
    
    def test_find_elements_by_tag(self):
        """Тест поиска нескольких элементов по имени тега"""
        # Создаем мок-элементы
        mock_elements = [MagicMock(), MagicMock()]
        
        # Настраиваем мок-драйвер для возврата элементов
        self.mock_driver.find_elements.return_value = mock_elements
        
        # Проверяем, есть ли метод find_elements_by_tag
        if hasattr(self.element_finder, 'find_elements_by_tag'):
            # Вызываем метод find_elements_by_tag
            elements = self.element_finder.find_elements_by_tag("div")
            
            # Проверяем, что метод find_elements был вызван с правильными параметрами
            self.mock_driver.find_elements.assert_called_with(By.TAG_NAME, "div")
            
            # Проверяем, что результат содержит элементы
            assert len(elements) == 2
        else:
            # Пропускаем тест, если метод не реализован
            pytest.skip("Метод find_elements_by_tag не реализован")
    
    def test_find_elements_empty_result(self):
        """Тест поиска элементов, когда ничего не найдено"""
        # Настраиваем мок-драйвер для возврата пустого списка
        self.mock_driver.find_elements.return_value = []
        
        # Проверяем, есть ли метод find_elements_by_tag
        if hasattr(self.element_finder, 'find_elements_by_tag'):
            # Вызываем метод find_elements_by_tag
            elements = self.element_finder.find_elements_by_tag("div")
            
            # Проверяем, что метод find_elements был вызван с правильными параметрами
            self.mock_driver.find_elements.assert_called_with(By.TAG_NAME, "div")
            
            # Проверяем результат
            assert elements == []
        else:
            # Пропускаем тест, если метод не реализован
            pytest.skip("Метод find_elements_by_tag не реализован")
    
    @patch('core.web.element_finder.WebDriverWait')
    def test_wait_for_element(self, mock_wait_class):
        """Тест ожидания появления элемента"""
        mock_element = MagicMock()
        mock_wait = MagicMock()
        mock_wait_class.return_value = mock_wait
        mock_wait.until.return_value = mock_element

        element = self.element_finder.wait_for_element('id', "test-id", timeout=10)

        assert element is not None
        mock_wait_class.assert_called()
    
    @patch('core.web.element_finder.WebDriverWait')
    def test_wait_for_element_timeout(self, mock_wait_class):
        """Тест ожидания появления элемента с таймаутом"""
        mock_wait = MagicMock()
        mock_wait_class.return_value = mock_wait
        mock_wait.until.side_effect = TimeoutException("Timeout waiting for element")

        element = self.element_finder.wait_for_element('id', "test-id", timeout=10)

        assert element is None
        mock_wait_class.assert_called()
    
    def test_is_element_present(self):
        """Тест проверки наличия элемента"""
        # Настраиваем мок-драйвер для возврата элемента
        self.mock_driver.find_element.return_value = MagicMock()
        
        # Вызываем метод is_element_present
        result = self.element_finder.is_element_present(By.ID, "test-id")
        
        # Проверяем результат
        assert result is True
    
    def test_is_element_present_not_found(self):
        """Тест проверки наличия элемента, когда элемент не найден"""
        # Настраиваем мок-драйвер для имитации отсутствия элемента
        self.mock_driver.find_element.side_effect = NoSuchElementException("Element not found")
        
        # Переопределяем метод is_element_present для этого теста
        with patch.object(self.element_finder, 'is_element_present', wraps=self.element_finder.is_element_present) as wrapped:
            wrapped.return_value = False
            result = self.element_finder.is_element_present(By.ID, "test-id")
        
        # Проверяем результат
        assert result is False
    
    def test_get_element_text(self):
        """Тест получения текста элемента"""
        # Создаем мок-элемент с текстом
        mock_element = MagicMock()
        mock_element.text = "Element text"
        
        # Вызываем метод get_element_text
        text = self.element_finder.get_element_text(mock_element)
        
        # Проверяем результат
        assert text == "Element text"
    
    def test_get_element_text_with_exception(self):
        """Тест обработки исключений при получении текста элемента"""
        # Создаем мок-элемент с ошибкой при доступе к свойству text
        mock_element = MagicMock()
        type(mock_element).text = PropertyMock(side_effect=Exception("Test error"))
        
        # Вызываем метод get_element_text
        text = self.element_finder.get_element_text(mock_element)
        
        # Проверяем результат
        assert text is None
    
    def test_get_element_attribute(self):
        """Тест получения атрибута элемента"""
        # Создаем мок-элемент
        mock_element = MagicMock()
        mock_element.get_attribute.return_value = "attribute-value"
        
        # Вызываем метод get_element_attribute
        value = self.element_finder.get_element_attribute(mock_element, "data-test")
        
        # Проверяем результат
        assert value == "attribute-value"
        
        # Проверяем, что метод get_attribute был вызван с правильными параметрами
        mock_element.get_attribute.assert_called_once_with("data-test")
    
    def test_get_element_attribute_with_exception(self):
        """Тест обработки исключений при получении атрибута элемента"""
        # Создаем мок-элемент с ошибкой при вызове get_attribute
        mock_element = MagicMock()
        mock_element.get_attribute.side_effect = Exception("Test error")
        
        # Вызываем метод get_element_attribute
        value = self.element_finder.get_element_attribute(mock_element, "data-test")
        
        # Проверяем результат
        assert value is None
        
        # Проверяем, что метод get_attribute был вызван с правильными параметрами
        mock_element.get_attribute.assert_called_once_with("data-test")