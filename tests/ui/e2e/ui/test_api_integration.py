import time

import pytest
import requests
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait


class TestAPIIntegration:
    @pytest.fixture(scope="function")
    def driver(self):
        driver = webdriver.Chrome()
        driver.maximize_window()
        yield driver
        driver.quit()

    def test_command_submission_api_call(self, driver):
        """Тест отправки команды через API"""
        driver.get("http://localhost:5000")

        # Находим поле ввода и кнопку отправки
        input_field = driver.find_element(By.ID, "user-input")
        submit_button = driver.find_element(By.ID, "submit-command")

        # Перехватываем сетевые запросы с помощью Selenium CDP
        driver.execute_cdp_cmd("Network.enable", {})

        # Очищаем лог запросов
        driver.execute_cdp_cmd("Network.clearBrowserCache", {})
        driver.execute_cdp_cmd("Network.clearBrowserCookies", {})

        # Вводим команду
        test_command = "Тестовая команда для API"
        input_field.clear()
        input_field.send_keys(test_command)

        # Отправляем команду
        submit_button.click()

        # Ждем завершения запроса
        time.sleep(2)

        # Получаем логи запросов
        logs = driver.execute_cdp_cmd("Network.getRequestPostData", {})

        # Проверяем, что был отправлен запрос к API
        api_call_found = False
        for log in logs:
            if "/api/command" in str(log):
                api_call_found = True
                break

        assert api_call_found, "Запрос к API не был отправлен при отправке команды"

    def test_history_api_integration(self, driver):
        """Тест интеграции истории команд с API"""
        # Сначала получаем историю напрямую через API
        try:
            api_response = requests.get("http://localhost:5000/api/history")
            api_history = api_response.json()
        except Exception as e:
            pytest.skip(f"Не удалось получить историю через API: {e}")

        # Загружаем страницу
        driver.get("http://localhost:5000")

        # Ждем загрузки таблицы истории
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "history-table")))

        # Получаем записи истории из таблицы
        history_rows = driver.find_elements(By.CSS_SELECTOR, "#history-table tbody tr")

        # Проверяем, что количество записей в таблице соответствует количеству записей в API
        assert len(history_rows) == len(
            api_history
        ), "Количество записей в таблице не соответствует количеству записей в API"

        # Если есть записи, проверяем содержимое первой записи
        if len(history_rows) > 0 and len(api_history) > 0:
            # Получаем текст команды из первой строки таблицы
            first_row_command = (
                history_rows[0].find_element(By.CSS_SELECTOR, "td:nth-child(2)").text
            )

            # Получаем текст команды из первой записи API
            first_api_command = api_history[0].get("command", "")

            # Проверяем, что команды совпадают
            assert (
                first_row_command == first_api_command
            ), "Текст команды в таблице не соответствует тексту команды в API"

    def test_ai_models_api_integration(self, driver):
        """Тест интеграции статуса нейросетей с API"""
        # Сначала получаем статус нейросетей напрямую через API
        try:
            api_response = requests.get("http://localhost:5000/api/ai_models")
            api_models = api_response.json()
        except Exception as e:
            pytest.skip(f"Не удалось получить статус нейросетей через API: {e}")

        # Загружаем страницу
        driver.get("http://localhost:5000")

        # Ждем загрузки списка нейросетей
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, "ai-models-list"))
        )

        # Получаем элементы нейросетей из списка
        model_elements = driver.find_elements(By.CSS_SELECTOR, ".ai-model-item")

        # Проверяем, что количество моделей в интерфейсе соответствует количеству моделей в API
        assert len(model_elements) == len(
            api_models
        ), "Количество моделей в интерфейсе не соответствует количеству моделей в API"

        # Если есть модели, проверяем статус первой модели
        if len(model_elements) > 0 and len(api_models) > 0:
            # Получаем имя первой модели из интерфейса
            first_model_name = model_elements[0].find_element(By.CSS_SELECTOR, ".model-name").text

            # Получаем статус первой модели из интерфейса
            first_model_status_element = model_elements[0].find_element(
                By.CSS_SELECTOR, ".model-status"
            )
            first_model_status = (
                "active"
                if "active" in first_model_status_element.get_attribute("class")
                else "inactive"
            )

            # Получаем имя и статус первой модели из API
            first_api_model = api_models[0]
            first_api_model_name = first_api_model.get("name", "")
            first_api_model_status = first_api_model.get("status", "")

            # Проверяем, что имя и статус совпадают
            assert (
                first_model_name == first_api_model_name
            ), "Имя модели в интерфейсе не соответствует имени модели в API"
            assert (
                first_model_status == first_api_model_status
            ), "Статус модели в интерфейсе не соответствует статусу модели в API"

    def test_interrupt_command_api_call(self, driver):
        """Тест прерывания команды через API"""
        driver.get("http://localhost:5000")

        # Находим поле ввода и кнопку отправки
        input_field = driver.find_element(By.ID, "user-input")
        submit_button = driver.find_element(By.ID, "submit-command")

        # Вводим длинную команду, которая займет время на обработку
        input_field.clear()
        input_field.send_keys(
            "Напиши очень длинный текст о нейронных сетях с подробным описанием всех типов"
            " архитектур"
        )

        # Перехватываем сетевые запросы с помощью Selenium CDP
        driver.execute_cdp_cmd("Network.enable", {})

        # Очищаем лог запросов
        driver.execute_cdp_cmd("Network.clearBrowserCache", {})
        driver.execute_cdp_cmd("Network.clearBrowserCookies", {})

        # Отправляем команду
        submit_button.click()

        # Ждем появления кнопки прерывания
        interrupt_button = WebDriverWait(driver, 5).until(
            EC.element_to_be_clickable((By.ID, "interrupt-command"))
        )

        # Нажимаем кнопку прерывания
        # Сначала подтверждаем диалог
        driver.execute_script("window.confirm = function() { return true; }")
        interrupt_button.click()

        # Ждем завершения запроса
        time.sleep(2)

        # Получаем логи запросов
        logs = driver.execute_cdp_cmd("Network.getRequestPostData", {})

        # Проверяем, что был отправлен запрос на прерывание
        interrupt_call_found = False
        for log in logs:
            if "/api/interrupt" in str(log):
                interrupt_call_found = True
                break

        assert (
            interrupt_call_found
        ), "Запрос на прерывание не был отправлен при нажатии кнопки прерывания"

    def test_ensure_log_files_api_call(self, driver):
        """Тест вызова API для проверки файлов журнала"""
        # Перехватываем сетевые запросы с помощью Selenium CDP
        driver.execute_cdp_cmd("Network.enable", {})

        # Очищаем лог запросов
        driver.execute_cdp_cmd("Network.clearBrowserCache", {})
        driver.execute_cdp_cmd("Network.clearBrowserCookies", {})

        # Загружаем страницу
        driver.get("http://localhost:5000")

        # Ждем завершения загрузки страницы
        WebDriverWait(driver, 10).until(
            lambda d: d.execute_script("return document.readyState") == "complete"
        )

        # Ждем завершения запроса
        time.sleep(2)

        # Получаем логи запросов
        logs = driver.execute_cdp_cmd("Network.getRequestPostData", {})

        # Проверяем, что был отправлен запрос на проверку файлов журнала
        log_files_call_found = False
        for log in logs:
            if "/api/ensure_log_files_exist" in str(log):
                log_files_call_found = True
                break

        assert (
            log_files_call_found
        ), "Запрос на проверку файлов журнала не был отправлен при загрузке страницы"
