"""
Фабрика для создания контроллеров ввода (устаревшая).
Для совместимости с существующим кодом.
"""

from typing import Union

from core.common.input.factory import get_keyboard, get_mouse
from core.platform.windows.input.keyboard import WindowsKeyboard
from core.platform.windows.input.mouse import WindowsMouse


class InputControllerFactory:
    """
    Фабрика для создания контроллеров ввода.
    Предоставляет методы для создания контроллеров клавиатуры и мыши.

    Примечание: Данный класс устарел. Рекомендуется использовать
    функции из core.common.input.factory вместо этого класса.
    """

    @staticmethod
    def get_keyboard_controller(human_like: bool = True) -> WindowsKeyboard:
        """
        Создает и возвращает контроллер клавиатуры.

        Args:
            human_like (bool, optional): Флаг, указывающий, должен ли контроллер
                                         имитировать человеческое поведение. По умолчанию True.

        Returns:
            WindowsKeyboard: Экземпляр контроллера клавиатуры.
        """
        return get_keyboard(human_like=human_like, new_instance=True)

    @staticmethod
    def get_mouse_controller(human_like: bool = True) -> WindowsMouse:
        """
        Создает и возвращает контроллер мыши.

        Args:
            human_like (bool, optional): Флаг, указывающий, должен ли контроллер
                                         имитировать человеческое поведение. По умолчанию True.

        Returns:
            WindowsMouse: Экземпляр контроллера мыши.
        """
        return get_mouse(human_like=human_like, new_instance=True)

    @staticmethod
    def get_input_controller(
        controller_type: str, human_like: bool = True
    ) -> Union[WindowsKeyboard, WindowsMouse]:
        """
        Создает и возвращает контроллер ввода указанного типа.

        Args:
            controller_type (str): Тип контроллера ('keyboard' или 'mouse').
            human_like (bool, optional): Флаг, указывающий, должен ли контроллер
                                         имитировать человеческое поведение. По умолчанию True.

        Returns:
            Union[WindowsKeyboard, WindowsMouse]: Экземпляр контроллера ввода.

        Raises:
            ValueError: Если указан неизвестный тип контроллера.
        """
        if controller_type.lower() == "keyboard":
            return InputControllerFactory.get_keyboard_controller(human_like)
        elif controller_type.lower() == "mouse":
            return InputControllerFactory.get_mouse_controller(human_like)
        else:
            raise ValueError(f"Unknown controller type: {controller_type}")
