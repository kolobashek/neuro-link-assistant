"""
Реализация мыши для Windows.
"""

import ctypes
import math
import random
import time
from ctypes import wintypes
from typing import Optional, Tuple

import win32api
import win32con
import win32gui

from core.common.error_handler import handle_error
from core.common.input.base import AbstractMouse


# Структуры для SendInput
class POINT(ctypes.Structure):
    _fields_ = [("x", ctypes.c_long), ("y", ctypes.c_long)]


class MOUSEINPUT(ctypes.Structure):
    _fields_ = [
        ("dx", wintypes.LONG),
        ("dy", wintypes.LONG),
        ("mouseData", wintypes.DWORD),
        ("dwFlags", wintypes.DWORD),
        ("time", wintypes.DWORD),
        ("dwExtraInfo", ctypes.POINTER(ctypes.c_ulong)),
    ]


class INPUT(ctypes.Structure):
    _fields_ = [("type", wintypes.DWORD), ("mi", MOUSEINPUT)]


# Константы для действий с мышью
MOUSEEVENTF_MOVE = 0x0001
MOUSEEVENTF_LEFTDOWN = 0x0002
MOUSEEVENTF_LEFTUP = 0x0004
MOUSEEVENTF_RIGHTDOWN = 0x0008
MOUSEEVENTF_RIGHTUP = 0x0010
MOUSEEVENTF_MIDDLEDOWN = 0x0020
MOUSEEVENTF_MIDDLEUP = 0x0040
MOUSEEVENTF_WHEEL = 0x0800
MOUSEEVENTF_ABSOLUTE = 0x8000


