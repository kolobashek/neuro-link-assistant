"""
Базовые классы и интерфейсы для подсистемы ввода.
"""

from abc import ABC, abstractmethod
from typing import Any, List, Optional, Tuple


class AbstractKeyboard(ABC):
    """
    Абстрактный базовый класс для контроллеров клавиатуры.
    Определяет интерфейс, который должен быть реализован всеми
    конкретными контроллерами клавиатуры.
    """

    def __init__(self, human_like: bool = True):
        """
        Инициализация контроллера клавиатуры.

        Args:
            human_like: Эмулировать человеческое поведение при вводе.
        """
        self.human_like = human_like

    @abstractmethod
    def press_key(self, key: str) -> bool:
        """
        Нажимает указанную клавишу.

        Args:
            key: Клавиша для нажатия. Может быть символом или специальным ключом,
                например, 'enter', 'shift', 'ctrl', и т.д.

        Returns:
            True, если нажатие выполнено успешно, иначе False.
        """
        pass

    @abstractmethod
    def press_keys(self, keys: List[str]) -> bool:
        """
        Последовательно нажимает комбинацию клавиш.

        Args:
            keys: Список клавиш для нажатия.

        Returns:
            True, если все нажатия выполнены успешно, иначе False.
        """
        pass

    @abstractmethod
    def key_down(self, key: str) -> bool:
        """
        Нажимает и удерживает клавишу.

        Args:
            key: Клавиша для удержания.

        Returns:
            True, если нажатие выполнено успешно, иначе False.
        """
        pass

    @abstractmethod
    def key_up(self, key: str) -> bool:
        """
        Отпускает ранее нажатую клавишу.

        Args:
            key: Клавиша для отпускания.

        Returns:
            True, если отпускание выполнено успешно, иначе False.
        """
        pass

    @abstractmethod
    def type_text(self, text: str, interval: Optional[float] = None) -> bool:
        """
        Вводит указанный текст с заданным интервалом между нажатиями.

        Args:
            text: Текст для ввода.
            interval: Интервал между нажатиями клавиш в секундах. Если None,
                      используется значение по умолчанию.

        Returns:
            True, если ввод выполнен успешно, иначе False.
        """
        pass

    @abstractmethod
    def paste_text(self, text: str) -> bool:
        """
        Вставляет текст через буфер обмена.

        Args:
            text: Текст для вставки.

        Returns:
            True, если вставка выполнена успешно, иначе False.
        """
        pass

    @abstractmethod
    def press_enter(self) -> bool:
        """
        Нажимает клавишу Enter.

        Returns:
            True, если нажатие выполнено успешно, иначе False.
        """

        pass

    @abstractmethod
    def press_ctrl_c(self) -> bool:
        """
        Нажимает комбинацию Ctrl+C (копирование).

        Returns:
            True, если нажатие выполнено успешно, иначе False.
        """
        pass


