import os
import shutil

# 1. Создать необходимые директории
def create_structure():
    new_dirs = [
        'core/common',
        'core/platform',
        'core/platform/windows'
    ]
    for directory in new_dirs:
        os.makedirs(directory, exist_ok=True)
    
    print("Создана новая структура директорий")

# 2. Объединение файловой системы
def merge_filesystem_modules():
    # Создать новый файл
    with open('core/common/file_system.py', 'w') as new_file:
        new_file.write("""
# Объединенный модуль файловой системы
# Содержит абстрактный класс и платформо-независимую функциональность

class AbstractFileSystem:
    \"\"\"Абстрактный класс для работы с файловой системой\"\"\"
    
    def list_directory(self, path):
        \"\"\"Получить список файлов в директории\"\"\"
        raise NotImplementedError("Метод должен быть реализован в дочернем классе")
    
    def file_exists(self, path):
        \"\"\"Проверить существование файла\"\"\"
        raise NotImplementedError("Метод должен быть реализован в дочернем классе")
    
    def create_directory(self, path):
        \"\"\"Создать директорию\"\"\"
        raise NotImplementedError("Метод должен быть реализован в дочернем классе")
    
    def read_file(self, path):
        \"\"\"Прочитать содержимое файла\"\"\"
        raise NotImplementedError("Метод должен быть реализован в дочернем классе")
    
    def write_file(self, path, content):
        \"\"\"Записать содержимое в файл\"\"\"
        raise NotImplementedError("Метод должен быть реализован в дочернем классе")
    
    def delete_file(self, path):
        \"\"\"Удалить файл\"\"\"
        raise NotImplementedError("Метод должен быть реализован в дочернем классе")
    
    def get_file_size(self, path):
        \"\"\"Получить размер файла\"\"\"
        raise NotImplementedError("Метод должен быть реализован в дочернем классе")
    
    def get_file_modification_time(self, path):
        \"\"\"Получить время последней модификации файла\"\"\"
        raise NotImplementedError("Метод должен быть реализован в дочернем классе")
""")
    
    # Создать Windows-специфичную реализацию
    with open('core/platform/windows/file_system.py', 'w') as windows_file:
        windows_file.write("""
# Windows-специфичная реализация файловой системы
import os
import shutil
from datetime import datetime
from core.common.file_system import AbstractFileSystem
from core.error_handler import handle_error

class WindowsFileSystem(AbstractFileSystem):
    \"\"\"Реализация файловой системы для Windows\"\"\"
    
    def list_directory(self, path):
        \"\"\"Получить список файлов в директории\"\"\"
        try:
            return os.listdir(path)
        except Exception as e:
            handle_error(f"Ошибка при получении списка файлов: {e}", e)
            return []
    
    def file_exists(self, path):
        \"\"\"Проверить существование файла\"\"\"
        return os.path.exists(path)
    
    def create_directory(self, path):
        \"\"\"Создать директорию\"\"\"
        try:
            os.makedirs(path, exist_ok=True)
            return True
        except Exception as e:
            handle_error(f"Ошибка при создании директории: {e}", e)
            return False
    
    def read_file(self, path):
        \"\"\"Прочитать содержимое файла\"\"\"
        try:
            with open(path, 'r', encoding='utf-8') as file:
                return file.read()
        except Exception as e:
            handle_error(f"Ошибка при чтении файла: {e}", e)
            return None
    
    def write_file(self, path, content):
        \"\"\"Записать содержимое в файл\"\"\"
        try:
            with open(path, 'w', encoding='utf-8') as file:
                file.write(content)
            return True
        except Exception as e:
            handle_error(f"Ошибка при записи в файл: {e}", e)
            return False
    
    def delete_file(self, path):
        \"\"\"Удалить файл\"\"\"
        try:
            if os.path.isfile(path):
                os.remove(path)
            elif os.path.isdir(path):
                shutil.rmtree(path)
            return True
        except Exception as e:
            handle_error(f"Ошибка при удалении файла: {e}", e)
            return False
    
    def get_file_size(self, path):
        \"\"\"Получить размер файла\"\"\"
        try:
            return os.path.getsize(path)
        except Exception as e:
            handle_error(f"Ошибка при получении размера файла: {e}", e)
            return -1
    
    def get_file_modification_time(self, path):
        \"\"\"Получить время последней модификации файла\"\"\"
        try:
            timestamp = os.path.getmtime(path)
            return datetime.fromtimestamp(timestamp)
        except Exception as e:
            handle_error(f"Ошибка при получении времени модификации: {e}", e)
            return None
""")
    
    # Создать фабрику для получения нужной реализации
    with open('core/filesystem/__init__.py', 'w') as init_file:
        init_file.write("""
# Модуль файловой системы
import platform

def get_file_system():
    \"\"\"Возвращает платформо-зависимую реализацию файловой системы\"\"\"
    system = platform.system().lower()
    
    if system == 'windows':
        from core.platform.windows.file_system import WindowsFileSystem
        return WindowsFileSystem()
    else:
        raise NotImplementedError(f"Платформа {system} не поддерживается")
""")
    
    print("Объединены модули файловой системы")

