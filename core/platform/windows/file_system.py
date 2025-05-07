
# Windows-специфичная реализация файловой системы
import os
import shutil
from datetime import datetime
from core.common.file_system import AbstractFileSystem
from core.common.error_handler import handle_error

class WindowsFileSystem(AbstractFileSystem):
    """Реализация файловой системы для Windows"""
    
    def list_directory(self, path):
        """Получить список файлов в директории"""
        try:
            return os.listdir(path)
        except Exception as e:
            handle_error(f"Ошибка при получении списка файлов: {e}", e)
            return []
    
    def file_exists(self, path):
        """Проверить существование файла"""
        return os.path.exists(path)
    
    def create_directory(self, path):
        """Создать директорию"""
        try:
            os.makedirs(path, exist_ok=True)
            return True
        except Exception as e:
            handle_error(f"Ошибка при создании директории: {e}", e)
            return False
    
    def read_file(self, path):
        """Прочитать содержимое файла"""
        try:
            with open(path, 'r', encoding='utf-8') as file:
                return file.read()
        except Exception as e:
            handle_error(f"Ошибка при чтении файла: {e}", e)
            return None
    
    def write_file(self, path, content):
        """Записать содержимое в файл"""
        try:
            with open(path, 'w', encoding='utf-8') as file:
                file.write(content)
            return True
        except Exception as e:
            handle_error(f"Ошибка при записи в файл: {e}", e)
            return False
    
    def delete_file(self, path):
        """Удалить файл"""
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
        """Получить размер файла"""
        try:
            return os.path.getsize(path)
        except Exception as e:
            handle_error(f"Ошибка при получении размера файла: {e}", e)
            return -1
    
    def get_file_modification_time(self, path):
        """Получить время последней модификации файла"""
        try:
            timestamp = os.path.getmtime(path)
            return datetime.fromtimestamp(timestamp)
        except Exception as e:
            handle_error(f"Ошибка при получении времени модификации: {e}", e)
            return None
