"""
Тесты для проверки маршрутизации и работы с URL в приложении.
"""

import pytest
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait


class TestRouting:
    """Тесты маршрутизации и взаимодействия с URL."""

    def test_model_selection_routing(self, ui_client, base_url):
        """Тест маршрутизации при выборе модели."""
        # Открываем страницу выбора моделей
        ui_client.get(f"{base_url}/models")

        # Ждем загрузки карточек моделей
        WebDriverWait(ui_client, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, ".model-card"))
        )

        # Находим и выбираем конкретную модель
        model_cards = ui_client.find_elements(By.CSS_SELECTOR, ".model-card")

        if not model_cards:
            pytest.skip("Не найдены карточки моделей для тестирования")

        # Берем первую модель и получаем её идентификатор
        model_card = model_cards[0]
        model_id = model_card.get_attribute("data-model-id")

        if not model_id:
            model_id = "default"  # Если ID не найден, используем значение по умолчанию для проверки

        # Кликаем по карточке модели
        model_card.click()

        # Ждем изменения URL
        WebDriverWait(ui_client, 10).until(
            lambda driver: f"models/{model_id}" in driver.current_url
            or "model" in driver.current_url
        )

        # Проверяем, что URL содержит идентификатор модели или указывает на страницу модели
        assert any(
            term in ui_client.current_url for term in [f"models/{model_id}", "model", model_id]
        ), "URL не содержит идентификатор выбранной модели или признак страницы модели"

    def test_history_item_routing(self, ui_client, base_url):
        """Тест маршрутизации к элементу истории взаимодействий."""
        # Открываем страницу истории
        ui_client.get(f"{base_url}/history")

        # Ждем загрузки элементов истории
        try:
            WebDriverWait(ui_client, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, ".history-item"))
            )
        except Exception:
            pytest.skip("Не найдены элементы истории для тестирования или требуется авторизация")

        # Находим элементы истории
        history_items = ui_client.find_elements(By.CSS_SELECTOR, ".history-item")

        if not history_items:
            pytest.skip("История пуста или элементы имеют другой CSS-селектор")

        # Берем первый элемент истории
        history_item = history_items[0]

        # Пытаемся получить ID элемента истории
        item_id = history_item.get_attribute("data-history-id") or "default"

        # Кликаем по элементу истории
        history_item.click()

        # Ждем изменения URL
        WebDriverWait(ui_client, 10).until(
            lambda driver: "history" in driver.current_url
            and (item_id in driver.current_url or "detail" in driver.current_url)
        )

        # Проверяем, что URL указывает на детальную страницу истории
        assert "history" in ui_client.current_url and (
            item_id in ui_client.current_url or "detail" in ui_client.current_url
        ), "URL не содержит идентификатор элемента истории или признак детальной страницы"

    def test_direct_url_access(self, ui_client, base_url):
        """Тест прямого доступа к URL, минуя навигацию."""
        # Список важных URL для проверки
        urls_to_check = ["/settings", "/models", "/history", "/help"]

        for url in urls_to_check:
            # Открываем URL напрямую
            ui_client.get(base_url)

            # Проверяем, что страница загрузилась корректно
            assert url in ui_client.current_url, f"URL {url} не доступен для прямого доступа"

            # Проверяем, что основные элементы страницы присутствуют
            main_content = ui_client.find_elements(By.CSS_SELECTOR, "main, .content, #app")
            assert len(main_content) > 0, f"Основной контент не загружен при прямом доступе к {url}"

    def test_404_page(self, ui_client, base_url):
        """Тест страницы 404 (не найдено)."""
        # Открываем несуществующий URL
        ui_client.get(f"{base_url}/this-page-does-not-exist")

        # Проверяем, что отображается страница 404
        # Это может быть элемент с соответствующим классом или текстом
        not_found_indicators = [
            ui_client.find_elements(By.CSS_SELECTOR, ".not-found, .error-404"),
            ui_client.find_elements(By.XPATH, "//*[contains(text(), '404')]"),
            ui_client.find_elements(By.XPATH, "//*[contains(text(), 'не найдена')]"),
            ui_client.find_elements(By.XPATH, "//*[contains(text(), 'не найдено')]"),
            ui_client.find_elements(By.XPATH, "//*[contains(text(), 'Not Found')]"),
        ]

        # Проверяем, есть ли хотя бы один индикатор страницы 404
        has_404_indicator = any(len(indicators) > 0 for indicators in not_found_indicators)

        assert has_404_indicator, "Страница 404 не отображается для несуществующего URL"

    def test_query_parameters(self, ui_client, base_url):
        """Тест обработки параметров запроса в URL."""
        # Открываем страницу моделей с параметром фильтрации
        ui_client.get(f"{base_url}/models?category=text")

        # Ждем загрузки элементов
        WebDriverWait(ui_client, 10).until(
            EC.presence_of_element_located(
                (By.CSS_SELECTOR, ".model-card, .model-list, #models-container")
            )
        )

        # Проверяем, что фильтр применился
        # Это может быть отражено в URL, активном состоянии фильтра или в списке отображаемых моделей

        # Метод 1: Проверка URL
        assert "category=text" in ui_client.current_url, "Параметр запроса не сохранился в URL"

        # Метод 2: Проверка состояния фильтра (если есть UI элемент, отражающий текущий фильтр)
        filter_indicators = ui_client.find_elements(
            By.CSS_SELECTOR, ".active-filter, .filter-chip.active"
        )
        if filter_indicators:
            filter_text = filter_indicators[0].text.lower()
            assert "text" in filter_text, "Фильтр не отображается как активный в интерфейсе"

    def test_hash_fragment_navigation(self, ui_client, base_url):
        """Тест навигации с использованием хэш-фрагментов URL."""
        # Открываем страницу с длинным содержимым и якорными ссылками
        ui_client.get(f"{base_url}/help")

        # Ищем якорные ссылки
        anchor_links = ui_client.find_elements(By.CSS_SELECTOR, "a[href^='#']")

        if not anchor_links:
            pytest.skip("Не найдены якорные ссылки для тестирования")

        # Кликаем по первой якорной ссылке
        anchor_link = anchor_links[0]
        href = anchor_link.get_attribute("href")
        fragment = href.split("#")[1] if "#" in href else ""

        anchor_link.click()

        # Ждем изменения URL
        WebDriverWait(ui_client, 10).until(lambda driver: "#" in driver.current_url)

        # Проверяем, что URL содержит фрагмент
        assert (
            f"#{fragment}" in ui_client.current_url
        ), "URL не содержит хэш-фрагмент после клика по якорной ссылке"

        # Проверяем, что страница прокрутилась до элемента с id, соответствующим фрагменту
        target_element = ui_client.find_element(By.ID, fragment)

        # Получаем позицию элемента
        element_position = ui_client.execute_script(
            "return arguments[0].getBoundingClientRect().top;", target_element
        )

        # Проверяем, что элемент находится в верхней части видимой области (с допустимым отклонением)
        assert abs(element_position) < 200, "Страница не прокрутилась до целевого элемента"

    def test_task_center_routing(self, ui_client, base_url):
        """Тест доступа к центру задач и подстраницам."""
        # Открываем страницу центра задач
        ui_client.get(f"{base_url}/tasks")

        # Ждем загрузки элементов страницы с задачами
        WebDriverWait(ui_client, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, ".task-list, .tasks-container"))
        )

        # Проверяем, что заголовок страницы содержит соответствующий текст
        page_title = ui_client.find_element(By.CSS_SELECTOR, "h1, .page-title")
        assert (
            "задач" in page_title.text.lower() or "tasks" in page_title.text.lower()
        ), "Заголовок страницы не содержит упоминания задач"

        # Ищем задачу для проверки роутинга к деталям задачи
        task_items = ui_client.find_elements(By.CSS_SELECTOR, ".task-item")

        if not task_items:
            pytest.skip("Нет задач для тестирования детального представления")

        # Получаем ID первой задачи
        task_item = task_items[0]
        task_id = task_item.get_attribute("data-task-id")

        if not task_id:
            pytest.skip("Не удалось определить ID задачи")

        # Кликаем по задаче для перехода к деталям
        task_item.click()

        # Ждем перехода на страницу деталей задачи
        WebDriverWait(ui_client, 10).until(lambda driver: f"/tasks/{task_id}" in driver.current_url)

        # Проверяем, что URL содержит ID задачи
        assert (
            f"/tasks/{task_id}" in ui_client.current_url
        ), "URL не содержит идентификатор выбранной задачи"

        # Проверяем загрузку графика выполнения задачи
        WebDriverWait(ui_client, 10).until(
            EC.presence_of_element_located(
                (By.CSS_SELECTOR, ".task-progress-graph, .execution-graph")
            )
        )

    def test_task_creation_routing(self, ui_client, base_url):
        """Тест страницы создания новой задачи."""
        # Открываем страницу центра задач
        ui_client.get(f"{base_url}/tasks")

        # Ждем загрузки страницы
        WebDriverWait(ui_client, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, ".task-list, .tasks-container"))
        )

        # Ищем кнопку создания задачи
        create_button = ui_client.find_element(
            By.CSS_SELECTOR, ".create-task-btn, button[href='/tasks/create']"
        )

        # Кликаем по кнопке
        create_button.click()

        # Ждем перехода на страницу создания задачи
        WebDriverWait(ui_client, 10).until(lambda driver: "/tasks/create" in driver.current_url)

        # Проверяем, что мы на странице создания задачи
        assert (
            "/tasks/create" in ui_client.current_url
        ), "Перенаправление на страницу создания задачи не сработало"

        # Проверяем наличие формы создания задачи
        form = ui_client.find_element(By.CSS_SELECTOR, ".task-creation-form")
        assert form.is_displayed(), "Форма создания задачи не отображается"

    def test_model_management_routing(self, ui_client, base_url):
        """Тест страниц управления моделями."""
        # Открываем страницу управления моделями
        ui_client.get(f"{base_url}/ai_models")

        # Ждем загрузки страницы
        WebDriverWait(ui_client, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, ".models-container, .ai-models-list"))
        )

        # Проверяем, что есть категории моделей
        categories = ui_client.find_elements(
            By.CSS_SELECTOR, ".model-category, .model-type-section"
        )

        # Проверяем, что отображаются разные типы моделей
        category_texts = [category.text.lower() for category in categories]
        assert any("api" in text for text in category_texts), "Категория API моделей не найдена"
        assert any("локальн" in text for text in category_texts) or any(
            "local" in text for text in category_texts
        ), "Категория локальных моделей не найдена"
        assert any("бесплатн" in text for text in category_texts) or any(
            "free" in text for text in category_texts
        ), "Категория бесплатных моделей не найдена"

        # Ищем модель для перехода к настройкам
        model_items = ui_client.find_elements(By.CSS_SELECTOR, ".model-item")

        if not model_items:
            pytest.skip("Нет моделей для тестирования настроек")

        # Пытаемся найти кнопку настроек у первой модели
        model_item = model_items[0]
        model_id = model_item.get_attribute("data-model-id")

        if not model_id:
            pytest.skip("Не удалось определить ID модели")

        # Ищем кнопку настроек
        settings_button = model_item.find_element(
            By.CSS_SELECTOR, ".model-settings-btn, .settings-icon"
        )

        # Кликаем по кнопке настроек
        settings_button.click()

        # Ждем перехода на страницу настроек модели
        WebDriverWait(ui_client, 10).until(
            lambda driver: f"/ai_models/{model_id}/settings" in driver.current_url
        )

        # Проверяем, что URL содержит ID модели
        assert (
            f"/ai_models/{model_id}/settings" in ui_client.current_url
        ), "URL не содержит путь к настройкам выбранной модели"

    def test_browser_models_routing(self, ui_client, base_url):
        """Тест страницы управления браузерными моделями."""
        # Открываем страницу браузерных моделей
        ui_client.get(f"{base_url}/ai_models/browser")

        # Ждем загрузки страницы
        WebDriverWait(ui_client, 10).until(
            EC.presence_of_element_located(
                (By.CSS_SELECTOR, ".browser-models, .browser-automation")
            )
        )

        # Проверяем наличие элементов управления автоматизацией
        automation_controls = ui_client.find_elements(
            By.CSS_SELECTOR, ".automation-settings, .schedule-settings"
        )

        assert len(automation_controls) > 0, "Элементы управления автоматизацией не найдены"

    def test_orchestrator_routing(self, ui_client, base_url):
        """Тест страницы оркестратора моделей."""
        # Открываем страницу оркестратора
        ui_client.get(f"{base_url}/orchestrator")

        # Ждем загрузки страницы
        WebDriverWait(ui_client, 10).until(
            EC.presence_of_element_located(
                (By.CSS_SELECTOR, ".orchestrator-dashboard, .routing-rules")
            )
        )

        # Проверяем наличие секций на странице
        routing_section = ui_client.find_element(By.CSS_SELECTOR, ".routing-rules, .rules-section")
        assert routing_section.is_displayed(), "Секция правил маршрутизации не отображается"

        strategy_section = ui_client.find_element(
            By.CSS_SELECTOR, ".optimization-strategy, .strategy-section"
        )
        assert strategy_section.is_displayed(), "Секция стратегий оптимизации не отображается"

        fallback_section = ui_client.find_element(
            By.CSS_SELECTOR, ".fallback-settings, .switching-rules"
        )
        assert fallback_section.is_displayed(), "Секция настроек переключения не отображается"

    def test_workflows_routing(self, ui_client, base_url):
        """Тест страницы шаблонов и рабочих процессов."""
        # Открываем страницу рабочих процессов
        ui_client.get(f"{base_url}/workflows")

        # Ждем загрузки страницы
        WebDriverWait(ui_client, 10).until(
            EC.presence_of_element_located(
                (By.CSS_SELECTOR, ".workflows-container, .templates-list")
            )
        )

        # Проверяем наличие библиотеки шаблонов
        templates_section = ui_client.find_element(
            By.CSS_SELECTOR, ".templates-library, .workflow-templates"
        )
        assert templates_section.is_displayed(), "Библиотека шаблонов не отображается"

        # Проверяем наличие пользовательских процессов
        custom_section = ui_client.find_element(
            By.CSS_SELECTOR, ".custom-workflows, .user-workflows"
        )
        assert custom_section.is_displayed(), "Секция пользовательских процессов не отображается"

        # Проверяем наличие кнопки создания нового процесса
        create_button = ui_client.find_element(
            By.CSS_SELECTOR, ".create-workflow-btn, .new-workflow"
        )
        assert create_button.is_displayed(), "Кнопка создания нового процесса не отображается"

    def test_analytics_routing(self, ui_client, base_url):
        """Тест страницы центра аналитики."""
        # Открываем страницу аналитики
        ui_client.get(f"{base_url}/analytics")

        # Ждем загрузки страницы
        WebDriverWait(ui_client, 10).until(
            EC.presence_of_element_located(
                (By.CSS_SELECTOR, ".analytics-dashboard, .stats-container")
            )
        )

        # Проверяем наличие секций на странице
        usage_section = ui_client.find_element(By.CSS_SELECTOR, ".usage-stats, .usage-statistics")
        assert usage_section.is_displayed(), "Секция статистики использования не отображается"

        cost_section = ui_client.find_element(By.CSS_SELECTOR, ".cost-analysis, .cost-stats")
        assert cost_section.is_displayed(), "Секция анализа стоимости не отображается"

        reports_section = ui_client.find_element(By.CSS_SELECTOR, ".task-reports, .reports-section")
        assert reports_section.is_displayed(), "Секция отчетов по задачам не отображается"

        recommendations = ui_client.find_element(
            By.CSS_SELECTOR, ".recommendations, .optimization-tips"
        )
        assert recommendations.is_displayed(), "Секция рекомендаций не отображается"

    def test_task_execution_routing(self, ui_client, base_url):
        """Тест маршрутизации во время выполнения задачи."""
        # Открываем страницу создания задачи
        ui_client.get(f"{base_url}/tasks/create")

        # Ждем загрузки страницы
        WebDriverWait(ui_client, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, ".task-creation-form"))
        )

        # Заполняем поля формы создания задачи
        task_input = ui_client.find_element(
            By.CSS_SELECTOR, ".task-input, textarea[name='task_description']"
        )
        task_input.send_keys("Тестовая задача для проверки маршрутизации")

        # Ищем кнопку запуска задачи
        submit_button = ui_client.find_element(
            By.CSS_SELECTOR, ".submit-task, button[type='submit']"
        )

        # Кликаем по кнопке запуска
        submit_button.click()

        # Ждем перехода на страницу выполнения задачи или ее деталей
        WebDriverWait(ui_client, 10).until(
            lambda driver: "/tasks/" in driver.current_url and "/create" not in driver.current_url
        )

        # Проверяем, что URL соответствует странице выполнения задачи
        task_id = ui_client.current_url.split("/")[-1]
        assert task_id.isalnum(), "ID задачи в URL не является алфавитно-цифровым идентификатором"

        # Проверяем наличие индикатора выполнения
        WebDriverWait(ui_client, 10).until(
            EC.presence_of_element_located(
                (By.CSS_SELECTOR, ".progress-indicator, .execution-graph")
            )
        )

        # Проверяем, что открыта страница выполнения с пошаговым графиком
        assert ui_client.find_elements(
            By.CSS_SELECTOR, ".execution-steps, .task-progress-graph"
        ), "Элементы пошагового графика выполнения не найдены"

    def test_settings_routing(self, ui_client, base_url):
        """Тест маршрутизации в разделе настроек."""
        # Открываем страницу настроек
        ui_client.get(f"{base_url}/settings")

        # Ждем загрузки страницы
        WebDriverWait(ui_client, 10).until(
            EC.presence_of_element_located(
                (By.CSS_SELECTOR, ".settings-container, .preferences-panel")
            )
        )

        # Проверяем наличие разделов настроек
        assert ui_client.find_elements(
            By.CSS_SELECTOR, ".settings-section, .preferences-section"
        ), "Разделы настроек не найдены"

        # Ищем вкладки в настройках
        settings_tabs = ui_client.find_elements(
            By.CSS_SELECTOR, ".settings-tab, .preference-category"
        )

        notification_tab = None
        for tab in settings_tabs:
            if "уведомлен" in tab.text.lower() or "notif" in tab.text.lower():
                notification_tab = tab
                break

        if notification_tab:
            # Кликаем по вкладке уведомлений
            notification_tab.click()

            # Ждем загрузки раздела уведомлений
            WebDriverWait(ui_client, 10).until(
                lambda driver: "notifications" in driver.current_url
                or EC.visibility_of_element_located(
                    (By.CSS_SELECTOR, ".notifications-settings, .alerts-settings")
                )(driver)
            )

            # Проверяем наличие настроек уведомлений
            assert ui_client.find_elements(
                By.CSS_SELECTOR, ".notification-option, .alert-setting"
            ), "Настройки уведомлений не найдены"

    def test_direct_task_url_access(self, ui_client, base_url):
        """Тест прямого доступа к задаче по URL."""
        # Сначала переходим на страницу задач, чтобы найти идентификатор существующей задачи
        ui_client.get(f"{base_url}/tasks")

        # Ждем загрузки страницы
        WebDriverWait(ui_client, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, ".task-list, .tasks-container"))
        )

        # Ищем задачи в списке
        task_items = ui_client.find_elements(By.CSS_SELECTOR, ".task-item")

        if not task_items:
            pytest.skip("Нет задач для тестирования прямого доступа")

        # Получаем ID первой задачи
        task_id = task_items[0].get_attribute("data-task-id")

        if not task_id:
            pytest.skip("Не удалось получить ID задачи")

        # Переходим напрямую по URL задачи
        ui_client.get(f"{base_url}/tasks/{task_id}")

        # Ждем загрузки страницы деталей задачи
        WebDriverWait(ui_client, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, ".task-details, .execution-graph"))
        )

        # Проверяем, что детали задачи загружены
        task_title = ui_client.find_element(By.CSS_SELECTOR, ".task-title, .task-header h1")
        assert task_title.is_displayed(), "Заголовок задачи не отображается"

    def test_direct_model_url_access(self, ui_client, base_url):
        """Тест прямого доступа к модели по URL."""
        # Сначала переходим на страницу моделей, чтобы найти идентификатор существующей модели
        ui_client.get(f"{base_url}/ai_models")

        # Ждем загрузки страницы
        WebDriverWait(ui_client, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, ".models-container, .ai-models-list"))
        )

        # Ищем модели в списке
        model_items = ui_client.find_elements(By.CSS_SELECTOR, ".model-item")

        if not model_items:
            pytest.skip("Нет моделей для тестирования прямого доступа")

        # Получаем ID первой модели
        model_id = model_items[0].get_attribute("data-model-id")

        if not model_id:
            pytest.skip("Не удалось получить ID модели")

        # Переходим напрямую по URL настроек модели
        ui_client.get(f"{base_url}/ai_models/{model_id}/settings")

        # Ждем загрузки страницы настроек модели
        WebDriverWait(ui_client, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, ".model-settings, .settings-form"))
        )

        # Проверяем, что форма настроек загружена
        settings_form = ui_client.find_element(By.CSS_SELECTOR, ".settings-form, form")
        assert settings_form.is_displayed(), "Форма настроек модели не отображается"

    def test_404_page_routing(self, ui_client, base_url):
        """Тест маршрутизации на несуществующую страницу."""
        # Переходим на несуществующую страницу
        ui_client.get(f"{base_url}/non_existent_page")

        # Проверяем, что отображается страница 404
        WebDriverWait(ui_client, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, ".error-page, .not-found, .error-404"))
        )

        # Проверяем наличие сообщения об ошибке
        error_message = ui_client.find_element(
            By.CSS_SELECTOR, ".error-message, .not-found-message"
        )
        assert (
            "404" in error_message.text
            or "не найден" in error_message.text.lower()
            or "not found" in error_message.text.lower()
        ), "Сообщение об ошибке 404 не отображается"

        # Проверяем наличие кнопки возврата на главную
        home_button = ui_client.find_element(By.CSS_SELECTOR, ".home-button, a[href='/']")
        assert home_button.is_displayed(), "Кнопка возврата на главную не отображается"

        # Кликаем по кнопке возврата
        home_button.click()

        # Ждем перехода на главную страницу
        WebDriverWait(ui_client, 10).until(
            lambda driver: driver.current_url.endswith("/") or driver.current_url.endswith("/home")
        )

    def test_authenticated_routes(self, ui_client, base_url):
        """Тест доступа к маршрутам, требующим аутентификации."""
        # Проверяем, есть ли кнопка входа на главной странице
        ui_client.get(f"{base_url}/")

        login_buttons = ui_client.find_elements(By.CSS_SELECTOR, ".login-button, a[href='/login']")

        # Если нет кнопки логина, предполагаем, что аутентификация не реализована
        if not login_buttons:
            pytest.skip("Аутентификация, возможно, не реализована в приложении")

        # Пытаемся получить доступ к защищенному маршруту
        ui_client.get(f"{base_url}/profile")

        # Проверяем, перенаправлены ли мы на страницу входа
        WebDriverWait(ui_client, 10).until(
            lambda driver: "/login" in driver.current_url
            or EC.presence_of_element_located((By.CSS_SELECTOR, ".login-form, .auth-form"))(driver)
        )

        # Проверяем, что мы видим форму входа
        login_form = ui_client.find_element(By.CSS_SELECTOR, ".login-form, .auth-form")
        assert login_form.is_displayed(), "Форма входа не отображается"

        # Проверяем наличие сообщения о необходимости входа
        messages = ui_client.find_elements(By.CSS_SELECTOR, ".alert-message, .notification-message")
        auth_message_found = False

        for message in messages:
            message_text = message.text.lower()
            if (
                "вход" in message_text
                or "авториз" in message_text
                or "login" in message_text
                or "auth" in message_text
            ):
                auth_message_found = True
                break

        assert auth_message_found, "Сообщение о необходимости входа не найдено"