# 3. Объединение обработчиков ошибок
def merge_error_handlers():
    # Проверяем, существуют ли файлы
    core_handler_path = 'core/error_handler.py'
    llm_handler_path = 'core/llm/error_handler.py'
    
    core_content = ""
    if os.path.exists(core_handler_path):
        try:
            # Пробуем сначала UTF-8
            try:
                with open(core_handler_path, 'r', encoding='utf-8') as f:
                    core_content = f.read()
            except UnicodeDecodeError:
                # Если UTF-8 не сработал, пробуем cp1251
                with open(core_handler_path, 'r', encoding='cp1251') as f:
                    core_content = f.read()
        except Exception as e:
            print(f"Предупреждение: не удалось прочитать файл {core_handler_path}: {e}")
    
    llm_content = ""
    if os.path.exists(llm_handler_path):
        try:
            # Пробуем сначала UTF-8
            try:
                with open(llm_handler_path, 'r', encoding='utf-8') as f:
                    llm_content = f.read()
            except UnicodeDecodeError:
                # Если UTF-8 не сработал, пробуем cp1251
                with open(llm_handler_path, 'r', encoding='cp1251') as f:
                    llm_content = f.read()
        except Exception as e:
            print(f"Предупреждение: не удалось прочитать файл {llm_handler_path}: {e}")
    
    # Создаем новый объединенный обработчик ошибок
    with open('core/common/error_handler.py', 'w') as new_file:
        new_file.write("""
# Объединенный обработчик ошибок
import logging
import traceback
import sys

# Настройка логирования
logger = logging.getLogger('error_handler')

def handle_error(message, exception=None, module='general', log_level='error'):
    \"\"\"
    Обработка ошибок с логированием
    
    Args:
        message (str): Сообщение об ошибке
        exception (Exception, optional): Исключение, вызвавшее ошибку
        module (str, optional): Модуль, в котором произошла ошибка
        log_level (str, optional): Уровень логирования ('error', 'warning', 'critical')
    
    Returns:
        bool: True, если ошибка обработана, False в противном случае
    \"\"\"
    # Формируем полное сообщение
    full_message = f"[{module}] {message}"
    
    # Если предоставлено исключение, добавляем трассировку
    if exception:
        trace = ''.join(traceback.format_exception(
            type(exception), exception, exception.__traceback__
        ))
        full_message += f"\\nException: {str(exception)}\\nTraceback: {trace}"
    
    # Логируем в зависимости от уровня
    if log_level.lower() == 'warning':
        logger.warning(full_message)
    elif log_level.lower() == 'critical':
        logger.critical(full_message)
    else:
        logger.error(full_message)
    
    return True

def handle_llm_error(message, exception=None, model=None, prompt=None):
    \"\"\"
    Специализированный обработчик ошибок для LLM
    
    Args:
        message (str): Сообщение об ошибке
        exception (Exception, optional): Исключение, вызвавшее ошибку
        model (str, optional): Модель LLM, вызвавшая ошибку
        prompt (str, optional): Промпт, вызвавший ошибку
    
    Returns:
        bool: True, если ошибка обработана, False в противном случае
    \"\"\"
    # Формируем детали ошибки
    details = f"LLM Error"
    if model:
        details += f" in model {model}"
    if prompt:
        # Обрезаем длинные промпты
        max_prompt_length = 100
        short_prompt = prompt[:max_prompt_length] + "..." if len(prompt) > max_prompt_length else prompt
        details += f"\\nPrompt: {short_prompt}"
    
    # Используем общий обработчик с модулем 'llm'
    return handle_error(f"{message}\\n{details}", exception, module='llm')
""")
    
    # Создаем ссылку из старого местоположения на новое
    with open('core/error_handler.py', 'w') as link_file:
        link_file.write("""
# Реэкспорт из нового местоположения
from core.common.error_handler import handle_error, handle_llm_error

# Для обеспечения обратной совместимости
__all__ = ['handle_error', 'handle_llm_error']
""")
    
    # Удаляем старый файл LLM error handler, если он существует
    if os.path.exists(llm_handler_path):
        # Создаем ссылку в директории LLM
        with open(llm_handler_path, 'w') as llm_link:
            llm_link.write("""
# Реэкспорт из нового местоположения
from core.common.error_handler import handle_llm_error, handle_error

# Для обеспечения обратной совместимости
__all__ = ['handle_llm_error', 'handle_error']
""")
    
    print("Объединены обработчики ошибок")

