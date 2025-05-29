"""
Тесты для Windows-реализаций контроллеров ввода.
"""

from unittest.mock import MagicMock, patch

import pytest
import win32con

from core.common.input.base import AbstractKeyboard, AbstractMouse
from core.platform.windows.input.keyboard import WindowsKeyboard
from core.platform.windows.input.mouse import WindowsMouse


class TestWindowsKeyboard:
    """Тесты для Windows-реализации контроллера клавиатуры."""

    @pytest.fixture
    def keyboard(self):
        """Создает экземпляр WindowsKeyboard для тестов."""
        with patch("win32api.keybd_event") as mock_keybd_event:
            keyboard = WindowsKeyboard(human_like=False)
            yield keyboard, mock_keybd_event

    def test_inheritance(self):
        """Проверка, что WindowsKeyboard наследуется от AbstractKeyboard."""
        assert issubclass(WindowsKeyboard, AbstractKeyboard)

    def test_press_key(self, keyboard):
        """Тест метода press_key."""
        kb, mock_keybd_event = keyboard

        # Проверяем нажатие клавиши 'a'
        result = kb.press_key("a")

        # Проверяем результат и вызовы win32api.keybd_event
        assert result is True
        assert mock_keybd_event.call_count == 2  # press и release

        # Сначала нажатие
        mock_keybd_event.assert_any_call(ord("A"), 0, 0, 0)
        # Затем отпускание
        mock_keybd_event.assert_any_call(ord("A"), 0, win32con.KEYEVENTF_KEYUP, 0)

    def test_press_keys(self, keyboard):
        """Тест метода press_keys."""
        kb, mock_keybd_event = keyboard

        # Проверяем нажатие комбинации Ctrl+C
        result = kb.press_keys(["ctrl", "c"])

        # Проверяем результат
        assert result is True
        assert mock_keybd_event.call_count == 4  # два press и два release

        # Получаем код клавиши Ctrl
        ctrl_code = kb._get_code("ctrl")
        c_code = kb._get_code("c")

        # Проверяем последовательность вызовов
        mock_keybd_event.assert_any_call(ctrl_code, 0, 0, 0)  # press Ctrl
        mock_keybd_event.assert_any_call(c_code, 0, 0, 0)  # press C
        mock_keybd_event.assert_any_call(c_code, 0, win32con.KEYEVENTF_KEYUP, 0)  # release C
        mock_keybd_event.assert_any_call(ctrl_code, 0, win32con.KEYEVENTF_KEYUP, 0)  # release Ctrl

    def test_type_text(self, keyboard):
        """Тест метода type_text."""
        kb, mock_keybd_event = keyboard

        with patch.object(kb, "press_key") as mock_press_key:
            # Вводим текст "Hello"
            result = kb.type_text("Hello")

            # Проверяем результат
            assert result is True
            assert mock_press_key.call_count == 5  # 5 символов

            # Проверяем последовательность вызовов
            mock_press_key.assert_any_call("h")
            mock_press_key.assert_any_call("e")
            mock_press_key.assert_any_call("l")  # Дважды для 'l'
            mock_press_key.assert_any_call("o")

    def test_key_down_and_up(self, keyboard):
        """Тест методов key_down и key_up."""
        kb, mock_keybd_event = keyboard

        # Нажимаем клавишу без отпускания
        result_down = kb.key_down("shift")

        # Проверяем результат нажатия
        assert result_down is True
        mock_keybd_event.assert_called_with(kb._get_code("shift"), 0, 0, 0)

        # Сбрасываем мок для следующего теста
        mock_keybd_event.reset_mock()

        # Отпускаем клавишу
        result_up = kb.key_up("shift")

        # Проверяем результат отпускания
        assert result_up is True
        mock_keybd_event.assert_called_with(kb._get_code("shift"), 0, win32con.KEYEVENTF_KEYUP, 0)

    def test_paste_text(self, keyboard):
        """Тест метода paste_text."""
        kb, _ = keyboard

        with patch("win32clipboard.OpenClipboard") as mock_open, patch(
            "win32clipboard.EmptyClipboard"
        ) as mock_empty, patch("win32clipboard.SetClipboardText") as mock_set, patch(
            "win32clipboard.CloseClipboard"
        ) as mock_close, patch.object(
            kb, "press_keys"
        ) as mock_press_keys:
            # Вставляем текст
            result = kb.paste_text("Test paste")

            # Проверяем результат
            assert result is True

            # Проверяем работу с буфером обмена
            mock_open.assert_called_once()
            mock_empty.assert_called_once()
            mock_set.assert_called_once()
            mock_close.assert_called_once()

            # Проверяем нажатие Ctrl+V
            mock_press_keys.assert_called_once_with(["ctrl", "v"])

    def test_special_methods(self, keyboard):
        """Тест специальных методов press_enter и press_ctrl_c."""
        kb, _ = keyboard

        with patch.object(kb, "press_key") as mock_press_key, patch.object(
            kb, "press_keys"
        ) as mock_press_keys:
            # Нажимаем Enter
            result_enter = kb.press_enter()

            # Проверяем результат
            assert result_enter is True
            mock_press_key.assert_called_once_with("enter")

            # Нажимаем Ctrl+C
            result_ctrl_c = kb.press_ctrl_c()

            # Проверяем результат
            assert result_ctrl_c is True
            mock_press_keys.assert_called_once_with(["ctrl", "c"])


