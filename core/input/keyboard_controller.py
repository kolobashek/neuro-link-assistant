import random
import time

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

    def type_text(self, text, interval=0.0, delay=None):
        """
        Вводит указанный текст с заданным интервалом между символами.

        Args:
            text (str): Текст для ввода
            interval (float, optional): Интервал между нажатиями клавиш в секундах
            delay (float, optional): Альтернативное название для интервала (для совместимости с тестами)

        Returns:
            bool: True в случае успешного ввода
        """
        # Если указан delay, используем его вместо interval
        if delay is not None:
            interval = delay

        try:
            if self.human_like:
                # Имитация человеческого ввода с вариациями интервалов
                for char in text:
                    # Рассчитываем случайный интервал
                    random_interval = interval
                    if interval > 0:
                        # Добавляем случайную вариацию ±30%
                        variation = interval * 0.3 * (random.random() * 2 - 1)
                        random_interval = max(0, interval + variation)

                    # Вводим символ
                    self.controller.press(char)
                    self.controller.release(char)

                    # Делаем паузу между нажатиями
                    if random_interval > 0:
                        time.sleep(random_interval)
            else:
                # Для совместимости с тестами используем последовательные вызовы press/release
                # вместо единичного вызова type()
                for char in text:
                    self.controller.press(char)
                    self.controller.release(char)

            return True
        except Exception as e:
            print(f"Error typing text: {e}")
            return False

    def press_key(self, key):
        """
        Нажимает клавишу.

        Args:
            key (str): Символ клавиши или имя специальной клавиши

        Returns:
            bool: True в случае успешного нажатия
        """
        try:
            key_obj = self.get_key_object(key) if isinstance(key, str) else key
            self.controller.press(key_obj)
            self.controller.release(key_obj)
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
                key_obj = self.get_key_object(key) if isinstance(key, str) else key
                self.controller.press(key_obj)

            for key in reversed(keys):
                key_obj = self.get_key_object(key) if isinstance(key, str) else key
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
            key_name (str or Key): Имя клавиши или объект Key

        Returns:
            Key: Объект клавиши
        """
        # Если уже передан объект Key, просто возвращаем его
        if isinstance(key_name, Key):
            return key_name

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
