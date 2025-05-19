"""
Абстрактные базовые классы для системы ввода.
Предоставляет интерфейсы для клавиатуры и мыши.
"""

from abc import ABC, abstractmethod
from typing import List, Optional, Tuple


class AbstractKeyboard(ABC):
    """Абстрактный класс для клавиатуры"""

    @abstractmethod
    def press_key(self, key: str) -> bool:
        """
        Нажимает клавишу и сразу отпускает её.

        Args:
            key (str): Клавиша для нажатия.

        Returns:
            bool: True если успешно, иначе False.
        """
        pass

    @abstractmethod
    def press_keys(self, keys: List[str]) -> bool:
        """
        Нажимает комбинацию клавиш.

        Args:
            keys (List[str]): Список клавиш для нажатия.

        Returns:
            bool: True если успешно, иначе False.
        """
        pass

    @abstractmethod
    def key_down(self, key: str) -> bool:
        """
        Удерживает клавишу нажатой.

        Args:
            key (str): Клавиша для удержания.

        Returns:
            bool: True если успешно, иначе False.
        """
        pass

    @abstractmethod
    def key_up(self, key: str) -> bool:
        """
        Отпускает удерживаемую клавишу.

        Args:
            key (str): Клавиша для отпускания.

        Returns:
            bool: True если успешно, иначе False.
        """
        pass

    @abstractmethod
    def type_text(self, text: str, interval: Optional[float] = None) -> bool:
        """
        Вводит текст с указанным интервалом между нажатиями.

        Args:
            text (str): Текст для ввода.
            interval (Optional[float]): Интервал между нажатиями в секундах.

        Returns:
            bool: True если успешно, иначе False.
        """
        pass

    @abstractmethod
    def paste_text(self, text: str) -> bool:
        """
        Вставляет текст через буфер обмена.

        Args:
            text (str): Текст для вставки.

        Returns:
            bool: True если успешно, иначе False.
        """
        pass


class AbstractMouse(ABC):
    """Абстрактный класс для мыши"""

    @abstractmethod
    def move_to(self, x: int, y: int, duration: Optional[float] = None) -> bool:
        """
        Перемещает курсор в указанную позицию.

        Args:
            x (int): X-координата.
            y (int): Y-координата.
            duration (Optional[float]): Длительность перемещения в секундах.

        Returns:
            bool: True если успешно, иначе False.
        """
        pass

    @abstractmethod
    def move_by(self, dx: int, dy: int, duration: Optional[float] = None) -> bool:
        """
        Перемещает курсор на указанное расстояние.

        Args:
            dx (int): Смещение по X.
            dy (int): Смещение по Y.
            duration (Optional[float]): Длительность перемещения в секундах.

        Returns:
            bool: True если успешно, иначе False.
        """
        pass

    @abstractmethod
    def click(self, button: str = "left", count: int = 1) -> bool:
        """
        Выполняет клик мышью.

        Args:
            button (str): Кнопка ("left", "right", "middle").
            count (int): Количество кликов.

        Returns:
            bool: True если успешно, иначе False.
        """
        pass

    @abstractmethod
    def double_click(self, button: str = "left") -> bool:
        """
        Выполняет двойной клик мышью.

        Args:
            button (str): Кнопка ("left", "right", "middle").

        Returns:
            bool: True если успешно, иначе False.
        """
        pass

    @abstractmethod
    def right_click(self) -> bool:
        """
        Выполняет правый клик мышью.

        Returns:
            bool: True если успешно, иначе False.
        """
        pass

    @abstractmethod
    def mouse_down(self, button: str = "left") -> bool:
        """
        Удерживает кнопку мыши нажатой.

        Args:
            button (str): Кнопка ("left", "right", "middle").

        Returns:
            bool: True если успешно, иначе False.
        """

        pass

    @abstractmethod
    def mouse_up(self, button: str = "left") -> bool:
        """
        Отпускает удерживаемую кнопку мыши.

        Args:
            button (str): Кнопка ("left", "right", "middle").

        Returns:
            bool: True если успешно, иначе False.
        """
        pass

    @abstractmethod
    def drag_to(
        self, x: int, y: int, button: str = "left", duration: Optional[float] = None
    ) -> bool:
        """
        Перетаскивает курсор в указанную позицию с нажатой кнопкой мыши.

        Args:
            x (int): X-координата.
            y (int): Y-координата.
            button (str): Кнопка ("left", "right", "middle").
            duration (Optional[float]): Длительность перетаскивания в секундах.

        Returns:
            bool: True если успешно, иначе False.
        """
        pass

    @abstractmethod
    def scroll(self, clicks: int, direction: str = "down") -> bool:
        """
        Выполняет прокрутку мыши.

        Args:
            clicks (int): Количество щелчков колеса мыши.
            direction (str): Направление ("up", "down", "left", "right").

        Returns:
            bool: True если успешно, иначе False.
        """

        pass

    @abstractmethod
    def get_position(self) -> Tuple[int, int]:
        """
        Получает текущую позицию курсора.

        Returns:
            Tuple[int, int]: Кортеж (x, y) с координатами курсора.
        """
        pass


class InputController:
    """
    Комбинированный контроллер ввода, объединяющий клавиатуру и мышь.
    """

    def __init__(self, keyboard: AbstractKeyboard, mouse: AbstractMouse):
        """
        Инициализирует контроллер ввода.

        Args:
            keyboard (AbstractKeyboard): Контроллер клавиатуры.
            mouse (AbstractMouse): Контроллер мыши.
        """
        self.keyboard = keyboard
        self.mouse = mouse
