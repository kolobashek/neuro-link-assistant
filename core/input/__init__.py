
# ������ �����
import platform
from core.common.input.base import InputController

def get_input_controller():
    """���������� ���������-��������� ���������� �����"""
    system = platform.system().lower()
    
    if system == 'windows':
        from core.platform.windows.input.keyboard import WindowsKeyboard
        from core.platform.windows.input.mouse import WindowsMouse
        return InputController(WindowsKeyboard(), WindowsMouse())
    else:
        raise NotImplementedError(f"��������� {system} �� ��������������")
