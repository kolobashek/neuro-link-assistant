"""
Реестр контроллеров ввода.
"""

from typing import Dict, Optional, Type

from core.common.input.base import AbstractKeyboard, AbstractMouse

# Глобальный экземпляр реестра для использования в качестве синглтона
_instance = None


class InputRegistry:
    """
    Реестр контроллеров ввода.
    Хранит информацию о доступных классах контроллеров клавиатуры и мыши.
    """

    def __new__(cls):
        """Создает единственный экземпляр класса (синглтон)."""
        global _instance
        if _instance is None:
            _instance = super(InputRegistry, cls).__new__(cls)
            _instance._initialized = False
        return _instance

    def __init__(self):
        """Инициализирует реестр контроллеров."""
        if getattr(self, "_initialized", False):
            return

        self._keyboard_classes: Dict[str, Type[AbstractKeyboard]] = {}
        self._mouse_classes: Dict[str, Type[AbstractMouse]] = {}
        self._initialized = True

        # Регистрируем стандартные контроллеры для текущей платформы
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

    def register_keyboard(self, name: str, keyboard_class: Type[AbstractKeyboard]) -> bool:
        """
        Регистрирует класс контроллера клавиатуры.

        Args:
            name: Уникальное имя контроллера.
            keyboard_class: Класс контроллера клавиатуры.

        Returns:
            True если регистрация успешна, иначе False.
        """
        # Проверяем, что класс наследуется от AbstractKeyboard
        if not issubclass(keyboard_class, AbstractKeyboard):
            return False
        if name in self._keyboard_classes:
            return False
        self._keyboard_classes[name] = keyboard_class
        return True

    def register_mouse(self, name: str, mouse_class: Type[AbstractMouse]) -> bool:
        """
        Регистрирует класс контроллера мыши.

        Args:
            name: Уникальное имя контроллера.
            mouse_class: Класс контроллера мыши.

        Returns:
            True если регистрация успешна, иначе False.
        """
        # Проверяем, что класс наследуется от AbstractMouse
        if not issubclass(mouse_class, AbstractMouse):
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