class AbstractMouse(ABC):
    """
    Абстрактный базовый класс для контроллеров мыши.
    Определяет интерфейс, который должен быть реализован всеми
    конкретными контроллерами мыши.
    """

    def __init__(self, human_like: bool = True):
        """
        Инициализация контроллера мыши.

        Args:
            human_like: Эмулировать человеческое поведение при движении мыши.
        """
        self.human_like = human_like

    @abstractmethod
    def move_to(self, x: int, y: int, duration: Optional[float] = None) -> bool:
        """
        Перемещает курсор мыши в указанные координаты.

        Args:
            x: X-координата.
            y: Y-координата.
            duration: Длительность перемещения в секундах.

        Returns:
            True, если перемещение выполнено успешно, иначе False.
        """
        pass

    @abstractmethod
    def move_by(self, dx: int, dy: int, duration: Optional[float] = None) -> bool:
        """
        Перемещает курсор мыши относительно текущей позиции.

        Args:
            dx: Смещение по X.
            dy: Смещение по Y.
            duration: Длительность перемещения в секундах.

        Returns:
            True, если перемещение выполнено успешно, иначе False.
        """
        pass

    @abstractmethod
    def click(self, button: str = "left", count: int = 1) -> bool:
        """
        Выполняет клик мышью.

        Args:
            button: Кнопка мыши ('left', 'right', 'middle').
            count: Количество кликов.

        Returns:
            True, если клик выполнен успешно, иначе False.
        """
        pass

    @abstractmethod
    def double_click(self, button: str = "left") -> bool:
        """
        Выполняет двойной клик мышью.

        Args:
            button: Кнопка мыши ('left', 'right', 'middle').

        Returns:
            True, если двойной клик выполнен успешно, иначе False.
        """
        pass

    @abstractmethod
    def right_click(self) -> bool:
        """
        Выполняет клик правой кнопкой мыши.

        Returns:
            True, если клик выполнен успешно, иначе False.
        """
        pass

    @abstractmethod
    def mouse_down(self, button: str = "left") -> bool:
        """
        Нажимает и удерживает кнопку мыши.

        Args:
            button: Кнопка мыши ('left', 'right', 'middle').

        Returns:
            True, если нажатие выполнено успешно, иначе False.
        """
        pass

    @abstractmethod
    def mouse_up(self, button: str = "left") -> bool:
        """
        Отпускает ранее нажатую кнопку мыши.

        Args:
            button: Кнопка мыши ('left', 'right', 'middle').

        Returns:
            True, если отпускание выполнено успешно, иначе False.
        """
        pass

    @abstractmethod
    def drag_to(
        self, x: int, y: int, button: str = "left", duration: Optional[float] = None
    ) -> bool:
        """
        Перетаскивает курсор мыши в указанные координаты с зажатой кнопкой.

        Args:
            x: X-координата.
            y: Y-координата.
            button: Кнопка мыши ('left', 'right', 'middle').
            duration: Длительность перетаскивания в секундах.

        Returns:
            True, если перетаскивание выполнено успешно, иначе False.
        """
        pass

    @abstractmethod
    def scroll(self, clicks: int, direction: str = "down") -> bool:
        """
        Выполняет прокрутку колесика мыши.

        Args:
            clicks: Количество щелчков прокрутки.
            direction: Направление прокрутки ('up', 'down').

        Returns:
            True, если прокрутка выполнена успешно, иначе False.
        """
        pass

    @abstractmethod
    def get_position(self) -> Tuple[int, int]:
        """
        Получает текущую позицию курсора мыши.

        Returns:
            Кортеж (x, y) с координатами.
        """
        pass

    @abstractmethod
    def move_to_element(
        self, element: Any, offset_x: int = 0, offset_y: int = 0, duration: Optional[float] = None
    ) -> bool:
        """
        Перемещает курсор мыши к указанному элементу.

        Args:
            element: Элемент, к которому нужно переместить курсор.
            offset_x: Смещение по X относительно центра элемента.
            offset_y: Смещение по Y относительно центра элемента.
            duration: Длительность перемещения в секундах.

        Returns:
            True, если перемещение выполнено успешно, иначе False.
        """
        pass

    @abstractmethod
    def click_element(
        self, element: Any, button: str = "left", offset_x: int = 0, offset_y: int = 0
    ) -> bool:
        """
        Выполняет клик по указанному элементу.

        Args:
            element: Элемент, по которому нужно кликнуть.
            button: Кнопка мыши ('left', 'right', 'middle').
            offset_x: Смещение по X относительно центра элемента.
            offset_y: Смещение по Y относительно центра элемента.

        Returns:
            True, если клик выполнен успешно, иначе False.
        """
        pass


class InputController:
    """
    Комбинированный контроллер ввода, объединяющий функциональность
    клавиатуры и мыши.
    """

    def __init__(self, keyboard: AbstractKeyboard, mouse: AbstractMouse):
        """
        Инициализация контроллера ввода.

        Args:
            keyboard: Экземпляр контроллера клавиатуры.
            mouse: Экземпляр контроллера мыши.
        """
        self.keyboard = keyboard
        self.mouse = mouse

    def is_human_like(self) -> bool:
        """
        Проверяет, включен ли режим эмуляции человеческого ввода.

        Returns:
            True, если режим включен, иначе False.
        """
        return self.keyboard.human_like and self.mouse.human_like

    def set_human_like(self, enabled: bool) -> None:
        """
        Включает или выключает режим эмуляции человеческого ввода.

        Args:
            enabled: True для включения, False для выключения.
        """
        self.keyboard.human_like = enabled
        self.mouse.human_like = enabled
