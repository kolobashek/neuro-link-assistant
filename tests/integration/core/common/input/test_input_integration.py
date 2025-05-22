from unittest.mock import patch


class TestInputIntegration:
    """Интеграционные тесты для подсистемы ввода."""

    def test_keyboard_mouse_integration(self):
        """Тест интеграции клавиатуры и мыши."""
        # Импортируем необходимые компоненты
        from core.common.input.factory import get_input_controller

        # Патчим реальные вызовы клавиатуры и мыши для предотвращения
        # фактического ввода во время тестирования
        with patch(
            "core.platform.windows.input.keyboard.WindowsKeyboard.press_key"
        ) as mock_press_key, patch(
            "core.platform.windows.input.mouse.WindowsMouse.click"
        ) as mock_click:

            # Получаем контроллер ввода
            controller = get_input_controller()

            # Проверяем доступность методов
            assert hasattr(controller.keyboard, "press_key")
            assert hasattr(controller.mouse, "click")

            # Тестируем последовательность действий
            controller.keyboard.press_key("a")
            controller.mouse.click()

            # Проверяем, что методы были вызваны
            mock_press_key.assert_called_once()
            mock_click.assert_called_once()

    def test_keyboard_text_input(self):
        """Тест ввода текста через клавиатуру."""
        from core.common.input.factory import get_keyboard

        with patch(
            "core.platform.windows.input.keyboard.WindowsKeyboard.type_text"
        ) as mock_type_text:
            keyboard = get_keyboard()

            # Вводим текст
            text = "Hello, World!"
            keyboard.type_text(text)

            # Проверяем, что метод был вызван с правильными параметрами
            mock_type_text.assert_called_once_with(text)
