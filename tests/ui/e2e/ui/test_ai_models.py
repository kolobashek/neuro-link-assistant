import time

import pytest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait


class TestAIModels:
    @pytest.fixture(scope="function")
    def driver(self):
        driver = webdriver.Chrome()
        driver.maximize_window()
        yield driver
        driver.quit()

    def test_ai_models_container_elements(self, driver):
        """Тест наличия всех элементов контейнера моделей ИИ"""
        driver.get("http://localhost:5001")
        wait = WebDriverWait(driver, 10)

        # Проверка контейнера моделей ИИ
        models_container = wait.until(
            EC.presence_of_element_located((By.CLASS_NAME, "ai-models-container"))
        )
        assert models_container is not None

        # Проверка заголовка
        models_header = models_container.find_element(By.CLASS_NAME, "section-header")
        assert "Модели ИИ" in models_header.text

        # Проверка списка моделей
        models_list = models_container.find_element(By.CLASS_NAME, "ai-models-list")
        assert models_list is not None

        # Попытка найти статические элементы
        model_items_static = models_list.find_elements(By.CSS_SELECTOR, "div.ai-model-item")

        if len(model_items_static) > 0:
            model_items = model_items_static
            print(f"✅ Найдены статические ai-model-item: {len(model_items)}")
        else:
            print("⏳ Ожидание динамической загрузки ai-model-item...")
            try:
                # Ждем появления хотя бы одного элемента
                wait.until(EC.presence_of_element_located((By.CLASS_NAME, "ai-model-item")))
                model_items = models_list.find_elements(By.CLASS_NAME, "ai-model-item")
                print(f"✅ Загружены динамические ai-model-item: {len(model_items)}")
            except Exception as e:
                print(f"❌ Не удалось загрузить ai-model-item: {e}")
                inner_html_attr = models_list.get_attribute("innerHTML")
                inner_html = inner_html_attr if inner_html_attr is not None else ""
                print(
                    "🔍 HTML models_list:"
                    f" {inner_html[:500] if inner_html else 'Атрибут innerHTML отсутствует'}..."
                )
                model_items = []

        assert len(model_items) > 0, f"Ожидались ai-model-item элементы, найдено {len(model_items)}"

    def test_model_item_structure(self, driver):
        """Тест структуры элемента модели"""
        driver.get("http://localhost:5001")
        wait = WebDriverWait(driver, 10)

        # Ожидаем появления хотя бы одного элемента модели
        model_item = wait.until(EC.presence_of_element_located((By.CLASS_NAME, "ai-model-item")))
        assert model_item is not None

        model_info = model_item.find_element(By.CLASS_NAME, "model-info")
        assert model_info is not None

        model_name = model_info.find_element(By.CLASS_NAME, "model-name")
        assert model_name.text != ""

        model_status = model_info.find_element(By.CLASS_NAME, "model-status")
        assert model_status is not None
        print(f"✅ Модель: {model_name.text}, Статус: {model_status.text}")

    def test_model_status_indicator(self, driver):
        """Тест индикатора статуса модели"""
        driver.get("http://localhost:5001")
        wait = WebDriverWait(driver, 10)

        try:
            # Ожидаем, что хотя бы один элемент статуса будет видимым/присутствующим
            # Используем presence_of_all_elements_located, чтобы получить список
            model_statuses = wait.until(
                EC.presence_of_all_elements_located(
                    (By.CSS_SELECTOR, ".ai-model-item .model-status")
                )
            )
            print(f"✅ Элементы .model-status ({len(model_statuses)}) найдены после ожидания.")
        except Exception as e:
            print(f"❌ Не удалось найти .model-status даже после ожидания: {e}")
            try:
                models_container_html_attr = driver.find_element(
                    By.CLASS_NAME, "ai-models-container"
                ).get_attribute("innerHTML")
                models_container_html = (
                    models_container_html_attr if models_container_html_attr is not None else ""
                )
                print(f"🔍 HTML ai-models-container: {models_container_html[:1000]}...")
            except:
                print("🔍 Не удалось получить HTML контейнера моделей для отладки.")
            model_statuses = []

        assert len(model_statuses) > 0, "Не найдено статусов моделей"

        for status_element in model_statuses:
            parent_item = status_element.find_element(
                By.XPATH, "./ancestor::div[contains(@class, 'ai-model-item')]"
            )
            status_classes_attr = parent_item.get_attribute("class")
            status_classes = status_classes_attr if status_classes_attr is not None else ""
            status_text = status_element.text.lower()
            print(f"🔍 Статус модели: '{status_text}', классы родителя: '{status_classes}'")

            if "недоступна" in status_text:
                assert "unavailable" in status_classes or "offline" in status_classes, (
                    f"Ожидался класс 'unavailable' или 'offline' для статуса '{status_text}',"
                    f" классы: '{status_classes}'"
                )
            elif "доступна" in status_text:
                assert "available" in status_classes or "online" in status_classes, (
                    f"Ожидался класс 'available' или 'online' для статуса '{status_text}', классы:"
                    f" '{status_classes}'"
                )

    def test_refresh_models_button(self, driver):
        """Тест кнопки обновления статуса моделей"""
        driver.get("http://localhost:5001")
        wait = WebDriverWait(driver, 10)

        refresh_button = wait.until(EC.element_to_be_clickable((By.ID, "check-ai-models-btn")))
        assert refresh_button is not None
        refresh_button.click()

        try:
            time.sleep(1)
            all_statuses = wait.until(
                EC.presence_of_all_elements_located(
                    (By.CSS_SELECTOR, ".ai-model-item .model-status")
                )
            )
            print(f"✅ Найдено статусов после обновления: {len(all_statuses)}")
            assert (
                len(all_statuses) > 0
            ), "Статусы моделей не обновились или не найдены после нажатия кнопки."
        except Exception as e:
            print(
                "❌ Статусы моделей не обнаружены/не обновились после нажатия кнопки и"
                f" ожидания: {e}"
            )
            pytest.fail(f"Статусы моделей не обновились: {e}")

    def test_model_selection(self, driver):
        """Тест выбора модели"""
        driver.get("http://localhost:5001")
        wait = WebDriverWait(driver, 20)

        try:
            initial_model_items = wait.until(
                EC.presence_of_all_elements_located((By.CLASS_NAME, "ai-model-item"))
            )
            print(f"✅ Изначально найдено {len(initial_model_items)} ai-model-item элементов.")
            assert len(initial_model_items) > 0, "Элементы ai-model-item не загружены."
        except Exception as e:
            print(f"❌ Элементы ai-model-item не загружены: {e}")
            pytest.fail(f"Элементы ai-model-item не загружены: {e}")

        available_models_info = []
        for index, model_element in enumerate(initial_model_items):
            try:
                if not EC.staleness_of(model_element)(driver):
                    classes_attr = model_element.get_attribute("class")
                    classes = classes_attr if classes_attr is not None else ""
                    if "available" in classes or "online" in classes:
                        model_name_element = model_element.find_element(By.CLASS_NAME, "model-name")
                        available_models_info.append(
                            {
                                "index": index,
                                "name": model_name_element.text,
                                "original_classes": classes,
                            }
                        )
                else:
                    print(f"⚠️ Элемент {index} устарел перед проверкой классов.")
            except Exception as e:
                print(f"⚠️ Ошибка при получении атрибутов для элемента {index}: {e}. Пропускаем.")
                continue

        print(f"Найдено доступных моделей для выбора: {len(available_models_info)}")

        if not available_models_info:
            print("ℹ️ Нет доступных моделей для выбора. Тест выбора пропускается.")
            return

        model_to_select_info = available_models_info[0]
        print(
            f"ℹ️ Попытка выбрать модель: '{model_to_select_info['name']}' с индексом"
            f" {model_to_select_info['index']}"
        )

        try:
            current_model_items = driver.find_elements(By.CLASS_NAME, "ai-model-item")
            if model_to_select_info["index"] < len(current_model_items):
                model_to_click = current_model_items[model_to_select_info["index"]]

                wait.until(EC.element_to_be_clickable(model_to_click))
                print(f"🖱️ Клик по модели: '{model_to_select_info['name']}'")
                model_to_click.click()

                # ОЖИДАНИЕ ПОЯВЛЕНИЯ КЛАССА
                def check_selection_class(driver_instance):
                    refreshed_items = driver_instance.find_elements(By.CLASS_NAME, "ai-model-item")
                    if model_to_select_info["index"] < len(refreshed_items):
                        selected_item_after_click = refreshed_items[model_to_select_info["index"]]
                        current_classes_attr = selected_item_after_click.get_attribute("class")
                        current_classes = (
                            current_classes_attr if current_classes_attr is not None else ""
                        )
                        print(
                            f"🔍 Проверка классов для '{model_to_select_info['name']}':"
                            f" '{current_classes}'"
                        )  # Отладочный вывод
                        return "selected" in current_classes or "active" in current_classes
                    return False

                # Используем таймаут из 'wait' объекта, который равен 20 секундам
                wait.until(
                    check_selection_class,
                    message=(
                        "Класс 'selected' или 'active' не появился у модели"
                        f" '{model_to_select_info['name']}' после клика в течение"
                        f" {wait._timeout} секунд."
                    ),
                )

                final_model_items = driver.find_elements(By.CLASS_NAME, "ai-model-item")
                selected_model_element_final = final_model_items[model_to_select_info["index"]]
                updated_classes_attr = selected_model_element_final.get_attribute("class")
                updated_classes = updated_classes_attr if updated_classes_attr is not None else ""

                print(
                    f"✅ Модель '{model_to_select_info['name']}' выбрана, классы: {updated_classes}"
                )
                assert "selected" in updated_classes or "active" in updated_classes, (
                    f"Модель '{model_to_select_info['name']}' должна иметь класс 'selected' или"
                    f" 'active', но имеет '{updated_classes}'"
                )
            else:
                pytest.fail(
                    f"Индекс модели {model_to_select_info['index']} вышел за пределы списка после"
                    " обновления."
                )

        except Exception as e:
            print(
                "❌ Ошибка во время выбора или проверки модели"
                f" '{model_to_select_info['name']}': {e}"
            )
            timestamp = time.strftime("%Y%m%d-%H%M%S")
            screenshot_filename = f"error_model_selection_{timestamp}.png"
            driver.save_screenshot(screenshot_filename)
            print(f"📷 Скриншот сохранен: {screenshot_filename}")
            pytest.fail(f"Ошибка при выборе модели: {e}")