# 4. Объединение модулей эмуляции ввода
def merge_input_modules():
    # Создаем структуру директорий
    os.makedirs('core/common/input', exist_ok=True)
    os.makedirs('core/platform/windows/input', exist_ok=True)
    
    # Создаем базовые абстрактные классы
    with open('core/common/input/base.py', 'w') as base_file:
        base_file.write("""
# Базовые абстрактные классы ввода
class AbstractKeyboard:
    \"\"\"Абстрактный класс для эмуляции клавиатуры\"\"\"
    
    def press_key(self, key):
        \"\"\"Нажать клавишу\"\"\"
        raise NotImplementedError("Метод должен быть реализован в дочернем классе")
    
    def release_key(self, key):
        \"\"\"Отпустить клавишу\"\"\"
        raise NotImplementedError("Метод должен быть реализован в дочернем классе")
    
    def press_and_release(self, key):
        \"\"\"Нажать и отпустить клавишу\"\"\"
        self.press_key(key)
        self.release_key(key)
    
    def type_text(self, text):
        \"\"\"Напечатать текст\"\"\"
        raise NotImplementedError("Метод должен быть реализован в дочернем классе")
    
    def hotkey(self, *keys):
        \"\"\"Нажать комбинацию клавиш\"\"\"
        raise NotImplementedError("Метод должен быть реализован в дочернем классе")


class AbstractMouse:
    \"\"\"Абстрактный класс для эмуляции мыши\"\"\"
    
    def move_to(self, x, y):
        \"\"\"Переместить курсор в указанные координаты\"\"\"
        raise NotImplementedError("Метод должен быть реализован в дочернем классе")
    
    def click(self, button='left'):
        \"\"\"Кликнуть указанной кнопкой мыши\"\"\"
        raise NotImplementedError("Метод должен быть реализован в дочернем классе")
    
    def double_click(self, button='left'):
        \"\"\"Сделать двойной клик\"\"\"
        raise NotImplementedError("Метод должен быть реализован в дочернем классе")
    
    def drag_to(self, x, y, button='left'):
        \"\"\"Перетащить с зажатой кнопкой мыши\"\"\"
        raise NotImplementedError("Метод должен быть реализован в дочернем классе")
    
    def scroll(self, amount):
        \"\"\"Прокрутить колесо мыши\"\"\"
        raise NotImplementedError("Метод должен быть реализован в дочернем классе")


class InputController:
    \"\"\"Контроллер ввода, объединяющий клавиатуру и мышь\"\"\"
    
    def __init__(self, keyboard, mouse):
        self.keyboard = keyboard
        self.mouse = mouse
    
    def perform_action(self, action_type, **params):
        \"\"\"
        Выполнить действие ввода
        
        Args:
            action_type (str): Тип действия ('key_press', 'mouse_click', и т.д.)
            **params: Параметры действия
        
        Returns:
            bool: True, если действие выполнено успешно
        \"\"\"
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
            handle_error(f"Неизвестный тип действия: {action_type}", module='input')
            return False
""")
    
    # Создаем Windows-специфичные реализации
    with open('core/platform/windows/input/keyboard.py', 'w') as kb_file:
        kb_file.write("""
# Windows-специфичная реализация эмуляции клавиатуры
import time
try:
    import pyautogui
except ImportError:
    pyautogui = None

from core.common.input.base import AbstractKeyboard
from core.common.error_handler import handle_error

class WindowsKeyboard(AbstractKeyboard):
    \"\"\"Реализация эмуляции клавиатуры для Windows с использованием PyAutoGUI\"\"\"
    
    def __init__(self):
        if pyautogui is None:
            handle_error("PyAutoGUI не установлен. Установите его: pip install pyautogui", 
                        module='keyboard')
    
    def press_key(self, key):
        \"\"\"Нажать клавишу\"\"\"
        try:
            if pyautogui:
                pyautogui.keyDown(key)
            return True
        except Exception as e:
            handle_error(f"Ошибка при нажатии клавиши {key}: {e}", e, module='keyboard')
            return False
    
    def release_key(self, key):
        \"\"\"Отпустить клавишу\"\"\"
        try:
            if pyautogui:
                pyautogui.keyUp(key)
            return True
        except Exception as e:
            handle_error(f"Ошибка при отпускании клавиши {key}: {e}", e, module='keyboard')
            return False
    
    def type_text(self, text):
        \"\"\"Напечатать текст\"\"\"
        try:
            if pyautogui:
                pyautogui.write(text)
            return True
        except Exception as e:
            handle_error(f"Ошибка при вводе текста: {e}", e, module='keyboard')
            return False
    
    def hotkey(self, *keys):
        \"\"\"Нажать комбинацию клавиш\"\"\"
        try:
            if pyautogui:
                pyautogui.hotkey(*keys)
            return True
        except Exception as e:
            handle_error(f"Ошибка при нажатии комбинации клавиш {keys}: {e}", e, module='keyboard')
            return False
""")
    
    with open('core/platform/windows/input/mouse.py', 'w') as mouse_file:
        mouse_file.write("""
# Windows-специфичная реализация эмуляции мыши
import time
try:
    import pyautogui
except ImportError:
    pyautogui = None

from core.common.input.base import AbstractMouse
from core.common.error_handler import handle_error

class WindowsMouse(AbstractMouse):
    \"\"\"Реализация эмуляции мыши для Windows с использованием PyAutoGUI\"\"\"
    
    def __init__(self):
        if pyautogui is None:
            handle_error("PyAutoGUI не установлен. Установите его: pip install pyautogui", 
                        module='mouse')
        
        # Настройка параметров
        self.duration = 0.1  # Длительность движения мыши
    
    def move_to(self, x, y):
        \"\"\"Переместить курсор в указанные координаты\"\"\"
        try:
            if pyautogui:
                pyautogui.moveTo(x, y, duration=self.duration)
            return True
        except Exception as e:
            handle_error(f"Ошибка при перемещении мыши на координаты ({x}, {y}): {e}", 
                        e, module='mouse')
            return False
    
    def click(self, button='left'):
        \"\"\"Кликнуть указанной кнопкой мыши\"\"\"
        try:
            if pyautogui:
                pyautogui.click(button=button)
            return True
        except Exception as e:
            handle_error(f"Ошибка при клике мышью ({button}): {e}", e, module='mouse')
            return False
    
    def double_click(self, button='left'):
        \"\"\"Сделать двойной клик\"\"\"
        try:
            if pyautogui:
                pyautogui.doubleClick(button=button)
            return True
        except Exception as e:
            handle_error(f"Ошибка при двойном клике мышью ({button}): {e}", e, module='mouse')
            return False
    
    def drag_to(self, x, y, button='left'):
        \"\"\"Перетащить с зажатой кнопкой мыши\"\"\"
        try:
            if pyautogui:
                pyautogui.dragTo(x, y, duration=self.duration, button=button)
            return True
        except Exception as e:
            handle_error(f"Ошибка при перетаскивании мышью на координаты ({x}, {y}): {e}", 
                        e, module='mouse')
            return False
    
    def scroll(self, amount):
        \"\"\"Прокрутить колесо мыши\"\"\"
        try:
            if pyautogui:
                pyautogui.scroll(amount)
            return True
        except Exception as e:
            handle_error(f"Ошибка при прокрутке колеса мыши: {e}", e, module='mouse')
            return False
""")
    
    # Создаем фабрику ввода
    with open('core/input/__init__.py', 'w') as init_file:
        init_file.write("""
# Модуль ввода
import platform
from core.common.input.base import InputController

def get_input_controller():
    \"\"\"Возвращает платформо-зависимый контроллер ввода\"\"\"
    system = platform.system().lower()
    
    if system == 'windows':
        from core.platform.windows.input.keyboard import WindowsKeyboard
        from core.platform.windows.input.mouse import WindowsMouse
        return InputController(WindowsKeyboard(), WindowsMouse())
    else:
        raise NotImplementedError(f"Платформа {system} не поддерживается")
""")
    
    print("Объединены модули эмуляции ввода")

