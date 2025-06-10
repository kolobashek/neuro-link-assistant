"""
Тесты навигации и корректности ссылок в пользовательском интерфейсе.
"""

import time

import pytest
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait


class TestNavigation:
    """Тесты для навигационных элементов и переходов между страницами."""

    def test_main_navigation_links(self, ui_client):
        """Тест основных навигационных ссылок."""
        # Открываем главную страницу
        ui_client.get("http://localhost:5001/")

        # Находим все основные навигационные ссылки
        nav_links = ui_client.find_elements(By.CSS_SELECTOR, "nav a")

        # Проверяем наличие ожидаемых ссылок
        expected_links = ["Модели", "История", "Настройки", "Помощь"]
        nav_texts = [link.text for link in nav_links]

        for expected in expected_links:
            assert any(
                expected in text for text in nav_texts
            ), f"Ссылка '{expected}' не найдена в навигации"

    def test_url_changes_on_navigation(self, ui_client):
        """Тест изменения URL при навигации."""
        # Открываем главную страницу
        ui_client.get("http://localhost:5001/")

        # Находим и кликаем по ссылке на раздел моделей
        models_link = ui_client.find_element(By.XPATH, "//a[contains(text(), 'Модели')]")
        models_link.click()

        # Ждем изменения URL
        WebDriverWait(ui_client, 10).until(lambda driver: "/models" in driver.current_url)

        # Проверяем, что URL изменился соответственно
        assert "/models" in ui_client.current_url, "URL не содержит раздел моделей после клика"

    def test_browser_history_navigation(self, ui_client):
        """Тест навигации с использованием истории браузера."""
        # Открываем главную страницу
        ui_client.get("http://localhost:5001/")
        initial_url = ui_client.current_url

        # Переходим в раздел настроек
        settings_link = ui_client.find_element(By.XPATH, "//a[contains(text(), 'Настройки')]")
        settings_link.click()

        # Ждем загрузки страницы настроек
        WebDriverWait(ui_client, 10).until(lambda driver: "/settings" in driver.current_url)
        settings_url = ui_client.current_url

        # Переходим в раздел истории
        history_link = ui_client.find_element(By.XPATH, "//a[contains(text(), 'История')]")
        history_link.click()

        # Ждем загрузки страницы истории
        WebDriverWait(ui_client, 10).until(lambda driver: "/history" in driver.current_url)
        # history_url = ui_client.current_url

        # Небольшая пауза для стабильности теста
        time.sleep(0.5)

        # Проверяем навигацию "назад"
        ui_client.back()

        # Ждем возврата на страницу настроек
        WebDriverWait(ui_client, 10).until(lambda driver: driver.current_url == settings_url)
        assert (
            ui_client.current_url == settings_url
        ), "Навигация назад не вернула на страницу настроек"

        ui_client.back()

        # Ждем возврата на главную страницу
        WebDriverWait(ui_client, 10).until(lambda driver: driver.current_url == initial_url)
        assert (
            ui_client.current_url == initial_url
        ), "Навигация назад не вернула на главную страницу"

        # Проверяем навигацию "вперед"
        ui_client.forward()

        # Ждем перехода на страницу настроек
        WebDriverWait(ui_client, 10).until(lambda driver: driver.current_url == settings_url)
        assert (
            ui_client.current_url == settings_url
        ), "Навигация вперед не перешла на страницу настроек"

    def test_footer_navigation_links(self, ui_client):
        """Тест навигационных ссылок в футере."""
        # Открываем главную страницу
        ui_client.get("http://localhost:5001/")

        # Прокручиваем страницу до футера
        footer = ui_client.find_element(By.CSS_SELECTOR, "footer")
        ui_client.execute_script("arguments[0].scrollIntoView();", footer)

        # Проверяем наличие и работоспособность ссылок в футере
        footer_links = footer.find_elements(By.CSS_SELECTOR, "a")
        assert len(footer_links) > 0, "В футере не найдены навигационные ссылки"

        # Проверяем первую ссылку (например, Политика конфиденциальности)
        privacy_link = footer.find_element(By.XPATH, ".//a[contains(text(), 'Конфиденциальность')]")
        privacy_link.click()

        # Ждем загрузки страницы с политикой
        WebDriverWait(ui_client, 10).until(
            lambda driver: "privacy" in driver.current_url or "policy" in driver.current_url
        )

        # Проверяем, что URL содержит ожидаемый путь
        assert any(
            term in ui_client.current_url for term in ["privacy", "policy", "конфиденциальность"]
        ), "Переход по ссылке на политику конфиденциальности не сработал"

    def test_navigation_breadcrumbs(self, ui_client):
        """Тест навигации с использованием хлебных крошек."""
        # Открываем страницу, которая имеет достаточную глубину для хлебных крошек
        ui_client.get("http://localhost:5001/models/categories")

        # Проверяем наличие элемента хлебных крошек
        breadcrumbs = ui_client.find_elements(By.CSS_SELECTOR, ".breadcrumbs")
        if not breadcrumbs:
            pytest.skip("Хлебные крошки не реализованы в интерфейсе")

        # Проверяем наличие ссылок в хлебных крошках
        breadcrumb_links = ui_client.find_elements(By.CSS_SELECTOR, ".breadcrumbs a")
        assert len(breadcrumb_links) > 0, "В хлебных крошках не найдены ссылки"

        # Кликаем по ссылке на главную страницу
        home_link = breadcrumb_links[0]  # Обычно первая ссылка ведет на главную
        home_link.click()

        # Ждем перехода на главную страницу
        WebDriverWait(ui_client, 10).until(
            lambda driver: driver.current_url.endswith("/") or driver.current_url.endswith("/home")
        )

        # Проверяем, что мы вернулись на главную
        assert (
            ui_client.current_url.rstrip("/").endswith("5000") or "/home" in ui_client.current_url
        ), "Навигация через хлебные крошки не привела на главную страницу"

    def test_main_navigation_structure(self, ui_client):
        """Тест структуры основной навигации, включая все новые разделы."""
        # Открываем главную страницу
        ui_client.get("http://localhost:5001/")

        # Находим все основные навигационные ссылки
        nav_links = ui_client.find_elements(By.CSS_SELECTOR, "nav a, .main-navigation a")

        # Проверяем наличие всех необходимых разделов в навигации
        nav_texts = [link.text.lower() for link in nav_links]
        nav_hrefs = [link.get_attribute("href") for link in nav_links]

        expected_sections = [
            {"text": ["главная", "дашборд", "home", "dashboard"], "url": "/"},
            {"text": ["задачи", "tasks"], "url": "/tasks"},
            {"text": ["модели", "models"], "url": "/ai_models"},
            {"text": ["оркестратор", "orchestrator"], "url": "/orchestrator"},
            {"text": ["процесс", "шаблон", "workflow"], "url": "/workflows"},
            {"text": ["настройки", "settings"], "url": "/settings"},
            {"text": ["аналитика", "analytics"], "url": "/analytics"},
        ]

        for section in expected_sections:
            # Проверяем, что хотя бы один из возможных текстов ссылки присутствует
            text_exists = any(
                any(expected_text in nav_text for expected_text in section["text"])
                for nav_text in nav_texts
            )
            # Проверяем, что URL присутствует в навигации
            url_exists = any(section["url"] in href for href in nav_hrefs)

            assert (
                text_exists and url_exists
            ), f"Раздел {section['text'][0]} с URL {section['url']} не найден в главной навигации"

    def test_task_navigation(self, ui_client):
        """Тест навигации в разделе задач."""
        # Открываем страницу задач
        ui_client.get("http://localhost:5001/tasks")

        # Ждем загрузки страницы
        WebDriverWait(ui_client, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, ".task-list, .tasks-container"))
        )

        # Проверяем наличие кнопки создания новой задачи
        create_button = ui_client.find_element(
            By.CSS_SELECTOR, ".create-task-btn, button[href='/tasks/create']"
        )

        # Кликаем по кнопке создания задачи
        create_button.click()

        # Ждем перехода на страницу создания задачи
        WebDriverWait(ui_client, 10).until(lambda driver: "/tasks/create" in driver.current_url)

        # Возвращаемся назад
        ui_client.back()

        # Ждем возврата на страницу задач
        WebDriverWait(ui_client, 10).until(lambda driver: driver.current_url.endswith("/tasks"))

        # Проверяем наличие фильтров задач
        filters = ui_client.find_elements(By.CSS_SELECTOR, ".task-filter, .filter-option")
        assert len(filters) > 0, "Фильтры задач не найдены"

        # Проверяем, что есть фильтр по статусу и кликаем по нему
        status_filter = None
        for filter_elem in filters:
            if "статус" in filter_elem.text.lower() or "status" in filter_elem.text.lower():
                status_filter = filter_elem
                break

        if status_filter:
            status_filter.click()

            # Ждем появления опций фильтра
            WebDriverWait(ui_client, 10).until(
                EC.visibility_of_element_located(
                    (By.CSS_SELECTOR, ".filter-dropdown, .status-options")
                )
            )

            # Выбираем опцию "В процессе"
            filter_options = ui_client.find_elements(
                By.CSS_SELECTOR, ".filter-option, .status-option"
            )
            for option in filter_options:
                if "процесс" in option.text.lower() or "progress" in option.text.lower():
                    option.click()
                    break

            # Проверяем, что URL изменился и содержит параметр фильтра
            WebDriverWait(ui_client, 10).until(
                lambda driver: "status=" in driver.current_url or "filter=" in driver.current_url
            )

    def test_model_navigation(self, ui_client):
        """Тест навигации в разделе моделей."""
        # Открываем страницу моделей
        ui_client.get("http://localhost:5001/ai_models")

        # Ждем загрузки страницы
        WebDriverWait(ui_client, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, ".models-container, .ai-models-list"))
        )

        # Проверяем наличие вкладок для разных типов моделей
        tabs = ui_client.find_elements(By.CSS_SELECTOR, ".model-tab, .model-category-tab")

        browser_tab = None
        for tab in tabs:
            if "браузер" in tab.text.lower() or "browser" in tab.text.lower():
                browser_tab = tab
                break

        if browser_tab:
            # Кликаем по вкладке браузерных моделей
            browser_tab.click()

            # Ждем перехода на страницу браузерных моделей
            WebDriverWait(ui_client, 10).until(
                lambda driver: "/ai_models/browser" in driver.current_url
                or "type=browser" in driver.current_url
            )

            # Проверяем наличие элементов управления браузерными моделями
            assert ui_client.find_elements(
                By.CSS_SELECTOR, ".browser-model-item, .browser-automation"
            ), "Элементы управления браузерными моделями не найдены"

    def test_orchestrator_navigation(self, ui_client):
        """Тест навигации в разделе оркестратора."""
        # Открываем страницу оркестратора
        ui_client.get("http://localhost:5001/orchestrator")

        # Ждем загрузки страницы
        WebDriverWait(ui_client, 10).until(
            EC.presence_of_element_located(
                (By.CSS_SELECTOR, ".orchestrator-dashboard, .routing-rules")
            )
        )

        # Проверяем наличие вкладок для разных разделов оркестратора
        tabs = ui_client.find_elements(By.CSS_SELECTOR, ".orchestrator-tab, .rules-tab")

        # Проверяем, что есть вкладка стратегий и кликаем по ней
        strategy_tab = None
        for tab in tabs:
            if "стратег" in tab.text.lower() or "strateg" in tab.text.lower():
                strategy_tab = tab
                break

        if strategy_tab:
            strategy_tab.click()

            # Ждем загрузки раздела стратегий
            WebDriverWait(ui_client, 10).until(
                EC.visibility_of_element_located(
                    (By.CSS_SELECTOR, ".strategy-section, .optimization-strategy")
                )
            )

            # Проверяем наличие списка стратегий
            assert ui_client.find_elements(
                By.CSS_SELECTOR, ".strategy-item, .optimization-option"
            ), "Список стратегий оптимизации не найден"

    def test_workflows_navigation(self, ui_client):
        """Тест навигации в разделе рабочих процессов."""
        # Открываем страницу рабочих процессов
        ui_client.get("http://localhost:5001/workflows")

        # Ждем загрузки страницы
        WebDriverWait(ui_client, 10).until(
            EC.presence_of_element_located(
                (By.CSS_SELECTOR, ".workflows-container, .templates-list")
            )
        )

        # Проверяем наличие вкладок для библиотеки и пользовательских процессов
        tabs = ui_client.find_elements(By.CSS_SELECTOR, ".workflow-tab, .template-category")

        custom_tab = None
        for tab in tabs:
            if (
                "пользовател" in tab.text.lower()
                or "custom" in tab.text.lower()
                or "user" in tab.text.lower()
            ):
                custom_tab = tab
                break

        if custom_tab:
            # Кликаем по вкладке пользовательских процессов
            custom_tab.click()

            # Ждем загрузки пользовательских процессов
            WebDriverWait(ui_client, 10).until(
                EC.visibility_of_element_located(
                    (By.CSS_SELECTOR, ".user-workflows, .custom-workflows")
                )
            )

            # Проверяем наличие кнопки создания нового процесса
            create_button = ui_client.find_element(
                By.CSS_SELECTOR, ".create-workflow-btn, .new-workflow"
            )

            # Кликаем по кнопке создания
            create_button.click()

            # Ждем появления модального окна или перехода на страницу редактора
            WebDriverWait(ui_client, 10).until(
                lambda driver: EC.visibility_of_element_located(
                    (By.CSS_SELECTOR, ".workflow-editor, .editor-modal")
                )(driver)
                or "/workflows/create" in driver.current_url
                or "/workflows/editor" in driver.current_url
            )

    def test_analytics_navigation(self, ui_client):
        """Тест навигации в разделе аналитики."""
        # Открываем страницу аналитики
        ui_client.get("http://localhost:5001/analytics")

        # Ждем загрузки страницы
        WebDriverWait(ui_client, 10).until(
            EC.presence_of_element_located(
                (By.CSS_SELECTOR, ".analytics-dashboard, .stats-container")
            )
        )

        # Проверяем наличие вкладок для разных разделов аналитики
        tabs = ui_client.find_elements(By.CSS_SELECTOR, ".analytics-tab, .report-tab")

        cost_tab = None
        for tab in tabs:
            if "стоимост" in tab.text.lower() or "cost" in tab.text.lower():
                cost_tab = tab
                break

        if cost_tab:
            # Кликаем по вкладке анализа стоимости
            cost_tab.click()

            # Ждем загрузки раздела анализа стоимости
            WebDriverWait(ui_client, 10).until(
                EC.visibility_of_element_located((By.CSS_SELECTOR, ".cost-analysis, .cost-stats"))
            )

            # Проверяем наличие графиков стоимости
            assert ui_client.find_elements(
                By.CSS_SELECTOR, ".cost-chart, .expense-graph"
            ), "Графики анализа стоимости не найдены"

    def test_breadcrumb_navigation(self, ui_client):
        """Тест навигации с использованием хлебных крошек."""
        # Открываем страницу с достаточной глубиной вложенности
        ui_client.get("http://localhost:5001/tasks")

        # Ждем загрузки страницы
        WebDriverWait(ui_client, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, ".task-list, .tasks-container"))
        )

        # Ищем задачу для перехода в детали
        task_items = ui_client.find_elements(By.CSS_SELECTOR, ".task-item")

        if not task_items:
            pytest.skip("Нет задач для тестирования хлебных крошек")

        # Кликаем по первой задаче
        task_items[0].click()

        # Ждем перехода на страницу деталей задачи
        WebDriverWait(ui_client, 10).until(
            lambda driver: "/tasks/" in driver.current_url
            and not driver.current_url.endswith("/tasks")
        )

        # Проверяем наличие хлебных крошек
        breadcrumbs = ui_client.find_elements(By.CSS_SELECTOR, ".breadcrumbs, .navigation-path")

        if not breadcrumbs:
            pytest.skip("Хлебные крошки не реализованы в интерфейсе")

        # Находим ссылку на раздел задач в хлебных крошках
        tasks_crumb = None
        crumb_links = ui_client.find_elements(By.CSS_SELECTOR, ".breadcrumbs a, .navigation-path a")

        for link in crumb_links:
            if "задачи" in link.text.lower() or "tasks" in link.text.lower():
                tasks_crumb = link
                break

        if tasks_crumb:
            # Кликаем по ссылке на раздел задач
            tasks_crumb.click()

            # Ждем перехода на страницу задач
            WebDriverWait(ui_client, 10).until(lambda driver: driver.current_url.endswith("/tasks"))

            # Проверяем, что мы вернулись в раздел задач
            assert ui_client.current_url.endswith(
                "/tasks"
            ), "Навигация по хлебным крошкам не привела к странице задач"

    def test_sidebar_navigation(self, ui_client):
        """Тест навигации через боковое меню."""
        # Открываем главную страницу
        ui_client.get("http://localhost:5001/")

        # Ждем загрузки страницы
        WebDriverWait(ui_client, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "nav, .sidebar, .main-navigation"))
        )

        # Ищем боковое меню или основную навигацию
        sidebar = ui_client.find_element(By.CSS_SELECTOR, ".sidebar, nav, .main-navigation")

        # Проверяем, что ссылки в боковом меню работают
        nav_links = sidebar.find_elements(By.TAG_NAME, "a")
        assert len(nav_links) > 0, "В боковом меню нет навигационных ссылок"

        # Находим ссылку на страницу оркестратора
        orchestrator_link = None
        for link in nav_links:
            if (
                "оркестратор" in link.text.lower() or "orchestrator" in link.text.lower()
            ) and "orchestrator" in link.get_attribute("href"):
                orchestrator_link = link
                break

        if not orchestrator_link:
            pytest.skip("Ссылка на оркестратор не найдена в боковом меню")

        # Кликаем по ссылке на оркестратор
        orchestrator_link.click()

        # Ждем перехода на страницу оркестратора
        WebDriverWait(ui_client, 10).until(lambda driver: "/orchestrator" in driver.current_url)

        # Проверяем, что URL изменился соответственно
        assert (
            "/orchestrator" in ui_client.current_url
        ), "URL не содержит раздел оркестратора после клика"

        # Возвращаемся на главную
        home_link = ui_client.find_element(By.CSS_SELECTOR, "a[href='/'], .home-link, .logo")
        home_link.click()

        # Ждем возврата на главную страницу
        WebDriverWait(ui_client, 10).until(
            lambda driver: driver.current_url.endswith("/") or driver.current_url.endswith("/home")
        )

    def test_task_details_navigation(self, ui_client):
        """Тест навигации внутри деталей задачи."""
        # Открываем страницу задач
        ui_client.get("http://localhost:5001/tasks")

        # Ждем загрузки страницы
        WebDriverWait(ui_client, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, ".task-list, .tasks-container"))
        )

        # Ищем задачу для перехода в детали
        task_items = ui_client.find_elements(By.CSS_SELECTOR, ".task-item")

        if not task_items:
            pytest.skip("Нет задач для тестирования навигации в деталях")

        # Кликаем по первой задаче
        task_items[0].click()

        # Ждем перехода на страницу деталей задачи
        WebDriverWait(ui_client, 10).until(
            lambda driver: "/tasks/" in driver.current_url
            and not driver.current_url.endswith("/tasks")
        )

        # Проверяем наличие вкладок на странице деталей
        tabs = ui_client.find_elements(By.CSS_SELECTOR, ".task-tab, .details-tab")

        if not tabs:
            pytest.skip("Вкладки деталей задачи не реализованы в интерфейсе")

        # Проверяем, что есть вкладка логов и кликаем по ней
        logs_tab = None
        for tab in tabs:
            if "лог" in tab.text.lower() or "logs" in tab.text.lower():
                logs_tab = tab
                break

        if logs_tab:
            # Кликаем по вкладке логов
            logs_tab.click()

            # Ждем загрузки секции логов
            WebDriverWait(ui_client, 10).until(
                EC.visibility_of_element_located((By.CSS_SELECTOR, ".task-logs, .execution-log"))
            )

            # Проверяем наличие логов
            assert ui_client.find_elements(
                By.CSS_SELECTOR, ".log-entry, .log-item"
            ), "Записи логов не найдены"

    def test_model_details_navigation(self, ui_client):
        """Тест навигации внутри деталей модели."""
        # Открываем страницу моделей
        ui_client.get("http://localhost:5001/ai_models")

        # Ждем загрузки страницы
        WebDriverWait(ui_client, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, ".models-container, .ai-models-list"))
        )

        # Ищем модель для перехода в детали
        model_items = ui_client.find_elements(By.CSS_SELECTOR, ".model-item")

        if not model_items:
            pytest.skip("Нет моделей для тестирования навигации в деталях")

        # Ищем кнопку подробностей у первой модели
        details_button = None
        try:
            details_button = model_items[0].find_element(
                By.CSS_SELECTOR, ".model-details-btn, .details-icon"
            )
        except Exception:
            pytest.skip("Кнопка подробностей не найдена у модели")

        # Кликаем по кнопке подробностей
        details_button.click()

        # Ждем перехода на страницу деталей модели или открытия модального окна
        WebDriverWait(ui_client, 10).until(
            lambda driver: "/ai_models/" in driver.current_url
            and not driver.current_url.endswith("/ai_models")
            or EC.visibility_of_element_located(
                (By.CSS_SELECTOR, ".model-details-modal, .model-info-panel")
            )(driver)
        )

        # Проверяем наличие метрик использования
        assert ui_client.find_elements(
            By.CSS_SELECTOR, ".usage-metrics, .model-metrics"
        ), "Метрики использования модели не найдены"

        # Проверяем наличие секции параметров
        assert ui_client.find_elements(
            By.CSS_SELECTOR, ".model-parameters, .parameters-section"
        ), "Секция параметров модели не найдена"

    def test_mobile_navigation(self, ui_client):
        """Тест мобильной навигации при узком экране."""
        # Устанавливаем размер окна как у мобильного устройства
        ui_client.set_window_size(375, 667)  # Размер iPhone 6/7/8

        # Открываем главную страницу
        ui_client.get("http://localhost:5001/")

        # Ждем загрузки страницы
        WebDriverWait(ui_client, 10).until(EC.presence_of_element_located((By.TAG_NAME, "body")))

        # Ищем иконку мобильного меню (гамбургер)
        try:
            mobile_menu_button = ui_client.find_element(
                By.CSS_SELECTOR, ".mobile-menu-toggle, .hamburger-icon, button[aria-label='меню']"
            )
        except Exception:
            # Если мобильное меню не найдено, восстанавливаем размер окна и пропускаем тест
            ui_client.maximize_window()
            pytest.skip(
                "Кнопка мобильного меню не найдена, возможно адаптивная навигация не реализована"
            )

        # Кликаем по кнопке меню
        mobile_menu_button.click()

        # Ждем появления мобильного меню
        WebDriverWait(ui_client, 10).until(
            EC.visibility_of_element_located(
                (By.CSS_SELECTOR, ".mobile-menu, .nav-drawer, .menu-dropdown")
            )
        )

        # Ищем ссылку на задачи в мобильном меню
        mobile_links = ui_client.find_elements(
            By.CSS_SELECTOR, ".mobile-menu a, .nav-drawer a, .menu-dropdown a"
        )

        tasks_link = None
        for link in mobile_links:
            if "задачи" in link.text.lower() or "tasks" in link.text.lower():
                tasks_link = link
                break

        if not tasks_link:
            # Восстанавливаем размер окна
            ui_client.maximize_window()
            pytest.skip("Ссылка на задачи не найдена в мобильном меню")

        # Кликаем по ссылке на задачи
        tasks_link.click()

        # Ждем перехода на страницу задач
        WebDriverWait(ui_client, 10).until(lambda driver: "/tasks" in driver.current_url)

        # Проверяем, что URL изменился соответственно
        assert (
            "/tasks" in ui_client.current_url
        ), "URL не содержит раздел задач после клика в мобильном меню"

        # Восстанавливаем размер окна
        ui_client.maximize_window()

    def test_notifications_navigation(self, ui_client):
        """Тест навигации через уведомления."""
        # Открываем главную страницу
        ui_client.get("http://localhost:5001/")

        # Ждем загрузки страницы
        WebDriverWait(ui_client, 10).until(EC.presence_of_element_located((By.TAG_NAME, "body")))

        # Ищем иконку уведомлений
        try:
            notifications_icon = ui_client.find_element(
                By.CSS_SELECTOR, ".notifications-icon, .bell-icon, [aria-label='уведомления']"
            )
        except Exception:
            pytest.skip(
                "Иконка уведомлений не найдена, возможно система уведомлений не реализована"
            )

        # Кликаем по иконке уведомлений
        notifications_icon.click()

        # Ждем появления списка уведомлений
        WebDriverWait(ui_client, 10).until(
            EC.visibility_of_element_located(
                (By.CSS_SELECTOR, ".notifications-dropdown, .notifications-panel")
            )
        )

        # Ищем уведомления в выпадающем списке
        notifications = ui_client.find_elements(By.CSS_SELECTOR, ".notification-item, .alert-item")

        if not notifications:
            pytest.skip("В списке уведомлений нет элементов")

        # Кликаем по первому уведомлению
        notifications[0].click()

        # Ждем перехода на соответствующую страницу
        WebDriverWait(ui_client, 10).until(
            lambda driver: driver.current_url != "http://localhost:5001/"
        )

        # Проверяем, что URL изменился
        assert (
            ui_client.current_url != "http://localhost:5001/"
        ), "URL не изменился после клика по уведомлению"

    def test_footer_links_navigation(self, ui_client):
        """Тест навигации через ссылки в футере."""
        # Открываем главную страницу
        ui_client.get("http://localhost:5001/")

        # Ждем загрузки страницы
        WebDriverWait(ui_client, 10).until(EC.presence_of_element_located((By.TAG_NAME, "footer")))

        # Прокручиваем страницу до футера
        footer = ui_client.find_element(By.TAG_NAME, "footer")
        ui_client.execute_script("arguments[0].scrollIntoView();", footer)

        # Ищем ссылки в футере
        footer_links = footer.find_elements(By.TAG_NAME, "a")

        if not footer_links:
            pytest.skip("В футере нет ссылок")

        # Ищем ссылку на документацию или помощь
        help_link = None
        for link in footer_links:
            link_text = link.text.lower()
            link_href = link.get_attribute("href")
            if (
                "документ" in link_text
                or "помощь" in link_text
                or "help" in link_text
                or "docs" in link_text
            ) and ("help" in link_href or "docs" in link_href):
                help_link = link
                break

        if not help_link:
            pytest.skip("Ссылка на документацию или помощь не найдена в футере")

        # Кликаем по ссылке на документацию
        help_link.click()

        # Ждем перехода на страницу документации
        WebDriverWait(ui_client, 10).until(
            lambda driver: "/help" in driver.current_url or "/docs" in driver.current_url
        )

        # Проверяем, что URL изменился соответственно
        assert (
            "/help" in ui_client.current_url or "/docs" in ui_client.current_url
        ), "URL не содержит раздел помощи или документации после клика"
