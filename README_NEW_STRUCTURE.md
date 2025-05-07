
# ����� ��������� ������� neuro-link-assistant

������ ��� ������������� ��� ���������� ������������ � ��������� �����������. ���� ������� ����� ��������� �������.

## �������� ���������

1. **���������� �� ���������-��������� � ���������-����������� ���**
   - ����� ���������� � ����������: `core/common/`
   - ���������-��������� ����������: `core/platform/windows/`

2. **���������� ������������**
   - ���������� ������ �������� �������
   - ���������� ����������� ������
   - ���������� ������ �������� ����� (���������� � ����)
   - ���������� ������ ���������� ����������
   - ���������� ������ ���������� ������

3. **������� ��� ������� � �����������**
   - `core/filesystem/__init__.py` - ��������� ���������� �������� �������
   - `core/input/__init__.py` - ��������� ����������� �����
   - `core/process/__init__.py` - ��������� ��������� ���������
   - `core/window/__init__.py` - ��������� ��������� ����

## ����� ��������� ���������

## ������� ������������� ����� ���������

### ������ � �������� ��������


from core.filesystem import get_file_system

# ��������� ���������� �������� �������
fs = get_file_system()

# ������������� �������
if fs.file_exists('path/to/file.txt'):
    content = fs.read_file('path/to/file.txt')
    print(content)

from core.input import get_input_controller

# ��������� ����������� �����
input_ctrl = get_input_controller()

# �������� ����������
input_ctrl.keyboard.type_text('Hello, World!')
input_ctrl.keyboard.hotkey('ctrl', 'a')

# �������� ����
input_ctrl.mouse.move_to(100, 100)
input_ctrl.mouse.click()

from core.process import get_process_manager

# ��������� ��������� ���������
proc_mgr = get_process_manager()

# ������ ��������
pid = proc_mgr.start_process('notepad.exe')

# �������� ���������� ���������
if proc_mgr.is_process_running('notepad.exe'):
    print('Notepad �������')

# ���������� ��������
proc_mgr.kill_process(pid)

from core.window import get_window_manager

# ��������� ��������� ����
win_mgr = get_window_manager()

# ��������� ���� �� ���������
notepad_window = win_mgr.get_window_by_title('�������')

if notepad_window:
    # ��������� ����
    win_mgr.activate_window(notepad_window)
    
    # ������������ ����
    win_mgr.maximize_window(notepad_window)
    
    # �������� ����
    win_mgr.close_window(notepad_window)

from core.common.error_handler import handle_error, handle_llm_error

# ����� ��������� ������
try:
    # �����-�� ���
    pass
except Exception as e:
    handle_error("��������� ������", e, module='my_module')

# ��������� ������ LLM
try:
    # ������ � ����������
    pass
except Exception as e:
    handle_llm_error("������ ��� ������ � LLM", e, model="gpt-4", prompt="����� �������")

                      # ����
from core.windows.file_system import FileSystem
fs = FileSystem()

# �����
from core.filesystem import get_file_system
fs = get_file_system()
                     
                     # ����
from core.input.keyboard_controller import KeyboardController
from core.input.mouse_controller import MouseController
kb = KeyboardController()
mouse = MouseController()

# �����
from core.input import get_input_controller
input_ctrl = get_input_controller()
# ����� ����������� input_ctrl.keyboard � input_ctrl.mouse
                     