# 5. Объединение модулей управления процессами Windows
def merge_process_modules():
    # Создаем Windows-специфичную реализацию управления процессами
    with open('core/platform/windows/process_manager.py', 'w') as process_file:
        process_file.write("""
# Windows-специфичная реализация управления процессами
import os
import subprocess
import psutil
import time
from core.common.error_handler import handle_error

class WindowsProcessManager:
    \"\"\"Управление процессами в Windows\"\"\"
    
    def start_process(self, command, shell=True, cwd=None, env=None):
        \"\"\"
        Запустить процесс
        
        Args:
            command (str): Команда для запуска
            shell (bool): Использовать ли оболочку
            cwd (str, optional): Рабочая директория
            env (dict, optional): Переменные окружения
        
        Returns:
            int: ID процесса или None в случае ошибки
        \"\"\"
        try:
            process = subprocess.Popen(
                command, 
                shell=shell, 
                cwd=cwd, 
                env=env
            )
            return process.pid
        except Exception as e:
            handle_error(f"Ошибка при запуске процесса '{command}': {e}", e, module='process')
            return None
    
    def kill_process(self, pid):
        \"\"\"
        Завершить процесс по ID
        
        Args:
            pid (int): ID процесса
        
        Returns:
            bool: True, если процесс успешно завершен
        \"\"\"
        try:
            if psutil.pid_exists(pid):
                process = psutil.Process(pid)
                process.terminate()
                
                # Ждем завершения процесса
                gone, still_alive = psutil.wait_procs([process], timeout=3)
                if still_alive:
                    # Если процесс не завершился, убиваем его
                    process.kill()
                return True
            else:
                handle_error(f"Процесс с ID {pid} не найден", module='process', log_level='warning')
                return False
        except Exception as e:
            handle_error(f"Ошибка при завершении процесса {pid}: {e}", e, module='process')
            return False
    
    def is_process_running(self, name):
        \"\"\"
        Проверить, запущен ли процесс с указанным именем
        
        Args:
            name (str): Имя процесса
        
        Returns:
            bool: True, если процесс запущен
        \"\"\"
        try:
            for proc in psutil.process_iter(['pid', 'name']):
                if name.lower() in proc.info['name'].lower():
                    return True
            return False
        except Exception as e:
            handle_error(f"Ошибка при проверке процесса {name}: {e}", e, module='process')
            return False
    
    def get_process_by_name(self, name):
        \"\"\"
        Получить список процессов с указанным именем
        
        Args:
            name (str): Имя процесса
        
        Returns:
            list: Список объектов процессов
        \"\"\"
        try:
            matching_processes = []
            for proc in psutil.process_iter(['pid', 'name']):
                if name.lower() in proc.info['name'].lower():
                    matching_processes.append(proc)
            return matching_processes
        except Exception as e:
            handle_error(f"Ошибка при получении процесса {name}: {e}", e, module='process')
            return []
    
    def get_all_processes(self):
        \"\"\"
        Получить список всех запущенных процессов
        
        Returns:
            list: Список объектов процессов
        \"\"\"
        try:
            return list(psutil.process_iter(['pid', 'name', 'username']))
        except Exception as e:
            handle_error(f"Ошибка при получении списка процессов: {e}", e, module='process')
            return []
""")    # Создаем фабрику для управления процессами
    with open('core/process/__init__.py', 'w') as init_file:
        init_file.write("""
# Модуль управления процессами
import platform

def get_process_manager():
    \"""Возвращает платформо-зависимый менеджер процессов\"""
    system = platform.system().lower()
    
    if system == 'windows':
        from core.platform.windows.process_manager import WindowsProcessManager
        return WindowsProcessManager()
    else:
        raise NotImplementedError(f"Платформа {system} не поддерживается")
""")    
        print("Объединены модули управления процессами")

