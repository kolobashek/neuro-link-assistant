import time

import pytest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait


class TestCommandHistory:
    @pytest.fixture(scope="function")
    def driver(self):
        driver = webdriver.Chrome()
        driver.maximize_window()
        yield driver
        driver.quit()

    def test_history_container_elements(self, driver):
        """Тест наличия всех элементов контейнера истории команд"""
        driver.get("http://localhost:5001")

        # Проверка контейнера истории
        history_container = driver.find_element(By.CLASS_NAME, "command-history-container")
        assert history_container is not None

        # Проверка заголовка
        history_header = history_container.find_element(By.CLASS_NAME, "section-header")
        assert "История команд" in history_header.text

        # Проверка таблицы истории
        history_table = history_container.find_element(By.ID, "history-table")
        assert history_table is not None

        # Проверка заголовков таблицы
        table_headers = history_table.find_elements(By.TAG_NAME, "th")
        assert len(table_headers) >= 3  # Должно быть минимум 3 столбца

        # Проверка наличия кнопки очистки истории
        clear_history_btn = history_container.find_element(By.ID, "clear-history")
        assert clear_history_btn is not None

    def test_history_search_functionality(self, driver):
        """Тест функциональности поиска в истории"""
        driver.get("http://localhost:5001")

        # Проверка наличия поля поиска
        history_search = driver.find_element(By.ID, "history-search")
        assert history_search is not None

        # Проверяем, есть ли записи в истории
        history_rows = driver.find_elements(By.CSS_SELECTOR, "#history-table tbody tr")

        if len(history_rows) > 0:
            # Получаем текст команды из первой строки
            first_command = history_rows[0].find_element(By.CSS_SELECTOR, "td:nth-child(2)").text
            search_term = first_command.split()[0]  # Берем первое слово команды

            # Вводим поисковый запрос
            history_search.send_keys(search_term)

            # Даем время для фильтрации
            time.sleep(1)

            # Проверяем, что отображаются только соответствующие записи
            filtered_rows = [
                row
                for row in driver.find_elements(By.CSS_SELECTOR, "#history-table tbody tr")
                if row.is_displayed()
            ]

            for row in filtered_rows:
                command_cell = row.find_element(By.CSS_SELECTOR, "td:nth-child(2)")
                assert search_term.lower() in command_cell.text.lower()

    def test_history_item_reuse(self, driver):
        """Тест повторного использования команды из истории"""
        driver.get("http://localhost:5001")

        # Проверяем, есть ли записи в истории
        history_rows = driver.find_elements(By.CSS_SELECTOR, "#history-table tbody tr")

        if len(history_rows) > 0:
            # Получаем текст команды из первой строки
            first_command = history_rows[0].find_element(By.CSS_SELECTOR, "td:nth-child(2)").text

            # Нажимаем на кнопку повторного использования
            reuse_btn = history_rows[0].find_element(By.CLASS_NAME, "reuse-command")
            reuse_btn.click()

            # Проверяем, что команда появилась в поле ввода
            user_input = driver.find_element(By.ID, "user-input")
            assert user_input.get_attribute("value") == first_command

    def test_history_item_details(self, driver):
        """Тест просмотра деталей команды из истории"""
        driver.get("http://localhost:5001")

        # Проверяем, есть ли записи в истории
        history_rows = driver.find_elements(By.CSS_SELECTOR, "#history-table tbody tr")

        if len(history_rows) > 0:
            # Нажимаем на кнопку просмотра деталей
            details_btn = history_rows[0].find_element(By.CLASS_NAME, "view-details")
            details_btn.click()

            # Ждем открытия модального окна
            WebDriverWait(driver, 5).until(
                EC.visibility_of_element_located((By.ID, "command-details-modal"))
            )

            # Проверяем содержимое модального окна
            modal = driver.find_element(By.ID, "command-details-modal")
            assert modal.is_displayed()

            # Проверяем заголовок модального окна
            modal_header = modal.find_element(By.CLASS_NAME, "modal-header").find_element(
                By.TAG_NAME, "h2"
            )
            assert "Детали команды" in modal_header.text

            # Проверяем наличие деталей команды
            command_details = modal.find_element(By.ID, "command-details")
            assert command_details.text != ""

            # Закрываем модальное окно
            close_btn = modal.find_element(By.CLASS_NAME, "close-modal")
            close_btn.click()

            # Ждем закрытия модального окна
            WebDriverWait(driver, 5).until_not(
                EC.visibility_of_element_located((By.ID, "command-details-modal"))
            )

            # Проверяем, что модальное окно закрыто
            assert not modal.is_displayed()

    def test_clear_history_functionality(self, driver):
        """Тест функциональности очистки истории"""
        driver.get("http://localhost:5001")

        # Проверяем, есть ли записи в истории
        history_rows = driver.find_elements(By.CSS_SELECTOR, "#history-table tbody tr")

        if len(history_rows) > 0:
            # Нажимаем на кнопку очистки истории
            clear_history_btn = driver.find_element(By.ID, "clear-history")
            clear_history_btn.click()

            # Ждем появления модального окна подтверждения
            WebDriverWait(driver, 5).until(
                EC.visibility_of_element_located((By.ID, "confirm-modal"))
            )

            # Проверяем содержимое модального окна
            modal = driver.find_element(By.ID, "confirm-modal")
            assert modal.is_displayed()

            # Подтверждаем очистку истории
            confirm_btn = modal.find_element(By.ID, "confirm-yes")
            confirm_btn.click()

            # Ждем закрытия модального окна
            WebDriverWait(driver, 5).until_not(
                EC.visibility_of_element_located((By.ID, "confirm-modal"))
            )

            # Ждем обновления таблицы истории
            time.sleep(1)

            # Проверяем, что история очищена
            empty_history = driver.find_elements(
                By.CSS_SELECTOR, "#history-table tbody tr.empty-history"
            )
            assert len(empty_history) > 0
