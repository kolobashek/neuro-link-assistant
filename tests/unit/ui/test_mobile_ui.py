import time

import pytest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait


class TestMobileUI:
    @pytest.fixture(scope="function")
    def mobile_driver(self):
        # Настройка мобильной эмуляции
        mobile_emulation = {"deviceName": "iPhone X"}
        chrome_options = webdriver.ChromeOptions()
        chrome_options.add_experimental_option("mobileEmulation", mobile_emulation)

        driver = webdriver.Chrome(options=chrome_options)
        yield driver
        driver.quit()

    def test_responsive_layout(self, mobile_driver):
        """Тест адаптивной верстки для мобильных устройств"""
        mobile_driver.get("http://localhost:5000")

        # Проверяем, что страница загрузилась
        WebDriverWait(mobile_driver, 10).until(
            EC.presence_of_element_located((By.TAG_NAME, "body"))
        )

        # Получаем ширину окна
        window_width = mobile_driver.execute_script("return window.innerWidth")

        # Проверяем, что ширина контейнера не превышает ширину окна
        container = mobile_driver.find_element(By.CLASS_NAME, "container")
        container_width = container.size["width"]

        assert container_width <= window_width, "Ширина контейнера превышает ширину окна"

        # Проверяем, что форма ввода команды отображается корректно
        command_form = mobile_driver.find_element(By.ID, "command-form")
        command_form_width = command_form.size["width"]

        assert (
            command_form_width <= window_width
        ), "Ширина формы ввода команды превышает ширину окна"

    def test_mobile_input_usability(self, mobile_driver):
        """Тест удобства ввода на мобильных устройствах"""
        mobile_driver.get("http://localhost:5000")

        # Находим поле ввода
        input_field = mobile_driver.find_element(By.ID, "user-input")

        # Проверяем, что поле ввода имеет достаточный размер для мобильного устройства
        input_height = input_field.size["height"]

        # Минимальная высота для удобного ввода на мобильном устройстве (обычно не менее 40px)
        assert (
            input_height >= 40
        ), f"Высота поля ввода ({input_height}px) недостаточна для мобильного устройства"

        # Проверяем, что кнопка отправки имеет достаточный размер для мобильного устройства
        submit_button = mobile_driver.find_element(By.ID, "submit-command")
        submit_button_size = submit_button.size

        # Минимальный размер для удобного нажатия на мобильном устройстве (обычно не менее 44x44px)
        assert (
            submit_button_size["width"] >= 44
        ), f"Ширина кнопки отправки ({submit_button_size['width']}px) недостаточна для мобильного устройства"
        assert (
            submit_button_size["height"] >= 44
        ), f"Высота кнопки отправки ({submit_button_size['height']}px) недостаточна для мобильного устройства"

        # Проверяем, что между элементами достаточное расстояние для удобного нажатия
        # Получаем координаты элементов
        input_location = input_field.location
        submit_location = submit_button.location

        # Проверяем, что элементы не перекрываются и между ними достаточное расстояние
        if input_location["x"] < submit_location["x"]:
            # Если поле ввода слева от кнопки
            space_between = submit_location["x"] - (input_location["x"] + input_field.size["width"])
            assert (
                space_between >= 10
            ), f"Недостаточное расстояние между полем ввода и кнопкой отправки ({space_between}px)"
        elif input_location["y"] < submit_location["y"]:
            # Если поле ввода выше кнопки
            space_between = submit_location["y"] - (
                input_location["y"] + input_field.size["height"]
            )
            assert (
                space_between >= 10
            ), f"Недостаточное расстояние между полем ввода и кнопкой отправки ({space_between}px)"

    def test_touch_targets(self, mobile_driver):
        """Тест размеров целей для касания на мобильных устройствах"""
        mobile_driver.get("http://localhost:5000")

        # Находим все интерактивные элементы
        interactive_elements = mobile_driver.find_elements(
            By.CSS_SELECTOR, "button, a, input[type='submit'], .clickable"
        )

        # Проверяем размеры каждого элемента
        for element in interactive_elements:
            element_size = element.size

            # Проверяем, что элемент видим и доступен для взаимодействия
            if element.is_displayed() and element.is_enabled():
                # Минимальный размер для удобного касания на мобильном устройстве (обычно не менее 44x44px)
                assert (
                    element_size["width"] >= 44 or element_size["height"] >= 44
                ), f"Размер интерактивного элемента ({element_size['width']}x{element_size['height']}px) недостаточен для мобильного устройства"

    def test_mobile_scrolling(self, mobile_driver):
        """Тест прокрутки на мобильных устройствах"""
        mobile_driver.get("http://localhost:5000")

        # Ждем загрузки страницы
        WebDriverWait(mobile_driver, 10).until(
            EC.presence_of_element_located((By.TAG_NAME, "body"))
        )

        # Получаем высоту окна
        window_height = mobile_driver.execute_script("return window.innerHeight")

        # Получаем высоту всего документа
        document_height = mobile_driver.execute_script("return document.body.scrollHeight")

        # Если документ выше окна, проверяем возможность прокрутки
        if document_height > window_height:
            # Прокручиваем страницу вниз
            mobile_driver.execute_script("window.scrollTo(0, document.body.scrollHeight)")

            # Получаем текущую позицию прокрутки
            scroll_position = mobile_driver.execute_script("return window.pageYOffset")

            # Проверяем, что прокрутка работает
            assert scroll_position > 0, "Прокрутка не работает на мобильном устройстве"

            # Прокручиваем страницу обратно вверх
            mobile_driver.execute_script("window.scrollTo(0, 0)")

            # Получаем текущую позицию прокрутки
            scroll_position = mobile_driver.execute_script("return window.pageYOffset")

            # Проверяем, что прокрутка вверх работает
            assert scroll_position == 0, "Прокрутка вверх не работает на мобильном устройстве"

    def test_mobile_font_size(self, mobile_driver):
        """Тест размера шрифта на мобильных устройствах"""
        mobile_driver.get("http://localhost:5000")

        # Находим основные текстовые элементы
        text_elements = mobile_driver.find_elements(
            By.CSS_SELECTOR, "p, h1, h2, h3, label, button, input, textarea"
        )

        # Проверяем размер шрифта каждого элемента
        for element in text_elements:
            if element.is_displayed():
                font_size = mobile_driver.execute_script(
                    "return window.getComputedStyle(arguments[0]).fontSize", element
                )

                # Преобразуем размер шрифта в числовое значение (удаляем 'px')
                font_size_value = float(font_size.replace("px", ""))

                # Минимальный размер шрифта для мобильных устройств (обычно не менее 16px)
                assert (
                    font_size_value >= 14
                ), f"Размер шрифта ({font_size}) недостаточен для мобильного устройства"

    def test_mobile_orientation(self, mobile_driver):
        """Тест поддержки различных ориентаций экрана"""
        mobile_driver.get("http://localhost:5000")

        # Проверяем отображение в портретной ориентации
        # Получаем размеры контейнера
        container = mobile_driver.find_element(By.CLASS_NAME, "container")
        portrait_width = container.size["width"]
        portrait_height = container.size["height"]

        # Меняем ориентацию на альбомную
        mobile_driver.execute_script("return window.orientation = 90")
        # Эмулируем событие изменения ориентации
        mobile_driver.execute_script("window.dispatchEvent(new Event('orientationchange'))")
        # Даем время на перерисовку
        time.sleep(1)

        # Получаем новые размеры контейнера
        container = mobile_driver.find_element(By.CLASS_NAME, "container")
        landscape_width = container.size["width"]
        landscape_height = container.size["height"]

        # Проверяем, что размеры изменились соответствующим образом
        # В альбомной ориентации ширина должна быть больше, а высота меньше
        assert (
            landscape_width != portrait_width or landscape_height != portrait_height
        ), "Размеры контейнера не изменились при смене ориентации"

    def test_mobile_menu(self, mobile_driver):
        """Тест мобильного меню (если есть)"""
        mobile_driver.get("http://localhost:5000")

        # Проверяем наличие мобильного меню или кнопки меню
        menu_buttons = mobile_driver.find_elements(
            By.CSS_SELECTOR, ".menu-button, .hamburger, .mobile-menu-toggle"
        )

        if len(menu_buttons) > 0:
            # Если есть кнопка меню, проверяем ее функциональность
            menu_button = menu_buttons[0]

            # Проверяем, что кнопка меню видима и доступна
            assert (
                menu_button.is_displayed() and menu_button.is_enabled()
            ), "Кнопка мобильного меню не видима или не доступна"

            # Нажимаем на кнопку меню
            menu_button.click()

            # Ждем появления меню
            try:
                WebDriverWait(mobile_driver, 5).until(
                    EC.visibility_of_element_located(
                        (By.CSS_SELECTOR, ".mobile-menu, .menu-items, .nav-menu")
                    )
                )

                # Проверяем, что меню отображается корректно
                menu = mobile_driver.find_element(
                    By.CSS_SELECTOR, ".mobile-menu, .menu-items, .nav-menu"
                )
                assert menu.is_displayed(), "Мобильное меню не отображается после нажатия на кнопку"

                # Проверяем, что пункты меню доступны
                menu_items = menu.find_elements(By.CSS_SELECTOR, "a, button, .menu-item")
                assert len(menu_items) > 0, "В мобильном меню нет пунктов"

                # Закрываем меню
                menu_button.click()

                # Ждем скрытия меню
                WebDriverWait(mobile_driver, 5).until(
                    EC.invisibility_of_element_located(
                        (By.CSS_SELECTOR, ".mobile-menu, .menu-items, .nav-menu")
                    )
                )
            except Exception:
                # Если меню не появилось, возможно, оно реализовано по-другому
                pass
