import pytest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

class TestCommandForm:
    @pytest.fixture(scope="function")
    def driver(self):
        driver = webdriver.Chrome()
        driver.maximize_window()
        yield driver
        driver.quit()
    
    def test_command_form_elements(self, driver):
        """Тест наличия всех элементов формы команд"""
        driver.get("http://localhost:5000")
        
        # Проверка контейнера формы
        form_container = driver.find_element(By.CLASS_NAME, "command-form-container")
        assert form_container is not None
        
        # Проверка заголовка формы
        form_header = form_container.find_element(By.CLASS_NAME, "command-form-header")
        assert "Команды" in form_header.text
        
        # Проверка контейнера чата
        chat_container = form_container.find_element(By.CLASS_NAME, "chat-container")
        assert chat_container is not None
        
        # Проверка формы ввода
        query_form = form_container.find_element(By.ID, "query-form")
        assert query_form is not None
        
        # Проверка поля ввода
        user_input = query_form.find_element(By.ID, "user-input")
        assert user_input is not None
        assert user_input.get_attribute("placeholder") is not None
        
        # Проверка кнопки отправки
        submit_btn = query_form.find_element(By.CLASS_NAME, "submit-btn")
        assert submit_btn is not None
    
    def test_command_input_and_submission(self, driver):
        """Тест ввода и отправки команды"""
        driver.get("http://localhost:5000")
        
        # Находим поле ввода и вводим команду
        user_input = driver.find_element(By.ID, "user-input")
        test_command = "помощь"
        user_input.send_keys(test_command)
        
        # Проверяем, что текст введен корректно
        assert user_input.get_attribute("value") == test_command
        
        # Отправляем форму
        query_form = driver.find_element(By.ID, "query-form")
        query_form.submit()
        
        # Ждем появления сообщения пользователя в чате
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, "user-message"))
        )
        
        # Проверяем, что сообщение пользователя отображается
        user_messages = driver.find_elements(By.CLASS_NAME, "user-message")
        assert len(user_messages) > 0
        assert test_command in user_messages[-1].text
        
        # Проверяем, что поле ввода очищено
        assert user_input.get_attribute("value") == ""
        
        # Ждем появления элементов управления командой
        WebDriverWait(driver, 10).until(
            EC.visibility_of_element_located((By.CLASS_NAME, "command-controls"))
        )
        
        # Ждем ответа ассистента
        WebDriverWait(driver, 30).until(
            EC.presence_of_element_located((By.CLASS_NAME, "assistant-message"))
        )
        
        # Проверяем, что ответ ассистента отображается
        assistant_messages = driver.find_elements(By.CLASS_NAME, "assistant-message")
        assert len(assistant_messages) > 0
    
    def test_command_autocomplete(self, driver):
        """Тест автодополнения команд"""
        driver.get("http://localhost:5000")
        
        # Находим поле ввода и вводим часть команды
        user_input = driver.find_element(By.ID, "user-input")
        user_input.send_keys("от")
        
        # Ждем появления подсказки автодополнения
        time.sleep(1)  # Даем время для появления подсказки
        
        # Проверяем, есть ли элемент подсказки
        suggestion_element = driver.find_elements(By.ID, "command-suggestion")
        
        if suggestion_element:
            # Если подсказка есть, проверяем, что она содержит ожидаемую команду
            assert "открой" in suggestion_element[0].text or "открыть" in suggestion_element[0].text
            
            # Нажимаем Tab для автодополнения
            user_input.send_keys(Keys.TAB)
            
            # Проверяем, что команда автодополнена
            assert "открой" in user_input.get_attribute("value") or "открыть" in user_input.get_attribute("value")
    
    def test_available_commands_display(self, driver):
        """Тест отображения доступных команд"""
        driver.get("http://localhost:5000")
        
        # Проверяем наличие секции доступных команд
        available_commands = driver.find_element(By.CLASS_NAME, "available-commands")
        assert available_commands is not None
        
        # Проверяем наличие заголовка секции
        commands_header = available_commands.find_element(By.TAG_NAME, "h3")
        assert "Доступные команды" in commands_header.text
        
        # Проверяем наличие фильтра команд
        command_filter = available_commands.find_element(By.ID, "command-filter")
        assert command_filter is not None
        
        # Проверяем наличие сетки команд
        commands_grid = available_commands.find_element(By.CLASS_NAME, "commands-grid")
        assert commands_grid is not None
        
        # Проверяем наличие кнопок команд
        command_buttons = commands_grid.find_elements(By.CLASS_NAME, "command-button")
        assert len(command_buttons) > 0
    
    def test_command_filter_functionality(self, driver):
        """Тест функциональности фильтра команд"""
        driver.get("http://localhost:5000")
        
        # Находим фильтр команд
        command_filter = driver.find_element(By.ID, "command-filter")
        
        # Вводим текст фильтра
        filter_text = "открой"
        command_filter.send_keys(filter_text)
        
        # Даем время для фильтрации
        time.sleep(1)
        
        # Проверяем, что отображаются только соответствующие команды
        commands_grid = driver.find_element(By.CLASS_NAME, "commands-grid")
        visible_buttons = [btn for btn in commands_grid.find_elements(By.CLASS_NAME, "command-button") 
                          if btn.is_displayed()]
        
        # Проверяем, что все видимые кнопки содержат текст фильтра
        for button in visible_buttons:
            button_text = button.text.lower()
            assert filter_text in button_text or any(alt in button_text for alt in ["открыть", "запусти"])