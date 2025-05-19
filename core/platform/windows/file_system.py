# Windows-специфичная реализация файловой системы
import csv
import fnmatch
import glob
import json
import os
import pickle
import shutil
import tempfile
import zipfile
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Union

import psutil

from core.common.error_handler import handle_error
from core.common.file_system import AbstractFileSystem


class WindowsFileSystem(AbstractFileSystem):
    """Реализация файловой системы для Windows"""

    def list_directory(self, path: str, pattern: str = "*", recursive: bool = False) -> List[str]:
        """Получить список файлов в директории"""
        try:
            if not os.path.exists(path):
                return []

            if recursive:
                result = []
                for root, _, files in os.walk(path):
                    for file in files:
                        if fnmatch.fnmatch(file, pattern):
                            result.append(os.path.join(root, file))
                return result
            else:
                return glob.glob(os.path.join(path, pattern))
        except Exception as e:
            handle_error(f"Ошибка при получении списка файлов: {e}", e)
            return []

    def file_exists(self, path: str) -> bool:
        """Проверить существование файла"""
        return os.path.exists(path) and os.path.isfile(path)

    def create_directory(self, path: str) -> bool:
        """Создать директорию"""
        try:
            os.makedirs(path, exist_ok=True)
            return True
        except Exception as e:
            handle_error(f"Ошибка при создании директории: {e}", e)
            return False

    def read_file(self, path: str, encoding: str = "utf-8") -> Optional[str]:
        """Прочитать содержимое файла"""
        try:
            with open(path, "r", encoding=encoding) as file:
                return file.read()
        except Exception as e:
            handle_error(f"Ошибка при чтении файла: {e}", e)
            return None

    def write_file(self, path: str, content: str, encoding: str = "utf-8") -> bool:
        """Записать содержимое в файл"""
        try:
            # Создаем директорию, если она не существует
            directory = os.path.dirname(path)
            if directory and not os.path.exists(directory):
                os.makedirs(directory, exist_ok=True)

            with open(path, "w", encoding=encoding) as file:
                file.write(content)
            return True
        except Exception as e:
            handle_error(f"Ошибка при записи в файл: {e}", e)
            return False

    def delete_file(self, path: str) -> bool:
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

    def get_file_size(self, path: str) -> int:
        """Получить размер файла"""
        try:
            return os.path.getsize(path)
        except Exception as e:
            handle_error(f"Ошибка при получении размера файла: {e}", e)
            return -1

    def get_file_modification_time(self, path: str) -> Optional[datetime]:
        """Получить время последней модификации файла"""
        try:
            timestamp = os.path.getmtime(path)
            return datetime.fromtimestamp(timestamp)
        except Exception as e:
            handle_error(f"Ошибка при получении времени модификации: {e}", e)
            return None

    def create_file(self, path: str, content: str = "", encoding: str = "utf-8") -> bool:
        """Создает файл с указанным содержимым"""
        return self.write_file(path, content, encoding)

    def append_to_file(self, path: str, content: str, encoding: str = "utf-8") -> bool:
        """Добавляет содержимое в конец файла"""
        try:
            # Создаем директорию, если она не существует
            directory = os.path.dirname(path)
            if directory and not os.path.exists(directory):
                os.makedirs(directory, exist_ok=True)

            with open(path, "a", encoding=encoding) as file:
                file.write(content)
            return True
        except Exception as e:
            handle_error(f"Ошибка при добавлении в файл: {e}", e)
            return False

    def delete_directory(self, path: str, recursive: bool = True) -> bool:
        """Удаляет директорию"""
        try:
            if not os.path.exists(path):
                return False

            if recursive:
                shutil.rmtree(path)
            else:
                os.rmdir(path)
            return True
        except Exception as e:
            handle_error(f"Ошибка при удалении директории: {e}", e)
            return False

    def copy_file(self, source: str, destination: str) -> bool:
        """Копирует файл"""
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
            handle_error(f"Ошибка при копировании файла: {e}", e)
            return False

    def move_file(self, source: str, destination: str) -> bool:
        """Перемещает файл"""
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
            handle_error(f"Ошибка при перемещении файла: {e}", e)
            return False

    def rename_file(self, path: str, new_name: str) -> bool:
        """Переименовывает файл"""
        try:
            directory = os.path.dirname(path)
            new_path = os.path.join(directory, new_name)

            os.rename(path, new_path)
            return True
        except Exception as e:
            handle_error(f"Ошибка при переименовании файла: {e}", e)
            return False

    def get_file_info(self, path: str) -> Optional[Dict[str, Any]]:
        """Получает информацию о файле"""
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
                "extension": file_path.suffix,
            }

            return info
        except Exception as e:
            handle_error(f"Ошибка при получении информации о файле: {e}", e)
            return None

    def is_directory_exists(self, path: str) -> bool:
        """Проверяет существование директории"""
        return os.path.exists(path) and os.path.isdir(path)

    def get_file_extension(self, path: str) -> str:
        """Получает расширение файла"""
        return os.path.splitext(path)[1]

    def search_files(
        self, directory: str, pattern: str = "*", recursive: bool = False
    ) -> List[str]:
        """Ищет файлы по шаблону"""
        return self.list_directory(directory, pattern, recursive)

    def zip_files(self, file_paths: List[str], zip_path: str) -> bool:
        """Создает ZIP-архив из указанных файлов"""
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
            handle_error(f"Ошибка при создании ZIP-архива: {e}", e)
            return False

    def unzip_file(self, zip_path: str, extract_to: str) -> bool:
        """Распаковывает ZIP-архив"""
        try:
            # Создаем директорию для распаковки, если она не существует
            if not os.path.exists(extract_to):
                os.makedirs(extract_to, exist_ok=True)

            with zipfile.ZipFile(zip_path, "r") as zipf:
                zipf.extractall(extract_to)

            return True
        except Exception as e:
            handle_error(f"Ошибка при распаковке ZIP-архива: {e}", e)
            return False

    def read_json(self, path: str) -> Optional[Dict]:
        """Читает JSON-файл"""
        try:
            with open(path, "r", encoding="utf-8") as file:
                return json.load(file)
        except Exception as e:
            handle_error(f"Ошибка при чтении JSON-файла: {e}", e)
            return None

    def write_json(self, path: str, data: Dict, indent: int = 4) -> bool:
        """Записывает данные в JSON-файл"""
        try:
            # Создаем директорию, если она не существует
            directory = os.path.dirname(path)
            if directory and not os.path.exists(directory):
                os.makedirs(directory, exist_ok=True)

            with open(path, "w", encoding="utf-8") as file:
                json.dump(data, file, indent=indent)

            return True
        except Exception as e:
            handle_error(f"Ошибка при записи JSON-файла: {e}", e)
            return False

    def read_csv(self, path: str, delimiter: str = ",") -> Optional[List[List[str]]]:
        """Читает CSV-файл"""
        try:
            data = []
            with open(path, "r", encoding="utf-8", newline="") as file:
                csv_reader = csv.reader(file, delimiter=delimiter)
                for row in csv_reader:
                    data.append(row)

            return data
        except Exception as e:
            handle_error(f"Ошибка при чтении CSV-файла: {e}", e)
            return None

    def write_csv(self, path: str, data: List[List[str]], delimiter: str = ",") -> bool:
        """Записывает данные в CSV-файл"""
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
            handle_error(f"Ошибка при записи CSV-файла: {e}", e)
            return False

    def read_binary(self, path: str) -> Optional[bytes]:
        """Читает бинарный файл"""
        try:
            with open(path, "rb") as file:
                return file.read()
        except Exception as e:
            handle_error(f"Ошибка при чтении бинарного файла: {e}", e)
            return None

    def write_binary(self, path: str, data: bytes) -> bool:
        """Записывает данные в бинарный файл"""
        try:
            # Создаем директорию, если она не существует
            directory = os.path.dirname(path)
            if directory and not os.path.exists(directory):
                os.makedirs(directory, exist_ok=True)

            with open(path, "wb") as file:
                file.write(data)

            return True
        except Exception as e:
            handle_error(f"Ошибка при записи бинарного файла: {e}", e)
            return False

    def read_pickle(self, path: str) -> Optional[Any]:
        """Читает объект из файла pickle"""
        try:
            with open(path, "rb") as file:
                return pickle.load(file)
        except Exception as e:
            handle_error(f"Ошибка при чтении pickle-файла: {e}", e)
            return None

    def write_pickle(self, path: str, data: Any) -> bool:
        """Записывает объект в файл pickle"""
        try:
            # Создаем директорию, если она не существует
            directory = os.path.dirname(path)
            if directory and not os.path.exists(directory):
                os.makedirs(directory, exist_ok=True)

            with open(path, "wb") as file:
                pickle.dump(data, file)

            return True
        except Exception as e:
            handle_error(f"Ошибка при записи pickle-файла: {e}", e)
            return False

    def get_directory_size(self, directory_path: str) -> int:
        """Вычисляет размер директории"""
        try:
            total_size = 0
            for dirpath, _, filenames in os.walk(directory_path):
                for filename in filenames:
                    file_path = os.path.join(dirpath, filename)
                    if not os.path.islink(file_path):  # Исключаем символические ссылки
                        total_size += os.path.getsize(file_path)
            return total_size
        except Exception as e:
            handle_error(f"Ошибка при вычислении размера директории: {e}", e)
            return -1

    def is_path_exists(self, path: str) -> bool:
        """Проверяет существование пути"""
        return os.path.exists(path)

    def get_absolute_path(self, path: str) -> str:
        """Получает абсолютный путь"""
        try:
            return os.path.abspath(path)
        except Exception as e:
            handle_error(f"Ошибка при получении абсолютного пути: {e}", e)
            return path

    def join_paths(self, *paths: str) -> str:
        """Объединяет пути"""
        try:
            return os.path.join(*paths)
        except Exception as e:
            handle_error(f"Ошибка при объединении путей: {e}", e)
            return ""

    def get_parent_directory(self, path: str) -> str:
        """Получает родительскую директорию"""
        try:
            return os.path.dirname(path)
        except Exception as e:
            handle_error(f"Ошибка при получении родительской директории: {e}", e)
            return ""

    def get_file_name(self, path: str) -> str:
        """Получает имя файла из пути"""
        try:
            return os.path.basename(path)
        except Exception as e:
            handle_error(f"Ошибка при получении имени файла: {e}", e)
            return ""

    def get_file_name_without_extension(self, path: str) -> str:
        """Получает имя файла без расширения"""
        try:
            base_name = os.path.basename(path)
            return os.path.splitext(base_name)[0]
        except Exception as e:
            handle_error(f"Ошибка при получении имени файла без расширения: {e}", e)
            return ""

    def create_temp_file(
        self, prefix: str = "", suffix: str = "", content: str = ""
    ) -> Tuple[str, bool]:
        """Создает временный файл"""
        try:
            fd, path = tempfile.mkstemp(suffix=suffix, prefix=prefix, text=True)

            # Записываем содержимое, если оно предоставлено
            if content:
                with os.fdopen(fd, "w") as temp_file:
                    temp_file.write(content)
            else:
                os.close(fd)

            return path, True
        except Exception as e:
            handle_error(f"Ошибка при создании временного файла: {e}", e)
            return "", False

    def create_temp_directory(self, prefix: str = "") -> Tuple[str, bool]:
        """Создает временную директорию"""
        try:
            path = tempfile.mkdtemp(prefix=prefix)
            return path, True
        except Exception as e:
            handle_error(f"Ошибка при создании временной директории: {e}", e)
            return "", False

    def is_readable(self, path: str) -> bool:
        """Проверяет, можно ли прочитать файл или директорию"""
        try:
            return os.access(path, os.R_OK)
        except Exception as e:
            handle_error(f"Ошибка при проверке доступа на чтение: {e}", e)
            return False

    def is_writable(self, path: str) -> bool:
        """Проверяет, можно ли записать в файл или директорию"""
        try:
            return os.access(path, os.W_OK)
        except Exception as e:
            handle_error(f"Ошибка при проверке доступа на запись: {e}", e)
            return False

    def is_executable(self, path: str) -> bool:
        """Проверяет, можно ли выполнить файл"""
        try:
            return os.access(path, os.X_OK)
        except Exception as e:
            handle_error(f"Ошибка при проверке доступа на выполнение: {e}", e)
            return False

    def get_drive_info(self) -> Dict[str, Dict[str, Union[str, int, float]]]:
        """Получает информацию о дисках в Windows"""
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
            handle_error(f"Ошибка при получении информации о дисках: {e}", e)
            return {}

    def get_home_directory(self) -> str:
        """Получает путь к домашней директории пользователя"""
        try:
            return os.path.expanduser("~")
        except Exception as e:
            handle_error(f"Ошибка при получении домашней директории: {e}", e)
            return ""

    def get_temp_directory(self) -> str:
        """Получает путь к временной директории"""
        try:
            return tempfile.gettempdir()
        except Exception as e:
            handle_error(f"Ошибка при получении временной директории: {e}", e)
            return ""

    def get_current_directory(self) -> str:
        """Получает путь к текущей рабочей директории"""
        try:
            return os.getcwd()
        except Exception as e:
            handle_error(f"Ошибка при получении текущей директории: {e}", e)
            return ""

    def set_current_directory(self, path: str) -> bool:
        """Устанавливает текущую рабочую директорию"""
        try:
            os.chdir(path)
            return True
        except Exception as e:
            handle_error(f"Ошибка при изменении текущей директории: {e}", e)
            return False

    def is_symlink(self, path: str) -> bool:
        """Проверяет, является ли путь символической ссылкой"""
        try:
            return os.path.islink(path)
        except Exception as e:
            handle_error(f"Ошибка при проверке символической ссылки: {e}", e)
            return False

    def create_symlink(self, source: str, link_name: str) -> bool:
        """Создает символическую ссылку"""
        try:
            os.symlink(source, link_name)
            return True
        except Exception as e:
            handle_error(f"Ошибка при создании символической ссылки: {e}", e)
            return False

    def read_symlink(self, path: str) -> Optional[str]:
        """Читает цель символической ссылки"""
        try:
            if not os.path.islink(path):
                return None
            return os.readlink(path)
        except Exception as e:
            handle_error(f"Ошибка при чтении символической ссылки: {e}", e)
            return None
