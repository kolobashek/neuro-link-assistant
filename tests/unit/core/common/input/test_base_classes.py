"""
Тесты для базовых классов подсистемы ввода.
Проверяет корректность интерфейсов и базовую функциональность.
"""

import inspect
from typing import List, Optional, Tuple
from unittest.mock import MagicMock, patch

import pytest

from core.common.input.base import AbstractKeyboard, AbstractMouse, InputController


class TestKeyboardInterface:
    """Тесты для проверки интерфейса клавиатуры."""

    def test_abstract_keyboard_methods(self):
        """Проверка наличия всех необходимых абстрактных методов."""
        # Получаем все абстрактные методы
        abstract_methods = {
            name
            for name, method in inspect.getmembers(AbstractKeyboard)
            if getattr(method, "__isabstractmethod__", False)
        }

        # Проверяем наличие всех необходимых методов
        required_methods = {
            "press_key",
            "press_keys",
            "key_down",
            "key_up",
            "type_text",
            "paste_text",
            "press_enter",
            "press_ctrl_c",
        }

        # Проверяем, что все требуемые методы являются абстрактными
        assert required_methods.issubset(abstract_methods), (
            f"Не все необходимые методы определены как абстрактные. "
            f"Отсутствуют: {required_methods - abstract_methods}"
        )

    def test_keyboard_implementation_compatibility(self):
        """
        Тест для проверки, что конкретная реализация клавиатуры
        может быть успешно создана и соответствует интерфейсу.
        """

        # Создаем заглушку, реализующую AbstractKeyboard
        class TestKeyboard(AbstractKeyboard):
            def press_key(self, key: str) -> bool:
                return True

            def press_keys(self, keys: List[str]) -> bool:
                return True

            def key_down(self, key: str) -> bool:
                return True

            def key_up(self, key: str) -> bool:
                return True

            def type_text(self, text: str, interval: Optional[float] = None) -> bool:
                return True

            def paste_text(self, text: str) -> bool:
                return True

            def press_enter(self) -> bool:
                return True

            def press_ctrl_c(self) -> bool:
                return True

        # Проверяем, что можно создать экземпляр
        keyboard = TestKeyboard()
        assert isinstance(keyboard, AbstractKeyboard)

        # Проверяем, что все методы доступны и возвращают ожидаемый результат
        assert keyboard.press_key("a") is True
        assert keyboard.press_keys(["ctrl", "c"]) is True
        assert keyboard.key_down("shift") is True
        assert keyboard.key_up("shift") is True
        assert keyboard.type_text("Hello, world!") is True
        assert keyboard.paste_text("Pasted text") is True
        assert keyboard.press_enter() is True
        assert keyboard.press_ctrl_c() is True


