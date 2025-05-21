"""
Реестр контроллеров ввода.
"""

from typing import Any, Dict, Optional, Type

from core.common.input.base import AbstractKeyboard, AbstractMouse

# Глобальный экземпляр реестра для использования в качестве синглтона
_instance = None


class InputRegistry:
    """
    Реестр контроллеров ввода.
    Хранит информацию о доступных классах контроллеров клавиатуры и мыши.
    """

    def __new__(cls, auto_register=True):
        """
        Создает единственный экземпляр класса (синглтон).

        Args:
            auto_register (bool): Если True, автоматически регистрирует стандартные контроллеры.
        """
        global _instance
        if _instance is None:
            _instance = super(InputRegistry, cls).__new__(cls)
            _instance._initialized = False
        return _instance

    def __init__(self, auto_register=True):
        """
        Инициализирует реестр контроллеров.

        Args:
            auto_register (bool): Если True, автоматически регистрирует стандартные контроллеры.
        """
        if getattr(self, "_initialized", False):
            return

        self._keyboard_classes: Dict[str, Type[AbstractKeyboard]] = {}
        self._mouse_classes: Dict[str, Type[AbstractMouse]] = {}
        self._initialized = True

        # Регистрируем стандартные контроллеры для текущей платформы если запрошено
        if auto_register:
            self._register_platform_controllers()

    def _register_platform_controllers(self):
        """Регистрирует стандартные контроллеры для текущей платформы."""
        import platform

        system = platform.system().lower()

        if system == "windows":
            try:
                from core.platform.windows.input.keyboard import WindowsKeyboard
                from core.platform.windows.input.mouse import WindowsMouse

                self.register_keyboard("windows", WindowsKeyboard)
                self.register_mouse("windows", WindowsMouse)
            except ImportError:
                # Логируем ошибку, но продолжаем работу
                import logging

                logging.warning("Не удалось зарегистрировать Windows-контроллеры ввода")
        # В будущем добавить поддержку других платформ (Linux, MacOS)

    def register_keyboard(self, name: str, keyboard_class: Any) -> bool:
        """
        Регистрирует класс контроллера клавиатуры.

        Args:
            name: Уникальное имя контроллера.
            keyboard_class: Класс контроллера клавиатуры.

        Returns:
            True если регистрация успешна, иначе False.
        """
        # Проверяем, что класс наследуется от AbstractKeyboard
        if not isinstance(keyboard_class, type) or not issubclass(keyboard_class, AbstractKeyboard):
            return False
        if name in self._keyboard_classes:
            return False
        self._keyboard_classes[name] = keyboard_class
        return True

    def register_mouse(self, name: str, mouse_class: Any) -> bool:
        """
        Регистрирует класс контроллера мыши.

        Args:
            name: Уникальное имя контроллера.
            mouse_class: Класс контроллера мыши.

        Returns:
            True если регистрация успешна, иначе False.
        """
        # Проверяем, что класс наследуется от AbstractMouse
        if not isinstance(mouse_class, type) or not issubclass(mouse_class, AbstractMouse):
            return False

        if name in self._mouse_classes:
            return False
        self._mouse_classes[name] = mouse_class
        return True

    def get_keyboard(self, name: str) -> Optional[Type[AbstractKeyboard]]:
        """
        Возвращает класс контроллера клавиатуры по имени.

        Args:
            name: Имя контроллера.

        Returns:
            Класс контроллера или None, если не найден.
        """
        return self._keyboard_classes.get(name)

    def get_mouse(self, name: str) -> Optional[Type[AbstractMouse]]:
        """
        Возвращает класс контроллера мыши по имени.

        Args:
            name: Имя контроллера.

        Returns:
            Класс контроллера или None, если не найден.
        """
        return self._mouse_classes.get(name)

    def get_keyboard_instance(self, name: str, human_like=True) -> Optional[AbstractKeyboard]:
        """
        Возвращает экземпляр контроллера клавиатуры по имени.

        Args:
            name: Имя контроллера.
            human_like: Признак человекоподобного поведения.

        Returns:
            Экземпляр контроллера или None, если не найден.
        """
        keyboard_class = self.get_keyboard(name)
        if keyboard_class:
            return keyboard_class(human_like=human_like)
        return None

    def get_mouse_instance(self, name: str, human_like=True) -> Optional[AbstractMouse]:
        """
        Возвращает экземпляр контроллера мыши по имени.

        Args:
            name: Имя контроллера.
            human_like: Признак человекоподобного поведения.

        Returns:
            Экземпляр контроллера или None, если не найден.
        """
        mouse_class = self.get_mouse(name)
        if mouse_class:
            return mouse_class(human_like=human_like)
        return None

    @classmethod
    def reset_instance(cls):
        """Сбрасывает глобальный экземпляр реестра (для тестирования)."""
        global _instance
        _instance = None

    @classmethod
    def get_instance_direct(cls):
        """Возвращает текущий экземпляр синглтона, если он существует, иначе None.
        Для внутреннего использования и тестирования."""
        return _instance
