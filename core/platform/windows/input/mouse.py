
# Windows-����������� ���������� �������� ����
import time
try:
    import pyautogui
except ImportError:
    pyautogui = None

from core.common.input.base import AbstractMouse
from core.common.error_handler import handle_error

class WindowsMouse(AbstractMouse):
    """���������� �������� ���� ��� Windows � �������������� PyAutoGUI"""
    
    def __init__(self):
        if pyautogui is None:
            handle_error("PyAutoGUI �� ����������. ���������� ���: pip install pyautogui", 
                        module='mouse')
        
        # ��������� ����������
        self.duration = 0.1  # ������������ �������� ����
    
    def move_to(self, x, y):
        """����������� ������ � ��������� ����������"""
        try:
            if pyautogui:
                pyautogui.moveTo(x, y, duration=self.duration)
            return True
        except Exception as e:
            handle_error(f"������ ��� ����������� ���� �� ���������� ({x}, {y}): {e}", 
                        e, module='mouse')
            return False
    
    def click(self, button='left'):
        """�������� ��������� ������� ����"""
        try:
            if pyautogui:
                pyautogui.click(button=button)
            return True
        except Exception as e:
            handle_error(f"������ ��� ����� ����� ({button}): {e}", e, module='mouse')
            return False
    
    def double_click(self, button='left'):
        """������� ������� ����"""
        try:
            if pyautogui:
                pyautogui.doubleClick(button=button)
            return True
        except Exception as e:
            handle_error(f"������ ��� ������� ����� ����� ({button}): {e}", e, module='mouse')
            return False
    
    def drag_to(self, x, y, button='left'):
        """���������� � ������� ������� ����"""
        try:
            if pyautogui:
                pyautogui.dragTo(x, y, duration=self.duration, button=button)
            return True
        except Exception as e:
            handle_error(f"������ ��� �������������� ����� �� ���������� ({x}, {y}): {e}", 
                        e, module='mouse')
            return False
    
    def scroll(self, amount):
        """���������� ������ ����"""
        try:
            if pyautogui:
                pyautogui.scroll(amount)
            return True
        except Exception as e:
            handle_error(f"������ ��� ��������� ������ ����: {e}", e, module='mouse')
            return False
