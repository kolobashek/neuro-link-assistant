# -*- coding: utf-8 -*-
"""
Базовый абстрактный класс для файловой системы.
Определяет интерфейс для работы с файлами и директориями.
"""
from abc import ABC, abstractmethod
from datetime import datetime
from typing import Any, Dict, List, Optional


class AbstractFileSystem(ABC):
    """
    Абстрактный класс для работы с файловой системой.
    Определяет методы для работы с файлами и директориями.
    """

    @abstractmethod
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
        pass

    @abstractmethod
    def list_directory_names(self, path, pattern="*"):
        """
        Получает список имен файлов и директорий в указанной директории.

        Args:
            path (str): Путь к директории
            pattern (str, optional): Шаблон для фильтрации файлов. По умолчанию "*".

        Returns:
            list: Список имен файлов и директорий (без полных путей)
        """
        pass

    @abstractmethod
    def file_exists(self, path: str) -> bool:
        """
        Проверить существование файла.

        Args:
            path (str): Путь к файлу.

        Returns:
            bool: True, если файл существует, иначе False.
        """
        pass

    @abstractmethod
    def create_directory(self, path: str) -> bool:
        """
        Создать директорию.

        Args:
            path (str): Путь к создаваемой директории.

        Returns:
            bool: True в случае успешного создания.
        """
        pass

    @abstractmethod
    def read_file(self, path: str, encoding: str = "utf-8") -> Optional[str]:
        """
        Прочитать содержимое файла.

        Args:
            path (str): Путь к файлу.
            encoding (str, optional): Кодировка файла. По умолчанию "utf-8".

        Returns:
            Optional[str]: Содержимое файла или None в случае ошибки.
        """
        pass

    @abstractmethod
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
        pass

    @abstractmethod
    def delete_file(self, path: str) -> bool:
        """
        Удалить файл.

        Args:
            path (str): Путь к файлу.

        Returns:
            bool: True в случае успешного удаления.
        """
        pass

    @abstractmethod
    def get_file_size(self, path: str) -> int:
        """
        Получить размер файла.

        Args:
            path (str): Путь к файлу.

        Returns:
            int: Размер файла в байтах или -1 в случае ошибки.
        """
        pass

    @abstractmethod
    def get_file_modification_time(self, path: str) -> Optional[datetime]:
        """
        Получить время последней модификации файла.

        Args:
            path (str): Путь к файлу.

        Returns:
            Optional[datetime]: Время модификации или None в случае ошибки.
        """
        pass

    @abstractmethod
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
        pass

    @abstractmethod
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
        pass

    @abstractmethod
    def delete_directory(self, path: str, recursive: bool = True) -> bool:
        """
        Удалить директорию.

        Args:
            path (str): Путь к директории.
            recursive (bool, optional): Флаг рекурсивного удаления. По умолчанию True.

        Returns:
            bool: True в случае успешного удаления.
        """
        pass

    @abstractmethod
    def copy_file(self, source: str, destination: str) -> bool:
        """
        Копировать файл.

        Args:
            source (str): Путь к исходному файлу.
            destination (str): Путь к файлу назначения.

        Returns:
            bool: True в случае успешного копирования.
        """
        pass

    @abstractmethod
    def move_file(self, source: str, destination: str) -> bool:
        """
        Переместить файл.

        Args:
            source (str): Путь к исходному файлу.
            destination (str): Путь к файлу назначения.

        Returns:
            bool: True в случае успешного перемещения.
        """
        pass

    @abstractmethod
    def rename_file(self, path: str, new_name: str) -> bool:
        """
        Переименовать файл.

        Args:
            path (str): Путь к файлу.
            new_name (str): Новое имя файла.

        Returns:
            bool: True в случае успешного переименования.
        """
        pass

    @abstractmethod
    def get_file_info(self, path: str) -> Optional[Dict[str, Any]]:
        """
        Получить информацию о файле.

        Args:
            path (str): Путь к файлу.

        Returns:
            Optional[Dict[str, Any]]: Информация о файле или None в случае ошибки.
        """
        pass

    @abstractmethod
    def is_directory_exists(self, path: str) -> bool:
        """
        Проверить существование директории.

        Args:
            path (str): Путь к директории.

        Returns:
            bool: True, если директория существует, иначе False.
        """
        pass

    @abstractmethod
    def get_file_extension(self, path: str) -> str:
        """
        Получить расширение файла.

        Args:
            path (str): Путь к файлу.

        Returns:
            str: Расширение файла.
        """
        pass

    @abstractmethod
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
        pass

    @abstractmethod
    def zip_files(self, file_paths: List[str], zip_path: str) -> bool:
        """
        Создать ZIP-архив из указанных файлов.

        Args:
            file_paths (List[str]): Список путей к файлам.
            zip_path (str): Путь к создаваемому ZIP-архиву.

        Returns:
            bool: True в случае успешного создания архива.
        """
        pass

    @abstractmethod
    def unzip_file(self, zip_path: str, extract_to: str) -> bool:
        """
        Распаковать ZIP-архив.

        Args:
            zip_path (str): Путь к ZIP-архиву.
            extract_to (str): Путь для распаковки.

        Returns:
            bool: True в случае успешной распаковки.
        """
        pass

    @abstractmethod
    def read_json(self, path: str) -> Optional[Dict]:
        """
        Прочитать JSON-файл.

        Args:
            path (str): Путь к JSON-файлу.

        Returns:
            Optional[Dict]: Данные из JSON-файла или None в случае ошибки.
        """
        pass

    @abstractmethod
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
        pass

    @abstractmethod
    def read_csv(self, path: str, delimiter: str = ",") -> Optional[List[List[str]]]:
        """
        Прочитать CSV-файл.

        Args:
            path (str): Путь к CSV-файлу.
            delimiter (str, optional): Разделитель полей. По умолчанию ",".

        Returns:
            Optional[List[List[str]]]: Данные из CSV-файла или None в случае ошибки.
        """
        pass

    @abstractmethod
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
        pass

    @abstractmethod
    def read_binary(self, path: str) -> Optional[bytes]:
        """
        Прочитать бинарный файл.

        Args:
            path (str): Путь к файлу.

        Returns:
            Optional[bytes]: Содержимое файла или None в случае ошибки.
        """
        pass

    @abstractmethod
    def write_binary(self, path: str, data: bytes) -> bool:
        """
        Записать данные в бинарный файл.

        Args:
            path (str): Путь к файлу.
            data (bytes): Данные для записи.

        Returns:
            bool: True в случае успешной записи.
        """
        pass

    @abstractmethod
    def read_pickle(self, path: str) -> Optional[Any]:
        """
        Прочитать объект из файла pickle.

        Args:
            path (str): Путь к файлу.

        Returns:
                        Optional[Any]: Объект из файла или None в случае ошибки.
        """
        pass

    @abstractmethod
    def write_pickle(self, path: str, data: Any) -> bool:
        """
        Записать объект в файл pickle.

        Args:
            path (str): Путь к файлу.
            data (Any): Объект для записи.

        Returns:
            bool: True в случае успешной записи.
        """
        pass
