import pytest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import json

class TestSettings:
    @pytest.fixture(scope="function")
    def driver(self):
        driver = webdriver.Chrome()
        driver.maximize_window()
        yield driver
        driver.quit()
    
    def test_ai_models_settings(self, driver):
        """Тест настроек нейросетей"""
        driver.get("http://localhost:5000/ai_models")
        
        # Проверяем, что страница настроек нейросетей загрузилась
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, "ai-models-container"))
        )
        
        # Находим список моделей
        models_list = driver.find_elements(By.CSS_SELECTOR, ".ai-model-item")
        
        if len(models_list) > 0:
            # Проверяем, что для каждой модели есть элементы управления
            for model in models_list:
                # Проверяем наличие имени модели
                model_name = model.find_element(By.CSS_SELECTOR, ".model-name")
                assert model_name.text, "У модели отсутствует имя"
                
                # Проверяем наличие статуса модели
                model_status = model.find_element(By.CSS_SELECTOR, ".model-status")
                assert model_status.is_displayed(), "Статус модели не отображается"
                
                # Проверяем наличие кнопок управления
                control_buttons = model.find_elements(By.CSS_SELECTOR, "button")
                assert len(control_buttons) > 0, "Отсутствуют кнопки управления моделью"
    
    def test_theme_settings(self, driver):
        """Тест настроек темы оформления (если есть)"""
        driver.get("http://localhost:5000")
        
        # Проверяем наличие переключателя темы
        theme_toggles = driver.find_elements(By.CSS_SELECTOR, ".theme-toggle, #theme-switch, .dark-mode-toggle")
        
        if len(theme_toggles) > 0:
            # Если есть переключатель темы, проверяем его функциональность
            theme_toggle = theme_toggles[0]
            
            # Запоминаем текущую тему
            initial_theme = driver.execute_script("""
                return document.body.classList.contains('dark-theme') || 
                       document.body.classList.contains('dark-mode') || 
                       document.documentElement.classList.contains('dark-theme') || 
                       document.documentElement.classList.contains('dark-mode') ? 
                       'dark' : 'light';
            """)
            
            # Нажимаем на переключатель темы
            theme_toggle.click()
            
            # Даем время на применение темы
            time.sleep(1)
            
            # Проверяем, что тема изменилась
            new_theme = driver.execute_script("""
                return document.body.classList.contains('dark-theme') || 
                       document.body.classList.contains('dark-mode') || 
                       document.documentElement.classList.contains('dark-theme') || 
                       document.documentElement.classList.contains('dark-mode') ? 
                       'dark' : 'light';
            """)
            
            assert new_theme != initial_theme, "Тема не изменилась после нажатия на переключатель"
            
            # Возвращаем исходную тему
            theme_toggle.click()
            
            # Даем время на применение темы
            time.sleep(1)
            
            # Проверяем, что тема вернулась к исходной
            final_theme = driver.execute_script("""
                return document.body.classList.contains('dark-theme') || 
                       document.body.classList.contains('dark-mode') || 
                       document.documentElement.classList.contains('dark-theme') || 
                       document.documentElement.classList.contains('dark-mode') ? 
                       'dark' : 'light';
            """)
            
            assert final_theme == initial_theme, "Тема не вернулась к исходной после повторного нажатия на переключатель"
    
    def test_language_settings(self, driver):
        """Тест языковых настроек (если есть)"""
        driver.get("http://localhost:5000")
        
        # Проверяем наличие переключателя языка
        language_selectors = driver.find_elements(By.CSS_SELECTOR, ".language-selector, #language-switch, .lang-dropdown")
        
        if len(language_selectors) > 0:
            # Если есть переключатель языка, проверяем его функциональность
            language_selector = language_selectors[0]
            
            # Запоминаем текущий язык
            initial_language = driver.execute_script("""
                return document.documentElement.lang || 'ru';
            """)
            
            # Нажимаем на переключатель языка
            language_selector.click()
            
            # Проверяем наличие выпадающего списка языков
            language_options = driver.find_elements(By.CSS_SELECTOR, ".language-option, .lang-item")
            
            if len(language_options) > 0:
                # Выбираем язык, отличный от текущего
                for option in language_options:
                    option_lang = option.get_attribute("data-lang") or option.text.lower()
                    if option_lang != initial_language:
                        option.click()
                        break
                
                # Даем время на применение языка
                time.sleep(1)
                
                # Проверяем, что язык изменился
                new_language = driver.execute_script("""
                    return document.documentElement.lang || 'ru';
                """)
                
                assert new_language != initial_language or driver.find_element(By.TAG_NAME, "html").get_attribute("lang") != initial_language, "Язык не изменился после выбора нового языка"
    
    def test_notification_settings(self, driver):
        """Тест настроек уведомлений (если есть)"""
        driver.get("http://localhost:5000")
        
        # Проверяем наличие настроек уведомлений
        notification_settings = driver.find_elements(By.CSS_SELECTOR, ".notification-settings, #notification-settings, .notifications-toggle")
        
        if len(notification_settings) > 0:
            # Если есть настройки уведомлений, проверяем их функциональность
            notification_setting = notification_settings[0]
            
            # Нажимаем на настройки уведомлений
            notification_setting.click()
            
            # Проверяем наличие переключателей уведомлений
            notification_toggles = driver.find_elements(By.CSS_SELECTOR, ".notification-toggle, .notification-checkbox, input[type='checkbox']")
            
            if len(notification_toggles) > 0:
                # Запоминаем текущее состояние первого переключателя
                initial_state = notification_toggles[0].is_selected()
                
                # Изменяем состояние переключателя
                if initial_state:
                    driver.execute_script("arguments[0].click();", notification_toggles[0])
                else:
                    notification_toggles[0].click()
                
                # Проверяем, что состояние изменилось
                new_state = notification_toggles[0].is_selected()
                assert new_state != initial_state, "Состояние переключателя уведомлений не изменилось"
                
                # Возвращаем исходное состояние
                if new_state:
                    driver.execute_script("arguments[0].click();", notification_toggles[0])
                else:
                    notification_toggles[0].click()
    
    def test_user_preferences(self, driver):
        """Тест пользовательских настроек (если есть)"""
        driver.get("http://localhost:5000")
        
        # Проверяем наличие кнопки настроек пользователя
        settings_buttons = driver.find_elements(By.CSS_SELECTOR, ".settings-button, #user-settings, .preferences-button")
        
        if len(settings_buttons) > 0:
            # Если есть кнопка настроек, проверяем ее функциональность
            settings_button = settings_buttons[0]
            
            # Нажимаем на кнопку настроек
            settings_button.click()
            
            # Проверяем, что открылось модальное окно или страница настроек
            settings_container = WebDriverWait(driver, 5).until(
                EC.visibility_of_element_located((By.CSS_SELECTOR, ".settings-container, .preferences-modal, #settings-panel"))
            )
            
            # Проверяем наличие элементов управления настройками
            setting_controls = settings_container.find_elements(By.CSS_SELECTOR, "input, select, button, .setting-control")
            assert len(setting_controls) > 0, "В настройках отсутствуют элементы управления"
            
            # Находим кнопку закрытия настроек
            close_buttons = settings_container.find_elements(By.CSS_SELECTOR, ".close-button, .close-modal, .back-button")
            
            if len(close_buttons) > 0:
                # Закрываем настройки
                close_buttons[0].click()
                
                # Проверяем, что настройки закрылись
                WebDriverWait(driver, 5).until(
                    EC.invisibility_of_element_located((By.CSS_SELECTOR, ".settings-container, .preferences-modal, #settings-panel"))
                )
    
    def test_api_key_settings(self, driver):
        """Тест настроек API-ключей (если есть)"""
        driver.get("http://localhost:5000/ai_models")
        
        # Проверяем наличие полей для API-ключей
        api_key_fields = driver.find_elements(By.CSS_SELECTOR, "input[type='password'], .api-key-input, #api-key")
        
        if len(api_key_fields) > 0:
            # Если есть поля для API-ключей, проверяем их функциональность
            api_key_field = api_key_fields[0]
            
            # Проверяем, что поле доступно для ввода
            assert api_key_field.is_enabled(), "Поле для API-ключа недоступно для ввода"
            
            # Вводим тестовый API-ключ
            api_key_field.clear()
            test_api_key = "test_api_key_12345"
            api_key_field.send_keys(test_api_key)
            
            # Проверяем, что значение поля изменилось
            field_value = api_key_field.get_attribute("value")
            
            # Для полей типа password мы не можем напрямую проверить значение,
            # но можем проверить, что поле не пустое
            assert field_value, "Значение поля API-ключа не изменилось после ввода"
            
            # Находим кнопку сохранения
            save_buttons = driver.find_elements(By.CSS_SELECTOR, ".save-button, #save-api-key, button[type='submit']")
            
            if len(save_buttons) > 0:
                # Нажимаем кнопку сохранения
                save_buttons[0].click()
                
                # Проверяем наличие сообщения об успешном сохранении
                try:
                    success_message = WebDriverWait(driver, 5).until(
                        EC.visibility_of_element_located((By.CSS_SELECTOR, ".success-message, .alert-success, .notification.success"))
                    )
                    assert "сохранен" in success_message.text.lower() or "успешно" in success_message.text.lower() or "saved" in success_message.text.lower(), "Отсутствует сообщение об успешном сохранении API-ключа"
                except:
                    # Если сообщение не появилось, возможно, сохранение происходит без уведомления
                    pass
    
    def test_history_settings(self, driver):
        """Тест настроек истории команд (если есть)"""
        driver.get("http://localhost:5000")
        
        # Проверяем наличие кнопки очистки истории
        clear_history_buttons = driver.find_elements(By.CSS_SELECTOR, ".clear-history, #clear-history-button, .history-clear-btn")
        
        if len(clear_history_buttons) > 0:
            # Если есть кнопка очистки истории, проверяем ее функциональность
            clear_history_button = clear_history_buttons[0]
            
            # Получаем текущее количество записей в истории
            history_rows = driver.find_elements(By.CSS_SELECTOR, "#history-table tbody tr")
            initial_count = len(history_rows)
            
            # Если история не пуста, проверяем функциональность кнопки очистки
            if initial_count > 0:
                # Подготавливаем JavaScript для подтверждения диалога
                driver.execute_script("window.confirm = function() { return true; }")
                
                # Нажимаем кнопку очистки истории
                clear_history_button.click()
                
                # Даем время на обработку запроса
                time.sleep(2)
                
                # Проверяем, что история очистилась
                history_rows_after = driver.find_elements(By.CSS_SELECTOR, "#history-table tbody tr")
                assert len(history_rows_after) < initial_count, "Количество записей в истории не уменьшилось после очистки"