# 6. Объединение модулей управления окнами
def merge_window_modules():
    # Создаем Windows-специфичную реализацию управления окнами
    with open('core/platform/windows/window_manager.py', 'w') as window_file:
        window_file.write("""
# Windows-специфичная реализация управления окнами
import time
try:
    import pygetwindow as gw
except ImportError:
    gw = None

from core.common.error_handler import handle_error

class WindowsWindowManager:
    \"""Управление окнами в Windows\"""
    
    def __init__(self):
        if gw is None:
            handle_error("PyGetWindow не установлен. Установите его: pip install pygetwindow", 
                        module='window')
    
    def get_all_windows(self):
        \"""
        Получить список всех окон
        
        Returns:
            list: Список объектов окон
        \"""
        try:
            if gw:
                return gw.getAllWindows()
            return []
        except Exception as e:
            handle_error(f"Ошибка при получении списка окон: {e}", e, module='window')
            return []
    
    def get_window_by_title(self, title):
        \"""
        Найти окно по заголовку (частичное совпадение)
        
        Args:
            title (str): Заголовок окна
        
        Returns:
            object: Объект окна или None, если окно не найдено
        \"""
        try:
            if gw:
                matching_windows = gw.getWindowsWithTitle(title)
                if matching_windows:
                    return matching_windows[0]
            return None
        except Exception as e:
            handle_error(f"Ошибка при поиске окна '{title}': {e}", e, module='window')
            return None
    
    def activate_window(self, window):
        \"""
        Активировать окно
        
        Args:
            window: Объект окна
        
        Returns:
            bool: True, если окно успешно активировано
        \"""
        try:
            if window:
                window.activate()
                # Даем время на активацию окна
                time.sleep(0.5)
                return True
            return False
        except Exception as e:
            handle_error(f"Ошибка при активации окна: {e}", e, module='window')
            return False
    
    def close_window(self, window):
        \"""
        Закрыть окно
        
        Args:
            window: Объект окна
        
        Returns:
            bool: True, если окно успешно закрыто
        \"""
        try:
            if window:
                window.close()
                return True
            return False
        except Exception as e:
            handle_error(f"Ошибка при закрытии окна: {e}", e, module='window')
            return False
    
    def minimize_window(self, window):
        \"""
        Свернуть окно
        
        Args:
            window: Объект окна
        
        Returns:
            bool: True, если окно успешно свернуто
        \"""
        try:
            if window:
                window.minimize()
                return True
            return False
        except Exception as e:
            handle_error(f"Ошибка при сворачивании окна: {e}", e, module='window')
            return False
    
    def maximize_window(self, window):
        \"""
        Развернуть окно
        
        Args:
            window: Объект окна
        
        Returns:
            bool: True, если окно успешно развернуто
        \"""
        try:
            if window:
                window.maximize()
                return True
            return False
        except Exception as e:
            handle_error(f"Ошибка при разворачивании окна: {e}", e, module='window')
            return False
    
    def wait_for_window(self, title, timeout=10):
        \"""
        Ждать появления окна с заданным заголовком
        
        Args:
            title (str): Заголовок окна
            timeout (int): Таймаут в секундах
        
        Returns:
            object: Объект окна или None, если окно не появилось за указанное время
        \"""
        try:
            start_time = time.time()
            while time.time() - start_time < timeout:
                window = self.get_window_by_title(title)
                if window:
                    return window
                time.sleep(0.5)
            return None
        except Exception as e:
            handle_error(f"Ошибка при ожидании окна '{title}': {e}", e, module='window')
            return None
""")    # Создаем фабрику для управления окнами
    with open('core/window/__init__.py', 'w') as init_file:
        init_file.write("""
# Модуль управления окнами
import platform

def get_window_manager():
    \"""Возвращает платформо-зависимый менеджер окон\"""
    system = platform.system().lower()
    
    if system == 'windows':
        from core.platform.windows.window_manager import WindowsWindowManager
        return WindowsWindowManager()
    else:
        raise NotImplementedError(f"Платформа {system} не поддерживается")
""")    
        print("Объединены модули управления окнами")

