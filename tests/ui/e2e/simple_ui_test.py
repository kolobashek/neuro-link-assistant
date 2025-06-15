import pytest
from selenium.webdriver.common.by import By


class TestSimpleUI:
    def test_homepage_opens(self, ui_client, base_url):
        """Простейший тест - открытие главной страницы"""
        print("🔍 Открываем главную страницу...")
        ui_client.get(base_url)

        print("🔍 Получаем заголовок...")
        title = ui_client.driver.title
        print(f"📋 Заголовок: {title}")

        assert title is not None
        assert len(title) > 0

    def test_user_input_exists(self, ui_client, base_url):
        """Проверяем наличие поля ввода"""
        ui_client.get(base_url)

        # Ищем поле ввода пользователя
        user_input = ui_client.find_element(By.ID, "user-input")
        assert user_input is not None
        assert user_input.is_displayed()

    def test_page_has_content(self, ui_client, base_url):
        """Проверяем что страница содержит контент"""
        print(f"🔍 Подключаемся к: {base_url}")
        print(f"🔍 Текущий URL браузера: {ui_client.driver.current_url}")

        # Добавляем отладку перед запросом
        try:
            ui_client.get(base_url)
            print(f"✅ Успешно загружена страница: {ui_client.driver.current_url}")
        except Exception as e:
            print(f"❌ Ошибка загрузки страницы: {e}")
            print(f"🔍 base_url: {base_url}")
            raise

        body = ui_client.find_element(By.TAG_NAME, "body")
        content = body.text

        assert len(content) > 100  # Страница не пустая
        print(f"✅ Контент найден: {len(content)} символов")
