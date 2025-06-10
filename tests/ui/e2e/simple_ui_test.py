import pytest
from selenium.webdriver.common.by import By


class TestSimpleUI:
    def test_homepage_opens(self, ui_client):
        """Простейший тест - открытие главной страницы"""
        print("🔍 Открываем главную страницу...")
        ui_client.get("http://localhost:5001/")

        print("🔍 Получаем заголовок...")
        title = ui_client.driver.title
        print(f"📋 Заголовок: {title}")

        assert title is not None
        assert len(title) > 0

    def test_user_input_exists(self, ui_client):
        """Проверяем наличие поля ввода"""
        ui_client.get("http://localhost:5001/")

        # Ищем поле ввода пользователя
        user_input = ui_client.find_element(By.ID, "user-input")
        assert user_input is not None
        assert user_input.is_displayed()

    def test_page_has_content(self, ui_client):
        """Проверяем что страница содержит контент"""
        ui_client.get("http://localhost:5001/")

        body = ui_client.find_element(By.TAG_NAME, "body")
        content = body.text

        assert len(content) > 100  # Страница не пустая
        print(f"✅ Контент найден: {len(content)} символов")