# 7. Обновление структуры импортов в существующих файлах
def update_imports():
    # Список файлов и директорий, которые нужно обработать
    dirs_to_process = [
        'core', 
        'routes', 
        'services', 
        'utils', 
        'tests'
    ]
    
    import_replacements = {
        'from core.error_handler import': 'from core.common.error_handler import',
        'from core.windows.file_system import': 'from core.filesystem import get_file_system',
        'from core.windows.filesystem_manager import': 'from core.filesystem import get_file_system',
        'from core.filesystem.file_manager import': 'from core.filesystem import get_file_system',
        'from core.input.keyboard_controller import': 'from core.input import get_input_controller',
        'from core.input.keyboard_emulator import': 'from core.input import get_input_controller',
        'from core.input.mouse_controller import': 'from core.input import get_input_controller',
        'from core.input.mouse_emulator import': 'from core.input import get_input_controller',
        'from core.windows.process_manager import': 'from core.process import get_process_manager',
        'from core.windows.window_manager import': 'from core.window import get_window_manager',
    }
    
    print("Процесс обновления импортов может занять некоторое время...")
    
    for directory in dirs_to_process:
        if os.path.exists(directory):
            for root, _, files in os.walk(directory):
                for file in files:
                    if file.endswith('.py'):
                        file_path = os.path.join(root, file)
                        try:
                            # Пробуем сначала UTF-8
                            try:
                                with open(file_path, 'r', encoding='utf-8') as f:
                                    content = f.read()
                            except UnicodeDecodeError:
                                # Если UTF-8 не сработал, пробуем cp1251 (стандарт для Windows в русской локали)
                                with open(file_path, 'r', encoding='cp1251') as f:
                                    content = f.read()
                            
                            # Заменяем импорты
                            modified = False
                            for old_import, new_import in import_replacements.items():
                                if old_import in content:
                                    content = content.replace(old_import, new_import)
                                    modified = True
                            
                            # Сохраняем изменения только если были модификации
                            if modified:
                                with open(file_path, 'w', encoding='utf-8') as f:
                                    f.write(content)
                                print(f"Обновлены импорты в файле: {file_path}")
                        except Exception as e:
                            print(f"Ошибка при обработке файла {file_path}: {e}")
                            # Пропускаем проблемные файлы, но продолжаем работу
                            continue
    
    print("Обновление импортов завершено")

