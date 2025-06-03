import time

import pytest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait


class TestPerformance:
    @pytest.fixture(scope="function")
    def driver(self):
        driver = webdriver.Chrome()
        driver.maximize_window()
        yield driver
        driver.quit()

    def test_page_load_time(self, driver):
        """Тест времени загрузки страницы"""
        # Измеряем время загрузки страницы
        start_time = time.time()
        driver.get("http://localhost:5000")

        # Ждем, пока страница полностью загрузится
        WebDriverWait(driver, 10).until(
            lambda d: d.execute_script("return document.readyState") == "complete"
        )

        # Вычисляем время загрузки
        load_time = time.time() - start_time

        # Проверяем, что время загрузки не превышает допустимое значение (например, 3 секунды)
        assert (
            load_time < 3
        ), f"Время загрузки страницы ({load_time:.2f} с) превышает допустимое значение"

    def test_command_response_time(self, driver):
        """Тест времени отклика на команду"""
        driver.get("http://localhost:5000")

        # Находим поле ввода и кнопку отправки
        input_field = driver.find_element(By.ID, "user-input")
        submit_button = driver.find_element(By.ID, "submit-command")

        # Вводим простую команду
        input_field.clear()
        input_field.send_keys("Привет")

        # Отправляем команду и замеряем время
        start_time = time.time()
        submit_button.click()

        # Ждем появления ответа
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, "message-content"))
        )

        # Вычисляем время отклика
        response_time = time.time() - start_time

        # Проверяем, что время отклика не превышает допустимое значение
        # Для простой команды 5 секунд должно быть достаточно
        assert (
            response_time < 5
        ), f"Время отклика на команду ({response_time:.2f} с) превышает допустимое значение"

    def test_history_load_time(self, driver):
        """Тест времени загрузки истории команд"""
        driver.get("http://localhost:5000")

        # Измеряем время загрузки истории
        start_time = time.time()

        # Ждем загрузки таблицы истории
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "history-table")))

        # Вычисляем время загрузки
        load_time = time.time() - start_time

        # Проверяем, что время загрузки не превышает допустимое значение
        assert (
            load_time < 2
        ), f"Время загрузки истории ({load_time:.2f} с) превышает допустимое значение"

    def test_ui_responsiveness(self, driver):
        """Тест отзывчивости пользовательского интерфейса"""
        driver.get("http://localhost:5000")

        # Находим поле ввода
        input_field = driver.find_element(By.ID, "user-input")

        # Измеряем время отклика при вводе текста
        start_time = time.time()

        # Вводим длинный текст
        input_field.clear()
        long_text = "Это тест производительности пользовательского интерфейса. " * 10
        input_field.send_keys(long_text)

        # Вычисляем время отклика
        response_time = time.time() - start_time

        # Проверяем, что время отклика не превышает допустимое значение
        assert (
            response_time < 1
        ), f"Время отклика интерфейса ({response_time:.2f} с) превышает допустимое значение"

    def test_modal_open_close_performance(self, driver):
        """Тест производительности открытия и закрытия модальных окон"""
        driver.get("http://localhost:5000")

        # Проверяем, есть ли записи в истории
        history_rows = driver.find_elements(By.CSS_SELECTOR, "#history-table tbody tr")

        if len(history_rows) > 0:
            # Измеряем время открытия модального окна
            details_btn = history_rows[0].find_element(By.CLASS_NAME, "view-details")

            start_time = time.time()
            details_btn.click()

            # Ждем появления модального окна
            WebDriverWait(driver, 5).until(
                EC.visibility_of_element_located((By.ID, "command-details-modal"))
            )

            # Вычисляем время открытия
            open_time = time.time() - start_time

            # Проверяем, что время открытия не превышает допустимое значение
            assert (
                open_time < 0.5
            ), f"Время открытия модального окна ({open_time:.2f} с) превышает допустимое значение"

            # Измеряем время закрытия модального окна
            close_btn = driver.find_element(By.CSS_SELECTOR, "#command-details-modal .close-modal")

            start_time = time.time()
            close_btn.click()

            # Ждем исчезновения модального окна
            WebDriverWait(driver, 5).until(
                EC.invisibility_of_element_located((By.ID, "command-details-modal"))
            )

            # Вычисляем время закрытия
            close_time = time.time() - start_time

            # Проверяем, что время закрытия не превышает допустимое значение
            assert (
                close_time < 0.5
            ), f"Время закрытия модального окна ({close_time:.2f} с) превышает допустимое значение"

    def test_scroll_performance(self, driver):
        """Тест производительности прокрутки"""
        driver.get("http://localhost:5000")

        # Добавляем много контента с помощью JavaScript для тестирования прокрутки
        driver.execute_script("""
            const container = document.querySelector('.container');
            if (container) {
                // Добавляем временный контент для теста прокрутки
                const tempContent = document.createElement('div');
                tempContent.id = 'temp-scroll-test';
                tempContent.style.height = '2000px';
                tempContent.style.background = 'linear-gradient(to bottom, #f0f0f0, #e0e0e0)';
                container.appendChild(tempContent);
            }
        """)

        # Измеряем время прокрутки
        start_time = time.time()

        # Прокручиваем страницу вниз
        driver.execute_script("window.scrollTo(0, 1000)")

        # Ждем завершения прокрутки
        time.sleep(0.1)

        # Вычисляем время прокрутки
        scroll_time = time.time() - start_time

        # Проверяем, что время прокрутки не превышает допустимое значение
        assert (
            scroll_time < 0.5
        ), f"Время прокрутки ({scroll_time:.2f} с) превышает допустимое значение"

        # Удаляем временный контент
        driver.execute_script("""
            const tempContent = document.getElementById('temp-scroll-test');
            if (tempContent) {
                tempContent.remove();
            }
        """)

    def test_memory_usage(self, driver):
        """Тест использования памяти"""
        driver.get("http://localhost:5000")

        # Получаем начальное использование памяти
        initial_memory = driver.execute_script(
            "return window.performance.memory ? window.performance.memory.usedJSHeapSize : 0"
        )

        # Если браузер не поддерживает API памяти, пропускаем тест
        if initial_memory == 0:
            pytest.skip("Браузер не поддерживает API памяти")

        # Выполняем действия, которые могут потреблять память
        # Например, открываем и закрываем модальные окна, отправляем команды и т.д.

        # Находим поле ввода и кнопку отправки
        input_field = driver.find_element(By.ID, "user-input")
        submit_button = driver.find_element(By.ID, "submit-command")

        # Отправляем несколько команд
        for i in range(5):
            input_field.clear()
            input_field.send_keys(f"Тестовая команда {i}")
            submit_button.click()
            time.sleep(1)  # Ждем обработки команды

        # Получаем конечное использование памяти
        final_memory = driver.execute_script(
            "return window.performance.memory ? window.performance.memory.usedJSHeapSize : 0"
        )

        # Вычисляем прирост памяти в МБ
        memory_increase_mb = (final_memory - initial_memory) / (1024 * 1024)

        # Проверяем, что прирост памяти не превышает допустимое значение (например, 50 МБ)
        assert memory_increase_mb < 50, (
            f"Прирост использования памяти ({memory_increase_mb:.2f} МБ) превышает допустимое"
            " значение"
        )
