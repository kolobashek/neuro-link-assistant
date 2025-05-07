import os
import shutil
import glob
import datetime
import psutil

class FileSystem:
    """
    Класс для работы с файловой системой Windows.
    Предоставляет функции для операций с файлами и директориями.
    """
    
    def create_directory(self, path):
        """
        Создает директорию.
        
        Args:
            path (str): Путь к создаваемой директории
            
        Returns:
            bool: True в случае успешного создания или если директория уже существует
        """
        try:
            os.makedirs(path, exist_ok=True)
            return True
        except Exception as e:
            print(f"Error creating directory {path}: {e}")
            return False
    
    def delete_directory(self, path):
        """
        Удаляет директорию.
        
        Args:
            path (str): Путь к удаляемой директории
            
        Returns:
            bool: True в случае успешного удаления
        """
        try:
            if not os.path.exists(path):
                return False
            
            shutil.rmtree(path)
            return True
        except Exception as e:
            print(f"Error deleting directory {path}: {e}")
            return False
    
    def list_directory(self, path):
        """
        Получает список файлов и директорий в указанной директории.
        
        Args:
            path (str): Путь к директории
            
        Returns:
            list: Список имен файлов и директорий
        """
        try:
            if not os.path.exists(path):
                return []
            
            # Получаем список файлов и директорий
            items = os.listdir(path)
            
            # Возвращаем только имена файлов и директорий (без полных путей)
            return items
        except Exception as e:
            print(f"Error listing directory {path}: {e}")
            return []
    
    def create_file(self, path, content=""):
        """
        Создает файл с указанным содержимым.
        
        Args:
            path (str): Путь к создаваемому файлу
            content (str, optional): Содержимое файла
            
        Returns:
            bool: True в случае успешного создания
        """
        try:
            # Создаем директорию, если она не существует
            directory = os.path.dirname(path)
            if directory and not os.path.exists(directory):
                os.makedirs(directory, exist_ok=True)
            
            # Создаем файл и записываем содержимое
            with open(path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            return True
        except Exception as e:
            print(f"Error creating file {path}: {e}")
            return False
    
    def read_file(self, path):
        """
        Читает содержимое файла.
        
        Args:
            path (str): Путь к файлу
            
        Returns:
            str: Содержимое файла или None в случае ошибки
        """
        try:
            if not os.path.exists(path):
                return None
            
            with open(path, 'r', encoding='utf-8') as f:
                return f.read()
        except Exception as e:
            print(f"Error reading file {path}: {e}")
            return None
    
    def write_file(self, path, content):
        """
        Записывает содержимое в файл.
        
        Args:
            path (str): Путь к файлу
            content (str): Содержимое для записи
            
        Returns:
            bool: True в случае успешной записи
        """
        try:
            # Создаем директорию, если она не существует
            directory = os.path.dirname(path)
            if directory and not os.path.exists(directory):
                os.makedirs(directory, exist_ok=True)
            
            # Записываем содержимое в файл
            with open(path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            return True
        except Exception as e:
            print(f"Error writing to file {path}: {e}")
            return False
    
    def append_file(self, path, content):
        """
        Добавляет содержимое в конец файла.
        
        Args:
            path (str): Путь к файлу
            content (str): Содержимое для добавления
            
        Returns:
            bool: True в случае успешного добавления
        """
        try:
            # Проверяем, существует ли файл
            if not os.path.exists(path):
                return self.write_file(path, content)
            
            # Добавляем содержимое в конец файла
            with open(path, 'a', encoding='utf-8') as f:
                f.write(content)
            
            return True
        except Exception as e:
            print(f"Error appending to file {path}: {e}")
            return False
    
    def delete_file(self, path):
        """
        Удаляет файл.
        
        Args:
            path (str): Путь к файлу
            
        Returns:
            bool: True в случае успешного удаления
        """
        try:
            if not os.path.exists(path):
                return False
            
            os.remove(path)
            return True
        except Exception as e:
            print(f"Error deleting file {path}: {e}")
            return False
    
    def copy_file(self, source, destination):
        """
        Копирует файл.
        
        Args:
            source (str): Путь к исходному файлу
            destination (str): Путь к целевому файлу
            
        Returns:
            bool: True в случае успешного копирования
        """
        try:
            if not os.path.exists(source):
                return False
            
            # Создаем директорию назначения, если она не существует
            dest_dir = os.path.dirname(destination)
            if dest_dir and not os.path.exists(dest_dir):
                os.makedirs(dest_dir, exist_ok=True)
            
            shutil.copy2(source, destination)
            return True
        except Exception as e:
            print(f"Error copying file from {source} to {destination}: {e}")
            return False
    
    def move_file(self, source, destination):
        """
        Перемещает файл.
        
        Args:
            source (str): Путь к исходному файлу
            destination (str): Путь к целевому файлу
            
        Returns:
            bool: True в случае успешного перемещения
        """
        try:
            if not os.path.exists(source):
                return False
            
            # Создаем директорию назначения, если она не существует
            dest_dir = os.path.dirname(destination)
            if dest_dir and not os.path.exists(dest_dir):
                os.makedirs(dest_dir, exist_ok=True)
            
            shutil.move(source, destination)
            return True
        except Exception as e:
            print(f"Error moving file from {source} to {destination}: {e}")
            return False
    
    def get_file_info(self, path):
        """
        Получает информацию о файле или директории.
        
        Args:
            path (str): Путь к файлу или директории
            
        Returns:
            dict: Словарь с информацией о файле или None в случае ошибки
        """
        try:
            if not os.path.exists(path):
                return None
            
            # Получаем статистику файла
            stats = os.stat(path)
            
            # Формируем словарь с информацией
            info = {
                "path": path,
                "name": os.path.basename(path),
                "size": stats.st_size,
                "created": stats.st_ctime,
                "modified": stats.st_mtime,
                "accessed": stats.st_atime,
                "is_directory": os.path.isdir(path)
            }
            
            return info
        except Exception as e:
            print(f"Error getting file info: {e}")
            return None
    
    def search_files(self, directory, pattern, recursive=False):
        """
        Ищет файлы по шаблону.
        
        Args:
            directory (str): Директория для поиска
            pattern (str): Шаблон поиска (например, "*.txt")
            recursive (bool, optional): Рекурсивный поиск в поддиректориях
            
        Returns:
            list: Список путей к найденным файлам
        """
        try:
            if not os.path.exists(directory):
                return []
            
            # Формируем путь для поиска
            if recursive:
                search_path = os.path.join(directory, "**", pattern)
                return glob.glob(search_path, recursive=True)
            else:
                search_path = os.path.join(directory, pattern)
                return glob.glob(search_path)
        except Exception as e:
            print(f"Error searching files in {directory}: {e}")
            return []
    
    def get_drive_info(self):
        """
        Получает информацию о дисках.
        
        Returns:
            dict: Словарь с информацией о дисках
        """
        try:
            drives = {}
            
            # Получаем список дисков
            partitions = psutil.disk_partitions()
            
            for partition in partitions:
                try:
                    # Пропускаем CD-ROM и другие специальные устройства
                    if 'cdrom' in partition.opts or partition.fstype == '':
                        continue
                    
                    # Получаем информацию о диске
                    usage = psutil.disk_usage(partition.mountpoint)
                    
                    drives[partition.device] = {
                        "mountpoint": partition.mountpoint,
                        "fstype": partition.fstype,
                        "total": usage.total,
                        "used": usage.used,
                        "free": usage.free,
                        "percent": usage.percent
                    }
                except Exception:
                    # Пропускаем диски, к которым нет доступа
                    continue
            
            return drives
        except Exception as e:
            print(f"Error getting drive info: {e}")
            return {}