import pytest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

class TestAccessibility:
    @pytest.fixture(scope="function")
    def driver(self):
        driver = webdriver.Chrome()
        driver.maximize_window()
        yield driver
        driver.quit()
    
    def test_keyboard_navigation(self, driver):
        """Тест навигации с помощью клавиатуры"""
        driver.get("http://localhost:5000")
        
        # Находим основные интерактивные элементы
        input_field = driver.find_element(By.ID, "user-input")
        submit_button = driver.find_element(By.ID, "submit-command")
        
        # Фокусируемся на поле ввода
        input_field.click()
        
        # Проверяем, что поле ввода в фокусе
        active_element = driver.execute_script("return document.activeElement")
        assert active_element.get_attribute("id") == "user-input"
        
        # Переходим к кнопке отправки с помощью Tab
        active_element.send_keys("\t")  # Tab
        
        # Проверяем, что кнопка отправки в фокусе
        active_element = driver.execute_script("return document.activeElement")
        assert active_element.get_attribute("id") == "submit-command"
        
        # Нажимаем Enter для отправки формы
        active_element.send_keys("\n")  # Enter
        
        # Ждем появления сообщения об ошибке или ответа
        WebDriverWait(driver, 5).until(
            EC.presence_of_element_located((By.CLASS_NAME, "message"))
        )
    
    def test_aria_attributes(self, driver):
        """Тест наличия ARIA-атрибутов для доступности"""
        driver.get("http://localhost:5000")
        
        # Проверяем наличие ARIA-атрибутов у основных элементов
        
        # Проверяем форму ввода команды
        command_form = driver.find_element(By.ID, "command-form")
        assert command_form.get_attribute("role") is not None
        
        # Проверяем поле ввода
        input_field = driver.find_element(By.ID, "user-input")
        assert input_field.get_attribute("aria-label") is not None
        
        # Проверяем кнопку отправки
        submit_button = driver.find_element(By.ID, "submit-command")
        assert submit_button.get_attribute("aria-label") is not None
        
        # Проверяем таблицу истории
        history_table = driver.find_element(By.ID, "history-table")
        assert history_table.get_attribute("aria-label") is not None
    
    def test_color_contrast(self, driver):
        """Тест контрастности цветов для доступности"""
        driver.get("http://localhost:5000")
        
        # Проверяем контрастность текста и фона для основных элементов
        
        # Проверяем заголовок
        header = driver.find_element(By.TAG_NAME, "h1")
        header_color = driver.execute_script(
            "return window.getComputedStyle(arguments[0]).color", header
        )
        header_bg = driver.execute_script(
            "return window.getComputedStyle(arguments[0]).backgroundColor", header
        )
        
        # Проверяем, что цвета не совпадают (минимальная проверка контрастности)
        assert header_color != header_bg
        
        # Проверяем кнопку отправки
        submit_button = driver.find_element(By.ID, "submit-command")
        button_color = driver.execute_script(
            "return window.getComputedStyle(arguments[0]).color", submit_button
        )
        button_bg = driver.execute_script(
            "return window.getComputedStyle(arguments[0]).backgroundColor", submit_button
        )
        
        # Проверяем, что цвета не совпадают
        assert button_color != button_bg
    
    def test_focus_indicators(self, driver):
        """Тест индикаторов фокуса для доступности"""
        driver.get("http://localhost:5000")
        
        # Находим поле ввода
        input_field = driver.find_element(By.ID, "user-input")
        
        # Получаем исходные стили
        initial_outline = driver.execute_script(
            "return window.getComputedStyle(arguments[0]).outline", input_field
        )
        
        # Фокусируемся на поле ввода
        input_field.click()
        
        # Получаем стили в фокусе
        focus_outline = driver.execute_script(
            "return window.getComputedStyle(arguments[0]).outline", input_field
        )
        
        # Проверяем, что стили изменились при фокусе
        assert initial_outline != focus_outline or focus_outline != "none"
    
    def test_screen_reader_compatibility(self, driver):
        """Тест совместимости с программами чтения с экрана"""
        driver.get("http://localhost:5000")
        
        # Проверяем наличие альтернативного текста для изображений
        images = driver.find_elements(By.TAG_NAME, "img")
        for img in images:
            assert img.get_attribute("alt") is not None
        
        # Проверяем наличие подписей для полей ввода
        input_fields = driver.find_elements(By.TAG_NAME, "input")
        for field in input_fields:
            # Проверяем наличие либо label, либо aria-label, либо placeholder
            field_id = field.get_attribute("id")
            if field_id:
                # Ищем связанный label
                labels = driver.find_elements(By.CSS_SELECTOR, f"label[for='{field_id}']")
                has_label = len(labels) > 0
            else:
                has_label = False
            
            has_aria_label = field.get_attribute("aria-label") is not None
            has_placeholder = field.get_attribute("placeholder") is not None
            
            # Должен быть хотя бы один способ идентификации поля
            assert has_label or has_aria_label or has_placeholder
    
    def test_heading_structure(self, driver):
        """Тест структуры заголовков для доступности"""
        driver.get("http://localhost:5000")
        
        # Проверяем наличие заголовка h1
        h1_elements = driver.find_elements(By.TAG_NAME, "h1")
        assert len(h1_elements) == 1  # Должен быть только один h1 на странице
        
        # Проверяем, что заголовки идут в правильном порядке (без пропусков)
        headings = []
        for i in range(1, 7):  # h1 до h6
            elements = driver.find_elements(By.TAG_NAME, f"h{i}")
            headings.extend(elements)
        
        # Проверяем, что заголовки идут в правильном порядке
        heading_levels = [int(h.tag_name[1]) for h in headings]
        
        # Проверяем, что нет пропусков уровней (например, h1 -> h3 без h2)
        for i in range(len(heading_levels) - 1):
            if heading_levels[i+1] > heading_levels[i]:
                assert heading_levels[i+1] - heading_levels[i] <= 1
    
    def test_language_attribute(self, driver):
        """Тест атрибута языка для доступности"""
        driver.get("http://localhost:5000")
        
        # Проверяем наличие атрибута lang в теге html
        html = driver.find_element(By.TAG_NAME, "html")
        lang = html.get_attribute("lang")
        
        assert lang is not None and lang != ""
        # Проверяем, что язык указан правильно (ru для русского интерфейса)
        assert lang.startswith("ru")