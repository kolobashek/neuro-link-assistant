import datetime
import glob
import os
import shutil


class FileSystemManager:
    """
    Класс для работы с файловой системой Windows.
    Предоставляет функции для операций с файлами и директориями.
    """

    def list_directory(self, directory_path):
        """
        Получает список файлов и директорий в указанной директории.

        Args:
            directory_path (str): Путь к директории

        Returns:
            list: Список словарей с информацией о файлах и директориях
        """
        try:
            if not os.path.exists(directory_path) or not os.path.isdir(directory_path):
                return []

            items = []
            for item in os.listdir(directory_path):
                item_path = os.path.join(directory_path, item)
                item_info = {
                    "name": item,
                    "path": item_path,
                    "type": "directory" if os.path.isdir(item_path) else "file",
                    "size": os.path.getsize(item_path) if os.path.isfile(item_path) else 0,
                }
                items.append(item_info)

            return items
        except Exception as e:
            print(f"Error listing directory {directory_path}: {e}")
            return []

    def create_directory(self, directory_path):
        """
        Создает директорию.

        Args:
            directory_path (str): Путь к создаваемой директории

        Returns:
            bool: True в случае успешного создания
        """
        try:
            if os.path.exists(directory_path):
                return True

            os.makedirs(directory_path)
            return True
        except Exception as e:
            print(f"Error creating directory {directory_path}: {e}")
            return False

    def delete_directory(self, directory_path, recursive=False):
        """
        Удаляет директорию.

        Args:
            directory_path (str): Путь к удаляемой директории
            recursive (bool, optional): Удалять рекурсивно с содержимым

        Returns:
            bool: True в случае успешного удаления
        """
        try:
            if not os.path.exists(directory_path) or not os.path.isdir(directory_path):
                return False

            if recursive:
                shutil.rmtree(directory_path)
            else:
                os.rmdir(directory_path)

            return True
        except Exception as e:
            print(f"Error deleting directory {directory_path}: {e}")
            return False

    def read_file(self, file_path, binary=False):
        """
        Читает содержимое файла.

        Args:
            file_path (str): Путь к файлу
            binary (bool, optional): Читать в бинарном режиме

        Returns:
            str or bytes: Содержимое файла или None в случае ошибки
        """
        try:
            if not os.path.exists(file_path) or not os.path.isfile(file_path):
                return None

            mode = "rb" if binary else "r"
            with open(file_path, mode) as f:
                return f.read()
        except Exception as e:
            print(f"Error reading file {file_path}: {e}")
            return None

    def write_file(self, file_path, content, binary=False):
        """
        Записывает содержимое в файл.

        Args:
            file_path (str): Путь к файлу
            content (str or bytes): Содержимое для записи
            binary (bool, optional): Записать в бинарном режиме

        Returns:
            bool: True в случае успешной записи
        """
        try:
            mode = "wb" if binary else "w"
            with open(file_path, mode) as f:
                f.write(content)

            return True
        except Exception as e:
            print(f"Error writing to file {file_path}: {e}")
            return False

    def append_to_file(self, file_path, content, binary=False):
        """
        Добавляет содержимое в конец файла.

        Args:
            file_path (str): Путь к файлу
            content (str or bytes): Содержимое для добавления
            binary (bool, optional): Добавить в бинарном режиме

        Returns:
            bool: True в случае успешного добавления
        """
        try:
            mode = "ab" if binary else "a"
            with open(file_path, mode) as f:
                f.write(content)

            return True
        except Exception as e:
            print(f"Error appending to file {file_path}: {e}")
            return False

    def delete_file(self, file_path):
        """
        Удаляет файл.

        Args:
            file_path (str): Путь к удаляемому файлу

        Returns:
            bool: True в случае успешного удаления
        """
        try:
            if not os.path.exists(file_path) or not os.path.isfile(file_path):
                return False

            os.remove(file_path)
            return True
        except Exception as e:
            print(f"Error deleting file {file_path}: {e}")
            return False

    def copy_file(self, source_path, dest_path):
        """
        Копирует файл.

        Args:
            source_path (str): Путь к исходному файлу
            dest_path (str): Путь к файлу назначения

        Returns:
            bool: True в случае успешного копирования
        """
        try:
            if not os.path.exists(source_path) or not os.path.isfile(source_path):
                return False

            shutil.copy2(source_path, dest_path)
            return True
        except Exception as e:
            print(f"Error copying file from {source_path} to {dest_path}: {e}")
            return False

    def move_file(self, source_path, dest_path):
        """
        Перемещает файл.

        Args:
            source_path (str): Путь к исходному файлу
            dest_path (str): Путь к файлу назначения

        Returns:
            bool: True в случае успешного перемещения
        """
        try:
            if not os.path.exists(source_path) or not os.path.isfile(source_path):
                return False

            shutil.move(source_path, dest_path)
            return True
        except Exception as e:
            print(f"Error moving file from {source_path} to {dest_path}: {e}")
            return False

    def get_file_info(self, file_path):
        """
        Получает подробную информацию о файле.

        Args:
            file_path (str): Путь к файлу

        Returns:
            dict: Словарь с информацией о файле или None в случае ошибки
        """
        try:
            if not os.path.exists(file_path):
                return None

            stat_info = os.stat(file_path)

            info = {
                "name": os.path.basename(file_path),
                "path": file_path,
                "size": stat_info.st_size,
                "is_file": os.path.isfile(file_path),
                "is_directory": os.path.isdir(file_path),
                "created": datetime.datetime.fromtimestamp(stat_info.st_ctime).isoformat(),
                "modified": datetime.datetime.fromtimestamp(stat_info.st_mtime).isoformat(),
                "accessed": datetime.datetime.fromtimestamp(stat_info.st_atime).isoformat(),
                "permissions": stat_info.st_mode,
            }

            return info
        except Exception as e:
            print(f"Error getting file info for {file_path}: {e}")
            return None

    def search_files(self, directory_path, pattern="*", recursive=True):
        """
        Ищет файлы по маске в указанной директории.

        Args:
            directory_path (str): Путь к директории для поиска
            pattern (str, optional): Маска поиска (например, "*.txt")
            recursive (bool, optional): Искать рекурсивно в поддиректориях

        Returns:
            list: Список словарей с информацией о найденных файлах
        """
        try:
            if not os.path.exists(directory_path) or not os.path.isdir(directory_path):
                return []

            result = []

            if recursive:
                search_path = os.path.join(directory_path, "**", pattern)
                files = glob.glob(search_path, recursive=True)
            else:
                search_path = os.path.join(directory_path, pattern)
                files = glob.glob(search_path)

            for file_path in files:
                if os.path.isfile(file_path):
                    file_info = self.get_file_info(file_path)
                    if file_info:
                        result.append(file_info)

            return result
        except Exception as e:
            print(f"Error searching files in {directory_path}: {e}")
            return []

    def get_drive_info(self):
        """
        Получает информацию о дисках в системе.

        Returns:
            list: Список словарей с информацией о дисках
        """
        try:
            import psutil

            drives = []

            for partition in psutil.disk_partitions():
                try:
                    usage = psutil.disk_usage(partition.mountpoint)
                    drive_info = {
                        "device": partition.device,
                        "mountpoint": partition.mountpoint,
                        "fstype": partition.fstype,
                        "opts": partition.opts,
                        "total": usage.total,
                        "used": usage.used,
                        "free": usage.free,
                        "percent": usage.percent,
                    }
                    drives.append(drive_info)
                except PermissionError:
                    # Некоторые диски могут быть недоступны
                    continue

            return drives
        except Exception as e:
            print(f"Error getting drive info: {e}")
            return []

    def get_directory_size(self, directory_path):
        """
        Вычисляет размер директории.

        Args:
            directory_path (str): Путь к директории

        Returns:
            int: Размер директории в байтах или -1 в случае ошибки
        """
        try:
            if not os.path.exists(directory_path) or not os.path.isdir(directory_path):
                return -1

            total_size = 0

            for dirpath, dirnames, filenames in os.walk(directory_path):
                for filename in filenames:
                    file_path = os.path.join(dirpath, filename)
                    if os.path.isfile(file_path):
                        total_size += os.path.getsize(file_path)

            return total_size
        except Exception as e:
            print(f"Error calculating directory size for {directory_path}: {e}")
            return -1

    def is_path_exists(self, path):
        """
        Проверяет существование пути.

        Args:
            path (str): Путь для проверки

        Returns:
            bool: True, если путь существует
        """
        return os.path.exists(path)

    def is_file(self, path):
        """
        Проверяет, является ли путь файлом.

        Args:
            path (str): Путь для проверки

        Returns:
            bool: True, если путь является файлом
        """
        return os.path.isfile(path)

    def is_directory(self, path):
        """
        Проверяет, является ли путь директорией.

        Args:
            path (str): Путь для проверки

        Returns:
            bool: True, если путь является директорией
        """
        return os.path.isdir(path)

    def get_absolute_path(self, path):
        """
        Получает абсолютный путь.

        Args:
            path (str): Относительный или абсолютный путь

        Returns:
            str: Абсолютный путь
        """
        return os.path.abspath(path)

    def join_paths(self, *paths):
        """
        Объединяет пути.

        Args:
            *paths: Пути для объединения

        Returns:
            str: Объединенный путь
        """
        return os.path.join(*paths)
