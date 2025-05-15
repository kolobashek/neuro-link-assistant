import glob
import os
import shutil

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

    def list_directory(self, path, pattern="*"):
        """
        Получает список файлов и директорий в указанной директории.

        Args:
            path (str): Путь к директории
            pattern (str, optional): Шаблон для фильтрации файлов. Defaults to "*".

        Returns:
            list: Список имен файлов и директорий
        """
        try:
            if not os.path.exists(path):
                return []

            if pattern == "*":
                # Если шаблон по умолчанию, используем более быстрый os.listdir
                items = os.listdir(path)
            else:
                # Если указан шаблон, используем glob для фильтрации
                items = [os.path.basename(f) for f in glob.glob(os.path.join(path, pattern))]

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
            with open(path, "w", encoding="utf-8") as f:
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

            with open(path, "r", encoding="utf-8") as f:
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
            with open(path, "w", encoding="utf-8") as f:
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
            with open(path, "a", encoding="utf-8") as f:
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
                "is_directory": os.path.isdir(path),
                "is_file": os.path.isfile(path),
                "extension": os.path.splitext(path)[1],
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
                    if "cdrom" in partition.opts or partition.fstype == "":
                        continue

                    # Получаем информацию о диске
                    usage = psutil.disk_usage(partition.mountpoint)

                    drives[partition.device] = {
                        "mountpoint": partition.mountpoint,
                        "fstype": partition.fstype,
                        "total": usage.total,
                        "used": usage.used,
                        "free": usage.free,
                        "percent": usage.percent,
                    }
                except Exception:
                    # Пропускаем диски, к которым нет доступа
                    continue

            return drives
        except Exception as e:
            print(f"Error getting drive info: {e}")
            return {}

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
            if not os.path.exists(path):
                return False

            directory = os.path.dirname(path)
            new_path = os.path.join(directory, new_name)

            os.rename(path, new_path)
            return True
        except Exception as e:
            print(f"Error renaming file {path}: {e}")
            return False

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
                os.makedirs(zip_dir, exist_ok=True)

            import zipfile

            with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zipf:
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
                os.makedirs(extract_to, exist_ok=True)

            import zipfile

            with zipfile.ZipFile(zip_path, "r") as zipf:
                zipf.extractall(extract_to)

            return True
        except Exception as e:
            print(f"Error extracting ZIP archive: {e}")
            return False
