import os
import shutil
import glob
import json
import csv
import pickle
import zipfile
from pathlib import Path
from datetime import datetime

class FileManager:
    """
    Класс для работы с файловой системой.
    Предоставляет методы для создания, чтения, записи, удаления файлов и директорий.
    """
    
    def create_file(self, path, content="", encoding="utf-8"):
        """
        Создает файл с указанным содержимым.
        
        Args:
            path (str): Путь к файлу
            content (str, optional): Содержимое файла
            encoding (str, optional): Кодировка файла
            
        Returns:
            bool: True в случае успешного создания
        """
        try:
            # Создаем директорию, если она не существует
            directory = os.path.dirname(path)
            if directory and not os.path.exists(directory):
                os.makedirs(directory)
            
            with open(path, 'w', encoding=encoding) as file:
                file.write(content)
            
            return True
        except Exception as e:
            print(f"Error creating file: {e}")
            return False
    
    def read_file(self, path, encoding="utf-8"):
        """
        Читает содержимое файла.
        
        Args:
            path (str): Путь к файлу
            encoding (str, optional): Кодировка файла
            
        Returns:
            str: Содержимое файла или None в случае ошибки
        """
        try:
            with open(path, 'r', encoding=encoding) as file:
                return file.read()
        except Exception as e:
            print(f"Error reading file: {e}")
            return None
    
    def append_to_file(self, path, content, encoding="utf-8"):
        """
        Добавляет содержимое в конец файла.
        
        Args:
            path (str): Путь к файлу
            content (str): Содержимое для добавления
            encoding (str, optional): Кодировка файла
            
        Returns:
            bool: True в случае успешного добавления
        """
        try:
            with open(path, 'a', encoding=encoding) as file:
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
        except Exception as e:
            print(f"Error deleting file: {e}")
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
        except Exception as e:
            print(f"Error creating directory: {e}")
            return False
    
    def delete_directory(self, path):
        """
        Удаляет директорию.
        
        Args:
            path (str): Путь к директории
            
        Returns:
            bool: True в случае успешного удаления
        """
        try:
            if os.path.exists(path):
                shutil.rmtree(path)
            
            return True
        except Exception as e:
            print(f"Error deleting directory: {e}")
            return False
    
    def list_directory(self, path, pattern="*"):
        """
        Получает список файлов в директории.
        
        Args:
            path (str): Путь к директории
            pattern (str, optional): Шаблон для фильтрации файлов
            
        Returns:
            list: Список имен файлов или None в случае ошибки
        """
        try:
            if not os.path.exists(path):
                return None
            
            # Получаем список файлов с учетом шаблона
            files = [os.path.basename(f) for f in glob.glob(os.path.join(path, pattern))]
            
            return files
        except Exception as e:
            print(f"Error listing directory: {e}")
            return None
    
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
            # Создаем директорию назначения, если она не существует
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
            # Создаем директорию назначения, если она не существует
            dest_dir = os.path.dirname(destination)
            if dest_dir and not os.path.exists(dest_dir):
                os.makedirs(dest_dir)
            
            shutil.move(source, destination)
            
            return True
        except Exception as e:
            print(f"Error moving file: {e}")
            return False
    
    def rename_file(self, path, new_name):
        """
        Переименовывает файл.
        
        Args:
            path (str): Путь к файлу
            new_name (str): Новое имя файла (без пути)
            
        Returns:
            bool: True в случае успешного переименования
        """
        try:
            directory = os.path.dirname(path)
            new_path = os.path.join(directory, new_name)
            
            os.rename(path, new_path)
            
            return True
        except Exception as e:
            print(f"Error renaming file: {e}")
            return False
    
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
            
            file_stat = os.stat(path)
            file_path = Path(path)
            
            info = {
                "name": file_path.name,
                "path": str(file_path.absolute()),
                "size": file_stat.st_size,
                "created": datetime.fromtimestamp(file_stat.st_ctime).isoformat(),
                "modified": datetime.fromtimestamp(file_stat.st_mtime).isoformat(),
                "accessed": datetime.fromtimestamp(file_stat.st_atime).isoformat(),
                "is_file": os.path.isfile(path),
                "is_directory": os.path.isdir(path),
                "extension": file_path.suffix
            }
            
            return info
        except Exception as e:
            print(f"Error getting file info: {e}")
            return None
    
    def zip_files(self, file_paths, zip_path):
        """
        Создает ZIP-архив из указанных файлов.
        
        Args:
            file_paths (list): Список путей к файлам
            zip_path (str): Путь к создаваемому ZIP-архиву
            
        Returns:
            bool: True в случае успешного создания архива
        """
        try:
            # Создаем директорию для архива, если она не существует
            zip_dir = os.path.dirname(zip_path)
            if zip_dir and not os.path.exists(zip_dir):
                os.makedirs(zip_dir)
            
            with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                for file_path in file_paths:
                    if os.path.exists(file_path):
                        # Добавляем файл в архив с именем файла (без пути)
                        zipf.write(file_path, os.path.basename(file_path))
            
            return True
        except Exception as e:
            print(f"Error creating ZIP archive: {e}")
            return False
    
    def unzip_file(self, zip_path, extract_to):
        """
        Распаковывает ZIP-архив.
        
        Args:
            zip_path (str): Путь к ZIP-архиву
            extract_to (str): Путь для распаковки
            
        Returns:
            bool: True в случае успешной распаковки
        """
        try:
            # Создаем директорию для распаковки, если она не существует
            if not os.path.exists(extract_to):
                os.makedirs(extract_to)
            
            with zipfile.ZipFile(zip_path, 'r') as zipf:
                zipf.extractall(extract_to)
            
            return True
        except Exception as e:
            print(f"Error extracting ZIP archive: {e}")
            return False
    
    def read_json(self, path):
        """
        Читает JSON-файл.
        
        Args:
            path (str): Путь к JSON-файлу
            
        Returns:
            dict: Данные из JSON-файла или None в случае ошибки
        """
        try:
            with open(path, 'r', encoding='utf-8') as file:
                return json.load(file)
        except Exception as e:
            print(f"Error reading JSON file: {e}")
            return None
    
    def write_json(self, path, data, indent=4):
        """
        Записывает данные в JSON-файл.
        
        Args:
            path (str): Путь к JSON-файлу
            data (dict): Данные для записи
            indent (int, optional): Отступ для форматирования JSON
            
        Returns:
            bool: True в случае успешной записи
        """
        try:
            # Создаем директорию, если она не существует
            directory = os.path.dirname(path)
            if directory and not os.path.exists(directory):
                os.makedirs(directory)
            
            with open(path, 'w', encoding='utf-8') as file:
                json.dump(data, file, indent=indent)
            
            return True
        except Exception as e:
            print(f"Error writing JSON file: {e}")
            return False
    
    def read_csv(self, path, delimiter=','):
        """
        Читает CSV-файл.
        
        Args:
            path (str): Путь к CSV-файлу
            delimiter (str, optional): Разделитель полей
            
        Returns:
            list: Данные из CSV-файла или None в случае ошибки
        """
        try:
            data = []
            with open(path, 'r', encoding='utf-8', newline='') as file:
                csv_reader = csv.reader(file, delimiter=delimiter)
                for row in csv_reader:
                    data.append(row)
            
            return data
        except Exception as e:
            print(f"Error reading CSV file: {e}")
            return None
    
    def write_csv(self, path, data, delimiter=','):
        """
        Записывает данные в CSV-файл.
        
        Args:
            path (str): Путь к CSV-файлу
            data (list): Данные для записи (список списков)
            delimiter (str, optional): Разделитель полей
            
        Returns:
            bool: True в случае успешной записи
        """
        try:
            # Создаем директорию, если она не существует
            directory = os.path.dirname(path)
            if directory and not os.path.exists(directory):
                os.makedirs(directory)
            
            with open(path, 'w', encoding='utf-8', newline='') as file:
                csv_writer = csv.writer(file, delimiter=delimiter)
                csv_writer.writerows(data)
            
            return True
        except Exception as e:
            print(f"Error writing CSV file: {e}")
            return False
    
    def read_binary(self, path):
        """
        Читает бинарный файл.
        
        Args:
            path (str): Путь к файлу
            
        Returns:
            bytes: Содержимое файла или None в случае ошибки
        """
        try:
            with open(path, 'rb') as file:
                return file.read()
        except Exception as e:
            print(f"Error reading binary file: {e}")
            return None
    
    def write_binary(self, path, data):
        """
        Записывает данные в бинарный файл.
        
        Args:
            path (str): Путь к файлу
            data (bytes): Данные для записи
            
        Returns:
            bool: True в случае успешной записи
        """
        try:
            # Создаем директорию, если она не существует
            directory = os.path.dirname(path)
            if directory and not os.path.exists(directory):
                os.makedirs(directory)
            
            with open(path, 'wb') as file:
                file.write(data)
            
            return True
        except Exception as e:
            print(f"Error writing binary file: {e}")
            return False
    
    def read_pickle(self, path):
        """
        Читает объект из файла pickle.
        
        Args:
            path (str): Путь к файлу
            
        Returns:
            object: Объект из файла или None в случае ошибки
        """
        try:
            with open(path, 'rb') as file:
                return pickle.load(file)
        except Exception as e:
            print(f"Error reading pickle file: {e}")
            return None
    
    def write_pickle(self, path, data):
        """
        Записывает объект в файл pickle.
        
        Args:
            path (str): Путь к файлу
            data (object): Объект для записи
            
        Returns:
            bool: True в случае успешной записи
        """
        try:
            # Создаем директорию, если она не существует
            directory = os.path.dirname(path)
            if directory and not os.path.exists(directory):
                os.makedirs(directory)
            
            with open(path, 'wb') as file:
                pickle.dump(data, file)
            
            return True
        except Exception as e:
            print(f"Error writing pickle file: {e}")
            return False
    
    def search_files(self, directory, pattern="*", recursive=False):
        """
        Ищет файлы в директории по шаблону.
        
        Args:
            directory (str): Путь к директории
            pattern (str, optional): Шаблон для поиска
            recursive (bool, optional): Рекурсивный поиск в поддиректориях
            
        Returns:
            list: Список путей к найденным файлам или None в случае ошибки
        """
        try:
            if not os.path.exists(directory):
                return None
            
            if recursive:
                # Рекурсивный поиск
                return [str(path) for path in Path(directory).rglob(pattern) if path.is_file()]
            else:
                # Поиск только в указанной директории
                return [str(path) for path in Path(directory).glob(pattern) if path.is_file()]
        except Exception as e:
            print(f"Error searching files: {e}")
            return None
    
    def is_file_exists(self, path):
        """
        Проверяет существование файла.
        
        Args:
            path (str): Путь к файлу
            
        Returns:
            bool: True, если файл существует
        """
        return os.path.isfile(path)
    
    def is_directory_exists(self, path):
        """
        Проверяет существование директории.
        
        Args:
            path (str): Путь к директории
            
        Returns:
            bool: True, если директория существует
        """
        return os.path.isdir(path)
    
    def get_file_size(self, path):
        """
        Получает размер файла в байтах.
        
        Args:
            path (str): Путь к файлу
            
        Returns:
            int: Размер файла в байтах или -1 в случае ошибки
        """
        try:
            if os.path.isfile(path):
                return os.path.getsize(path)
            return -1
        except Exception as e:
            print(f"Error getting file size: {e}")
            return -1
    
    def get_file_extension(self, path):
        """
        Получает расширение файла.
        
        Args:
            path (str): Путь к файлу
            
        Returns:
            str: Расширение файла или пустая строка
        """
        return os.path.splitext(path)[1]