class TestMouseInterface:
    """Тесты для проверки интерфейса мыши."""

    def test_abstract_mouse_methods(self):
        """Проверка наличия всех необходимых абстрактных методов."""
        # Получаем все абстрактные методы
        abstract_methods = {
            name
            for name, method in inspect.getmembers(AbstractMouse)
            if getattr(method, "__isabstractmethod__", False)
        }

        # Проверяем наличие всех необходимых методов
        required_methods = {
            "move_to",
            "move_by",
            "click",
            "double_click",
            "right_click",
            "mouse_down",
            "mouse_up",
            "drag_to",
            "scroll",
            "get_position",
            "move_to_element",
            "click_element",
        }

        # Проверяем, что все требуемые методы являются абстрактными
        assert required_methods.issubset(abstract_methods), (
            f"Не все необходимые методы определены как абстрактные. "
            f"Отсутствуют: {required_methods - abstract_methods}"
        )

    def test_mouse_implementation_compatibility(self):
        """
        Тест для проверки, что конкретная реализация мыши
        может быть успешно создана и соответствует интерфейсу.
        """

        # Создаем заглушку, реализующую AbstractMouse
        class TestMouse(AbstractMouse):
            def move_to(self, x: int, y: int, duration: Optional[float] = None) -> bool:
                return True

            def move_by(self, dx: int, dy: int, duration: Optional[float] = None) -> bool:
                return True

            def click(self, button: str = "left", count: int = 1) -> bool:
                return True

            def double_click(self, button: str = "left") -> bool:
                return True

            def right_click(self) -> bool:
                return True

            def mouse_down(self, button: str = "left") -> bool:
                return True

            def mouse_up(self, button: str = "left") -> bool:
                return True

            def drag_to(
                self, x: int, y: int, button: str = "left", duration: Optional[float] = None
            ) -> bool:
                return True

            def scroll(self, clicks: int, direction: str = "down") -> bool:
                return True

            def get_position(self) -> Tuple[int, int]:
                return (100, 200)

            def move_to_element(
                self,
                element,
                offset_x: int = 0,
                offset_y: int = 0,
                duration: Optional[float] = None,
            ) -> bool:
                return True

            def click_element(
                self, element, button: str = "left", offset_x: int = 0, offset_y: int = 0
            ) -> bool:
                return True

        # Проверяем, что можно создать экземпляр
        mouse = TestMouse()
        assert isinstance(mouse, AbstractMouse)

        # Проверяем, что все методы доступны и возвращают ожидаемый результат
        assert mouse.move_to(100, 200) is True
        assert mouse.move_by(10, -10) is True
        assert mouse.click() is True
        assert mouse.double_click() is True
        assert mouse.right_click() is True
        assert mouse.mouse_down() is True
        assert mouse.mouse_up() is True
        assert mouse.drag_to(150, 250) is True
        assert mouse.scroll(5, "down") is True
        assert mouse.get_position() == (100, 200)
        assert mouse.move_to_element(MagicMock()) is True
        assert mouse.click_element(MagicMock()) is True


class TestInputController:
    """Тесты для комбинированного контроллера ввода."""

    def test_input_controller_initialization(self):
        """Проверка правильной инициализации InputController."""
        # Создаем моки для клавиатуры и мыши
        mock_keyboard = MagicMock(spec=AbstractKeyboard)
        mock_mouse = MagicMock(spec=AbstractMouse)

        # Создаем InputController
        controller = InputController(mock_keyboard, mock_mouse)

        # Проверяем, что контроллер правильно инициализирован
        assert controller.keyboard is mock_keyboard
        assert controller.mouse is mock_mouse

    def test_input_controller_keyboard_delegation(self):
        """Проверка, что InputController правильно делегирует методы клавиатуры."""
        mock_keyboard = MagicMock(spec=AbstractKeyboard)
        mock_mouse = MagicMock(spec=AbstractMouse)

        controller = InputController(mock_keyboard, mock_mouse)

        # Проверяем делегирование методов клавиатуры
        controller.keyboard.type_text("Test text")
        mock_keyboard.type_text.assert_called_once_with("Test text")

        controller.keyboard.press_key("Enter")
        mock_keyboard.press_key.assert_called_once_with("Enter")

        controller.keyboard.press_keys(["Ctrl", "C"])
        mock_keyboard.press_keys.assert_called_once_with(["Ctrl", "C"])

    def test_input_controller_mouse_delegation(self):
        """Проверка, что InputController правильно делегирует методы мыши."""
        mock_keyboard = MagicMock(spec=AbstractKeyboard)
        mock_mouse = MagicMock(spec=AbstractMouse)

        controller = InputController(mock_keyboard, mock_mouse)

        # Проверяем делегирование методов мыши
        controller.mouse.move_to(100, 200)
        mock_mouse.move_to.assert_called_once_with(100, 200)

        controller.mouse.click("left", 2)
        mock_mouse.click.assert_called_once_with("left", 2)

        controller.mouse.drag_to(300, 400)
        mock_mouse.drag_to.assert_called_once_with(300, 400)

    def test_human_like_mode(self):
        """Проверка функциональности человекоподобного режима."""
        mock_keyboard = MagicMock(spec=AbstractKeyboard)
        mock_mouse = MagicMock(spec=AbstractMouse)

        # Устанавливаем атрибуты human_like для моков
        mock_keyboard.human_like = False
        mock_mouse.human_like = False

        controller = InputController(mock_keyboard, mock_mouse)

        # Проверяем изначальное состояние
        assert not controller.is_human_like()

        # Включаем человекоподобный режим
        controller.set_human_like(True)

        # Проверяем, что атрибуты изменились
        assert controller.is_human_like()
        assert mock_keyboard.human_like is True
        assert mock_mouse.human_like is True

        # Отключаем человекоподобный режим
        controller.set_human_like(False)

        # Проверяем, что атрибуты изменились обратно
        assert not controller.is_human_like()
        assert mock_keyboard.human_like is False
        assert mock_mouse.human_like is False


