import os
import shutil
import glob
import stat

class FileSystem:
    """
    Класс для работы с файловой системой Windows.
    """
    
    def create_file(self, path, content=""):
        """
        Создает файл с указанным содержимым.
        
        Args:
            path (str): Путь к файлу
            content (str, optional): Содержимое файла
            
        Returns:
            bool: True в случае успешного создания
        """
        try:
            # Создаем директории, если они не существуют
            directory = os.path.dirname(path)
            if directory and not os.path.exists(directory):
                os.makedirs(directory)
            
            # Записываем содержимое в файл
            with open(path, 'w', encoding='utf-8') as file:
                file.write(content)
            
            return True
        except Exception as e:
            print(f"Error creating file: {e}")
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
            with open(path, 'r', encoding='utf-8') as file:
                return file.read()
        except Exception as e:
            print(f"Error reading file: {e}")
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
            with open(path, 'w', encoding='utf-8') as file:
                file.write(content)
            return True
        except Exception as e:
            print(f"Error writing file: {e}")
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
            with open(path, 'a', encoding='utf-8') as file:
                file.write(content)
            return True
        except Exception as e:
            print(f"Error appending to file: {e}")
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
            if os.path.exists(path):
                os.remove(path)
                return True
            return False
        except Exception as e:
            print(f"Error deleting file: {e}")
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
            # Создаем директории назначения, если они не существуют
            dest_dir = os.path.dirname(destination)
            if dest_dir and not os.path.exists(dest_dir):
                os.makedirs(dest_dir)
            
            shutil.copy2(source, destination)
            return True
        except Exception as e:
            print(f"Error copying file: {e}")
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
            # Создаем директории назначения, если они не существуют
            dest_dir = os.path.dirname(destination)
            if dest_dir and not os.path.exists(dest_dir):
                os.makedirs(dest_dir)
            
            shutil.move(source, destination)
            return True
        except Exception as e:
            print(f"Error moving file: {e}")
            return False
    
    def create_directory(self, path):
        """
        Создает директорию.
        
        Args:
            path (str): Путь к директории
            
        Returns:
            bool: True в случае успешного создания
        """
        try:
            if not os.path.exists(path):
                os.makedirs(path)
                return True
            return False
        except Exception as e:
            print(f"Error creating directory: {e}")
            return False
    
    def delete_directory(self, path, recursive=False):
        """
        Удаляет директорию.
        
        Args:
            path (str): Путь к директории
            recursive (bool, optional): Удалять рекурсивно
            
        Returns:
            bool: True в случае успешного удаления
        """
        try:
            if os.path.exists(path):
                if recursive:
                    shutil.rmtree(path)
                else:
                    os.rmdir(path)
                return True
            return False
        except Exception as e:
            print(f"Error deleting directory: {e}")
            return False
    
    def list_directory(self, path, pattern="*"):
        """
        Получает список файлов и директорий.
        
        Args:
            path (str): Путь к директории
            pattern (str, optional): Шаблон для фильтрации
            
        Returns:
            list: Список файлов и директорий
        """
        try:
            if not os.path.exists(path):
                return []
            
            items = []
            for item in glob.glob(os.path.join(path, pattern)):
                item_info = {
                    "name": os.path.basename(item),
                    "path": item,
                    "is_dir": os.path.isdir(item),
                    "size": os.path.getsize(item) if os.path.isfile(item) else 0,
                    "modified": os.path.getmtime(item)
                }
                items.append(item_info)
            
            return items
        except Exception as e:
            print(f"Error listing directory: {e}")
            return []
    
    def get_file_info(self, path):
        """
        Получает информацию о файле.
        
        Args:
            path (str): Путь к файлу
            
        Returns:
            dict: Информация о файле или None в случае ошибки
        """
        try:
            if not os.path.exists(path):
                return None
            
            stat_info = os.stat(path)
            
            return {
                "name": os.path.basename(path),
                "path": path,
                "is_dir": os.path.isdir(path),
                "size": stat_info.st_size,
                "created": stat_info.st_ctime,
                "modified": stat_info.st_mtime,
                "accessed": stat_info.st_atime,
                "permissions": stat.filemode(stat_info.st_mode)
            }
        except Exception as e:
            print(f"Error getting file info: {e}")
            return None
    
    def search_files(self, path, pattern, recursive=True):
        """
        Ищет файлы по шаблону.
        
        Args:
            path (str): Путь для поиска
            pattern (str): Шаблон для поиска
            recursive (bool, optional): Искать рекурсивно
            
        Returns:
            list: Список найденных файлов
        """
        try:
            if not os.path.exists(path):
                return []
            
            if recursive:
                return glob.glob(os.path.join(path, "**", pattern), recursive=True)
            else:
                return glob.glob(os.path.join(path, pattern))
        except Exception as e:
            print(f"Error searching files: {e}")
            return []