# 8. Создание README с новой структурой проекта
def create_readme():
    with open('README_NEW_STRUCTURE.md', 'w') as readme:
        readme.write("""
# Новая структура проекта neuro-link-assistant

Проект был реорганизован для устранения дублирования и улучшения модульности. Ниже описана новая структура проекта.

## Основные изменения

1. **Разделение на платформо-зависимый и платформо-независимый код**
   - Общие интерфейсы и абстракции: `core/common/`
   - Платформо-зависимая реализация: `core/platform/windows/`

2. **Устранение дублирования**
   - Объединены модули файловой системы
   - Объединены обработчики ошибок
   - Объединены модули эмуляции ввода (клавиатура и мышь)
   - Объединены модули управления процессами
   - Объединены модули управления окнами

3. **Фабрики для доступа к реализациям**
   - `core/filesystem/__init__.py` - получение реализации файловой системы
   - `core/input/__init__.py` - получение контроллера ввода
   - `core/process/__init__.py` - получение менеджера процессов
   - `core/window/__init__.py` - получение менеджера окон

## Новая структура каталогов

## Примеры использования новой структуры

### Работа с файловой системой


from core.filesystem import get_file_system

# Получение экземпляра файловой системы
fs = get_file_system()

# Использование методов
if fs.file_exists('path/to/file.txt'):
    content = fs.read_file('path/to/file.txt')
    print(content)

from core.input import get_input_controller

# Получение контроллера ввода
input_ctrl = get_input_controller()

# Эмуляция клавиатуры
input_ctrl.keyboard.type_text('Hello, World!')
input_ctrl.keyboard.hotkey('ctrl', 'a')

# Эмуляция мыши
input_ctrl.mouse.move_to(100, 100)
input_ctrl.mouse.click()

from core.process import get_process_manager

# Получение менеджера процессов
proc_mgr = get_process_manager()

# Запуск процесса
pid = proc_mgr.start_process('notepad.exe')

# Проверка запущенных процессов
if proc_mgr.is_process_running('notepad.exe'):
    print('Notepad запущен')

# Завершение процесса
proc_mgr.kill_process(pid)

from core.window import get_window_manager

# Получение менеджера окон
win_mgr = get_window_manager()

# Получение окна по заголовку
notepad_window = win_mgr.get_window_by_title('Блокнот')

if notepad_window:
    # Активация окна
    win_mgr.activate_window(notepad_window)
    
    # Максимизация окна
    win_mgr.maximize_window(notepad_window)
    
    # Закрытие окна
    win_mgr.close_window(notepad_window)

from core.common.error_handler import handle_error, handle_llm_error

# Общая обработка ошибок
try:
    # Какой-то код
    pass
except Exception as e:
    handle_error("Произошла ошибка", e, module='my_module')

# Обработка ошибок LLM
try:
    # Работа с нейросетью
    pass
except Exception as e:
    handle_llm_error("Ошибка при работе с LLM", e, model="gpt-4", prompt="Текст промпта")

                      # Было
from core.windows.file_system import FileSystem
fs = FileSystem()

# Стало
from core.filesystem import get_file_system
fs = get_file_system()
                     
                     # Было
from core.input.keyboard_controller import KeyboardController
from core.input.mouse_controller import MouseController
kb = KeyboardController()
mouse = MouseController()

# Стало
from core.input import get_input_controller
input_ctrl = get_input_controller()
# Далее используйте input_ctrl.keyboard и input_ctrl.mouse
                     """)
        print("Создан файл README_NEW_STRUCTURE.md с описанием новой структуры проекта")

