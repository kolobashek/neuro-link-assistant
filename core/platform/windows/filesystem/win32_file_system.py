# -*- coding: utf-8 -*-
"""
Реализация файловой системы для Windows.
"""
import csv
import glob
import json
import os
import pickle
import shutil
import zipfile
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

from core.common.error_handler import handle_error
from core.common.filesystem.base import AbstractFileSystem


class Win32FileSystem(AbstractFileSystem):
    """
    Реализация работы с файловой системой для Windows.
    Предоставляет методы для работы с файлами и директориями.
    """

    def file_exists(self, path: str) -> bool:
        """
        Проверить существование файла.

        Args:
            path (str): Путь к файлу.

        Returns:
            bool: True, если файл существует, иначе False.
        """
        return os.path.isfile(path)

    def list_directory(self, path: str, pattern: str = "*", recursive: bool = False) -> List[str]:
        """
        Получить список файлов в директории.

        Args:
            path (str): Путь к директории.
            pattern (str, optional): Шаблон для фильтрации файлов. По умолчанию "*".
            recursive (bool, optional): Флаг рекурсивного поиска. По умолчанию False.

        Returns:
            List[str]: Список путей к файлам.
        """
        try:
            if not os.path.exists(path):
                return []

            if recursive:
                search_pattern = os.path.join(path, "**", pattern)
                files = glob.glob(search_pattern, recursive=True)
            else:
                search_pattern = os.path.join(path, pattern)
                files = glob.glob(search_pattern)

            return files
        except Exception as e:
            handle_error(f"Error listing directory {path}: {e}", e, module="filesystem")
            return []

    def list_directory_names(self, path, pattern="*"):
        """
        Получает список имен файлов и директорий в указанной директории.

        Args:
            path (str): Путь к директории
            pattern (str, optional): Шаблон для фильтрации файлов. По умолчанию "*".

        Returns:
            list: Список имен файлов и директорий (без полных путей)
        """
        items = self.list_directory(path, pattern)
        return [os.path.basename(item) for item in items]

    def create_directory(self, path: str) -> bool:
        """
        Создать директорию.

        Args:
            path (str): Путь к создаваемой директории.

        Returns:
            bool: True в случае успешного создания.
        """
        try:
            os.makedirs(path, exist_ok=True)
            return True
        except Exception as e:
            handle_error(f"Error creating directory {path}: {e}", e, module="filesystem")
            return False

    def read_file(self, path: str, encoding: str = "utf-8") -> Optional[str]:
        """
        Прочитать содержимое файла.

        Args:
            path (str): Путь к файлу.
            encoding (str, optional): Кодировка файла. По умолчанию "utf-8".

        Returns:
            Optional[str]: Содержимое файла или None в случае ошибки.
        """
        try:
            if not os.path.exists(path):
                return None

            with open(path, "r", encoding=encoding) as f:
                return f.read()
        except Exception as e:
            handle_error(f"Error reading file {path}: {e}", e, module="filesystem")
            return None

    def write_file(self, path: str, content: str, encoding: str = "utf-8") -> bool:
        """
        Записать содержимое в файл.

        Args:
            path (str): Путь к файлу.
            content (str): Содержимое для записи.
            encoding (str, optional): Кодировка файла. По умолчанию "utf-8".

        Returns:
            bool: True в случае успешной записи.
        """
        try:
            # Создаем директорию, если она не существует
            directory = os.path.dirname(path)
            if directory and not os.path.exists(directory):
                os.makedirs(directory, exist_ok=True)

            with open(path, "w", encoding=encoding) as f:
                f.write(content)

            return True
        except Exception as e:
            handle_error(f"Error writing to file {path}: {e}", e, module="filesystem")
            return False

    def delete_file(self, path: str) -> bool:
        """
        Удалить файл.

        Args:
            path (str): Путь к файлу.

        Returns:
            bool: True в случае успешного удаления.
        """
        try:
            if not os.path.exists(path):
                return False

            os.remove(path)
            return True
        except Exception as e:
            handle_error(f"Error deleting file {path}: {e}", e, module="filesystem")
            return False

    def get_file_size(self, path: str) -> int:
        """
        Получить размер файла.

        Args:
            path (str): Путь к файлу.

        Returns:
            int: Размер файла в байтах или -1 в случае ошибки.
        """
        try:
            if os.path.isfile(path):
                return os.path.getsize(path)
            return -1
        except Exception as e:
            handle_error(f"Error getting file size: {e}", e, module="filesystem")
            return -1

    def get_file_modification_time(self, path: str) -> Optional[datetime]:
        """
        Получить время последней модификации файла.

        Args:
            path (str): Путь к файлу.

        Returns:
            Optional[datetime]: Время модификации или None в случае ошибки.
        """
        try:
            if os.path.exists(path):
                mod_time = os.path.getmtime(path)
                return datetime.fromtimestamp(mod_time)
            return None
        except Exception as e:
            handle_error(f"Error getting file modification time: {e}", e, module="filesystem")
            return None

    def create_file(self, path: str, content: str = "", encoding: str = "utf-8") -> bool:
        """
        Создать файл с указанным содержимым.

        Args:
            path (str): Путь к файлу.
            content (str, optional): Содержимое файла. По умолчанию "".
            encoding (str, optional): Кодировка файла. По умолчанию "utf-8".

        Returns:
            bool: True в случае успешного создания.
        """
        return self.write_file(path, content, encoding)

    def append_to_file(self, path: str, content: str, encoding: str = "utf-8") -> bool:
        """
        Добавить содержимое в конец файла.

        Args:
            path (str): Путь к файлу.
            content (str): Содержимое для добавления.
            encoding (str, optional): Кодировка файла. По умолчанию "utf-8".

        Returns:
            bool: True в случае успешного добавления.
        """
        try:
            # Проверяем, существует ли файл
            if not os.path.exists(path):
                return self.write_file(path, content, encoding)

            # Добавляем содержимое в конец файла
            with open(path, "a", encoding=encoding) as f:
                f.write(content)

            return True
        except Exception as e:
            handle_error(f"Error appending to file {path}: {e}", e, module="filesystem")
            return False

    def delete_directory(self, path: str, recursive: bool = True) -> bool:
        """
        Удалить директорию.

        Args:
            path (str): Путь к директории.
            recursive (bool, optional): Флаг рекурсивного удаления. По умолчанию True.

        Returns:
            bool: True в случае успешного удаления.
        """
        try:
            if not os.path.exists(path):
                return False

            if recursive:
                shutil.rmtree(path)
            else:
                os.rmdir(path)
            return True
        except Exception as e:
            handle_error(f"Error deleting directory {path}: {e}", e, module="filesystem")
            return False

    def copy_file(self, source: str, destination: str) -> bool:
        """
        Копировать файл.

        Args:
            source (str): Путь к исходному файлу.
            destination (str): Путь к файлу назначения.

        Returns:
            bool: True в случае успешного копирования.
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
            handle_error(
                f"Error copying file from {source} to {destination}: {e}", e, module="filesystem"
            )
            return False

    def move_file(self, source: str, destination: str) -> bool:
        """
        Переместить файл.

        Args:
            source (str): Путь к исходному файлу.
            destination (str): Путь к файлу назначения.

        Returns:
            bool: True в случае успешного перемещения.
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
            handle_error(
                f"Error moving file from {source} to {destination}: {e}", e, module="filesystem"
            )
            return False

    def rename_file(self, path: str, new_name: str) -> bool:
        """
        Переименовать файл.

        Args:
            path (str): Путь к файлу.
            new_name (str): Новое имя файла.

        Returns:
            bool: True в случае успешного переименования.
        """
        try:
            if not os.path.exists(path):
                return False

            directory = os.path.dirname(path)
            new_path = os.path.join(directory, new_name)

            os.rename(path, new_path)
            return True
        except Exception as e:
            handle_error(f"Error renaming file {path}: {e}", e, module="filesystem")
            return False

    def get_file_info(self, path: str) -> Optional[Dict[str, Any]]:
        """
        Получить информацию о файле.

        Args:
            path (str): Путь к файлу.
                    Returns:
            Optional[Dict[str, Any]]: Информация о файле или None в случае ошибки.
        """
        try:
            if not os.path.exists(path):
                return None

            # Получаем статистику файла
            stats = os.stat(path)
            file_path = Path(path)

            # Формируем словарь с информацией
            info = {
                "path": str(file_path.absolute()),
                "name": file_path.name,
                "size": stats.st_size,
                "created": datetime.fromtimestamp(stats.st_ctime).isoformat(),
                "modified": datetime.fromtimestamp(stats.st_mtime).isoformat(),
                "accessed": datetime.fromtimestamp(stats.st_atime).isoformat(),
                "is_directory": os.path.isdir(path),
                "is_file": os.path.isfile(path),
                "extension": file_path.suffix,
            }

            return info
        except Exception as e:
            handle_error(f"Error getting file info: {e}", e, module="filesystem")
            return None

    def is_directory_exists(self, path: str) -> bool:
        """
        Проверить существование директории.

        Args:
            path (str): Путь к директории.

        Returns:
            bool: True, если директория существует, иначе False.
        """
        return os.path.isdir(path)

    def get_file_extension(self, path: str) -> str:
        """
        Получить расширение файла.

        Args:
            path (str): Путь к файлу.

        Returns:
            str: Расширение файла.
        """
        return os.path.splitext(path)[1]

    def search_files(
        self, directory: str, pattern: str = "*", recursive: bool = False
    ) -> List[str]:
        """
        Искать файлы по шаблону.

        Args:
            directory (str): Путь к директории.
            pattern (str, optional): Шаблон для поиска. По умолчанию "*".
            recursive (bool, optional): Флаг рекурсивного поиска. По умолчанию False.

        Returns:
            List[str]: Список путей к найденным файлам.
        """
        return self.list_directory(directory, pattern, recursive)

    def zip_files(self, file_paths: List[str], zip_path: str) -> bool:
        """
        Создать ZIP-архив из указанных файлов.

        Args:
            file_paths (List[str]): Список путей к файлам.
            zip_path (str): Путь к создаваемому ZIP-архиву.

        Returns:
            bool: True в случае успешного создания архива.
        """
        try:
            # Создаем директорию для архива, если она не существует
            zip_dir = os.path.dirname(zip_path)
            if zip_dir and not os.path.exists(zip_dir):
                os.makedirs(zip_dir, exist_ok=True)

            with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zipf:
                for file_path in file_paths:
                    if os.path.exists(file_path):
                        # Добавляем файл в архив с именем файла (без пути)
                        zipf.write(file_path, os.path.basename(file_path))

            return True
        except Exception as e:
            handle_error(f"Error creating ZIP archive: {e}", e, module="filesystem")
            return False

    def unzip_file(self, zip_path: str, extract_to: str) -> bool:
        """
        Распаковать ZIP-архив.

        Args:
            zip_path (str): Путь к ZIP-архиву.
            extract_to (str): Путь для распаковки.

        Returns:
            bool: True в случае успешной распаковки.
        """
        try:
            # Создаем директорию для распаковки, если она не существует
            if not os.path.exists(extract_to):
                os.makedirs(extract_to, exist_ok=True)

            with zipfile.ZipFile(zip_path, "r") as zipf:
                zipf.extractall(extract_to)

            return True
        except Exception as e:
            handle_error(f"Error extracting ZIP archive: {e}", e, module="filesystem")
            return False

    def read_json(self, path: str) -> Optional[Dict]:
        """
        Прочитать JSON-файл.

        Args:
            path (str): Путь к JSON-файлу.

        Returns:
            Optional[Dict]: Данные из JSON-файла или None в случае ошибки.
        """
        try:
            if not os.path.exists(path):
                return None

            with open(path, "r", encoding="utf-8") as file:
                return json.load(file)
        except Exception as e:
            handle_error(f"Error reading JSON file: {e}", e, module="filesystem")
            return None

    def write_json(self, path: str, data: Dict, indent: int = 4) -> bool:
        """
        Записать данные в JSON-файл.

        Args:
            path (str): Путь к JSON-файлу.
            data (Dict): Данные для записи.
            indent (int, optional): Отступ для форматирования JSON. По умолчанию 4.

        Returns:
            bool: True в случае успешной записи.
        """
        try:
            # Создаем директорию, если она не существует
            directory = os.path.dirname(path)
            if directory and not os.path.exists(directory):
                os.makedirs(directory, exist_ok=True)

            with open(path, "w", encoding="utf-8") as file:
                json.dump(data, file, indent=indent)

            return True
        except Exception as e:
            handle_error(f"Error writing JSON file: {e}", e, module="filesystem")
            return False

    def read_csv(self, path: str, delimiter: str = ",") -> Optional[List[List[str]]]:
        """
        Прочитать CSV-файл.

        Args:
            path (str): Путь к CSV-файлу.
            delimiter (str, optional): Разделитель полей. По умолчанию ",".

        Returns:
            Optional[List[List[str]]]: Данные из CSV-файла или None в случае ошибки.
        """
        try:
            if not os.path.exists(path):
                return None

            data = []
            with open(path, "r", encoding="utf-8", newline="") as file:
                csv_reader = csv.reader(file, delimiter=delimiter)
                for row in csv_reader:
                    data.append(row)

            return data
        except Exception as e:
            handle_error(f"Error reading CSV file: {e}", e, module="filesystem")
            return None

    def write_csv(self, path: str, data: List[List[str]], delimiter: str = ",") -> bool:
        """
        Записать данные в CSV-файл.

        Args:
            path (str): Путь к CSV-файлу.
            data (List[List[str]]): Данные для записи.
            delimiter (str, optional): Разделитель полей. По умолчанию ",".

        Returns:
            bool: True в случае успешной записи.
        """
        try:
            # Создаем директорию, если она не существует
            directory = os.path.dirname(path)
            if directory and not os.path.exists(directory):
                os.makedirs(directory, exist_ok=True)

            with open(path, "w", encoding="utf-8", newline="") as file:
                csv_writer = csv.writer(file, delimiter=delimiter)
                csv_writer.writerows(data)

            return True
        except Exception as e:
            handle_error(f"Error writing CSV file: {e}", e, module="filesystem")
            return False

    def read_binary(self, path: str) -> Optional[bytes]:
        """
        Прочитать бинарный файл.

        Args:
            path (str): Путь к файлу.

        Returns:
            Optional[bytes]: Содержимое файла или None в случае ошибки.
        """
        try:
            if not os.path.exists(path):
                return None

            with open(path, "rb") as file:
                return file.read()
        except Exception as e:
            handle_error(f"Error reading binary file: {e}", e, module="filesystem")
            return None

    def write_binary(self, path: str, data: bytes) -> bool:
        """
        Записать данные в бинарный файл.

        Args:
            path (str): Путь к файлу.
            data (bytes): Данные для записи.

        Returns:
            bool: True в случае успешной записи.
        """
        try:
            # Создаем директорию, если она не существует
            directory = os.path.dirname(path)
            if directory and not os.path.exists(directory):
                os.makedirs(directory, exist_ok=True)

            with open(path, "wb") as file:
                file.write(data)

            return True
        except Exception as e:
            handle_error(f"Error writing binary file: {e}", e, module="filesystem")
            return False

    def read_pickle(self, path: str) -> Optional[Any]:
        """
        Прочитать объект из файла pickle.

        Args:
            path (str): Путь к файлу.

        Returns:
            Optional[Any]: Объект из файла или None в случае ошибки.
        """
        try:
            if not os.path.exists(path):
                return None

            with open(path, "rb") as file:
                return pickle.load(file)
        except Exception as e:
            handle_error(f"Error reading pickle file: {e}", e, module="filesystem")
            return None

    def write_pickle(self, path: str, data: Any) -> bool:
        """
        Записать объект в файл pickle.

        Args:
            path (str): Путь к файлу.
            data (Any): Объект для записи.

        Returns:
            bool: True в случае успешной записи.
        """
        try:
            # Создаем директорию, если она не существует
            directory = os.path.dirname(path)
            if directory and not os.path.exists(directory):
                os.makedirs(directory, exist_ok=True)

            with open(path, "wb") as file:
                pickle.dump(data, file)

            return True
        except Exception as e:
            handle_error(f"Error writing pickle file: {e}", e, module="filesystem")
            return False
