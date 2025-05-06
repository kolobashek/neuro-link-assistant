import pyautogui
import time
import random

class KeyboardEmulator:
    """
    Класс для эмуляции ввода с клавиатуры.
    """
    
    def __init__(self, human_like=True):
        """
        Инициализация эмулятора клавиатуры.
        
        Args:
            human_like (bool, optional): Эмулировать человеческое поведение
        """
        self.human_like = human_like
    
    def press_key(self, key):
        """
        Нажимает клавишу.
        
        Args:
            key (str): Клавиша для нажатия
            
        Returns:
            bool: True в случае успешного нажатия
        """
        try:
            pyautogui.press(key)
            return True
        except Exception as e:
            print(f"Error pressing key: {e}")
            return False
    
    def hold_key(self, key, duration=1.0):
        """
        Удерживает клавишу.
        
        Args:
            key (str): Клавиша для удержания
            duration (float, optional): Продолжительность удержания в секундах
            
        Returns:
            bool: True в случае успешного удержания
        """
        try:
            pyautogui.keyDown(key)
            time.sleep(duration)
            pyautogui.keyUp(key)
            return True
        except Exception as e:
            print(f"Error holding key: {e}")
            # Убеждаемся, что клавиша отпущена
            try:
                pyautogui.keyUp(key)
            except:
                pass
            return False
    
    def press_keys(self, keys):
        """
        Нажимает последовательность клавиш.
        
        Args:
            keys (list): Список клавиш для нажатия
            
        Returns:
            bool: True в случае успешного нажатия всех клавиш
        """
        try:
            for key in keys:
                pyautogui.press(key)
                if self.human_like:
                    time.sleep(random.uniform(0.05, 0.2))
            return True
        except Exception as e:
            print(f"Error pressing keys: {e}")
            return False
    
    def type_text(self, text, interval=0.0):
        """
        Вводит текст.
        
        Args:
            text (str): Текст для ввода
            interval (float, optional): Интервал между нажатиями клавиш
            
        Returns:
            bool: True в случае успешного ввода
        """
        try:
            if self.human_like:
                # Используем случайные интервалы для имитации человеческого ввода
                for char in text:
                    pyautogui.write(char, interval=random.uniform(0.05, 0.2))
            else:
                pyautogui.write(text, interval=interval)
            return True
        except Exception as e:
            print(f"Error typing text: {e}")
            return False
    
    def press_hotkey(self, *keys):
        """
        Нажимает комбинацию клавиш.
        
        Args:
            *keys: Клавиши для комбинации
            
        Returns:
            bool: True в случае успешного нажатия
        """
        try:
            pyautogui.hotkey(*keys)
            return True
        except Exception as e:
            print(f"Error pressing hotkey: {e}")
            return False
    
    def press_ctrl_key(self, key):
        """
        Нажимает комбинацию Ctrl+клавиша.
        
        Args:
            key (str): Клавиша для комбинации с Ctrl
            
        Returns:
            bool: True в случае успешного нажатия
        """
        try:
            pyautogui.hotkey('ctrl', key)
            return True
        except Exception as e:
            print(f"Error pressing Ctrl+key: {e}")
            return False
    
    def press_alt_key(self, key):
        """
        Нажимает комбинацию Alt+клавиша.
        
        Args:
            key (str): Клавиша для комбинации с Alt
            
        Returns:
            bool: True в случае успешного нажатия
        """
        try:
            pyautogui.hotkey('alt', key)
            return True
        except Exception as e:
            print(f"Error pressing Alt+key: {e}")
            return False
    
    def press_shift_key(self, key):
        """
        Нажимает комбинацию Shift+клавиша.
        
        Args:
            key (str): Клавиша для комбинации с Shift
            
        Returns:
            bool: True в случае успешного нажатия
        """
        try:
            pyautogui.hotkey('shift', key)
            return True
        except Exception as e:
            print(f"Error pressing Shift+key: {e}")
            return False