# 9. Создание скрипта установки зависимостей
def create_requirements():
    with open('requirements.txt', 'w') as req_file:
        req_file.write("""
# Базовые зависимости
flask>=2.0.0
werkzeug>=2.0.0
python-dotenv>=0.19.0
pytest>=6.2.5
pytest-cov>=2.12.1

# Зависимости для Windows
pyautogui>=0.9.53
pygetwindow>=0.0.9
psutil>=5.8.0
pywin32>=301; sys_platform == 'win32'

# Зависимости для работы с данными
requests>=2.26.0
beautifulsoup4>=4.10.0
pillow>=8.3.2

# Зависимости для логирования
colorlog>=6.6.0
""")
    
    print("Создан файл requirements.txt с необходимыми зависимостями")

# 10. Собираем все в основную функцию и выполняем рефакторинг
def main():
    print("Начало реорганизации проекта...")
    
    # Создаем резервную копию проекта
    import time
    backup_dir = "backup_" + time.strftime("%Y%m%d_%H%M%S")
    print(f"Создание резервной копии проекта в папке {backup_dir}...")
    
    # Добавляем папки резервных копий в .gitignore
    gitignore_path = '.gitignore'
    gitignore_entry = '\n# Папки резервных копий\nbackup_*/'
    
    try:
        # Проверяем существование .gitignore
        if os.path.exists(gitignore_path):
            with open(gitignore_path, 'r', encoding='utf-8') as f:
                content = f.read()
                
            # Проверяем, есть ли уже запись о резервных копиях
            if 'backup_*/' not in content:
                with open(gitignore_path, 'a', encoding='utf-8') as f:
                    f.write(gitignore_entry)
                print("Папки резервных копий добавлены в .gitignore")
        else:
            # Создаем .gitignore, если его нет
            with open(gitignore_path, 'w', encoding='utf-8') as f:
                f.write(gitignore_entry.lstrip())
            print("Создан файл .gitignore с правилом для папок резервных копий")
    except Exception as e:
        print(f"Предупреждение: не удалось обновить .gitignore: {e}")
    
    try:
        # Копируем все файлы кроме виртуального окружения
        os.makedirs(backup_dir, exist_ok=True)
        for item in os.listdir():
            if item != backup_dir and item != "venv" and item != ".venv" and item != ".git":
                if os.path.isdir(item):
                    shutil.copytree(item, os.path.join(backup_dir, item))
                else:
                    shutil.copy2(item, os.path.join(backup_dir, item))
        
        print("Резервная копия создана успешно")
    except Exception as e:
        print(f"Ошибка при создании резервной копии: {e}")
        return
    
    # Выполняем рефакторинг
    functions = [
        ("Создание структуры директорий", create_structure),
        ("Объединение модулей файловой системы", merge_filesystem_modules),
        ("Объединение обработчиков ошибок", merge_error_handlers),
        ("Объединение модулей эмуляции ввода", merge_input_modules),
        ("Объединение модулей управления процессами", merge_process_modules),
        ("Объединение модулей управления окнами", merge_window_modules),
        ("Обновление импортов", update_imports),
        ("Создание README", create_readme),
        ("Создание файла зависимостей", create_requirements)
    ]
    
    for description, func in functions:
        try:
            print(f"Выполняется: {description}...")
            func()
        except Exception as e:
            print(f"Ошибка при выполнении '{description}': {e}")
            print(f"Пропуск этого шага и продолжение...")
            
    print("\n====================================")
    print("Реорганизация проекта завершена!")
    print("====================================")
    print(f"Резервная копия сохранена в папке: {backup_dir}")
    print("Ознакомьтесь с новой структурой в файле README_NEW_STRUCTURE.md")
    print("Установите необходимые зависимости: pip install -r requirements.txt")

if __name__ == "__main__":
    main()