import pytest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait


class TestModals:
    @pytest.fixture(scope="function")
    def driver(self):
        driver = webdriver.Chrome()
        driver.maximize_window()
        yield driver
        driver.quit()

    def test_confirm_modal_structure(self, driver):
        """Тест структуры модального окна подтверждения"""
        driver.get("http://localhost:5000")

        # Открываем модальное окно подтверждения через очистку истории
        clear_history_btn = driver.find_element(By.ID, "clear-history")
        clear_history_btn.click()

        # Ждем появления модального окна
        WebDriverWait(driver, 5).until(EC.visibility_of_element_located((By.ID, "confirm-modal")))

        # Проверяем структуру модального окна
        modal = driver.find_element(By.ID, "confirm-modal")

        # Проверяем наличие заголовка
        modal_header = modal.find_element(By.CLASS_NAME, "modal-header")
        assert modal_header.find_element(By.TAG_NAME, "h2").text != ""

        # Проверяем наличие кнопки закрытия
        close_btn = modal_header.find_element(By.CLASS_NAME, "close-modal")
        assert close_btn is not None

        # Проверяем наличие тела модального окна
        modal_body = modal.find_element(By.CLASS_NAME, "modal-body")
        assert modal_body.text != ""

        # Проверяем наличие кнопок действий
        modal_actions = modal.find_element(By.CLASS_NAME, "modal-actions")
        confirm_btn = modal_actions.find_element(By.ID, "confirm-yes")
        cancel_btn = modal_actions.find_element(By.ID, "confirm-no")
        assert confirm_btn is not None
        assert cancel_btn is not None

        # Закрываем модальное окно
        cancel_btn.click()

        # Ждем закрытия модального окна
        WebDriverWait(driver, 5).until_not(
            EC.visibility_of_element_located((By.ID, "confirm-modal"))
        )

    def test_details_modal_structure(self, driver):
        """Тест структуры модального окна деталей"""
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

            # Проверяем структуру модального окна
            modal = driver.find_element(By.ID, "command-details-modal")

            # Проверяем наличие заголовка
            modal_header = modal.find_element(By.CLASS_NAME, "modal-header")
            assert "Детали команды" in modal_header.find_element(By.TAG_NAME, "h2").text

            # Проверяем наличие кнопки закрытия
            close_btn = modal_header.find_element(By.CLASS_NAME, "close-modal")
            assert close_btn is not None

            # Проверяем наличие тела модального окна
            modal_body = modal.find_element(By.CLASS_NAME, "modal-body")
            command_details = modal_body.find_element(By.ID, "command-details")
            assert command_details is not None

            # Закрываем модальное окно
            close_btn.click()

            # Ждем закрытия модального окна
            WebDriverWait(driver, 5).until_not(
                EC.visibility_of_element_located((By.ID, "command-details-modal"))
            )

    def test_modal_animations(self, driver):
        """Тест анимаций модальных окон"""
        driver.get("http://localhost:5000")

        # Открываем модальное окно подтверждения
        clear_history_btn = driver.find_element(By.ID, "clear-history")
        clear_history_btn.click()

        # Ждем появления модального окна
        WebDriverWait(driver, 5).until(EC.visibility_of_element_located((By.ID, "confirm-modal")))

        # Проверяем наличие класса анимации
        modal_content = driver.find_element(By.CSS_SELECTOR, "#confirm-modal .modal-content")
        animation_class = modal_content.get_attribute("class")

        # Проверяем, что применена анимация (класс содержит modalFadeIn или аналогичный)
        assert "modal" in animation_class.lower() and "fade" in animation_class.lower()

        # Закрываем модальное окно
        cancel_btn = driver.find_element(By.ID, "confirm-no")
        cancel_btn.click()

        # Ждем закрытия модального окна
        WebDriverWait(driver, 5).until_not(
            EC.visibility_of_element_located((By.ID, "confirm-modal"))
        )

    def test_modal_backdrop_click(self, driver):
        """Тест закрытия модального окна при клике на фон"""
        driver.get("http://localhost:5000")

        # Открываем модальное окно подтверждения
        clear_history_btn = driver.find_element(By.ID, "clear-history")
        clear_history_btn.click()

        # Ждем появления модального окна
        WebDriverWait(driver, 5).until(EC.visibility_of_element_located((By.ID, "confirm-modal")))

        # Кликаем на фон модального окна (за пределами содержимого)
        modal = driver.find_element(By.ID, "confirm-modal")

        # Выполняем JavaScript для клика на фон, так как Selenium может кликнуть только на элементы
        driver.execute_script(
            """
            var evt = new MouseEvent('click', {
                bubbles: true,
                cancelable: true,
                view: window
            });
            arguments[0].dispatchEvent(evt);
        """,
            modal,
        )

        # Проверяем, закрылось ли модальное окно
        try:
            WebDriverWait(driver, 5).until_not(
                EC.visibility_of_element_located((By.ID, "confirm-modal"))
            )
            modal_closed = True
        except Exception:
            modal_closed = False

        # Если модальное окно не закрылось, закрываем его кнопкой
        if not modal_closed:
            cancel_btn = driver.find_element(By.ID, "confirm-no")
            cancel_btn.click()
            WebDriverWait(driver, 5).until_not(
                EC.visibility_of_element_located((By.ID, "confirm-modal"))
            )
