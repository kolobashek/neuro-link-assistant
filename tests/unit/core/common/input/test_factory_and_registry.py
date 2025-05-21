"""
Тесты для фабрики и реестра контроллеров ввода.
"""

from unittest.mock import MagicMock, patch

import pytest

from core.common.input.base import AbstractKeyboard, AbstractMouse
from core.common.input.factory import get_input_controller, get_keyboard, get_mouse
from core.common.input.registry import InputRegistry


class TestInputFactory:
    """Тесты для фабрики контроллеров ввода."""

    def test_get_keyboard_caching(self):
        """Тест кэширования экземпляров клавиатуры."""
        # Патчим реестр контроллеров ввода
        with patch("core.common.input.factory.registry") as mock_registry, patch(
            "platform.system", return_value="Windows"
        ):

            # Создаем моки для класса клавиатуры
            mock_keyboard_class = MagicMock()
            mock_keyboard = MagicMock()
            mock_keyboard_class.return_value = mock_keyboard

            # Настраиваем реестр для возврата моков
            mock_registry.get_keyboard.return_value = mock_keyboard_class

            # Первый вызов должен создать новый экземпляр
            kb1 = get_keyboard(human_like=True)
            assert kb1 == mock_keyboard
            mock_keyboard_class.assert_called_once_with(human_like=True)

            # Сбрасываем счетчик вызовов
            mock_keyboard_class.reset_mock()

            # Второй вызов должен вернуть тот же экземпляр (кэширование)
            kb2 = get_keyboard(human_like=True)
            assert kb2 == mock_keyboard
            mock_keyboard_class.assert_not_called()  # Новый экземпляр не создается

            # Третий вызов с new_instance=True должен создать новый экземпляр
            kb3 = get_keyboard(human_like=True, new_instance=True)
            assert kb3 == mock_keyboard
            mock_keyboard_class.assert_called_once_with(human_like=True)

    def test_get_mouse_caching(self):
        """Тест кэширования экземпляров мыши."""
        # Патчим реестр контроллеров ввода
        with patch("core.common.input.factory.registry") as mock_registry, patch(
            "platform.system", return_value="Windows"
        ):

            # Создаем моки для класса мыши
            mock_mouse_class = MagicMock()
            mock_mouse = MagicMock()
            mock_mouse_class.return_value = mock_mouse

            # Настраиваем реестр для возврата моков
            mock_registry.get_mouse.return_value = mock_mouse_class

            # Первый вызов должен создать новый экземпляр
            mouse1 = get_mouse(human_like=False)
            assert mouse1 == mock_mouse
            mock_mouse_class.assert_called_once_with(human_like=False)

            # Сбрасываем счетчик вызовов
            mock_mouse_class.reset_mock()

            # Второй вызов должен вернуть тот же экземпляр (кэширование)
            mouse2 = get_mouse(human_like=False)
            assert mouse2 == mock_mouse
            mock_mouse_class.assert_not_called()  # Новый экземпляр не создается

            # Третий вызов с new_instance=True должен создать новый экземпляр
            mouse3 = get_mouse(human_like=False, new_instance=True)
            assert mouse3 == mock_mouse
            mock_mouse_class.assert_called_once_with(human_like=False)

    def test_get_input_controller_integration(self):
        """Интеграционный тест получения комбинированного контроллера ввода."""
        with patch("platform.system", return_value="Windows"), patch(
            "core.common.input.factory._keyboard_instances", {}
        ), patch("core.common.input.factory._mouse_instances", {}), patch(
            "core.platform.windows.input.keyboard.WindowsKeyboard"
        ) as mock_keyboard_class, patch(
            "core.platform.windows.input.mouse.WindowsMouse"
        ) as mock_mouse_class, patch(
            "core.common.input.base.InputController"
        ) as mock_controller_class:

            # Создаем моки для экземпляров
            mock_keyboard = MagicMock()
            mock_mouse = MagicMock()
            mock_controller = MagicMock()

            mock_keyboard_class.return_value = mock_keyboard
            mock_mouse_class.return_value = mock_mouse
            mock_controller_class.return_value = mock_controller

            # Получаем контроллер ввода
            controller = get_input_controller(human_like=True)

            # Проверяем, что были созданы экземпляры клавиатуры и мыши
            mock_keyboard_class.assert_called_once_with(human_like=True)
            mock_mouse_class.assert_called_once_with(human_like=True)

            # Проверяем, что был создан InputController с правильными аргументами
            mock_controller_class.assert_called_once_with(mock_keyboard, mock_mouse)

            # Проверяем, что вернулся правильный контроллер
            assert controller == mock_controller


