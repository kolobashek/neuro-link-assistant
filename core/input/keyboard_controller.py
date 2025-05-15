from pynput.keyboard import Controller, Key


class KeyboardController:
    """
    Класс для эмуляции клавиатурного ввода.
    """

    def __init__(self, human_like=True):
        """
        Инициализация контроллера клавиатуры.

        Args:
            human_like (bool, optional): Эмулировать человеческий ввод с клавиатуры
        """
        self.controller = Controller()
        self.human_like = human_like

    def type_text(self, text):
        """
        Печатает текст.

        Args:
            text (str): Текст для ввода

        Returns:
            bool: True в случае успешного ввода
        """
        try:
            self.controller.type(text)
            return True
        except Exception as e:
            print(f"Ошибка при вводе текста: {e}")
            return False

    def press_key(self, key):
        """
        Нажимает клавишу.

        Args:
            key (str): Символ клавиши

        Returns:
            bool: True в случае успешного нажатия
        """
        try:
            self.controller.press(key)
            self.controller.release(key)
            return True
        except Exception as e:
            print(f"Ошибка при нажатии клавиши: {e}")
            return False

    def press_special_key(self, key_name):
        """
        Нажимает специальную клавишу.

        Args:
            key_name (str): Имя специальной клавиши

        Returns:
            bool: True в случае успешного нажатия
        """
        try:
            key_obj = self.get_key_object(key_name)
            self.controller.press(key_obj)
            self.controller.release(key_obj)
            return True
        except Exception as e:
            print(f"Ошибка при нажатии специальной клавиши: {e}")
            return False

    def press_and_hold(self, key, duration=0.5):
        """
        Нажимает и удерживает клавишу.

        Args:
            key (str): Символ клавиши
            duration (float): Длительность удержания в секундах

        Returns:
            bool: True в случае успешного нажатия и удержания
        """
        import time

        try:
            self.controller.press(key)
            time.sleep(duration)
            self.controller.release(key)
            return True
        except Exception as e:
            print(f"Ошибка при нажатии и удержании клавиши: {e}")
            return False

    def press_combination(self, keys):
        """
        Нажимает комбинацию клавиш.

        Args:
            keys (list): Список клавиш для нажатия

        Returns:
            bool: True в случае успешного нажатия комбинации
        """
        try:
            for key in keys:
                key_obj = key if isinstance(key, str) else self.get_key_object(key)
                self.controller.press(key_obj)

            for key in reversed(keys):
                key_obj = key if isinstance(key, str) else self.get_key_object(key)
                self.controller.release(key_obj)

            return True
        except Exception as e:
            print(f"Ошибка при нажатии комбинации клавиш: {e}")
            return False

    def press_hotkey(self, *keys):
        """
        Нажимает горячую клавишу (комбинацию клавиш).

        Args:
            *keys: Клавиши для нажатия

        Returns:
            bool: True в случае успешного нажатия горячей клавиши
        """
        return self.press_combination(keys)

    def press_enter(self):
        """
        Нажимает клавишу Enter.

        Returns:
            bool: True в случае успешного нажатия
        """
        return self.press_special_key("enter")

    def press_backspace(self):
        """
        Нажимает клавишу Backspace.

        Returns:
            bool: True в случае успешного нажатия
        """
        return self.press_special_key("backspace")

    def press_arrow(self, direction):
        """
        Нажимает клавишу со стрелкой.

        Args:
            direction (str): Направление ('up', 'down', 'left', 'right')

        Returns:
            bool: True в случае успешного нажатия
        """
        try:
            key_map = {"up": Key.up, "down": Key.down, "left": Key.left, "right": Key.right}

            if direction not in key_map:
                raise ValueError(f"Неизвестное направление: {direction}")

            self.controller.press(key_map[direction])
            self.controller.release(key_map[direction])
            return True
        except Exception as e:
            print(f"Ошибка при нажатии клавиши со стрелкой: {e}")
            return False

    def press_ctrl_c(self):
        """
        Нажимает комбинацию клавиш Ctrl+C.

        Returns:
            bool: True в случае успешного нажатия
        """
        return self.press_hotkey(Key.ctrl, "c")

    def get_key_object(self, key_name):
        """
        Получает объект клавиши по её имени.

        Args:
            key_name (str): Имя клавиши

        Returns:
            Key: Объект клавиши
        """
        key_map = {
            "enter": Key.enter,
            "backspace": Key.backspace,
            "tab": Key.tab,
            "space": Key.space,
            "esc": Key.esc,
            "escape": Key.esc,
            "delete": Key.delete,
            "shift": Key.shift,
            "ctrl": Key.ctrl,
            "alt": Key.alt,
            "up": Key.up,
            "down": Key.down,
            "left": Key.left,
            "right": Key.right,
            "home": Key.home,
            "end": Key.end,
            "page_up": Key.page_up,
            "page_down": Key.page_down,
            "f1": Key.f1,
            "f2": Key.f2,
            "f3": Key.f3,
            "f4": Key.f4,
            "f5": Key.f5,
            "f6": Key.f6,
            "f7": Key.f7,
            "f8": Key.f8,
            "f9": Key.f9,
            "f10": Key.f10,
            "f11": Key.f11,
            "f12": Key.f12,
        }

        if key_name in key_map:
            return key_map[key_name]
        elif len(key_name) == 1:
            return key_name
        else:
            raise ValueError(f"Неизвестная клавиша: {key_name}")
