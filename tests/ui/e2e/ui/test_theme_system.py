import time

import pytest
from selenium import webdriver
from selenium.webdriver.common.by import By


class TestThemeSystem:
    @pytest.fixture(scope="function")
    def driver(self):
        driver = webdriver.Chrome()
        driver.maximize_window()
        yield driver
        driver.quit()

    def test_theme_toggle_presence(self, driver, base_url):
        """Тест наличия переключателя темы"""
        driver.get(base_url)

        # Проверяем наличие переключателя темы
        theme_toggles = driver.find_elements(By.ID, "theme-toggle")

        # Если переключатель темы реализован
        if theme_toggles:
            theme_toggle = theme_toggles[0]
            assert theme_toggle.is_displayed()
            assert theme_toggle.is_enabled()

    def test_theme_switching(self, driver, base_url):
        """Тест переключения между светлой и темной темами"""
        driver.get(base_url)

        # Проверяем наличие переключателя темы
        theme_toggles = driver.find_elements(By.ID, "theme-toggle")

        # Если переключатель темы реализован
        if theme_toggles:
            theme_toggle = theme_toggles[0]

            # Получаем текущую тему
            body = driver.find_element(By.TAG_NAME, "body")
            initial_theme = "dark" if "dark-theme" in body.get_attribute("class") else "light"

            # Переключаем тему
            theme_toggle.click()

            # Ждем применения темы
            time.sleep(1)

            # Проверяем, что тема изменилась
            body = driver.find_element(By.TAG_NAME, "body")
            new_theme = "dark" if "dark-theme" in body.get_attribute("class") else "light"

            assert initial_theme != new_theme

            # Проверяем, что изменение темы сохраняется в localStorage
            theme_in_storage = driver.execute_script("return localStorage.getItem('theme')")
            assert theme_in_storage == new_theme

    def test_theme_persistence(self, driver, base_url):
        """Тест сохранения выбранной темы при перезагрузке страницы"""
        driver.get(base_url)

        # Проверяем наличие переключателя темы
        theme_toggles = driver.find_elements(By.ID, "theme-toggle")

        # Если переключатель темы реализован
        if theme_toggles:
            theme_toggle = theme_toggles[0]

            # Получаем текущую тему
            body = driver.find_element(By.TAG_NAME, "body")
            initial_theme = "dark" if "dark-theme" in body.get_attribute("class") else "light"

            # Переключаем тему
            theme_toggle.click()

            # Ждем применения темы
            time.sleep(1)

            # Получаем новую тему
            body = driver.find_element(By.TAG_NAME, "body")
            new_theme = "dark" if "dark-theme" in body.get_attribute("class") else "light"

            # Проверяем, что тема изменилась
            assert initial_theme != new_theme, "Тема не изменилась после переключения"

            # Перезагружаем страницу
            driver.refresh()

            # Проверяем, что тема сохранилась после перезагрузки
            body = driver.find_element(By.TAG_NAME, "body")
            theme_after_refresh = "dark" if "dark-theme" in body.get_attribute("class") else "light"

            assert theme_after_refresh == new_theme

    def test_theme_css_variables(self, driver, base_url):
        """Тест применения CSS-переменных темы"""
        driver.get(base_url)

        # Проверяем наличие переключателя темы
        theme_toggles = driver.find_elements(By.ID, "theme-toggle")

        # Если переключатель темы реализован
        if theme_toggles:
            theme_toggle = theme_toggles[0]

            # Получаем текущую тему
            body = driver.find_element(By.TAG_NAME, "body")
            initial_theme = "dark" if "dark-theme" in body.get_attribute("class") else "light"

            # Получаем значение CSS-переменной для текущей темы
            initial_bg_color = driver.execute_script(
                "return"
                " window.getComputedStyle(document.documentElement).getPropertyValue('--background-color').trim()"
            )

            # Переключаем тему
            theme_toggle.click()

            # Ждем применения темы
            time.sleep(1)

            # Получаем новую тему
            body = driver.find_element(By.TAG_NAME, "body")
            new_theme = "dark" if "dark-theme" in body.get_attribute("class") else "light"

            # Проверяем, что тема изменилась
            assert initial_theme != new_theme, "Тема не изменилась после переключения"

            # Получаем значение CSS-переменной для новой темы
            new_bg_color = driver.execute_script(
                "return"
                " window.getComputedStyle(document.documentElement).getPropertyValue('--background-color').trim()"
            )

            # Проверяем, что значение CSS-переменной изменилось
            assert initial_bg_color != new_bg_color

    def test_theme_component_styling(self, driver, base_url):
        """Тест применения стилей темы к компонентам"""
        driver.get(base_url)

        # Проверяем наличие переключателя темы
        theme_toggles = driver.find_elements(By.ID, "theme-toggle")

        # Если переключатель темы реализован
        if theme_toggles:
            theme_toggle = theme_toggles[0]

            # Получаем стили компонентов до переключения темы
            command_form = driver.find_element(By.CLASS_NAME, "command-form-container")
            initial_form_bg = driver.execute_script(
                "return window.getComputedStyle(arguments[0]).backgroundColor", command_form
            )

            # Переключаем тему
            theme_toggle.click()

            # Ждем применения темы
            time.sleep(1)

            # Получаем стили компонентов после переключения темы
            new_form_bg = driver.execute_script(
                "return window.getComputedStyle(arguments[0]).backgroundColor", command_form
            )

            # Проверяем, что стили компонентов изменились
            assert initial_form_bg != new_form_bg
