
# Windows-����������� ���������� ���������� ������
import time
try:
    import pygetwindow as gw
except ImportError:
    gw = None

from core.common.error_handler import handle_error

class WindowsWindowManager:
    """���������� ������ � Windows"""
    
    def __init__(self):
        if gw is None:
            handle_error("PyGetWindow �� ����������. ���������� ���: pip install pygetwindow", 
                        module='window')
    
    def get_all_windows(self):
        """
        �������� ������ ���� ����
        
        Returns:
            list: ������ �������� ����
        """
        try:
            if gw:
                return gw.getAllWindows()
            return []
        except Exception as e:
            handle_error(f"������ ��� ��������� ������ ����: {e}", e, module='window')
            return []
    
    def get_window_by_title(self, title):
        """
        ����� ���� �� ��������� (��������� ����������)
        
        Args:
            title (str): ��������� ����
        
        Returns:
            object: ������ ���� ��� None, ���� ���� �� �������
        """
        try:
            if gw:
                matching_windows = gw.getWindowsWithTitle(title)
                if matching_windows:
                    return matching_windows[0]
            return None
        except Exception as e:
            handle_error(f"������ ��� ������ ���� '{title}': {e}", e, module='window')
            return None
    
    def activate_window(self, window):
        """
        ������������ ����
        
        Args:
            window: ������ ����
        
        Returns:
            bool: True, ���� ���� ������� ������������
        """
        try:
            if window:
                window.activate()
                # ���� ����� �� ��������� ����
                time.sleep(0.5)
                return True
            return False
        except Exception as e:
            handle_error(f"������ ��� ��������� ����: {e}", e, module='window')
            return False
    
    def close_window(self, window):
        """
        ������� ����
        
        Args:
            window: ������ ����
        
        Returns:
            bool: True, ���� ���� ������� �������
        """
        try:
            if window:
                window.close()
                return True
            return False
        except Exception as e:
            handle_error(f"������ ��� �������� ����: {e}", e, module='window')
            return False
    
    def minimize_window(self, window):
        """
        �������� ����
        
        Args:
            window: ������ ����
        
        Returns:
            bool: True, ���� ���� ������� ��������
        """
        try:
            if window:
                window.minimize()
                return True
            return False
        except Exception as e:
            handle_error(f"������ ��� ������������ ����: {e}", e, module='window')
            return False
    
    def maximize_window(self, window):
        """
        ���������� ����
        
        Args:
            window: ������ ����
        
        Returns:
            bool: True, ���� ���� ������� ����������
        """
        try:
            if window:
                window.maximize()
                return True
            return False
        except Exception as e:
            handle_error(f"������ ��� �������������� ����: {e}", e, module='window')
            return False
    
    def wait_for_window(self, title, timeout=10):
        """
        ����� ��������� ���� � �������� ����������
        
        Args:
            title (str): ��������� ����
            timeout (int): ������� � ��������
        
        Returns:
            object: ������ ���� ��� None, ���� ���� �� ��������� �� ��������� �����
        """
        try:
            start_time = time.time()
            while time.time() - start_time < timeout:
                window = self.get_window_by_title(title)
                if window:
                    return window
                time.sleep(0.5)
            return None
        except Exception as e:
            handle_error(f"������ ��� �������� ���� '{title}': {e}", e, module='window')
            return None
