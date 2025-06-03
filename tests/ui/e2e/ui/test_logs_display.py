import time

import pytest
from selenium import webdriver
from selenium.webdriver.common.by import By


class TestLogsDisplay:
    @pytest.fixture(scope="function")
    def driver(self):
        driver = webdriver.Chrome()
        driver.maximize_window()
        yield driver
        driver.quit()

    def test_logs_page_structure(self, driver):
        """Тест структуры страницы логов"""
        # Переходим на страницу логов
        driver.get("http://localhost:5000/logs")

        # Проверяем наличие контейнера логов
        logs_container = driver.find_element(By.CLASS_NAME, "logs-container")
        assert logs_container is not None

        # Проверяем наличие заголовка
        logs_header = logs_container.find_element(By.TAG_NAME, "h2")
        assert "Логи системы" in logs_header.text

        # Проверяем наличие вкладок для разных типов логов
        logs_tabs = driver.find_element(By.CLASS_NAME, "logs-tabs")
        assert logs_tabs is not None

        # Проверяем наличие кнопок вкладок
        tab_buttons = logs_tabs.find_elements(By.CLASS_NAME, "tab-button")
        assert (
            len(tab_buttons) >= 3
        )  # Должно быть минимум 3 вкладки (системные, история, детальные)

        # Проверяем наличие контейнера содержимого логов
        logs_content = driver.find_element(By.CLASS_NAME, "logs-content")
        assert logs_content is not None

        # Проверяем наличие элемента для отображения логов
        log_display = logs_content.find_element(By.CLASS_NAME, "log-display")
        assert log_display is not None

    def test_logs_tabs_switching(self, driver):
        """Тест переключения между вкладками логов"""
        # Переходим на страницу логов
        driver.get("http://localhost:5000/logs")

        # Находим все кнопки вкладок
        tab_buttons = driver.find_elements(By.CLASS_NAME, "tab-button")

        # Проверяем, что первая вкладка активна по умолчанию
        assert "active" in tab_buttons[0].get_attribute("class")

        # Переключаемся на вторую вкладку
        tab_buttons[1].click()

        # Проверяем, что вторая вкладка стала активной
        assert "active" in tab_buttons[1].get_attribute("class")
        assert "active" not in tab_buttons[0].get_attribute("class")

        # Проверяем, что содержимое логов изменилось
        log_display = driver.find_element(By.CLASS_NAME, "log-display")
        first_tab_content = log_display.text

        # Переключаемся на третью вкладку
        tab_buttons[2].click()

        # Проверяем, что третья вкладка стала активной
        assert "active" in tab_buttons[2].get_attribute("class")

        # Проверяем, что содержимое логов изменилось
        log_display = driver.find_element(By.CLASS_NAME, "log-display")
        third_tab_content = log_display.text

        # Содержимое разных вкладок должно отличаться
        assert first_tab_content != third_tab_content

    def test_logs_refresh_functionality(self, driver):
        """Тест функциональности обновления логов"""
        # Переходим на страницу логов
        driver.get("http://localhost:5000/logs")

        # Находим кнопку обновления логов
        refresh_button = driver.find_element(By.ID, "refresh-logs")
        assert refresh_button is not None

        # Запоминаем текущее содержимое логов
        log_display = driver.find_element(By.CLASS_NAME, "log-display")
        log_display.text

        # Нажимаем на кнопку обновления
        refresh_button.click()

        # Ждем обновления логов
        time.sleep(1)

        # Проверяем, что содержимое логов обновилось или осталось тем же
        # (в зависимости от того, были ли новые записи)
        updated_content = driver.find_element(By.CLASS_NAME, "log-display").text

        # Если в системе не было новых событий, содержимое может не измениться
        # Поэтому проверяем только, что содержимое не пустое
        assert updated_content != ""

    def test_logs_search_functionality(self, driver):
        """Тест функциональности поиска в логах"""
        # Переходим на страницу логов
        driver.get("http://localhost:5000/logs")

        # Находим поле поиска
        search_input = driver.find_element(By.ID, "logs-search")
        assert search_input is not None

        # Проверяем, что в логах есть содержимое
        log_display = driver.find_element(By.CLASS_NAME, "log-display")
        log_content = log_display.text

        if log_content:
            # Берем первое слово из логов для поиска
            search_term = log_content.split()[0]

            # Вводим поисковый запрос
            search_input.clear()
            search_input.send_keys(search_term)

            # Нажимаем кнопку поиска или Enter
            search_button = driver.find_element(By.ID, "search-logs-btn")
            search_button.click()

            # Ждем результатов поиска
            time.sleep(1)

            # Проверяем, что результаты содержат искомый термин
            filtered_content = driver.find_element(By.CLASS_NAME, "log-display").text
            assert search_term in filtered_content

    def test_logs_download_functionality(self, driver):
        """Тест функциональности скачивания логов"""
        # Переходим на страницу логов
        driver.get("http://localhost:5000/logs")

        # Находим кнопку скачивания логов
        download_button = driver.find_element(By.ID, "download-logs")
        assert download_button is not None

        # Примечание: фактическое скачивание файла сложно проверить в автоматическом тесте,
        # так как это зависит от настроек браузера и системы.
        # Мы проверяем только наличие кнопки и возможность на нее нажать.

        # Проверяем, что кнопка кликабельна
        assert download_button.is_enabled()

    def test_logs_styling(self, driver):
        """Тест стилизации логов"""
        # Переходим на страницу логов
        driver.get("http://localhost:5000/logs")

        # Проверяем стилизацию контейнера логов
        logs_container = driver.find_element(By.CLASS_NAME, "logs-container")
        container_style = driver.execute_script(
            "return window.getComputedStyle(arguments[0])", logs_container
        )

        # Проверяем наличие отступов
        assert int(container_style.getPropertyValue("padding").split("px")[0]) > 0

        # Проверяем стилизацию элемента отображения логов
        log_display = driver.find_element(By.CLASS_NAME, "log-display")
        display_style = driver.execute_script(
            "return window.getComputedStyle(arguments[0])", log_display
        )

        # Проверяем наличие фона
        assert display_style.getPropertyValue("background-color") != "rgba(0, 0, 0, 0)"

        # Проверяем наличие скролла
        assert display_style.getPropertyValue("overflow") in ["auto", "scroll", "overlay"]

        # Проверяем стилизацию вкладок
        tab_button = driver.find_element(By.CLASS_NAME, "tab-button")
        tab_style = driver.execute_script(
            "return window.getComputedStyle(arguments[0])", tab_button
        )

        # Проверяем наличие стилей для кнопок вкладок
        assert tab_style.getPropertyValue("cursor") == "pointer"
        assert tab_style.getPropertyValue("border") != "none"

    def test_logs_error_highlighting(self, driver):
        """Тест подсветки ошибок в логах"""
        # Переходим на страницу логов
        driver.get("http://localhost:5000/logs")

        # Находим все строки логов
        log_lines = driver.find_elements(By.CSS_SELECTOR, ".log-display .log-line")

        # Проверяем, есть ли строки с ошибками
        error_lines = [line for line in log_lines if "error" in line.get_attribute("class").lower()]

        if error_lines:
            # Проверяем, что строки с ошибками имеют особое форматирование
            error_line = error_lines[0]
            error_style = driver.execute_script(
                "return window.getComputedStyle(arguments[0])", error_line
            )

            # Проверяем цвет текста или фона для ошибок
            assert (
                error_style.getPropertyValue("color") != "rgb(0, 0, 0)"
                or error_style.getPropertyValue("background-color") != "rgba(0, 0, 0, 0)"
            )
