
# ������������ ������ �������� �������
# �������� ����������� ����� � ���������-����������� ����������������

class AbstractFileSystem:
    """����������� ����� ��� ������ � �������� ��������"""
    
    def list_directory(self, path):
        """�������� ������ ������ � ����������"""
        raise NotImplementedError("����� ������ ���� ���������� � �������� ������")
    
    def file_exists(self, path):
        """��������� ������������� �����"""
        raise NotImplementedError("����� ������ ���� ���������� � �������� ������")
    
    def create_directory(self, path):
        """������� ����������"""
        raise NotImplementedError("����� ������ ���� ���������� � �������� ������")
    
    def read_file(self, path):
        """��������� ���������� �����"""
        raise NotImplementedError("����� ������ ���� ���������� � �������� ������")
    
    def write_file(self, path, content):
        """�������� ���������� � ����"""
        raise NotImplementedError("����� ������ ���� ���������� � �������� ������")
    
    def delete_file(self, path):
        """������� ����"""
        raise NotImplementedError("����� ������ ���� ���������� � �������� ������")
    
    def get_file_size(self, path):
        """�������� ������ �����"""
        raise NotImplementedError("����� ������ ���� ���������� � �������� ������")
    
    def get_file_modification_time(self, path):
        """�������� ����� ��������� ����������� �����"""
        raise NotImplementedError("����� ������ ���� ���������� � �������� ������")