class TestWindowsMouse:
    """Тесты для Windows-реализации контроллера мыши."""

    @pytest.fixture
    def mouse(self):
        """Создает экземпляр WindowsMouse для тестов."""
        with patch("win32api.SetCursorPos") as mock_set_cursor, patch(
            "win32api.mouse_event"
        ) as mock_mouse_event, patch(
            "win32gui.GetCursorPos", return_value=(100, 100)
        ) as mock_get_cursor:
            mouse = WindowsMouse(human_like=False)
            yield mouse, mock_set_cursor, mock_mouse_event, mock_get_cursor

    def test_inheritance(self):
        """Проверка, что WindowsMouse наследуется от AbstractMouse."""
        assert issubclass(WindowsMouse, AbstractMouse)

    def test_move_to(self, mouse):
        """Тест метода move_to."""
        m, mock_set_cursor, _, _ = mouse

        # Перемещаем курсор на позицию (200, 300)
        result = m.move_to(200, 300)

        # Проверяем результат
        assert result is True
        mock_set_cursor.assert_called_once_with((200, 300))

    def test_move_by(self, mouse):
        """Тест метода move_by."""
        m, mock_set_cursor, _, mock_get_cursor = mouse

        # Текущая позиция - (100, 100)
        # Перемещаем курсор на 50 пикселей вправо и 30 пикселей вниз
        result = m.move_by(50, 30)

        # Проверяем результат
        assert result is True
        mock_get_cursor.assert_called_once()
        mock_set_cursor.assert_called_once_with((150, 130))

    def test_click(self, mouse):
        """Тест метода click."""
        m, _, mock_mouse_event, _ = mouse

        # Выполняем левый клик
        result = m.click()

        # Проверяем результат
        assert result is True

        # Должно быть два вызова: нажатие и отпускание
        assert mock_mouse_event.call_count == 2

        # Проверяем вызовы
        mock_mouse_event.assert_any_call(win32con.MOUSEEVENTF_LEFTDOWN, 0, 0, 0, 0)
        mock_mouse_event.assert_any_call(win32con.MOUSEEVENTF_LEFTUP, 0, 0, 0, 0)

    def test_double_click(self, mouse):
        """Тест метода double_click."""
        m, _, _, _ = mouse

        with patch.object(m, "click") as mock_click:
            # Выполняем двойной клик
            result = m.double_click()

            # Проверяем результат
            assert result is True
            mock_click.assert_called_once_with("left", count=2)

    def test_right_click(self, mouse):
        """Тест метода right_click."""
        m, _, _, _ = mouse

        with patch.object(m, "click") as mock_click:
            # Выполняем правый клик
            result = m.right_click()

            # Проверяем результат
            assert result is True
            mock_click.assert_called_once_with(button="right")

    def test_mouse_down_and_up(self, mouse):
        """Тест методов mouse_down и mouse_up."""
        m, _, mock_mouse_event, _ = mouse

        # Нажимаем левую кнопку мыши
        result_down = m.mouse_down()

        # Проверяем результат
        assert result_down is True
        mock_mouse_event.assert_called_with(win32con.MOUSEEVENTF_LEFTDOWN, 0, 0, 0, 0)

        # Сбрасываем мок для следующего теста
        mock_mouse_event.reset_mock()

        # Отпускаем левую кнопку мыши
        result_up = m.mouse_up()

        # Проверяем результат
        assert result_up is True
        mock_mouse_event.assert_called_with(win32con.MOUSEEVENTF_LEFTUP, 0, 0, 0, 0)

        # Сбрасываем мок для следующего теста
        mock_mouse_event.reset_mock()

        # Проверяем правую кнопку
        result_right = m.mouse_down("right")

        # Проверяем результат
        assert result_right is True
        mock_mouse_event.assert_called_with(win32con.MOUSEEVENTF_RIGHTDOWN, 0, 0, 0, 0)

    def test_drag_to(self, mouse):
        """Тест метода drag_to."""
        m, _, _, _ = mouse

        with patch.object(m, "mouse_down") as mock_down, patch.object(
            m, "move_to"
        ) as mock_move, patch.object(m, "mouse_up") as mock_up, patch("time.sleep") as mock_sleep:
            # Перетаскиваем мышью из текущей позиции в (300, 400)
            result = m.drag_to(300, 400, duration=0.5)

            # Проверяем результат
            assert result is True

            # Проверяем последовательность вызовов
            mock_down.assert_called_once_with("left")
            mock_move.assert_called_once_with(300, 400, duration=0.5)
            mock_sleep.assert_called_once_with(0.1)  # Задержка после перемещения
            mock_up.assert_called_once_with("left")

    def test_scroll(self, mouse):
        """Тест метода scroll."""
        m, _, mock_mouse_event, _ = mouse

        # Прокручиваем колесо вниз на 5 щелчков
        result = m.scroll(5, "down")

        # Проверяем результат
        assert result is True
        mock_mouse_event.assert_called_once_with(
            win32con.MOUSEEVENTF_WHEEL, 0, 0, -5 * m.WHEEL_DELTA, 0
        )

        # Сбрасываем мок для следующего теста
        mock_mouse_event.reset_mock()

        # Прокручиваем колесо вверх на 3 щелчка
        result = m.scroll(3, "up")

        # Проверяем результат
        assert result is True
        mock_mouse_event.assert_called_once_with(
            win32con.MOUSEEVENTF_WHEEL, 0, 0, 3 * m.WHEEL_DELTA, 0
        )

    def test_get_position(self, mouse):
        """Тест метода get_position."""
        m, _, _, mock_get_cursor = mouse

        # Получаем текущую позицию курсора
        position = m.get_position()

        # Проверяем результат
        assert position == (100, 100)
        mock_get_cursor.assert_called_once()

    def test_move_to_element(self, mouse):
        """Тест метода move_to_element."""
        m, _, _, _ = mouse

        with patch.object(m, "move_to") as mock_move:
            # Создаем тестовый элемент
            element = MagicMock()
            element.location = {"x": 100, "y": 200}
            element.size = {"width": 50, "height": 30}

            # Перемещаем курсор к центру элемента с отступом
            result = m.move_to_element(element, offset_x=5, offset_y=10, duration=0.3)

            # Проверяем результат
            assert result is True
            # Должен переместиться к координатам (100 + 50/2 + 5, 200 + 30/2 + 10) = (130, 225)
            mock_move.assert_called_once_with(130, 225, duration=0.3)

    def test_click_element(self, mouse):
        """Тест метода click_element."""
        m, _, _, _ = mouse

        with patch.object(m, "move_to_element") as mock_move, patch.object(
            m, "click"
        ) as mock_click, patch("time.sleep") as mock_sleep:
            # Создаем тестовый элемент
            element = MagicMock()

            # Выполняем клик по элементу
            result = m.click_element(element, button="left", offset_x=5, offset_y=10)

            # Проверяем результат
            assert result is True

            # Проверяем последовательность вызовов
            mock_move.assert_called_once_with(element, offset_x=5, offset_y=10)
            mock_sleep.assert_called_once()  # Должна быть задержка перед кликом
            mock_click.assert_called_once_with(button="left")


