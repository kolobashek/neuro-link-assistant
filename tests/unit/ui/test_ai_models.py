import pytest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

class TestAIModels:
    @pytest.fixture(scope="function")
    def driver(self):
        driver = webdriver.Chrome()
        driver.maximize_window()
        yield driver
        driver.quit()
    
    def test_ai_models_container_elements(self, driver):
        """Тест наличия всех элементов контейнера моделей ИИ"""
        driver.get("http://localhost:5000")
        
        # Проверка контейнера моделей ИИ
        models_container = driver.find_element(By.CLASS_NAME, "ai-models-container")
        assert models_container is not None
        
        # Проверка заголовка
        models_header = models_container.find_element(By.CLASS_NAME, "section-header")
        assert "Модели ИИ" in models_header.text
        
        # Проверка списка моделей
        models_list = models_container.find_element(By.CLASS_NAME, "ai-models-list")
        assert models_list is not None
        
        # Проверка наличия элементов моделей
        model_items = models_list.find_elements(By.CLASS_NAME, "model-item")
        assert len(model_items) > 0
    
    def test_model_item_structure(self, driver):
        """Тест структуры элемента модели"""
        driver.get("http://localhost:5000")
        
        # Находим первый элемент модели
        model_item = driver.find_element(By.CLASS_NAME, "model-item")
        
        # Проверка иконки модели
        model_icon = model_item.find_element(By.CLASS_NAME, "model-icon")
        assert model_icon is not None
        
        # Проверка названия модели
        model_name = model_item.find_element(By.CLASS_NAME, "model-name")
        assert model_name.text != ""
        
        # Проверка статуса модели
        model_status = model_item.find_element(By.CLASS_NAME, "model-status")
        assert model_status is not None
        
        # Проверка типа API модели
        model_api_type = model_item.find_elements(By.CLASS_NAME, "model-api-type")
        if model_api_type:
            assert model_api_type[0].text != ""
    
    def test_model_status_indicator(self, driver):
        """Тест индикатора статуса модели"""
        driver.get("http://localhost:5000")
        
        # Находим все статусы моделей
        model_statuses = driver.find_elements(By.CLASS_NAME, "model-status")
        
        for status in model_statuses:
            # Проверяем, что у статуса есть один из классов: online, offline, loading
            status_classes = status.get_attribute("class")
            assert any(cls in status_classes for cls in ["online", "offline", "loading"])
            
            # Проверяем соответствие текста статуса и класса
            if "online" in status_classes:
                assert "Доступна" in status.text
            elif "offline" in status_classes:
                assert "Недоступна" in status.text
            elif "loading" in status_classes:
                assert "Проверка" in status.text
    
    def test_refresh_models_button(self, driver):
        """Тест кнопки обновления статуса моделей"""
        driver.get("http://localhost:5000")
        
        # Находим кнопку обновления
        refresh_button = driver.find_element(By.ID, "refresh-models")
        assert refresh_button is not None
        
        # Нажимаем на кнопку
        refresh_button.click()
        
        # Проверяем, что появился индикатор загрузки
        WebDriverWait(driver, 5).until(
            EC.presence_of_element_located((By.CLASS_NAME, "loading"))
        )
        
        # Ждем завершения обновления
        WebDriverWait(driver, 10).until_not(
            EC.presence_of_element_located((By.CLASS_NAME, "loading"))
        )
        
        # Проверяем, что статусы моделей обновлены
        model_statuses = driver.find_elements(By.CLASS_NAME, "model-status")
        assert len(model_statuses) > 0
    
    def test_model_selection(self, driver):
        """Тест выбора модели"""
        driver.get("http://localhost:5000")
        
        # Находим все элементы моделей
        model_items = driver.find_elements(By.CLASS_NAME, "model-item")
        
        # Находим модель со статусом "online"
        online_models = []
        for model in model_items:
            status = model.find_element(By.CLASS_NAME, "model-status")
            if "online" in status.get_attribute("class"):
                online_models.append(model)
        
        if online_models:
            # Выбираем первую доступную модель
            online_models[0].click()
            
            # Проверяем, что модель выбрана (добавлен класс selected)
            assert "selected" in online_models[0].get_attribute("class")
            
            # Проверяем, что в локальном хранилище сохранен выбор модели
            model_id = online_models[0].get_attribute("data-model-id")
            selected_model = driver.execute_script("return localStorage.getItem('selectedModel')")
            assert model_id == selected_model