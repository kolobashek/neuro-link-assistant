import random
import time

import pyautogui
from pynput.mouse import Button, Controller


class MouseController:
    """
    Класс для эмуляции действий мыши.
    """

    def __init__(self, human_like=True):
        """
        Инициализация контроллера мыши.

        Args:
            human_like (bool, optional): Эмулировать человеческие движения мыши
        """
        self.controller = Controller()  # Изменяем с mouse на controller для единообразия
        self.human_like = human_like

        # Настройка pyautogui для безопасности
        pyautogui.FAILSAFE = True

        # Настройка скорости движения мыши
        if human_like:
            pyautogui.PAUSE = 0.1
        else:
            pyautogui.PAUSE = 0.01

    def move_to(self, x, y, duration=0.5):
        """
        Перемещает курсор мыши в указанную позицию.

        Args:
            x (int): Координата X
            y (int): Координата Y
            duration (float, optional): Длительность перемещения в секундах

        Returns:
            bool: True в случае успешного перемещения
        """
        try:
            if self.human_like:
                # Используем pyautogui для плавного перемещения
                pyautogui.moveTo(x, y, duration=duration)
            else:
                # Мгновенное перемещение
                self.controller.position = (x, y)

            return True
        except Exception as e:
            print(f"Error moving mouse: {e}")
            return False

    def move_relative(self, dx, dy, duration=0.5):
        """
        Перемещает курсор мыши относительно текущей позиции.

        Args:
            dx (int): Смещение по X
            dy (int): Смещение по Y
            duration (float, optional): Длительность перемещения в секундах

        Returns:
            bool: True в случае успешного перемещения
        """
        try:
            current_x, current_y = self.get_position()

            if self.human_like:
                # Используем pyautogui для плавного перемещения
                pyautogui.moveTo(current_x + dx, current_y + dy, duration=duration)
            else:
                # Мгновенное перемещение
                self.controller.move(dx, dy)

            return True
        except Exception as e:
            print(f"Error moving mouse relatively: {e}")
            return False

    def click(self, button="left", count=1):
        """
        Выполняет клик мышью.

        Args:
            button (str, optional): Кнопка мыши ('left', 'right', 'middle')
            count (int, optional): Количество кликов

        Returns:
            bool: True в случае успешного клика
        """
        try:
            # Определяем кнопку мыши
            button_obj = self._get_button_object(button)

            # Выполняем указанное количество кликов
            for _ in range(count):
                self.controller.click(button_obj)

                # Добавляем задержку между кликами
                if self.human_like and count > 1:
                    time.sleep(0.1 + random.random() * 0.1)

            return True
        except Exception as e:
            print(f"Error clicking mouse: {e}")
            return False

    def double_click(self, button="left"):
        """
        Выполняет двойной клик мышью.

        Args:
            button (str, optional): Кнопка мыши ('left', 'right', 'middle')

        Returns:
            bool: True в случае успешного клика
        """
        return self.click(button, count=2)

    def right_click(self):
        """
        Выполняет клик правой кнопкой мыши.

        Returns:
            bool: True в случае успешного клика
        """
        return self.click(button="right")

    def press_and_hold(self, button="left", duration=0.5):
        """
        Нажимает и удерживает кнопку мыши.

        Args:
            button (str, optional): Кнопка мыши ('left', 'right', 'middle')
            duration (float, optional): Длительность удержания в секундах

        Returns:
            bool: True в случае успешного нажатия
        """
        try:
            # Определяем кнопку мыши
            button_obj = self._get_button_object(button)

            # Нажимаем и удерживаем кнопку
            self.controller.press(button_obj)
            time.sleep(duration)
            self.controller.release(button_obj)

            return True
        except Exception as e:
            print(f"Error pressing and holding mouse button: {e}")
            return False

    def drag_to(self, x, y, button="left", duration=0.5):
        """
        Перетаскивает объект в указанную позицию.

        Args:
            x (int): Координата X
            y (int): Координата Y
            button (str, optional): Кнопка мыши ('left', 'right', 'middle')
            duration (float, optional): Длительность перетаскивания в секундах

        Returns:
            bool: True в случае успешного перетаскивания
        """
        try:
            # Определяем кнопку мыши
            button_obj = self._get_button_object(button)

            if self.human_like:
                # Используем pyautogui для плавного перетаскивания
                pyautogui.dragTo(x, y, duration=duration, button=button.lower())
            else:
                # Нажимаем кнопку, перемещаем и отпускаем
                self.controller.press(button_obj)
                time.sleep(0.1)
                self.move_to(x, y, duration)
                time.sleep(0.1)
                self.controller.release(button_obj)

            return True
        except Exception as e:
            print(f"Error dragging mouse: {e}")
            return False

    def scroll(self, amount, direction="down"):
        """
        Выполняет прокрутку колесика мыши.

        Args:
            amount (int): Количество прокруток
            direction (str, optional): Направление прокрутки ('up', 'down')

        Returns:
            bool: True в случае успешной прокрутки
        """
        try:
            # Определяем направление прокрутки
            scroll_amount = amount
            if direction.lower() == "up":
                scroll_amount = amount
            elif direction.lower() == "down":
                scroll_amount = -amount
            else:
                raise ValueError(f"Unknown scroll direction: {direction}")

            # Выполняем прокрутку
            if self.human_like:
                # Прокручиваем постепенно
                steps = min(10, abs(scroll_amount))
                step_size = scroll_amount / steps

                for _ in range(steps):
                    self.controller.scroll(0, step_size)
                    time.sleep(0.05 + random.random() * 0.05)
            else:
                # Прокручиваем сразу
                self.controller.scroll(0, scroll_amount)

            return True
        except Exception as e:
            print(f"Error scrolling: {e}")
            return False

    def get_position(self):
        """
        Получает текущую позицию курсора мыши.

        Returns:
            tuple: Координаты (x, y)
        """
        try:
            return self.controller.position
        except Exception as e:
            print(f"Error getting mouse position: {e}")
            return (0, 0)

    def move_to_element(self, element, offset_x=0, offset_y=0, duration=0.5):
        """
        Перемещает курсор мыши к элементу.

        Args:
            element: Элемент (должен иметь атрибуты location или rect)
            offset_x (int, optional): Смещение по X
            offset_y (int, optional): Смещение по Y
            duration (float, optional): Длительность перемещения в секундах

        Returns:
            bool: True в случае успешного перемещения
        """
        try:
            # Определяем координаты элемента
            if hasattr(element, "location"):
                # Selenium WebElement
                x = element.location["x"]
                y = element.location["y"]
                if hasattr(element, "size"):
                    # Добавляем половину размера элемента, чтобы попасть в центр
                    x += element.size["width"] // 2
                    y += element.size["height"] // 2
            elif hasattr(element, "rect"):
                # Элемент с атрибутом rect (например, из компьютерного зрения)
                rect = element.rect
                x = (rect[0] + rect[2]) // 2
                y = (rect[1] + rect[3]) // 2
            else:
                raise ValueError("Element does not have location or rect attributes")

            # Добавляем смещение
            x += offset_x
            y += offset_y

            # Перемещаем курсор
            return self.move_to(x, y, duration)
        except Exception as e:
            print(f"Error moving to element: {e}")
            return False

    def click_element(self, element, button="left", offset_x=0, offset_y=0):
        """
        Перемещает курсор мыши к элементу и выполняет клик.

        Args:
            element: Элемент (должен иметь атрибуты location или rect)
            button (str, optional): Кнопка мыши ('left', 'right', 'middle')
            offset_x (int, optional): Смещение по X
            offset_y (int, optional): Смещение по Y

        Returns:
            bool: True в случае успешного клика
        """
        try:
            # Перемещаем курсор к элементу
            if not self.move_to_element(element, offset_x, offset_y):
                return False

            # Добавляем небольшую задержку перед кликом
            if self.human_like:
                time.sleep(0.1 + random.random() * 0.1)

            # Выполняем клик
            return self.click(button)
        except Exception as e:
            print(f"Error clicking element: {e}")
            return False

    def double_click_element(self, element, offset_x=0, offset_y=0):
        """
        Перемещает курсор мыши к элементу и выполняет двойной клик.

        Args:
            element: Элемент (должен иметь атрибуты location или rect)
            offset_x (int, optional): Смещение по X
            offset_y (int, optional): Смещение по Y

        Returns:
            bool: True в случае успешного клика
        """
        try:
            # Перемещаем курсор к элементу
            if not self.move_to_element(element, offset_x, offset_y):
                return False

            # Добавляем небольшую задержку перед кликом
            if self.human_like:
                time.sleep(0.1 + random.random() * 0.1)

            # Выполняем двойной клик
            return self.double_click()
        except Exception as e:
            print(f"Error double-clicking element: {e}")
            return False

    def right_click_element(self, element, offset_x=0, offset_y=0):
        """
        Перемещает курсор мыши к элементу и выполняет клик правой кнопкой.

        Args:
            element: Элемент (должен иметь атрибуты location или rect)
            offset_x (int, optional): Смещение по X
            offset_y (int, optional): Смещение по Y

        Returns:
            bool: True в случае успешного клика
        """
        try:
            # Перемещаем курсор к элементу
            if not self.move_to_element(element, offset_x, offset_y):
                return False

            # Добавляем небольшую задержку перед кликом
            if self.human_like:
                time.sleep(0.1 + random.random() * 0.1)

            # Выполняем клик правой кнопкой
            return self.right_click()
        except Exception as e:
            print(f"Error right-clicking element: {e}")
            return False

    def drag_element_to(self, element, to_x, to_y, offset_x=0, offset_y=0, duration=0.5):
        """
        Перетаскивает элемент в указанную позицию.

        Args:
            element: Элемент (должен иметь атрибуты location или rect)
            to_x (int): Целевая координата X
            to_y (int): Целевая координата Y
            offset_x (int, optional): Смещение по X
            offset_y (int, optional): Смещение по Y
            duration (float, optional): Длительность перетаскивания в секундах

        Returns:
            bool: True в случае успешного перетаскивания
        """
        try:
            # Перемещаем курсор к элементу
            if not self.move_to_element(element, offset_x, offset_y):
                return False

            # Добавляем небольшую задержку перед перетаскиванием
            if self.human_like:
                time.sleep(0.1 + random.random() * 0.1)

            # Выполняем перетаскивание
            return self.drag_to(to_x, to_y, duration=duration)
        except Exception as e:
            print(f"Error dragging element: {e}")
            return False

    def _get_button_object(self, button):
        """
        Преобразует строковое представление кнопки мыши в объект Button.

        Args:
            button (str or Button): Кнопка мыши

        Returns:
            Button: Объект кнопки мыши
        """
        # Если кнопка уже является объектом Button, возвращаем её
        if isinstance(button, Button):
            return button

        # Преобразуем строковые представления кнопок
        if isinstance(button, str):
            button_map = {"left": Button.left, "right": Button.right, "middle": Button.middle}

            if button.lower() in button_map:
                return button_map[button.lower()]

        # По умолчанию возвращаем левую кнопку
        return Button.left