class TestInputFactory:
    """Тесты для фабрики контроллеров ввода."""

    def test_get_keyboard(self):
        """Тест создания контроллера клавиатуры."""
        # Импортируем фабрику
        from core.common.input.factory import get_keyboard

        # Мокаем подходящий класс клавиатуры для текущей платформы
        with patch("platform.system", return_value="Windows"), patch(
            "core.common.input.registry.InputRegistry._register_platform_controllers"
        ), patch(
            "core.common.input.registry.InputRegistry.get_keyboard"
        ) as mock_get_keyboard_class:

            # Создаем мок для WindowsKeyboard
            mock_keyboard_class = MagicMock()
            mock_keyboard = MagicMock()
            mock_keyboard_class.return_value = mock_keyboard
            mock_get_keyboard_class.return_value = mock_keyboard_class

            # Получаем клавиатуру с человекоподобным режимом
            keyboard = get_keyboard(human_like=True)

            # Проверяем, что WindowsKeyboard был вызван с правильными параметрами
            mock_keyboard_class.assert_called_once_with(human_like=True)
            assert keyboard == mock_keyboard

    def test_get_mouse(self):
        """Тест создания контроллера мыши."""
        # Импортируем фабрику
        from core.common.input.factory import get_mouse

        # Мокаем подходящий класс мыши для текущей платформы
        with patch("platform.system", return_value="Windows"), patch(
            "core.common.input.registry.InputRegistry._register_platform_controllers"
        ), patch("core.common.input.registry.InputRegistry.get_mouse") as mock_get_mouse_class:

            # Создаем мок для WindowsMouse
            mock_mouse_class = MagicMock()
            mock_mouse = MagicMock()
            mock_mouse_class.return_value = mock_mouse
            mock_get_mouse_class.return_value = mock_mouse_class

            # Получаем мышь с человекоподобным режимом
            mouse = get_mouse(human_like=True)

            # Проверяем, что WindowsMouse был вызван с правильными параметрами
            mock_mouse_class.assert_called_once_with(human_like=True)
            assert mouse == mock_mouse

    def test_get_input_controller(self):
        """Тест получения контроллера ввода"""
        # ВАЖНО: патчим конкретное использование InputController в factory.py
        with patch(
            "core.common.input.factory.InputController"
        ) as mock_input_controller_class, patch("platform.system", return_value="Windows"), patch(
            "core.common.input.factory.get_keyboard"
        ) as mock_get_keyboard, patch(
            "core.common.input.factory.get_mouse"
        ) as mock_get_mouse:

            # Создаем мок-объекты для контроллеров
            mock_keyboard = MagicMock()
            mock_mouse = MagicMock()
            mock_get_keyboard.return_value = mock_keyboard
            mock_get_mouse.return_value = mock_mouse

            # Создаем мок-объект для InputController
            mock_input_controller = MagicMock()
            mock_input_controller_class.return_value = mock_input_controller

            # Импортируем функцию get_input_controller
            from core.common.input.factory import get_input_controller

            # Вызываем функцию
            controller = get_input_controller()

            # Проверяем вызовы
            mock_get_keyboard.assert_called_once_with(True, None, False)
            mock_get_mouse.assert_called_once_with(True, None, False)

            mock_input_controller_class.assert_called_once_with(mock_keyboard, mock_mouse)
            assert controller == mock_input_controller


