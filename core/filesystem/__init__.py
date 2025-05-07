
# ������ �������� �������
import platform

def get_file_system():
    """���������� ���������-��������� ���������� �������� �������"""
    system = platform.system().lower()
    
    if system == 'windows':
        from core.platform.windows.file_system import WindowsFileSystem
        return WindowsFileSystem()
    else:
        raise NotImplementedError(f"��������� {system} �� ��������������")
