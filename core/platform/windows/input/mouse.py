
# Windows-специфичная реализация эмуляции мыши
import time
try:
    import pyautogui
except ImportError:
    pyautogui = None

from core.common.input.base import AbstractMouse
from core.common.error_handler import handle_error

class WindowsMouse(AbstractMouse):
    """Реализация эмуляции мыши для Windows с использованием PyAutoGUI"""
    
    def __init__(self):
        if pyautogui is None:
            handle_error("PyAutoGUI не установлен. Установите его: pip install pyautogui", 
                        module='mouse')
        
        # Настройка параметров
        self.duration = 0.1  # Длительность движения мыши
    
    def move_to(self, x, y):
        """Переместить курсор в указанные координаты"""
        try:
            if pyautogui:
                pyautogui.moveTo(x, y, duration=self.duration)
            return True
        except Exception as e:
            handle_error(f"Ошибка при перемещении мыши на координаты ({x}, {y}): {e}", 
                        e, module='mouse')
            return False
    
    def click(self, button='left'):
        """Кликнуть указанной кнопкой мыши"""
        try:
            if pyautogui:
                pyautogui.click(button=button)
            return True
        except Exception as e:
            handle_error(f"Ошибка при клике мышью ({button}): {e}", e, module='mouse')
            return False
    
    def double_click(self, button='left'):
        """Сделать двойной клик"""
        try:
            if pyautogui:
                pyautogui.doubleClick(button=button)
            return True
        except Exception as e:
            handle_error(f"Ошибка при двойном клике мышью ({button}): {e}", e, module='mouse')
            return False
    
    def drag_to(self, x, y, button='left'):
        """Перетащить с зажатой кнопкой мыши"""
        try:
            if pyautogui:
                pyautogui.dragTo(x, y, duration=self.duration, button=button)
            return True
        except Exception as e:
            handle_error(f"Ошибка при перетаскивании мышью на координаты ({x}, {y}): {e}", 
                        e, module='mouse')
            return False
    
    def scroll(self, amount):
        """Прокрутить колесо мыши"""
        try:
            if pyautogui:
                pyautogui.scroll(amount)
            return True
        except Exception as e:
            handle_error(f"Ошибка при прокрутке колеса мыши: {e}", e, module='mouse')
            return False