class WindowsMouse(AbstractMouse):
    """Реализация мыши для операционной системы Windows."""

    def __init__(self, human_like: bool = True):
        """
        Инициализирует контроллер мыши.

        Args:
            human_like (bool): Флаг, указывающий, нужно ли эмулировать человеческое поведение.
        """
        self.human_like = human_like
        self.controller = None  # Для тестирования будет заменено моком

        # Настройки для эмуляции движения человеческой руки
        self.move_steps = 20  # Количество шагов при плавном перемещении
        self.click_delay = 0.1  # Задержка между нажатием и отпусканием кнопки мыши

        # Кэшируем размеры экрана
        self._screen_width = win32api.GetSystemMetrics(0)
        self._screen_height = win32api.GetSystemMetrics(1)

        # Константы для SendInput
        self.INPUT_MOUSE = 0

    def _human_move(
        self, start_x: int, start_y: int, end_x: int, end_y: int, duration: Optional[float] = None
    ) -> None:
        """
        Перемещает курсор с эмуляцией человеческого движения.

        Args:
            start_x (int): Начальная X-координата.
            start_y (int): Начальная Y-координата.
            end_x (int): Конечная X-координата.
            end_y (int): Конечная Y-координата.
            duration (Optional[float]): Длительность перемещения в секундах.
        """
        # Определяем количество промежуточных шагов
        steps = self.move_steps

        # Определяем, сколько времени должен занять каждый шаг
        step_sleep = (duration / steps) if duration else 0.01

        # Рассчитываем путь с небольшими отклонениями для реалистичности
        # Используем овальную траекторию вместо прямой линии
        for i in range(steps + 1):
            progress = i / steps

            # Добавляем небольшое отклонение для реалистичности
            if self.human_like and 0 < progress < 1:
                # Используем синусоидальную кривую для отклонения
                deviation_x = random.randint(-10, 10) * math.sin(progress * math.pi)
                deviation_y = random.randint(-10, 10) * math.sin(progress * math.pi)
            else:
                deviation_x = deviation_y = 0

            # Формула для плавного ускорения и замедления
            # (синусоидальная интерполяция вместо линейной)
            smooth_progress = 0.5 - 0.5 * math.cos(progress * math.pi)

            # Расчет координат с учетом отклонения
            current_x = int(start_x + (end_x - start_x) * smooth_progress + deviation_x)
            current_y = int(start_y + (end_y - start_y) * smooth_progress + deviation_y)

            # Устанавливаем курсор в новую позицию
            win32api.SetCursorPos((current_x, current_y))

            # Ждем перед следующим шагом
            time.sleep(step_sleep)

    def _send_mouse_event(self, flags: int, x: int = 0, y: int = 0, data: int = 0) -> None:
        """
        Отправляет событие мыши через SendInput API.

        Args:
            flags (int): Флаги события мыши.
            x (int): X-координата (относительная от текущей позиции).
            y (int): Y-координата (относительная от текущей позиции).
            data (int): Дополнительные данные для события (например, для прокрутки).
        """
        # Создаем структуру INPUT
        extra = ctypes.c_ulong(0)
        ii_ = INPUT(self.INPUT_MOUSE, MOUSEINPUT(x, y, data, flags, 0, ctypes.pointer(extra)))

        # Отправляем ввод
        ctypes.windll.user32.SendInput(1, ctypes.pointer(ii_), ctypes.sizeof(ii_))

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
        try:
            # Проверяем, что координаты в пределах экрана
            x = max(0, min(x, self._screen_width - 1))
            y = max(0, min(y, self._screen_height - 1))

            # Получаем текущую позицию курсора
            current_x, current_y = self.get_position()

            if self.human_like and duration:
                # Используем плавное перемещение для имитации человека
                self._human_move(current_x, current_y, x, y, duration)
            else:
                # Прямое перемещение без плавности
                win32api.SetCursorPos((x, y))

            return True
        except Exception as e:
            handle_error(f"Ошибка при перемещении курсора: {e}", e)
            return False

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
        try:
            # Получаем текущую позицию курсора
            current_x, current_y = self.get_position()

            # Рассчитываем новую позицию
            new_x = current_x + dx
            new_y = current_y + dy

            # Перемещаем курсор
            return self.move_to(new_x, new_y, duration)
        except Exception as e:
            handle_error(f"Ошибка при относительном перемещении курсора: {e}", e)
            return False

    def click(self, button: str = "left", count: int = 1) -> bool:
        """
        Выполняет клик мышью.

        Args:
            button (str): Кнопка ("left", "right", "middle").
            count (int): Количество кликов.

        Returns:
            bool: True если успешно, иначе False.
        """
        try:
            # Определяем флаги в зависимости от кнопки
            if button.lower() == "left":
                down_flag = win32con.MOUSEEVENTF_LEFTDOWN
                up_flag = win32con.MOUSEEVENTF_LEFTUP
            elif button.lower() == "right":
                down_flag = win32con.MOUSEEVENTF_RIGHTDOWN
                up_flag = win32con.MOUSEEVENTF_RIGHTUP
            elif button.lower() == "middle":
                down_flag = win32con.MOUSEEVENTF_MIDDLEDOWN
                up_flag = win32con.MOUSEEVENTF_MIDDLEUP
            else:
                raise ValueError(f"Неизвестная кнопка мыши: {button}")

            # Выполняем указанное количество кликов
            for _ in range(count):
                # Нажимаем кнопку
                win32api.mouse_event(down_flag, 0, 0, 0, 0)

                # Небольшая задержка для правдоподобности
                if self.human_like:
                    time.sleep(self.click_delay)

                # Отпускаем кнопку
                win32api.mouse_event(up_flag, 0, 0, 0, 0)

                # Задержка между кликами при множественных кликах
                if count > 1 and _ < count - 1:
                    time.sleep(0.1)

            return True
        except Exception as e:
            handle_error(f"Ошибка при выполнении клика мышью: {e}", e)
            return False

    def double_click(self, button: str = "left") -> bool:
        """
        Выполняет двойной клик мышью.

        Args:
            button (str): Кнопка ("left", "right", "middle").

        Returns:
            bool: True если успешно, иначе False.
        """
        return self.click(button, 2)

    def right_click(self) -> bool:
        """
        Выполняет правый клик мышью.

        Returns:
            bool: True если успешно, иначе False.
        """
        return self.click("right")

    def mouse_down(self, button: str = "left") -> bool:
        """
        Удерживает кнопку мыши нажатой.

        Args:
            button (str): Кнопка ("left", "right", "middle").

        Returns:
            bool: True если успешно, иначе False.
        """
        try:
            # Определяем флаг в зависимости от кнопки
            if button.lower() == "left":
                down_flag = win32con.MOUSEEVENTF_LEFTDOWN
            elif button.lower() == "right":
                down_flag = win32con.MOUSEEVENTF_RIGHTDOWN
            elif button.lower() == "middle":
                down_flag = win32con.MOUSEEVENTF_MIDDLEDOWN
            else:
                raise ValueError(f"Неизвестная кнопка мыши: {button}")

            # Нажимаем кнопку
            win32api.mouse_event(down_flag, 0, 0, 0, 0)

            return True
        except Exception as e:
            handle_error(f"Ошибка при нажатии кнопки мыши: {e}", e)
            return False

    def mouse_up(self, button: str = "left") -> bool:
        """
        Отпускает удерживаемую кнопку мыши.

        Args:
            button (str): Кнопка ("left", "right", "middle").

        Returns:
            bool: True если успешно, иначе False.
        """
        try:
            # Определяем флаг в зависимости от кнопки
            if button.lower() == "left":
                up_flag = win32con.MOUSEEVENTF_LEFTUP
            elif button.lower() == "right":
                up_flag = win32con.MOUSEEVENTF_RIGHTUP
            elif button.lower() == "middle":
                up_flag = win32con.MOUSEEVENTF_MIDDLEUP
            else:
                raise ValueError(f"Неизвестная кнопка мыши: {button}")

            # Отпускаем кнопку
            win32api.mouse_event(up_flag, 0, 0, 0, 0)

            return True
        except Exception as e:
            handle_error(f"Ошибка при отпускании кнопки мыши: {e}", e)
            return False

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
        try:
            # Нажимаем кнопку
            if not self.mouse_down(button):
                return False

            # Если имитируем человека, делаем небольшую паузу
            if self.human_like:
                time.sleep(0.1)

            # Перемещаем курсор
            if not self.move_to(x, y, duration):
                self.mouse_up(button)  # Обязательно отпускаем кнопку
                return False

            # Если имитируем человека, делаем небольшую паузу
            if self.human_like:
                time.sleep(0.1)

            # Отпускаем кнопку
            if not self.mouse_up(button):
                return False

            return True
        except Exception as e:
            handle_error(f"Ошибка при перетаскивании: {e}", e)

            # Пытаемся отпустить кнопку в случае ошибки
            try:
                self.mouse_up(button)
            except Exception:
                pass

            return False

    def scroll(self, clicks: int, direction: str = "down") -> bool:
        """
        Выполняет прокрутку мыши.

        Args:
            clicks (int): Количество щелчков колеса мыши.
            direction (str): Направление ("up", "down", "left", "right").

        Returns:
            bool: True если успешно, иначе False.
        """
        try:
            # Проверяем корректность направления
            if direction.lower() not in ["up", "down", "left", "right"]:
                raise ValueError(f"Неизвестное направление прокрутки: {direction}")

            # Определяем значение для прокрутки
            if direction.lower() == "up":
                wheel_value = 120 * clicks  # Положительное значение для прокрутки вверх
            elif direction.lower() == "down":
                wheel_value = -120 * clicks  # Отрицательное значение для прокрутки вниз
            elif direction.lower() == "left":
                # Горизонтальная прокрутка влево
                wheel_value = -120 * clicks
                win32api.mouse_event(win32con.MOUSEEVENTF_HWHEEL, 0, 0, wheel_value, 0)
                return True
            elif direction.lower() == "right":
                # Горизонтальная прокрутка вправо
                wheel_value = 120 * clicks
                win32api.mouse_event(win32con.MOUSEEVENTF_HWHEEL, 0, 0, wheel_value, 0)
                return True

            # Выполняем вертикальную прокрутку
            win32api.mouse_event(win32con.MOUSEEVENTF_WHEEL, 0, 0, wheel_value, 0)

            return True
        except Exception as e:
            handle_error(f"Ошибка при прокрутке: {e}", e)
            return False

    def get_position(self) -> Tuple[int, int]:
        """
        Получает текущую позицию курсора.

        Returns:
            Tuple[int, int]: Кортеж (x, y) с координатами курсора.
        """
        try:
            return win32gui.GetCursorPos()
        except Exception as e:
            handle_error(f"Ошибка при получении позиции курсора: {e}", e)
            # Возвращаем нулевые координаты в случае ошибки
            return (0, 0)

    def move_to_element(
        self, element, offset_x: int = 0, offset_y: int = 0, duration: Optional[float] = None
    ) -> bool:
        """
        Перемещает курсор к элементу с указанным смещением.

        Args:
            element: Элемент, к которому нужно переместить курсор.
            offset_x (int): Смещение по оси X от центра элемента.
            offset_y (int): Смещение по оси Y от центра элемента.
            duration (Optional[float]): Длительность перемещения в секундах.

        Returns:
            bool: True если успешно, иначе False.
        """
        try:
            # Получаем положение и размер элемента
            location = element.location
            size = element.size

            # Вычисляем центр элемента
            center_x = location["x"] + size["width"] // 2
            center_y = location["y"] + size["height"] // 2

            # Перемещаем курсор в центр элемента с учетом смещения
            target_x = center_x + offset_x
            target_y = center_y + offset_y

            return self.move_to(target_x, target_y, duration)
        except Exception as e:
            handle_error(f"Ошибка при перемещении курсора к элементу: {e}", e)
            return False

    def click_element(
        self, element, button: str = "left", offset_x: int = 0, offset_y: int = 0
    ) -> bool:
        """
        Выполняет клик по элементу с указанным смещением.

        Args:
            element: Элемент, по которому нужно кликнуть.
            button (str): Кнопка мыши ("left", "right", "middle").
            offset_x (int): Смещение по оси X от центра элемента.
            offset_y (int): Смещение по оси Y от центра элемента.

        Returns:
            bool: True если успешно, иначе False.
        """
        try:
            # Перемещаем курсор к элементу
            if not self.move_to_element(element, offset_x, offset_y):
                return False

            # Если имитируем человека, делаем небольшую паузу перед кликом
            if self.human_like:
                time.sleep(0.1)

            # Выполняем клик
            return self.click(button)
        except Exception as e:
            handle_error(f"Ошибка при клике по элементу: {e}", e)
            return False
