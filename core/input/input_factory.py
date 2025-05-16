from typing import Union

from core.input.keyboard_controller import KeyboardController
from core.input.mouse_controller import MouseController


class InputControllerFactory:
    """
    Фабрика для создания контроллеров ввода.
    Предоставляет методы для создания контроллеров клавиатуры и мыши.
    """

    @staticmethod
    def get_keyboard_controller(human_like: bool = True) -> KeyboardController:
        """
        Создает и возвращает контроллер клавиатуры.

        Args:
            human_like (bool, optional): Флаг, указывающий, должен ли контроллер
                                         имитировать человеческое поведение. По умолчанию True.

        Returns:
            KeyboardController: Экземпляр контроллера клавиатуры.
        """
        return KeyboardController(human_like=human_like)

    @staticmethod
    def get_mouse_controller(human_like: bool = True) -> MouseController:
        """
        Создает и возвращает контроллер мыши.

        Args:
            human_like (bool, optional): Флаг, указывающий, должен ли контроллер
                                         имитировать человеческое поведение. По умолчанию True.

        Returns:
            MouseController: Экземпляр контроллера мыши.
        """
        return MouseController(human_like=human_like)

    @staticmethod
    def get_input_controller(
        controller_type: str, human_like: bool = True
    ) -> Union[KeyboardController, MouseController]:
        """
        Создает и возвращает контроллер ввода указанного типа.

        Args:
            controller_type (str): Тип контроллера ('keyboard' или 'mouse').
            human_like (bool, optional): Флаг, указывающий, должен ли контроллер
                                         имитировать человеческое поведение. По умолчанию True.

        Returns:
            Union[KeyboardController, MouseController]: Экземпляр контроллера ввода.

        Raises:
            ValueError: Если указан неизвестный тип контроллера.
        """
        if controller_type.lower() == "keyboard":
            return InputControllerFactory.get_keyboard_controller(human_like)
        elif controller_type.lower() == "mouse":
            return InputControllerFactory.get_mouse_controller(human_like)
        else:
            raise ValueError(f"Unknown controller type: {controller_type}")
