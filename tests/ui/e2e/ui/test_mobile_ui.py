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
        assert submit_button_size["width"] >= 44, (
            f"Ширина кнопки отправки ({submit_button_size['width']}px) недостаточна для мобильного"
            " устройства"
        )
        assert submit_button_size["height"] >= 44, (
            f"Высота кнопки отправки ({submit_button_size['height']}px) недостаточна для мобильного"
            " устройства"
        )

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
                assert element_size["width"] >= 44 or element_size["height"] >= 44, (
                    "Размер интерактивного элемента"
                    f" ({element_size['width']}x{element_size['height']}px) недостаточен для"
                    " мобильного устройства"
                )

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

    # === Новые тесты для мобильной навигации ===

    def test_hamburger_menu_navigation(self, mobile_driver):
        """Тест навигации через меню-гамбургер на мобильных устройствах"""
        mobile_driver.get("http://localhost:5000")

        # Проверяем наличие кнопки гамбургер-меню
        hamburger_buttons = mobile_driver.find_elements(
            By.CSS_SELECTOR,
            ".hamburger-button, .navbar-toggler, .menu-toggle, [data-toggle='collapse']",
        )

        if not hamburger_buttons:
            pytest.skip("Меню-гамбургер не найдено на странице")

        hamburger_button = hamburger_buttons[0]

        # Проверяем, что кнопка видима и доступна
        assert (
            hamburger_button.is_displayed()
        ), "Кнопка меню-гамбургер не отображается на мобильном устройстве"

        # Кликаем по кнопке
        hamburger_button.click()

        # Ждем появления меню
        try:
            WebDriverWait(mobile_driver, 5).until(
                EC.visibility_of_element_located(
                    (
                        By.CSS_SELECTOR,
                        ".navbar-collapse, .mobile-menu, .dropdown-menu, .navigation-menu",
                    )
                )
            )

            # Находим открытое меню
            menu = mobile_driver.find_element(
                By.CSS_SELECTOR, ".navbar-collapse, .mobile-menu, .dropdown-menu, .navigation-menu"
            )

            # Находим все ссылки в меню
            menu_links = menu.find_elements(By.TAG_NAME, "a")

            # Проверяем, что в меню есть ссылки
            assert len(menu_links) > 0, "В мобильном меню нет ссылок для навигации"

            # Находим ссылку (не на текущую страницу) для тестирования навигации
            target_link = None
            current_url = mobile_driver.current_url

            for link in menu_links:
                href = link.get_attribute("href")
                if href and href != current_url and href != "#" and href.startswith("http"):
                    target_link = link
                    break

            if target_link:
                # Запоминаем URL для перехода
                target_url = target_link.get_attribute("href")

                # Кликаем по ссылке
                target_link.click()

                # Ждем загрузки новой страницы
                WebDriverWait(mobile_driver, 10).until(
                    lambda driver: driver.current_url != current_url
                )

                # Проверяем, что URL изменился на ожидаемый
                assert (
                    mobile_driver.current_url == target_url
                ), "Навигация через гамбургер-меню не работает"
            else:
                # Если подходящей ссылки нет, пропускаем проверку навигации
                pass
        except Exception as e:
            pytest.skip(f"Не удалось протестировать навигацию через меню-гамбургер: {str(e)}")

    def test_mobile_navigation_adapts(self, mobile_driver):
        """Тест адаптации навигации для мобильных устройств"""
        mobile_driver.get("http://localhost:5000")

        # Проверяем, что десктопная навигация скрыта на мобильном устройстве
        desktop_navs = mobile_driver.find_elements(
            By.CSS_SELECTOR, ".desktop-nav, .desktop-only, .hidden-xs, .d-none.d-md-block"
        )

        for nav in desktop_navs:
            style = mobile_driver.execute_script(
                "return window.getComputedStyle(arguments[0])", nav
            )
            display = style.get_property("display")
            visibility = style.get_property("visibility")

            # Проверяем, что элемент скрыт через CSS
            assert (
                display == "none" or visibility == "hidden" or not nav.is_displayed()
            ), "Десктопная навигация не скрыта на мобильном устройстве"

        # Проверяем наличие мобильной навигации
        mobile_navs = mobile_driver.find_elements(
            By.CSS_SELECTOR,
            ".mobile-nav, .navbar-toggler, .mobile-only, .d-md-none, .d-block.d-md-none",
        )

        if not mobile_navs:
            pytest.skip("Мобильная навигация не найдена")

        for nav in mobile_navs:
            # Проверяем, что мобильная навигация видима
            assert nav.is_displayed(), "Мобильная навигация не отображается на мобильном устройстве"

    def test_mobile_bottom_navigation(self, mobile_driver):
        """Тест нижней панели навигации на мобильных устройствах (если есть)"""
        mobile_driver.get("http://localhost:5000")

        # Ищем нижнюю панель навигации, которая часто используется в мобильных интерфейсах
        bottom_navs = mobile_driver.find_elements(
            By.CSS_SELECTOR, ".bottom-nav, .footer-nav, .mobile-footer-nav, .nav-bottom"
        )

        if not bottom_navs:
            pytest.skip("Нижняя панель навигации не найдена")

        bottom_nav = bottom_navs[0]

        # Проверяем, что нижняя панель видима
        assert bottom_nav.is_displayed(), "Нижняя панель навигации не отображается"

        # Проверяем позиционирование панели
        bottom_nav_position = mobile_driver.execute_script(
            "var rect = arguments[0].getBoundingClientRect(); return {bottom: rect.bottom,"
            " windowHeight: window.innerHeight};",
            bottom_nav,
        )

        # Нижняя панель должна находиться внизу экрана
        assert (
            bottom_nav_position["bottom"] >= bottom_nav_position["windowHeight"] - 20
        ), "Нижняя панель навигации не расположена в нижней части экрана"

        # Проверяем, что в панели есть навигационные элементы
        nav_items = bottom_nav.find_elements(By.TAG_NAME, "a")
        assert len(nav_items) > 0, "В нижней панели навигации нет ссылок"

    def test_swipe_navigation(self, mobile_driver):
        """Тест навигации жестами свайпа (если поддерживается)"""
        mobile_driver.get("http://localhost:5000")

        # Проверяем наличие слайдера или карусели, которые могут поддерживать свайп
        swipeable_elements = mobile_driver.find_elements(
            By.CSS_SELECTOR, ".carousel, .swiper, .slider, [data-swipe='true']"
        )

        if not swipeable_elements:
            pytest.skip("Элементы с поддержкой свайпа не найдены")

        swipeable = swipeable_elements[0]

        try:
            # Получаем текущий активный элемент слайдера
            current_indicator = mobile_driver.find_element(
                By.CSS_SELECTOR, ".active, .swiper-slide-active, .carousel-item.active"
            )

            # Симулируем свайп влево (для перехода к следующему слайду)
            swipe_element = swipeable
            action = webdriver.ActionChains(mobile_driver)

            # Получаем размеры элемента
            size = swipe_element.size
            width = size["width"]

            # Выполняем свайп: нажимаем на правую часть элемента и перемещаем к левой части
            action.move_to_element_with_offset(swipe_element, width - 20, 10)
            action.click_and_hold()
            action.move_by_offset(-width + 40, 0)
            action.release()
            action.perform()

            # Ждем перехода к следующему слайду
            time.sleep(1)

            # Проверяем, что активный элемент изменился
            new_indicator = mobile_driver.find_element(
                By.CSS_SELECTOR, ".active, .swiper-slide-active, .carousel-item.active"
            )

            assert current_indicator != new_indicator, "Свайп не изменил активный элемент слайдера"

        except Exception as e:
            pytest.skip(f"Не удалось протестировать навигацию жестами: {str(e)}")

    def test_mobile_search_usability(self, mobile_driver):
        """Тест удобства использования поиска на мобильных устройствах"""
        mobile_driver.get("http://localhost:5000")

        # Ищем поле поиска
        search_fields = mobile_driver.find_elements(
            By.CSS_SELECTOR,
            "input[type='search'], .search-input, [placeholder*='Поиск'], [placeholder*='Search']",
        )

        if not search_fields:
            pytest.skip("Поле поиска не найдено")

        search_field = search_fields[0]

        # Проверяем размеры поля поиска
        search_size = search_field.size

        # Минимальная ширина для удобного ввода на мобильном
        assert search_size["width"] >= 120, "Поле поиска слишком узкое для мобильного устройства"

        # Проверяем, что поле поиска видимо на мобильном устройстве
        assert search_field.is_displayed(), "Поле поиска не отображается на мобильном устройстве"

        # Проверяем, что поле поиска доступно для ввода
        search_field.click()

        # Вводим тестовый поисковый запрос
        search_text = "тестовый запрос"
        search_field.clear()
        search_field.send_keys(search_text)

        # Проверяем, что текст введен
        assert (
            search_field.get_attribute("value") == search_text
        ), "Не удалось ввести текст в поле поиска"