class TestWindowsInputIntegration:
    """Интеграционные тесты для WindowsKeyboard и WindowsMouse."""

    @pytest.fixture
    def input_controller(self):
        """Создает InputController с моками клавиатуры и мыши Windows."""
        with patch("win32api.keybd_event"), patch("win32api.SetCursorPos"), patch(
            "win32api.mouse_event"
        ):
            keyboard = WindowsKeyboard(human_like=False)
            mouse = WindowsMouse(human_like=False)

            from core.common.input.base import InputController

            controller = InputController(keyboard, mouse)

            yield controller

    def test_combined_operations(self, input_controller):
        """Тест комбинированных операций клавиатуры и мыши."""
        controller = input_controller

        with patch.object(controller.mouse, "move_to") as mock_move, patch.object(
            controller.mouse, "click"
        ) as mock_click, patch.object(controller.keyboard, "type_text") as mock_type:
            # Выполняем последовательность действий:
            # 1. Перемещаем мышь
            controller.mouse.move_to(100, 200)
            # 2. Кликаем
            controller.mouse.click()
            # 3. Вводим текст
            controller.keyboard.type_text("Hello, world!")

            # Проверяем вызовы
            mock_move.assert_called_once_with(100, 200)
            mock_click.assert_called_once()
            mock_type.assert_called_once_with("Hello, world!")

    def test_human_like_mode_integration(self, input_controller):
        """Тест интеграции человекоподобного режима."""
        controller = input_controller

        # Включаем человекоподобный режим
        controller.set_human_like(True)

        # Проверяем, что режим установлен для обоих контроллеров
        assert controller.keyboard.human_like is True
        assert controller.mouse.human_like is True

        # Отключаем человекоподобный режим
        controller.set_human_like(False)

        # Проверяем, что режим выключен для обоих контроллеров
        assert controller.keyboard.human_like is False
        assert controller.mouse.human_like is False


if __name__ == "__main__":
    pytest.main(["-v", __file__])
