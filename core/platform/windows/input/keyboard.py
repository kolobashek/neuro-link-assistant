
# Windows-����������� ���������� �������� ����������
import time
try:
    import pyautogui
except ImportError:
    pyautogui = None

from core.common.input.base import AbstractKeyboard
from core.common.error_handler import handle_error

class WindowsKeyboard(AbstractKeyboard):
    """���������� �������� ���������� ��� Windows � �������������� PyAutoGUI"""
    
    def __init__(self):
        if pyautogui is None:
            handle_error("PyAutoGUI �� ����������. ���������� ���: pip install pyautogui", 
                        module='keyboard')
    
    def press_key(self, key):
        """������ �������"""
        try:
            if pyautogui:
                pyautogui.keyDown(key)
            return True
        except Exception as e:
            handle_error(f"������ ��� ������� ������� {key}: {e}", e, module='keyboard')
            return False
    
    def release_key(self, key):
        """��������� �������"""
        try:
            if pyautogui:
                pyautogui.keyUp(key)
            return True
        except Exception as e:
            handle_error(f"������ ��� ���������� ������� {key}: {e}", e, module='keyboard')
            return False
    
    def type_text(self, text):
        """���������� �����"""
        try:
            if pyautogui:
                pyautogui.write(text)
            return True
        except Exception as e:
            handle_error(f"������ ��� ����� ������: {e}", e, module='keyboard')
            return False
    
    def hotkey(self, *keys):
        """������ ���������� ������"""
        try:
            if pyautogui:
                pyautogui.hotkey(*keys)
            return True
        except Exception as e:
            handle_error(f"������ ��� ������� ���������� ������ {keys}: {e}", e, module='keyboard')
            return False
