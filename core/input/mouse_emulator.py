import pyautogui
import time
import random
import math

class MouseEmulator:
    """
    Класс для эмуляции действий мыши.
    """
    
    def __init__(self, human_like=True):
        """
        Инициализация эмулятора мыши.
        
        Args:
            human_like (bool, optional): Эмулировать человеческое поведение
        """
        self.human_like = human_like
        
        # Настройки для человекоподобного движения
        if self.human_like:
            pyautogui.MINIMUM_DURATION = 0.1
            pyautogui.MINIMUM_SLEEP = 0.05
            pyautogui.PAUSE = 0.1
        else:
            pyautogui.MINIMUM_DURATION = 0.0
            pyautogui.MINIMUM_SLEEP = 0.0
            pyautogui.PAUSE = 0.0
    
    def move_to(self, x, y, duration=0.5):
        """
        Перемещает курсор в указанную позицию.
        
        Args:
            x (int): Координата X
            y (int): Координата Y
            duration (float, optional): Продолжительность перемещения
            
        Returns:
            bool: True в случае успешного перемещения
        """
        try:
            if self.human_like:
                # Добавляем небольшую неточность для имитации человеческого движения
                x += random.uniform(-5, 5)
                y += random.uniform(-5, 5)
                
                # Используем кривую Безье для более естественного движения
                pyautogui.moveTo(x, y, duration=duration, tween=pyautogui.easeOutQuad)
            else:
                pyautogui.moveTo(x, y, duration=duration)
            
            return True
        except Exception as e:
            print(f"Error moving mouse: {e}")
            return False
    
    def click(self, x=None, y=None, button='left', clicks=1, interval=0.0):
        """
        Выполняет клик мышью.
        
        Args:
            x (int, optional): Координата X
            y (int, optional): Координата Y
            button (str, optional): Кнопка мыши ('left', 'right', 'middle')
            clicks (int, optional): Количество кликов
            interval (float, optional): Интервал между кликами
            
        Returns:
            bool: True в случае успешного клика
        """
        try:
            if x is not None and y is not None:
                # Сначала перемещаем курсор
                self.move_to(x, y)
            
            if self.human_like:
                # Добавляем небольшую задержку перед кликом
                time.sleep(random.uniform(0.1, 0.3))
                
                # Используем случайный интервал между кликами
                interval = random.uniform(0.1, 0.3)
            
            pyautogui.click(button=button, clicks=clicks, interval=interval)
            
            return True
        except Exception as e:
            print(f"Error clicking: {e}")
            return False
    
    def double_click(self, x=None, y=None):
        """
        Выполняет двойной клик левой кнопкой мыши.
        
        Args:
            x (int, optional): Координата X
            y (int, optional): Координата Y
            
        Returns:
            bool: True в случае успешного двойного клика
        """
        return self.click(x, y, clicks=2)
    
    def right_click(self, x=None, y=None):
        """
        Выполняет клик правой кнопкой мыши.
        
        Args:
            x (int, optional): Координата X
            y (int, optional): Координата Y
            
        Returns:
            bool: True в случае успешного клика
        """
        return self.click(x, y, button='right')
    
    def drag_to(self, start_x, start_y, end_x, end_y, button='left', duration=0.5):
        """
        Перетаскивает объект из одной позиции в другую.
        
        Args:
            start_x (int): Начальная координата X
            start_y (int): Начальная координата Y
            end_x (int): Конечная координата X
            end_y (int): Конечная координата Y
            button (str, optional): Кнопка мыши ('left', 'right', 'middle')
            duration (float, optional): Продолжительность перетаскивания
            
        Returns:
            bool: True в случае успешного перетаскивания
        """
        try:
            # Перемещаем курсор в начальную позицию
            self.move_to(start_x, start_y)
            
            if self.human_like:
                # Добавляем небольшую задержку перед нажатием
                time.sleep(random.uniform(0.1, 0.3))
            
            # Выполняем перетаскивание
            pyautogui.dragTo(end_x, end_y, duration=duration, button=button)
            
            return True
        except Exception as e:
            print(f"Error dragging: {e}")
            return False
    
    def scroll(self, clicks, x=None, y=None):
        """
        Выполняет прокрутку колесика мыши.
        
        Args:
            clicks (int): Количество щелчков колесика (положительное - вверх, отрицательное - вниз)
            x (int, optional): Координата X
            y (int, optional): Координата Y
            
        Returns:
            bool: True в случае успешной прокрутки
        """
        try:
            if x is not None and y is not None:
                # Сначала перемещаем курсор
                self.move_to(x, y)
            
            if self.human_like:
                # Разбиваем прокрутку на несколько шагов для более естественного поведения
                steps = abs(clicks)
                direction = 1 if clicks > 0 else -1
                
                for _ in range(steps):
                    pyautogui.scroll(direction)
                    time.sleep(random.uniform(0.05, 0.2))
            else:
                pyautogui.scroll(clicks)
            
            return True
        except Exception as e:
            print(f"Error scrolling: {e}")
            return False
    
    def get_position(self):
        """
        Получает текущую позицию курсора.
        
        Returns:
            tuple: (x, y) координаты курсора
        """
        try:
            return pyautogui.position()
        except Exception as e:
            print(f"Error getting mouse position: {e}")
            return (0, 0)
    
    def move_relative(self, dx, dy, duration=0.5):
        """
        Перемещает курсор относительно текущей позиции.
        
        Args:
            dx (int): Смещение по X
            dy (int): Смещение по Y
            duration (float, optional): Продолжительность перемещения
            
        Returns:
            bool: True в случае успешного перемещения
        """
        try:
            current_x, current_y = self.get_position()
            return self.move_to(current_x + dx, current_y + dy, duration)
        except Exception as e:
            print(f"Error moving mouse relatively: {e}")
            return False