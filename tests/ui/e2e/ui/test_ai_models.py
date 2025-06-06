import time

import pytest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait


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

        # ИСПРАВЛЕНО: правильные селекторы
        model_items_static = models_list.find_elements(By.CSS_SELECTOR, "div.ai-model-item")

        if len(model_items_static) > 0:
            # Есть статические элементы - используем их
            model_items = model_items_static
            print(f"✅ Найдены статические ai-model-item: {len(model_items)}")
        else:
            # Нет статических - ждем динамической загрузки
            print("⏳ Ожидание динамической загрузки ai-model-item...")
            wait = WebDriverWait(driver, 10)

            try:
                # Ждем появления хотя бы одного элемента
                wait.until(EC.presence_of_element_located((By.CLASS_NAME, "ai-model-item")))
                model_items = models_list.find_elements(By.CLASS_NAME, "ai-model-item")
                print(f"✅ Загружены динамические ai-model-item: {len(model_items)}")
            except Exception as e:
                # Отладочная информация при неудаче
                print(f"❌ Не удалось загрузить ai-model-item: {e}")
                print(f"🔍 HTML models_list: {models_list.get_attribute('innerHTML')[:500]}...")
                model_items = []

        assert len(model_items) > 0, f"Ожидались ai-model-item элементы, найдено {len(model_items)}"

    def test_model_item_structure(self, driver):
        """Тест структуры элемента модели"""
        driver.get("http://localhost:5000")

        # ИСПРАВЛЕНО: правильный селектор
        model_item = driver.find_element(By.CLASS_NAME, "ai-model-item")

        # ИСПРАВЛЕНО: ищем элементы внутри model-info
        model_info = model_item.find_element(By.CLASS_NAME, "model-info")

        # Проверка названия модели
        model_name = model_info.find_element(By.CLASS_NAME, "model-name")
        assert model_name.text != ""

        # Проверка статуса модели
        model_status = model_info.find_element(By.CLASS_NAME, "model-status")
        assert model_status is not None

        print(f"✅ Модель: {model_name.text}, Статус: {model_status.text}")

    def test_model_status_indicator(self, driver):
        """Тест индикатора статуса модели"""
        driver.get("http://localhost:5000")

        # ИСПРАВЛЕНО: правильный путь к статусам
        model_statuses = driver.find_elements(By.CSS_SELECTOR, ".ai-model-item .model-status")

        assert len(model_statuses) > 0, "Не найдено статусов моделей"

        for status in model_statuses:
            # Проверяем, что у родительского элемента есть класс статуса
            parent_item = status.find_element(By.XPATH, "../..")  # ai-model-item
            status_classes = parent_item.get_attribute("class")

            print(f"🔍 Статус модели: '{status.text}', классы: '{status_classes}'")

            # Проверяем соответствие текста и классов
            status_text = status.text.lower()
            if "недоступна" in status_text:
                assert "unavailable" in status_classes or "offline" in status_classes
            elif "доступна" in status_text:
                assert "available" in status_classes or "online" in status_classes

    def test_refresh_models_button(self, driver):
        """Тест кнопки обновления статуса моделей"""
        driver.get("http://localhost:5000")

        # Находим кнопку обновления
        refresh_button = driver.find_element(By.ID, "check-ai-models-btn")
        assert refresh_button is not None

        # Нажимаем на кнопку
        refresh_button.click()

        # Даем время на обработку
        time.sleep(2)

        # Проверяем, что статусы моделей есть
        model_statuses = driver.find_elements(By.CSS_SELECTOR, ".ai-model-item .model-status")
        assert len(model_statuses) > 0
        print(f"✅ Найдено статусов после обновления: {len(model_statuses)}")

    def test_model_selection(self, driver):
        """Тест выбора модели"""
        driver.get("http://localhost:5000")

        # ИСПРАВЛЕНО: ищем ai-model-item элементы
        model_items = driver.find_elements(By.CLASS_NAME, "ai-model-item")
        assert len(model_items) > 0, "Не найдено элементов моделей"

        # Находим доступную модель
        available_models = []
        for model in model_items:
            classes = model.get_attribute("class")
            if "available" in classes or "online" in classes:
                available_models.append(model)

        if available_models:
            # Выбираем первую доступную модель
            model_to_select = available_models[0]
            model_to_select.click()

            # Проверяем, что модель выбрана
            updated_classes = model_to_select.get_attribute("class")
            print(f"✅ Модель выбрана, классы: {updated_classes}")

            # Может быть класс selected или active
            assert any(cls in updated_classes for cls in ["selected", "active"])
        else:
            print("ℹ️ Нет доступных моделей для выбора")
