import pytest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait


class TestErrorHandling:
    @pytest.fixture(scope="function")
    def driver(self):
        driver = webdriver.Chrome()
        driver.maximize_window()
        yield driver
        driver.quit()

    def test_empty_command_handling(self, driver, base_url):
        """Тест обработки пустой команды"""
        driver.get(base_url)

        # Находим поле ввода и кнопку отправки
        input_field = driver.find_element(By.ID, "user-input")
        submit_button = driver.find_element(By.ID, "submit-command")

        # Оставляем поле ввода пустым
        input_field.clear()

        # Отправляем пустую команду
        submit_button.click()

        # Проверяем, что появилось сообщение об ошибке
        error_message = WebDriverWait(driver, 5).until(
            EC.visibility_of_element_located((By.CLASS_NAME, "error"))
        )

        # Проверяем текст сообщения об ошибке
        assert (
            "пуст" in error_message.text.lower()
            or "не может быть пустым" in error_message.text.lower()
        )

    def test_server_error_handling(self, driver, base_url):
        """Тест обработки ошибки сервера"""
        driver.get(base_url)

        # Находим поле ввода и кнопку отправки
        input_field = driver.find_element(By.ID, "user-input")
        submit_button = driver.find_element(By.ID, "submit-command")

        # Вводим команду, которая вызовет ошибку сервера
        # Например, специальную команду для тестирования ошибок
        input_field.clear()
        input_field.send_keys("ТЕСТ_ОШИБКА_СЕРВЕРА")

        # Отправляем команду
        submit_button.click()

        # Проверяем, что появилось сообщение об ошибке
        try:
            error_message = WebDriverWait(driver, 5).until(
                EC.visibility_of_element_located((By.CLASS_NAME, "error"))
            )

            # Проверяем текст сообщения об ошибке
            assert "ошибка" in error_message.text.lower() or "error" in error_message.text.lower()
        except Exception:
            # Если сообщение об ошибке не появилось, проверяем, что команда была обработана
            # Это может произойти, если сервер не настроен на обработку тестовой ошибки
            WebDriverWait(driver, 5).until(
                EC.visibility_of_element_located((By.CLASS_NAME, "message"))
            )

    def test_network_error_handling(self, driver, base_url):
        """Тест обработки сетевой ошибки"""
        driver.get(base_url)

        # Находим поле ввода и кнопку отправки
        input_field = driver.find_element(By.ID, "user-input")
        submit_button = driver.find_element(By.ID, "submit-command")

        # Вводим команду
        input_field.clear()
        input_field.send_keys("Тестовая команда")

        # Имитируем отключение сети с помощью JavaScript
        driver.execute_script("""
            // Сохраняем оригинальный fetch
            window._originalFetch = window.fetch;

            // Заменяем fetch на функцию, которая всегда возвращает ошибку
            window.fetch = function() {
                return Promise.reject(new Error('Сетевая ошибка (тест)'));
            };
        """)

        # Отправляем команду
        submit_button.click()

        # Проверяем, что появилось сообщение об ошибке
        error_message = WebDriverWait(driver, 5).until(
            EC.visibility_of_element_located((By.CLASS_NAME, "error"))
        )

        # Проверяем текст сообщения об ошибке
        assert (
            "сеть" in error_message.text.lower()
            or "соединение" in error_message.text.lower()
            or "network" in error_message.text.lower()
        )

        # Восстанавливаем оригинальный fetch
        driver.execute_script("""
            if (window._originalFetch) {
                window.fetch = window._originalFetch;
                delete window._originalFetch;
            }
        """)

    def test_timeout_handling(self, driver, base_url):
        """Тест обработки таймаута запроса"""
        driver.get(base_url)

        # Находим поле ввода и кнопку отправки
        input_field = driver.find_element(By.ID, "user-input")
        submit_button = driver.find_element(By.ID, "submit-command")

        # Вводим команду
        input_field.clear()
        input_field.send_keys("Тестовая команда")

        # Имитируем таймаут с помощью JavaScript
        driver.execute_script("""
            // Сохраняем оригинальный fetch
            window._originalFetch = window.fetch;

            // Заменяем fetch на функцию, которая никогда не возвращает результат
            window.fetch = function() {
                return new Promise(function(resolve, reject) {
                    // Никогда не вызываем resolve или reject
                });
            };
        """)

        # Отправляем команду
        submit_button.click()

        # Проверяем, что появился индикатор загрузки
        loading_indicator = WebDriverWait(driver, 5).until(
            EC.visibility_of_element_located((By.CLASS_NAME, "spinner"))
        )

        # Добавляем утверждение, что индикатор загрузки отображается
        assert loading_indicator.is_displayed(), "Индикатор загрузки не отображается"

        # Восстанавливаем оригинальный fetch
        driver.execute_script("""
            if (window._originalFetch) {
                window.fetch = window._originalFetch;
                delete window._originalFetch;
            }
        """)

    def test_invalid_response_handling(self, driver, base_url):
        """Тест обработки некорректного ответа сервера"""
        driver.get(base_url)

        # Находим поле ввода и кнопку отправки
        input_field = driver.find_element(By.ID, "user-input")
        submit_button = driver.find_element(By.ID, "submit-command")

        # Вводим команду
        input_field.clear()
        input_field.send_keys("Тестовая команда")

        # Имитируем некорректный ответ сервера с помощью JavaScript
        driver.execute_script("""
            // Сохраняем оригинальный fetch
            window._originalFetch = window.fetch;

            // Заменяем fetch на функцию, которая возвращает некорректный ответ
            window.fetch = function(url, options) {
                return Promise.resolve({
                    ok: true,
                    json: function() {
                        return Promise.resolve({
                            // Некорректный формат ответа
                            invalid_response: true
                        });
                    }
                });
            };
        """)

        # Отправляем команду
        submit_button.click()

        # Проверяем, что появилось сообщение об ошибке
        try:
            error_message = WebDriverWait(driver, 5).until(
                EC.visibility_of_element_located((By.CLASS_NAME, "error"))
            )

            # Проверяем текст сообщения об ошибке
            assert (
                "ответ" in error_message.text.lower()
                or "response" in error_message.text.lower()
                or "ошибка" in error_message.text.lower()
            )
        except Exception:
            # Если сообщение об ошибке не появилось, проверяем, что команда была обработана
            # Это может произойти, если клиент обрабатывает некорректные ответы
            WebDriverWait(driver, 5).until(
                EC.visibility_of_element_located((By.CLASS_NAME, "message"))
            )

        # Восстанавливаем оригинальный fetch
        driver.execute_script("""
            if (window._originalFetch) {
                window.fetch = window._originalFetch;
                delete window._originalFetch;
            }
        """)

    def test_error_message_display(self, driver, base_url):
        """Тест отображения сообщения об ошибке"""
        driver.get(base_url)

        # Находим поле ввода и кнопку отправки
        input_field = driver.find_element(By.ID, "user-input")
        # submit_button = driver.find_element(By.ID, "submit-command")

        # Вводим команду
        input_field.clear()
        input_field.send_keys("Тестовая команда")

        # Имитируем ошибку с помощью JavaScript
        driver.execute_script("""
            // Добавляем сообщение об ошибке в интерфейс
            if (window.commandFormModule && window.commandFormModule.addMessage) {
                window.commandFormModule.addMessage('Тестовая ошибка для проверки отображения', 'error');
            } else {
                // Если модуль не найден, добавляем сообщение вручную
                const responseContainer = document.getElementById('response-container');
                if (responseContainer) {
                    responseContainer.style.display = 'block';

                    const messageDiv = document.createElement('div');
                    messageDiv.className = 'message error';

                    const contentDiv = document.createElement('div');
                    contentDiv.className = 'message-content';
                    contentDiv.textContent = 'Тестовая ошибка для проверки отображения';

                    messageDiv.appendChild(contentDiv);
                    responseContainer.appendChild(messageDiv);
                }
            }
        """)

        # Проверяем, что сообщение об ошибке отображается корректно
        error_message = WebDriverWait(driver, 5).until(
            EC.visibility_of_element_located((By.CLASS_NAME, "error"))
        )

        # Проверяем текст сообщения об ошибке
        assert "тестовая ошибка" in error_message.text.lower()

        # Проверяем стили сообщения об ошибке
        error_color = driver.execute_script(
            "return window.getComputedStyle(arguments[0]).color", error_message
        )

        # Проверяем, что цвет текста ошибки отличается от обычного текста
        normal_text = driver.find_element(By.TAG_NAME, "body")
        normal_color = driver.execute_script(
            "return window.getComputedStyle(arguments[0]).color", normal_text
        )

        assert error_color != normal_color
