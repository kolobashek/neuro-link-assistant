# Абстрактные классы ввода данных
class AbstractKeyboard:
    """Абстрактный класс для эмуляции клавиатуры"""

    def press_key(self, key):
        """Нажать клавишу"""
        raise NotImplementedError("Метод должен быть реализован в дочернем классе")

    def release_key(self, key):
        """Отпустить клавишу"""
        raise NotImplementedError("Метод должен быть реализован в дочернем классе")

    def press_and_release(self, key):
        """Нажать и отпустить клавишу"""
        self.press_key(key)
        self.release_key(key)

    def type_text(self, text):
        """Напечатать текст"""
        raise NotImplementedError("Метод должен быть реализован в дочернем классе")

    def hotkey(self, *keys):
        """Нажать комбинацию клавиш"""
        raise NotImplementedError("Метод должен быть реализован в дочернем классе")


class AbstractMouse:
    """Абстрактный класс для эмуляции мыши"""

    def move_to(self, x, y):
        """Переместить курсор в указанные координаты"""
        raise NotImplementedError("Метод должен быть реализован в дочернем классе")

    def click(self, button="left"):
        """Кликнуть указанной кнопкой мыши"""
        raise NotImplementedError("Метод должен быть реализован в дочернем классе")

    def double_click(self, button="left"):
        """Двойной клик мыши"""
        raise NotImplementedError("Метод должен быть реализован в дочернем классе")

    def drag_to(self, x, y, button="left"):
        """Перетащить с зажатой кнопкой мыши"""
        raise NotImplementedError("Метод должен быть реализован в дочернем классе")

    def scroll(self, amount):
        """Прокрутить колесо мыши"""
        raise NotImplementedError("Метод должен быть реализован в дочернем классе")


class InputController:
    """Контроллер ввода, объединяющий клавиатуру и мышь"""

    def __init__(self, keyboard, mouse):
        """
        Инициализация контроллера ввода.

        Args:
            keyboard: Контроллер клавиатуры
            mouse: Контроллер мыши
        """
        self.keyboard = keyboard
        self.mouse = mouse

    def perform_action(self, action_type, **params):
        """
        Выполнить действие ввода

        Args:
            action_type (str): Тип действия ('key_press', 'mouse_click', и т.д.)
            **params: Параметры действия

        Returns:
            bool: True, если действие выполнено успешно
        """
        if action_type == "key_press":
            return self.keyboard.press_key(params.get("key"))
        elif action_type == "key_release":
            return self.keyboard.release_key(params.get("key"))
        elif action_type == "type_text":
            return self.keyboard.type_text(params.get("text"))
        elif action_type == "hotkey":
            return self.keyboard.hotkey(*params.get("keys", []))
        elif action_type == "mouse_move":
            return self.mouse.move_to(params.get("x"), params.get("y"))
        elif action_type == "mouse_click":
            return self.mouse.click(params.get("button", "left"))
        elif action_type == "mouse_double_click":
            return self.mouse.double_click(params.get("button", "left"))
        elif action_type == "mouse_drag":
            return self.mouse.drag_to(
                params.get("x"), params.get("y"), params.get("button", "left")
            )
        elif action_type == "mouse_scroll":
            return self.mouse.scroll(params.get("amount"))
        else:
            from core.common.error_handler import handle_error

            handle_error(f"Неизвестный тип действия: {action_type}", module="input")
            return False
