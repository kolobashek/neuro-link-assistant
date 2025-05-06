import time
import random
import pyautogui
from pynput.keyboard import Controller, Key

class KeyboardController:
    """
    Класс для эмуляции клавиатурного ввода.
    """
    
    def __init__(self, human_like=True):
        """
        Инициализация контроллера клавиатуры.
        
        Args:
            human_like (bool, optional): Эмулировать человеческий ввод с задержками
        """
        self.keyboard = Controller()
        self.human_like = human_like
    
    def type_text(self, text, delay=0.1, random_delay=True):
        """
        Вводит текст с задержками между символами.
        
        Args:
            text (str): Текст для ввода
            delay (float, optional): Базовая задержка между символами в секундах
            random_delay (bool, optional): Добавлять случайные задержки для имитации человека
            
        Returns:
            bool: True в случае успешного ввода
        """
        try:
            for char in text:
                self.keyboard.press(char)
                self.keyboard.release(char)
                
                # Добавляем задержку между нажатиями клавиш
                if self.human_like:
                    if random_delay:
                        # Случайная задержка в диапазоне 0.5-1.5 от базовой
                        time.sleep(delay * (0.5 + random.random()))
                    else:
                        time.sleep(delay)
            
            return True
        except Exception as e:
            print(f"Error typing text: {e}")
            return False
    
    def press_key(self, key):
        """
        Нажимает и отпускает клавишу.
        
        Args:
            key (str or Key): Клавиша для нажатия
            
        Returns:
            bool: True в случае успешного нажатия
        """
        try:
            # Преобразуем строковое представление специальных клавиш
            key_obj = self._get_key_object(key)
            
            self.keyboard.press(key_obj)
            self.keyboard.release(key_obj)
            
            # Добавляем небольшую задержку после нажатия
            if self.human_like:
                time.sleep(0.05 + random.random() * 0.1)
            
            return True
        except Exception as e:
            print(f"Error pressing key: {e}")
            return False
    
    def press_and_hold(self, key, duration=0.5):
        """
        Нажимает и удерживает клавишу.
        
        Args:
            key (str or Key): Клавиша для нажатия
            duration (float, optional): Длительность удержания в секундах
            
        Returns:
            bool: True в случае успешного нажатия
        """
        try:
            # Преобразуем строковое представление специальных клавиш
            key_obj = self._get_key_object(key)
            
            self.keyboard.press(key_obj)
            time.sleep(duration)
            self.keyboard.release(key_obj)
            
            return True
        except Exception as e:
            print(f"Error pressing and holding key: {e}")
            return False
    
    def press_combination(self, keys):
        """
        Нажимает комбинацию клавиш.
        
        Args:
            keys (list): Список клавиш для нажатия
            
        Returns:
            bool: True в случае успешного нажатия
        """
        try:
            # Преобразуем строковые представления специальных клавиш
            key_objects = [self._get_key_object(key) for key in keys]
            
            # Нажимаем все клавиши
            for key in key_objects:
                self.keyboard.press(key)
            
            # Отпускаем все клавиши в обратном порядке
            for key in reversed(key_objects):
                self.keyboard.release(key)
            
            # Добавляем небольшую задержку после комбинации
            if self.human_like:
                time.sleep(0.1 + random.random() * 0.1)
            
            return True
        except Exception as e:
            print(f"Error pressing key combination: {e}")
            return False
    
    def press_hotkey(self, *keys):
        """
        Нажимает горячую клавишу (комбинацию клавиш).
        
        Args:
            *keys: Клавиши для нажатия
            
        Returns:
            bool: True в случае успешного нажатия
        """
        return self.press_combination(keys)
    
    def press_enter(self):
        """
        Нажимает клавишу Enter.
        
        Returns:
            bool: True в случае успешного нажатия
        """
        return self.press_key(Key.enter)
    
    def press_tab(self):
        """
        Нажимает клавишу Tab.
        
        Returns:
            bool: True в случае успешного нажатия
        """
        return self.press_key(Key.tab)
    
    def press_escape(self):
        """
        Нажимает клавишу Escape.
        
        Returns:
            bool: True в случае успешного нажатия
        """
        return self.press_key(Key.esc)
    
    def press_backspace(self, count=1):
        """
        Нажимает клавишу Backspace указанное количество раз.
        
        Args:
            count (int, optional): Количество нажатий
            
        Returns:
            bool: True в случае успешного нажатия
        """
        try:
            for _ in range(count):
                self.press_key(Key.backspace)
                if self.human_like and count > 1:
                    time.sleep(0.05 + random.random() * 0.05)
            
            return True
        except Exception as e:
            print(f"Error pressing backspace: {e}")
            return False
    
    def press_delete(self, count=1):
        """
        Нажимает клавишу Delete указанное количество раз.
        
        Args:
            count (int, optional): Количество нажатий
            
        Returns:
            bool: True в случае успешного нажатия
        """
        try:
            for _ in range(count):
                self.press_key(Key.delete)
                if self.human_like and count > 1:
                    time.sleep(0.05 + random.random() * 0.05)
            
            return True
        except Exception as e:
            print(f"Error pressing delete: {e}")
            return False
    
    def press_arrow(self, direction, count=1):
        """
        Нажимает клавишу стрелки указанное количество раз.
        
        Args:
            direction (str): Направление ('up', 'down', 'left', 'right')
            count (int, optional): Количество нажатий
            
        Returns:
            bool: True в случае успешного нажатия
        """
        try:
            # Определяем клавишу стрелки
            if direction.lower() == 'up':
                key = Key.up
            elif direction.lower() == 'down':
                key = Key.down
            elif direction.lower() == 'left':
                key = Key.left
            elif direction.lower() == 'right':
                key = Key.right
            else:
                raise ValueError(f"Unknown arrow direction: {direction}")
            
            # Нажимаем клавишу указанное количество раз
            for _ in range(count):
                self.press_key(key)
                if self.human_like and count > 1:
                    time.sleep(0.05 + random.random() * 0.05)
            
            return True
        except Exception as e:
            print(f"Error pressing arrow key: {e}")
            return False
    
    def press_ctrl_c(self):
        """
        Нажимает комбинацию Ctrl+C (копировать).
        
        Returns:
            bool: True в случае успешного нажатия
        """
        return self.press_combination([Key.ctrl, 'c'])
    
    def press_ctrl_v(self):
        """
        Нажимает комбинацию Ctrl+V (вставить).
        
        Returns:
            bool: True в случае успешного нажатия
        """
        return self.press_combination([Key.ctrl, 'v'])
    
    def press_ctrl_x(self):
        """
        Нажимает комбинацию Ctrl+X (вырезать).
        
        Returns:
            bool: True в случае успешного нажатия
        """
        return self.press_combination([Key.ctrl, 'x'])
    
    def press_ctrl_z(self):
        """
        Нажимает комбинацию Ctrl+Z (отменить).
        
        Returns:
            bool: True в случае успешного нажатия
        """
        return self.press_combination([Key.ctrl, 'z'])
    
    def press_ctrl_a(self):
        """
        Нажимает комбинацию Ctrl+A (выделить всё).
        
        Returns:
            bool: True в случае успешного нажатия
        """
        return self.press_combination([Key.ctrl, 'a'])
    
    def press_alt_tab(self):
        """
        Нажимает комбинацию Alt+Tab (переключение окон).
        
        Returns:
            bool: True в случае успешного нажатия
        """
        return self.press_combination([Key.alt, Key.tab])
    
    def press_win(self):
        """
        Нажимает клавишу Windows.
        
        Returns:
            bool: True в случае успешного нажатия
        """
        return self.press_key(Key.cmd)
    
    def press_win_r(self):
        """
        Нажимает комбинацию Win+R (выполнить).
        
        Returns:
            bool: True в случае успешного нажатия
        """
        return self.press_combination([Key.cmd, 'r'])
    
    def press_win_e(self):
        """
        Нажимает комбинацию Win+E (проводник).
        
        Returns:
            bool: True в случае успешного нажатия
        """
        return self.press_combination([Key.cmd, 'e'])
    
    def press_win_d(self):
        """
        Нажимает комбинацию Win+D (показать рабочий стол).
        
        Returns:
            bool: True в случае успешного нажатия
        """
        return self.press_combination([Key.cmd, 'd'])
    
    def press_alt_f4(self):
        """
        Нажимает комбинацию Alt+F4 (закрыть окно).
        
        Returns:
            bool: True в случае успешного нажатия
        """
        return self.press_combination([Key.alt, Key.f4])
    
    def _get_key_object(self, key):
        """
        Преобразует строковое представление клавиши в объект Key.
        
        Args:
            key (str or Key): Клавиша
            
        Returns:
            Key or str: Объект клавиши
        """
        # Если ключ уже является объектом Key, возвращаем его
        if isinstance(key, Key):
            return key
        
        # Преобразуем строковые представления специальных клавиш
        if isinstance(key, str):
            # Функциональные клавиши
            if key.lower().startswith('f') and key[1:].isdigit():
                f_num = int(key[1:])
                if 1 <= f_num <= 12:
                    return getattr(Key, f'f{f_num}')
            
            # Другие специальные клавиши
            special_keys = {
                'enter': Key.enter,
                'return': Key.enter,
                'tab': Key.tab,
                'space': Key.space,
                'esc': Key.esc,
                'escape': Key.esc,
                'backspace': Key.backspace,
                'delete': Key.delete,
                'del': Key.delete,
                'insert': Key.insert,
                'ins': Key.insert,
                'home': Key.home,
                'end': Key.end,
                'pageup': Key.page_up,
                'pagedown': Key.page_down,
                'up': Key.up,
                'down': Key.down,
                'left': Key.left,
                'right': Key.right,
                'ctrl': Key.ctrl,
                'control': Key.ctrl,
                'alt': Key.alt,
                'shift': Key.shift,
                'win': Key.cmd,
                'windows': Key.cmd,
                'cmd': Key.cmd,
                'command': Key.cmd,
                'menu': Key.menu
            }
            
            if key.lower() in special_keys:
                return special_keys[key.lower()]
        
        # Возвращаем ключ как есть (для обычных символов)
        return key