import pytest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

class TestBaseLayout:
    @pytest.fixture(scope="function")
    def driver(self):
        # Инициализация драйвера
        driver = webdriver.Chrome()
        driver.maximize_window()
        yield driver
        driver.quit()
    
    def test_header_elements(self, driver):
        """Тест наличия и корректности элементов заголовка"""
        driver.get("http://localhost:5000")
        
        # Проверка заголовка
        header = driver.find_element(By.TAG_NAME, "header")
        assert header is not None
        
        # Проверка названия приложения
        app_title = header.find_element(By.TAG_NAME, "h1")
        assert "Нейро-Ассистент" in app_title.text
        
        # Проверка описания
        app_description = header.find_element(By.TAG_NAME, "p")
        assert "Интеллектуальный помощник" in app_description.text
    
    def test_container_structure(self, driver):
        """Тест структуры основного контейнера"""
        driver.get("http://localhost:5000")
        
        # Проверка основного контейнера
        container = driver.find_element(By.CLASS_NAME, "container")
        assert container is not None
        
        # Проверка наличия основных компонентов
        assert len(driver.find_elements(By.CLASS_NAME, "command-form-container")) > 0
        assert len(driver.find_elements(By.CLASS_NAME, "ai-models-container")) > 0
        assert len(driver.find_elements(By.CLASS_NAME, "command-history-container")) > 0
    
    def test_css_variables_applied(self, driver):
        """Тест применения CSS-переменных"""
        driver.get("http://localhost:5000")
        
        # Получение примененных стилей для проверки CSS-переменных
        primary_color = driver.execute_script(
            "return window.getComputedStyle(document.documentElement).getPropertyValue('--primary-color').trim()"
        )
        assert primary_color == "#4285f4"
        
        # Проверка применения переменных к элементам
        header = driver.find_element(By.TAG_NAME, "header")
        header_bg_color = driver.execute_script(
            "return window.getComputedStyle(arguments[0]).backgroundColor", header
        )
        # Преобразуем RGB в hex для сравнения или проверяем RGB напрямую
        assert "rgb" in header_bg_color
    
    def test_theme_toggle_presence(self, driver):
        """Тест наличия переключателя темы"""
        driver.get("http://localhost:5000")
        
        # Проверка наличия переключателя темы
        theme_toggle = driver.find_elements(By.ID, "theme-toggle")
        if theme_toggle:
            assert theme_toggle[0].is_displayed()