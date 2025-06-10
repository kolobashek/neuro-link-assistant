import time

import pytest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait


class TestResponsiveDesign:
    @pytest.fixture(scope="function")
    def driver(self):
        driver = webdriver.Chrome()
        # Начинаем с большого размера окна
        driver.set_window_size(1200, 800)
        yield driver
        driver.quit()

    def test_desktop_layout(self, driver):
        """Тест макета для настольных компьютеров"""
        driver.get("http://localhost:5001")

        # Проверяем, что контейнер имеет правильную ширину
        container = driver.find_element(By.CLASS_NAME, "container")
        container_width = container.size["width"]
        assert container_width <= 1200  # Максимальная ширина контейнера

        # Проверяем, что основные компоненты отображаются в строку или сетку
        # в зависимости от дизайна
        command_form = driver.find_element(By.CLASS_NAME, "command-form-container")
        ai_models = driver.find_element(By.CLASS_NAME, "ai-models-container")
        history = driver.find_element(By.CLASS_NAME, "command-history-container")

        # Проверяем, что компоненты видимы
        assert command_form.is_displayed()
        assert ai_models.is_displayed()
        assert history.is_displayed()

        # Проверяем расположение компонентов (зависит от конкретного дизайна)
        # Например, если используется grid-layout:
        container_display = driver.execute_script(
            "return window.getComputedStyle(arguments[0]).display", container
        )
        if container_display == "grid":
            grid_template = driver.execute_script(
                "return window.getComputedStyle(arguments[0]).gridTemplateColumns", container
            )
            # Проверяем, что используется многоколоночный макет
            assert "1fr" in grid_template and grid_template.count("fr") > 1

    def test_tablet_layout(self, driver):
        """Тест макета для планшетов"""
        # Устанавливаем размер окна как у планшета
        driver.set_window_size(768, 1024)
        driver.get("http://localhost:5001")

        # Проверяем, что контейнер адаптировался
        container = driver.find_element(By.CLASS_NAME, "container")
        container_width = container.size["width"]
        assert container_width <= 768

        # Проверяем, что компоненты адаптировались к размеру планшета
        # Например, если используется grid-layout:
        container_display = driver.execute_script(
            "return window.getComputedStyle(arguments[0]).display", container
        )
        if container_display == "grid":
            grid_template = driver.execute_script(
                "return window.getComputedStyle(arguments[0]).gridTemplateColumns", container
            )
            # На планшете может быть меньше колонок
            assert "1fr" in grid_template

        # Проверяем, что все основные компоненты видимы
        command_form = driver.find_element(By.CLASS_NAME, "command-form-container")
        ai_models = driver.find_element(By.CLASS_NAME, "ai-models-container")
        history = driver.find_element(By.CLASS_NAME, "command-history-container")

        assert command_form.is_displayed()
        assert ai_models.is_displayed()
        assert history.is_displayed()

    def test_mobile_layout(self, driver):
        """Тест макета для мобильных устройств"""
        # Устанавливаем размер окна как у мобильного устройства
        driver.set_window_size(375, 667)
        driver.get("http://localhost:5001")

        # Проверяем, что контейнер адаптировался
        container = driver.find_element(By.CLASS_NAME, "container")
        container_width = container.size["width"]
        assert container_width <= 375

        # Проверяем, что компоненты адаптировались к размеру мобильного устройства
        # Например, если используется grid-layout:
        container_display = driver.execute_script(
            "return window.getComputedStyle(arguments[0]).display", container
        )
        if container_display == "grid":
            grid_template = driver.execute_script(
                "return window.getComputedStyle(arguments[0]).gridTemplateColumns", container
            )
            # На мобильном должна быть одна колонка
            assert grid_template.strip() == "1fr"

        # Проверяем, что все основные компоненты видимы
        command_form = driver.find_element(By.CLASS_NAME, "command-form-container")
        assert command_form.is_displayed()

        # На мобильном устройстве некоторые компоненты могут быть скрыты или отображаться по-другому
        # Например, через выпадающие меню или вкладки

    def test_modal_responsive_behavior(self, driver):
        """Тест адаптивного поведения модальных окон"""
        driver.get("http://localhost:5001")

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

            # Проверяем адаптивность модального окна на разных размерах экрана
            modal = driver.find_element(By.ID, "command-details-modal")
            modal_content = modal.find_element(By.CLASS_NAME, "modal-content")

            # Проверяем размер модального окна на десктопе
            desktop_width = modal_content.size["width"]

            # Изменяем размер окна на планшет
            driver.set_window_size(768, 1024)
            time.sleep(1)

            # Проверяем размер модального окна на планшете
            tablet_width = modal_content.size["width"]

            # Изменяем размер окна на мобильный
            driver.set_window_size(375, 667)
            time.sleep(1)

            # Проверяем размер модального окна на мобильном
            mobile_width = modal_content.size["width"]

            # Проверяем, что размер модального окна адаптируется
            assert desktop_width > tablet_width > mobile_width

            # Закрываем модальное окно
            close_btn = modal.find_element(By.CLASS_NAME, "close-modal")
            close_btn.click()

    def test_font_size_responsiveness(self, driver):
        """Тест адаптивности размера шрифта"""
        # Проверяем размер шрифта на десктопе
        driver.get("http://localhost:5001")

        header = driver.find_element(By.TAG_NAME, "h1")
        desktop_font_size = driver.execute_script(
            "return window.getComputedStyle(arguments[0]).fontSize", header
        )
        desktop_font_size = float(desktop_font_size.replace("px", ""))

        # Изменяем размер окна на планшет
        driver.set_window_size(768, 1024)
        time.sleep(1)

        # Проверяем размер шрифта на планшете
        tablet_font_size = driver.execute_script(
            "return window.getComputedStyle(arguments[0]).fontSize", header
        )
        tablet_font_size = float(tablet_font_size.replace("px", ""))

        # Изменяем размер окна на мобильный
        driver.set_window_size(375, 667)
        time.sleep(1)

        # Проверяем размер шрифта на мобильном
        mobile_font_size = driver.execute_script(
            "return window.getComputedStyle(arguments[0]).fontSize", header
        )
        mobile_font_size = float(mobile_font_size.replace("px", ""))

        # Проверяем, что размер шрифта адаптируется или остается читабельным
        # Размер может уменьшаться или оставаться тем же, но не должен быть слишком маленьким
        assert mobile_font_size >= 16  # Минимальный размер для читабельности

    def test_input_field_responsiveness(self, driver):
        """Тест адаптивности полей ввода"""
        # Проверяем поле ввода на десктопе
        driver.get("http://localhost:5001")

        input_field = driver.find_element(By.ID, "user-input")
        desktop_width = input_field.size["width"]

        # Изменяем размер окна на планшет
        driver.set_window_size(768, 1024)
        time.sleep(1)

        # Проверяем поле ввода на планшете
        tablet_width = input_field.size["width"]

        # Изменяем размер окна на мобильный
        driver.set_window_size(375, 667)
        time.sleep(1)

        # Проверяем поле ввода на мобильном
        mobile_width = input_field.size["width"]

        # Проверяем, что ширина поля ввода адаптируется к размеру экрана
        assert desktop_width > tablet_width > mobile_width

        # Проверяем, что поле ввода остается достаточно широким для использования
        assert mobile_width >= 200  # Минимальная ширина для удобства использования
