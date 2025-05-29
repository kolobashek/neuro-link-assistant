"""
Тесты для базовых интерфейсов подсистемы ввода.
Проверяют соответствие базовых классов заданным интерфейсам.
"""

import inspect
from abc import ABC


class TestInputBaseInterfaces:
    """Тесты для проверки базовых интерфейсов подсистемы ввода."""

    def test_keyboard_controller_base_exists(self):
        """Проверка существования и структуры базового класса для контроллера клавиатуры."""
        # Импортируем базовый класс
        from core.common.input.base import AbstractKeyboard

        # Проверяем, что это абстрактный класс
        assert issubclass(AbstractKeyboard, ABC)

        # Проверяем наличие необходимых абстрактных методов
        abstract_methods = {
            name
            for name, method in inspect.getmembers(AbstractKeyboard)
            if getattr(method, "__isabstractmethod__", False)
        }

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

        assert required_methods.issubset(abstract_methods), (
            "Не все необходимые абстрактные методы определены. Отсутствуют:"
            f" {required_methods - abstract_methods}"
        )

    def test_mouse_controller_base_exists(self):
        """Проверка существования и структуры базового класса для контроллера мыши."""
        # Импортируем базовый класс
        from core.common.input.base import AbstractMouse

        # Проверяем, что это абстрактный класс
        assert issubclass(AbstractMouse, ABC)

        # Проверяем наличие необходимых абстрактных методов
        abstract_methods = {
            name
            for name, method in inspect.getmembers(AbstractMouse)
            if getattr(method, "__isabstractmethod__", False)
        }

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

        assert required_methods.issubset(abstract_methods), (
            "Не все необходимые абстрактные методы определены. Отсутствуют:"
            f" {required_methods - abstract_methods}"
        )

    def test_input_controller_exists(self):
        """Проверка существования и структуры класса InputController."""
        # Импортируем класс
        from core.common.input.base import AbstractKeyboard, AbstractMouse, InputController

        # Создаем заглушки для клавиатуры и мыши
        keyboard_mock = type(
            "KeyboardMock",
            (AbstractKeyboard,),
            {
                "press_key": lambda self, key: True,
                "press_keys": lambda self, keys: True,
                "key_down": lambda self, key: True,
                "key_up": lambda self, key: True,
                "type_text": lambda self, text, interval=None: True,
                "paste_text": lambda self, text: True,
                "press_enter": lambda self: True,
                "press_ctrl_c": lambda self: True,
            },
        )()

        mouse_mock = type(
            "MouseMock",
            (AbstractMouse,),
            {
                "move_to": lambda self, x, y, duration=None: True,
                "move_by": lambda self, dx, dy, duration=None: True,
                "click": lambda self, button="left", count=1: True,
                "double_click": lambda self, button="left": True,
                "right_click": lambda self: True,
                "mouse_down": lambda self, button="left": True,
                "mouse_up": lambda self, button="left": True,
                "drag_to": lambda self, x, y, button="left", duration=None: True,
                "scroll": lambda self, clicks, direction="down": True,
                "get_position": lambda self: (0, 0),
                "move_to_element": (
                    lambda self, element, offset_x=0, offset_y=0, duration=None: True
                ),
                "click_element": lambda self, element, button="left", offset_x=0, offset_y=0: True,
            },
        )()

        # Создаем экземпляр с None вместо реальных объектов
        obj = InputController(keyboard_mock, mouse_mock)

        assert hasattr(obj, "keyboard"), "Отсутствует атрибут keyboard"
        assert hasattr(obj, "mouse"), "Отсутствует атрибут mouse"
        assert hasattr(obj, "is_human_like"), "Отсутствует метод is_human_like"
        assert hasattr(obj, "set_human_like"), "Отсутствует метод set_human_like"

    def test_input_controller_integration(self):
        """Проверка корректности интеграции контроллеров ввода."""
        from unittest.mock import MagicMock

        from core.common.input.base import AbstractKeyboard, AbstractMouse, InputController

        # Создаем моки для контроллеров

        class KeyboardMock(AbstractKeyboard):
            def press_key(self, key):
                return True

            def press_keys(self, keys):
                return True

            def key_down(self, key):
                return True

            def key_up(self, key):
                return True

            def type_text(self, text, interval=None):
                return True

            def paste_text(self, text):
                return True

            def press_enter(self):
                return True

            def press_ctrl_c(self):
                return True

        class MouseMock(AbstractMouse):
            def move_to(self, x, y, duration=None):
                return True

            def move_by(self, dx, dy, duration=None):
                return True

            def click(self, button="left", count=1):
                return True

            def double_click(self, button="left"):
                return True

            def right_click(self):
                return True

            def mouse_down(self, button="left"):
                return True

            def mouse_up(self, button="left"):
                return True

            def drag_to(self, x, y, button="left", duration=None):
                return True

            def scroll(self, clicks, direction="down"):
                return True

            def get_position(self):
                return (0, 0)

            def move_to_element(self, element, offset_x=0, offset_y=0, duration=None):
                return True

            def click_element(self, element, button="left", offset_x=0, offset_y=0):
                return True

        mock_keyboard = KeyboardMock()
        mock_mouse = MouseMock()

        # Добавляем возможность отслеживать вызовы
        mock_keyboard.type_text = MagicMock(return_value=True)
        mock_keyboard.press_key = MagicMock(return_value=True)
        mock_mouse.click = MagicMock(return_value=True)

        # Создаем объект InputController
        input_controller = InputController(mock_keyboard, mock_mouse)

        # Проверяем, что атрибуты установлены правильно
        assert input_controller.keyboard is mock_keyboard
        assert input_controller.mouse is mock_mouse

        # Проверяем, что методы keyboard вызываются через атрибут
        input_controller.keyboard.type_text("test")
        mock_keyboard.type_text.assert_called_once_with("test")

        # Проверяем, что методы mouse вызываются через атрибут
        input_controller.mouse.click()
        mock_mouse.click.assert_called_once()

        # Проверяем методы управления human_like режимом
        input_controller.set_human_like(True)
        assert mock_keyboard.human_like is True
        assert mock_mouse.human_like is True

        assert input_controller.is_human_like() is True
