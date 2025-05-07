import pytest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

class TestAnimations:
    @pytest.fixture(scope="function")
    def driver(self):
        driver = webdriver.Chrome()
        driver.maximize_window()
        yield driver
        driver.quit()
    
    def test_modal_animations(self, driver):
        """Тест анимаций модальных окон"""
        driver.get("http://localhost:5000")
        
        # Проверяем, есть ли записи в истории
        history_rows = driver.find_elements(By.CSS_SELECTOR, "#history-table tbody tr")
        
        if len(history_rows) > 0:
            # Открываем модальное окно деталей
            details_btn = history_rows[0].find_element(By.CLASS_NAME, "view-details")
            details_btn.click()
            
            # Ждем появления модального окна
            WebDriverWait(driver, 5).until(
                EC.visibility_of_element_located((By.ID, "command-details-modal"))
            )
            
            # Проверяем наличие анимации
            modal_content = driver.find_element(By.CSS_SELECTOR, "#command-details-modal .modal-content")
            animation = driver.execute_script(
                "return window.getComputedStyle(arguments[0]).animation", modal_content
            )
            
            # Проверяем, что анимация применена
            assert animation != "none" and animation != ""
            
            # Закрываем модальное окно
            close_btn = driver.find_element(By.CSS_SELECTOR, "#command-details-modal .close-modal")
            close_btn.click()
    
    def test_button_hover_effects(self, driver):
        """Тест эффектов наведения на кнопки"""
        driver.get("http://localhost:5000")
        
        # Находим кнопку отправки
        submit_button = driver.find_element(By.ID, "submit-command")
        
        # Получаем исходный цвет фона
        initial_bg_color = driver.execute_script(
            "return window.getComputedStyle(arguments[0]).backgroundColor", submit_button
        )
        
        # Наводим курсор на кнопку
        driver.execute_script("arguments[0].dispatchEvent(new MouseEvent('mouseover', {bubbles: true}))", submit_button)
        time.sleep(0.5)  # Ждем применения эффекта наведения
        
        # Получаем цвет фона при наведении
        hover_bg_color = driver.execute_script(
            "return window.getComputedStyle(arguments[0]).backgroundColor", submit_button
        )
        
        # Проверяем, что цвет изменился при наведении
        assert initial_bg_color != hover_bg_color
    
    def test_progress_bar_animation(self, driver):
        """Тест анимации индикатора прогресса"""
        driver.get("http://localhost:5000")
        
        # Находим поле ввода и кнопку отправки
        input_field = driver.find_element(By.ID, "user-input")
        submit_button = driver.find_element(By.ID, "submit-command")
        
        # Вводим простую команду
        input_field.clear()
        input_field.send_keys("Привет")
        
        # Отправляем команду
        submit_button.click()
        
        # Ждем появления индикатора прогресса
        progress_bar = WebDriverWait(driver, 5).until(
            EC.visibility_of_element_located((By.ID, "progress-bar"))
        )
        
        # Проверяем наличие анимации
        animation = driver.execute_script(
            "return window.getComputedStyle(arguments[0]).transition", progress_bar
        )
        
        # Проверяем, что анимация применена
        assert animation != "none" and animation != ""
        
        # Ждем завершения обработки команды
        WebDriverWait(driver, 10).until(
            EC.text_to_be_present_in_element((By.CLASS_NAME, "message-content"), "Привет")
        )
    
    def test_notification_animations(self, driver):
        """Тест анимаций уведомлений"""
        driver.get("http://localhost:5000")
        
        # Создаем уведомление с помощью JavaScript
        driver.execute_script("""
            // Проверяем, существует ли функция showNotification
            if (typeof showNotification === 'function') {
                showNotification('Тестовое уведомление', 'success');
            } else {
                // Создаем уведомление вручную
                const container = document.getElementById('notification-container') || 
                                  document.createElement('div');
                
                if (!container.id) {
                    container.id = 'notification-container';
                    document.body.appendChild(container);
                }
                
                const notification = document.createElement('div');
                notification.className = 'notification success';
                notification.textContent = 'Тестовое уведомление';
                container.appendChild(notification);
            }
        """)
        
        # Ждем появления уведомления
        notification = WebDriverWait(driver, 5).until(
            EC.visibility_of_element_located((By.CLASS_NAME, "notification"))
        )
        
        # Проверяем наличие анимации
        animation = driver.execute_script(
            "return window.getComputedStyle(arguments[0]).animation", notification
        )
        
        # Проверяем, что анимация применена
        assert animation != "none" and animation != ""
    
    def test_spinner_animation(self, driver):
        """Тест анимации спиннера загрузки"""
        driver.get("http://localhost:5000")
        
        # Находим поле ввода и кнопку отправки
        input_field = driver.find_element(By.ID, "user-input")
        submit_button = driver.find_element(By.ID, "submit-command")
        
        # Вводим команду, которая потребует некоторого времени на обработку
        input_field.clear()
        input_field.send_keys("Расскажи подробно о нейронных сетях")
        
        # Отправляем команду
        submit_button.click()
        
        # Ждем появления спиннера
        spinners = WebDriverWait(driver, 5).until(
            EC.presence_of_all_elements_located((By.CLASS_NAME, "spinner"))
        )
        
        if spinners:
            spinner = spinners[0]
            
            # Проверяем наличие анимации
            animation = driver.execute_script(
                "return window.getComputedStyle(arguments[0]).animation", spinner
            )
            
            # Проверяем, что анимация применена
            assert animation != "none" and animation != ""
            
            # Проверяем, что анимация содержит вращение
            assert "spin" in animation or "rotate" in animation
    
    def test_message_appearance_animation(self, driver):
        """Тест анимации появления сообщений"""
        driver.get("http://localhost:5000")
        
        # Находим поле ввода и кнопку отправки
        input_field = driver.find_element(By.ID, "user-input")
        submit_button = driver.find_element(By.ID, "submit-command")
        
        # Вводим простую команду
        input_field.clear()
        input_field.send_keys("Привет")
        
        # Отправляем команду
        submit_button.click()
        
        # Ждем появления сообщения
        message = WebDriverWait(driver, 10).until(
            EC.visibility_of_element_located((By.CLASS_NAME, "message"))
        )
        
        # Проверяем наличие анимации
        animation = driver.execute_script(
            "return window.getComputedStyle(arguments[0]).animation", message
        )
        
        # Если анимация не задана напрямую, проверяем transition
        if animation == "none" or animation == "":
            transition = driver.execute_script(
                "return window.getComputedStyle(arguments[0]).transition", message
            )
            assert transition != "none" and transition != ""
        else:
            assert animation != "none" and animation != ""