class TestInputRegistry:
    """Тесты для реестра контроллеров ввода."""

    def test_register_keyboard(self):
        """Тест регистрации контроллера клавиатуры."""
        from core.common.input.registry import InputRegistry

        # Создаем реестр
        registry = InputRegistry()

        # Создаем тестовый класс клавиатуры
        class TestKeyboard(AbstractKeyboard):
            def press_key(self, key: str) -> bool:
                return True

            def press_keys(self, keys: List[str]) -> bool:
                return True

            def key_down(self, key: str) -> bool:
                return True

            def key_up(self, key: str) -> bool:
                return True

            def type_text(self, text: str, interval: Optional[float] = None) -> bool:
                return True

            def paste_text(self, text: str) -> bool:
                return True

            def press_enter(self) -> bool:
                return True

            def press_ctrl_c(self) -> bool:
                return True

        # Регистрируем класс клавиатуры
        result = registry.register_keyboard("test_keyboard", TestKeyboard)

        # Проверяем, что регистрация прошла успешно
        assert result is True

        # Проверяем, что класс можно получить из реестра
        retrieved_class = registry.get_keyboard("test_keyboard")
        assert retrieved_class is TestKeyboard

        # Проверяем, что нельзя зарегистрировать класс с тем же именем повторно
        result = registry.register_keyboard("test_keyboard", TestKeyboard)
        assert result is False

    def test_register_mouse(self):
        """Тест регистрации контроллера мыши."""
        from core.common.input.registry import InputRegistry

        # Создаем реестр
        registry = InputRegistry()

        # Создаем тестовый класс мыши
        class TestMouse(AbstractMouse):
            def move_to(self, x: int, y: int, duration: Optional[float] = None) -> bool:
                return True

            def move_by(self, dx: int, dy: int, duration: Optional[float] = None) -> bool:
                return True

            def click(self, button: str = "left", count: int = 1) -> bool:
                return True

            def double_click(self, button: str = "left") -> bool:
                return True

            def right_click(self) -> bool:
                return True

            def mouse_down(self, button: str = "left") -> bool:
                return True

            def mouse_up(self, button: str = "left") -> bool:
                return True

            def drag_to(
                self, x: int, y: int, button: str = "left", duration: Optional[float] = None
            ) -> bool:
                return True

            def scroll(self, clicks: int, direction: str = "down") -> bool:
                return True

            def get_position(self) -> Tuple[int, int]:
                return (100, 200)

            def move_to_element(
                self,
                element,
                offset_x: int = 0,
                offset_y: int = 0,
                duration: Optional[float] = None,
            ) -> bool:
                return True

            def click_element(
                self, element, button: str = "left", offset_x: int = 0, offset_y: int = 0
            ) -> bool:
                return True

        # Регистрируем класс мыши
        result = registry.register_mouse("test_mouse", TestMouse)

        # Проверяем, что регистрация прошла успешно
        assert result is True

        # Проверяем, что класс можно получить из реестра
        retrieved_class = registry.get_mouse("test_mouse")
        assert retrieved_class is TestMouse

        # Проверяем, что нельзя зарегистрировать класс с тем же именем повторно
        result = registry.register_mouse("test_mouse", TestMouse)
        assert result is False

    def test_nonexistent_controller(self):
        """Тест получения несуществующего контроллера."""
        from core.common.input.registry import InputRegistry

        # Создаем реестр
        registry = InputRegistry()

        # Проверяем, что получение несуществующего контроллера возвращает None
        assert registry.get_keyboard("nonexistent") is None
        assert registry.get_mouse("nonexistent") is None


if __name__ == "__main__":
    pytest.main(["-v", __file__])