class TestInputRegistry:
    """Тесты для реестра контроллеров ввода."""

    def test_singleton_property(self):
        """
        Тест, что InputRegistry - синглтон
        (или что фабрика всегда возвращает один и тот же экземпляр).
        """
        # Получаем экземпляр реестра
        # Получаем еще один экземпляр
        from core.common.input.factory import registry as registry1
        from core.common.input.factory import registry as registry2

        # Проверяем, что это один и тот же объект
        assert registry1 is registry2

        # Проверяем, что при создании нового экземпляра он тоже будет тем же
        registry3 = InputRegistry()
        assert registry1 is registry3

    def test_initial_state(self):
        """Тест начального состояния реестра."""
        # Создаем новый реестр
        registry = InputRegistry()

        # Проверяем, что в нем пусто
        assert not registry._keyboard_classes  # Пустой словарь клавиатур
        assert not registry._mouse_classes  # Пустой словарь мышей

    def test_register_invalid_class(self):
        """Тест регистрации некорректного класса."""
        registry = InputRegistry()

        # Создаем класс, который не наследуется от AbstractKeyboard
        class InvalidKeyboard:
            pass

        # Попытка регистрации должна вернуть False
        result = registry.register_keyboard("invalid", InvalidKeyboard)
        assert result is False

        # Класс не должен быть добавлен в реестр
        assert "invalid" not in registry._keyboard_classes

        # Проверяем то же самое для мыши
        result = registry.register_mouse("invalid", InvalidKeyboard)
        assert result is False
        assert "invalid" not in registry._mouse_classes

    def test_default_registrations(self):
        """
        Тест, что при создании реестра регистрируются
        стандартные классы для текущей платформы.
        """
        # Создаем чистый реестр с перезагрузкой модуля
        with patch.dict("sys.modules", {"core.common.input.registry": None}):
            # Перезагружаем модуль реестра для сброса регистраций
            import importlib

            import core.common.input.registry

            importlib.reload(core.common.input.registry)

            # Патчим определение платформы
            with patch("platform.system", return_value="Windows"):
                # Проверяем, что WindowsKeyboard и WindowsMouse зарегистрированы
                from core.common.input.registry import InputRegistry

                registry = InputRegistry()

                # Получаем классы для Windows
                windows_keyboard = registry.get_keyboard("windows")
                windows_mouse = registry.get_mouse("windows")

                # Проверяем, что классы есть в реестре и они правильные
                from core.platform.windows.input.keyboard import WindowsKeyboard
                from core.platform.windows.input.mouse import WindowsMouse

                assert windows_keyboard is WindowsKeyboard
                assert windows_mouse is WindowsMouse

    def test_platform_specific_registrations(self):
        """Тест регистрации контроллеров для разных платформ."""
        registry = InputRegistry()

        # Создаем мок-классы для разных платформ
        class LinuxKeyboard(AbstractKeyboard):
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

        class MacMouse(AbstractMouse):
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

        # Регистрируем классы для разных платформ
        registry.register_keyboard("linux", LinuxKeyboard)
        registry.register_mouse("mac", MacMouse)

        # Проверяем, что классы зарегистрированы
        assert registry.get_keyboard("linux") is LinuxKeyboard
        assert registry.get_mouse("mac") is MacMouse

        # Регистрируем класс повторно и проверяем, что вернется False
        result = registry.register_keyboard("linux", LinuxKeyboard)
        assert result is False


if __name__ == "__main__":
    pytest.main(["-v", __file__])
