
# ������� ����������� ������ �����
class AbstractKeyboard:
    """����������� ����� ��� �������� ����������"""
    
    def press_key(self, key):
        """������ �������"""
        raise NotImplementedError("����� ������ ���� ���������� � �������� ������")
    
    def release_key(self, key):
        """��������� �������"""
        raise NotImplementedError("����� ������ ���� ���������� � �������� ������")
    
    def press_and_release(self, key):
        """������ � ��������� �������"""
        self.press_key(key)
        self.release_key(key)
    
    def type_text(self, text):
        """���������� �����"""
        raise NotImplementedError("����� ������ ���� ���������� � �������� ������")
    
    def hotkey(self, *keys):
        """������ ���������� ������"""
        raise NotImplementedError("����� ������ ���� ���������� � �������� ������")


class AbstractMouse:
    """����������� ����� ��� �������� ����"""
    
    def move_to(self, x, y):
        """����������� ������ � ��������� ����������"""
        raise NotImplementedError("����� ������ ���� ���������� � �������� ������")
    
    def click(self, button='left'):
        """�������� ��������� ������� ����"""
        raise NotImplementedError("����� ������ ���� ���������� � �������� ������")
    
    def double_click(self, button='left'):
        """������� ������� ����"""
        raise NotImplementedError("����� ������ ���� ���������� � �������� ������")
    
    def drag_to(self, x, y, button='left'):
        """���������� � ������� ������� ����"""
        raise NotImplementedError("����� ������ ���� ���������� � �������� ������")
    
    def scroll(self, amount):
        """���������� ������ ����"""
        raise NotImplementedError("����� ������ ���� ���������� � �������� ������")


class InputController:
    """���������� �����, ������������ ���������� � ����"""
    
    def __init__(self, keyboard, mouse):
        self.keyboard = keyboard
        self.mouse = mouse
    
    def perform_action(self, action_type, **params):
        """
        ��������� �������� �����
        
        Args:
            action_type (str): ��� �������� ('key_press', 'mouse_click', � �.�.)
            **params: ��������� ��������
        
        Returns:
            bool: True, ���� �������� ��������� �������
        """
        if action_type == 'key_press':
            return self.keyboard.press_key(params.get('key'))
        elif action_type == 'key_release':
            return self.keyboard.release_key(params.get('key'))
        elif action_type == 'type_text':
            return self.keyboard.type_text(params.get('text'))
        elif action_type == 'hotkey':
            return self.keyboard.hotkey(*params.get('keys', []))
        elif action_type == 'mouse_move':
            return self.mouse.move_to(params.get('x'), params.get('y'))
        elif action_type == 'mouse_click':
            return self.mouse.click(params.get('button', 'left'))
        elif action_type == 'mouse_double_click':
            return self.mouse.double_click(params.get('button', 'left'))
        elif action_type == 'mouse_drag':
            return self.mouse.drag_to(
                params.get('x'), 
                params.get('y'),
                params.get('button', 'left')
            )
        elif action_type == 'mouse_scroll':
            return self.mouse.scroll(params.get('amount'))
        else:
            from core.common.error_handler import handle_error
            handle_error(f"����������� ��� ��������: {action_type}", module='input')
            return False
