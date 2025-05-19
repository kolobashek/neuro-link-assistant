# Абстрактный класс файловой системы
# Позволяет унифицировать работу с локальной-удаленной инфраструктурой
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple, Union


class AbstractFileSystem:
    """Абстрактный класс для работы с файловой системой"""

    # Базовые операции с файлами
    def list_directory(self, path: str, pattern: str = "*", recursive: bool = False) -> List[str]:
        """Получить список файлов в директории

        Args:
            path: Путь к директории
            pattern: Шаблон для фильтрации файлов
            recursive: Рекурсивный поиск в поддиректориях

        Returns:
            Список имен файлов и директорий
        """
        raise NotImplementedError("Метод должен быть реализован в дочернем классе")

    def file_exists(self, path: str) -> bool:
        """Проверить существование файла

        Args:
            path: Путь к файлу

        Returns:
            True, если файл существует
        """
        raise NotImplementedError("Метод должен быть реализован в дочернем классе")

    def create_directory(self, path: str) -> bool:
        """Создать директорию

        Args:
            path: Путь к создаваемой директории

        Returns:
            True в случае успешного создания
        """
        raise NotImplementedError("Метод должен быть реализован в дочернем классе")

    def read_file(self, path: str, encoding: str = "utf-8") -> str:
        """Прочитать содержимое файла

        Args:
            path: Путь к файлу
            encoding: Кодировка файла

        Returns:
            Содержимое файла
        """
        raise NotImplementedError("Метод должен быть реализован в дочернем классе")

    def write_file(self, path: str, content: str, encoding: str = "utf-8") -> bool:
        """Записать содержимое в файл

        Args:
            path: Путь к файлу
            content: Содержимое для записи
            encoding: Кодировка файла

        Returns:
            True в случае успешной записи
        """
        raise NotImplementedError("Метод должен быть реализован в дочернем классе")

    def delete_file(self, path: str) -> bool:
        """Удалить файл

        Args:
            path: Путь к файлу

        Returns:
            True в случае успешного удаления
        """
        raise NotImplementedError("Метод должен быть реализован в дочернем классе")

    def get_file_size(self, path: str) -> int:
        """Получить размер файла

        Args:
            path: Путь к файлу

        Returns:
            Размер файла в байтах или -1 в случае ошибки
        """
        raise NotImplementedError("Метод должен быть реализован в дочернем классе")

    def get_file_modification_time(self, path: str) -> Optional[datetime]:
        """Получить время последнего изменения файла

        Args:
            path: Путь к файлу

        Returns:
            Время последнего изменения файла или None в случае ошибки
        """
        raise NotImplementedError("Метод должен быть реализован в дочернем классе")

    # Дополнительные операции с файлами из FileManager и других классов
    def create_file(self, path: str, content: str = "", encoding: str = "utf-8") -> bool:
        """Создает файл с указанным содержимым.

        Args:
            path: Путь к файлу
            content: Содержимое файла
            encoding: Кодировка файла

        Returns:
            True в случае успешного создания
        """
        raise NotImplementedError("Метод должен быть реализован в дочернем классе")

    def append_to_file(self, path: str, content: str, encoding: str = "utf-8") -> bool:
        """Добавляет содержимое в конец файла.

        Args:
            path: Путь к файлу
            content: Содержимое для добавления
            encoding: Кодировка файла

        Returns:
            True в случае успешного добавления
        """
        raise NotImplementedError("Метод должен быть реализован в дочернем классе")

    def delete_directory(self, path: str, recursive: bool = True) -> bool:
        """Удаляет директорию.

        Args:
            path: Путь к директории
            recursive: Удалять рекурсивно с содержимым

        Returns:
            True в случае успешного удаления
        """
        raise NotImplementedError("Метод должен быть реализован в дочернем классе")

    def copy_file(self, source: str, destination: str) -> bool:
        """Копирует файл.

        Args:
            source: Путь к исходному файлу
            destination: Путь к целевому файлу

        Returns:
            True в случае успешного копирования
        """
        raise NotImplementedError("Метод должен быть реализован в дочернем классе")

    def move_file(self, source: str, destination: str) -> bool:
        """Перемещает файл.

        Args:
            source: Путь к исходному файлу
            destination: Путь к целевому файлу

        Returns:
            True в случае успешного перемещения
        """
        raise NotImplementedError("Метод должен быть реализован в дочернем классе")

    def rename_file(self, path: str, new_name: str) -> bool:
        """Переименовывает файл.

        Args:
            path: Путь к файлу
            new_name: Новое имя файла (без пути)

        Returns:
            True в случае успешного переименования
        """
        raise NotImplementedError("Метод должен быть реализован в дочернем классе")

    def get_file_info(self, path: str) -> Optional[Dict[str, Any]]:
        """Получает информацию о файле.

        Args:
            path: Путь к файлу

        Returns:
            Словарь с информацией о файле или None в случае ошибки
        """
        raise NotImplementedError("Метод должен быть реализован в дочернем классе")

    def is_directory_exists(self, path: str) -> bool:
        """Проверяет существование директории.

        Args:
            path: Путь к директории

        Returns:
            True, если директория существует
        """
        raise NotImplementedError("Метод должен быть реализован в дочернем классе")

    def get_file_extension(self, path: str) -> str:
        """Получает расширение файла.

        Args:
            path: Путь к файлу или имя файла

        Returns:
            Расширение файла с точкой или пустая строка
        """
        raise NotImplementedError("Метод должен быть реализован в дочернем классе")

    def search_files(
        self, directory: str, pattern: str = "*", recursive: bool = False
    ) -> List[str]:
        """Ищет файлы по шаблону.

        Args:
            directory: Директория для поиска
            pattern: Шаблон поиска (например, "*.txt")
            recursive: Рекурсивный поиск в поддиректориях

        Returns:
            Список путей к найденным файлам
        """
        raise NotImplementedError("Метод должен быть реализован в дочернем классе")

    # Операции с ZIP-архивами
    def zip_files(self, file_paths: List[str], zip_path: str) -> bool:
        """Создает ZIP-архив из указанных файлов.

        Args:
            file_paths: Список путей к файлам
            zip_path: Путь к создаваемому ZIP-архиву

        Returns:
            True в случае успешного создания архива
        """
        raise NotImplementedError("Метод должен быть реализован в дочернем классе")

    def unzip_file(self, zip_path: str, extract_to: str) -> bool:
        """Распаковывает ZIP-архив.

        Args:
            zip_path: Путь к ZIP-архиву
            extract_to: Путь для распаковки

        Returns:
            True в случае успешной распаковки
        """
        raise NotImplementedError("Метод должен быть реализован в дочернем классе")

    # Операции с различными форматами данных
    def read_json(self, path: str) -> Optional[Dict]:
        """Читает JSON-файл.

        Args:
            path: Путь к JSON-файлу

        Returns:
            Данные из JSON-файла или None в случае ошибки
        """
        raise NotImplementedError("Метод должен быть реализован в дочернем классе")

    def write_json(self, path: str, data: Dict, indent: int = 4) -> bool:
        """Записывает данные в JSON-файл.

        Args:
            path: Путь к JSON-файлу
            data: Данные для записи
            indent: Отступ для форматирования JSON

        Returns:
            True в случае успешной записи
        """
        raise NotImplementedError("Метод должен быть реализован в дочернем классе")

    def read_csv(self, path: str, delimiter: str = ",") -> Optional[List[List[str]]]:
        """Читает CSV-файл.

        Args:
            path: Путь к CSV-файлу
            delimiter: Разделитель полей

        Returns:
            Данные из CSV-файла или None в случае ошибки
        """
        raise NotImplementedError("Метод должен быть реализован в дочернем классе")

    def write_csv(self, path: str, data: List[List[str]], delimiter: str = ",") -> bool:
        """Записывает данные в CSV-файл.

        Args:
            path: Путь к CSV-файлу
            data: Данные для записи (список списков)
            delimiter: Разделитель полей

        Returns:
            True в случае успешной записи
        """
        raise NotImplementedError("Метод должен быть реализован в дочернем классе")

    def read_binary(self, path: str) -> Optional[bytes]:
        """Читает бинарный файл.

        Args:
            path: Путь к файлу

        Returns:
            Содержимое файла или None в случае ошибки
        """
        raise NotImplementedError("Метод должен быть реализован в дочернем классе")

    def write_binary(self, path: str, data: bytes) -> bool:
        """Записывает данные в бинарный файл.

        Args:
            path: Путь к файлу
            data: Данные для записи

        Returns:
            True в случае успешной записи
        """
        raise NotImplementedError("Метод должен быть реализован в дочернем классе")

    def read_pickle(self, path: str) -> Optional[Any]:
        """Читает объект из файла pickle.

        Args:
            path: Путь к файлу

        Returns:
            Объект из файла или None в случае ошибки
        """
        raise NotImplementedError("Метод должен быть реализован в дочернем классе")

    def write_pickle(self, path: str, data: Any) -> bool:
        """Записывает объект в файл pickle.

        Args:
            path: Путь к файлу
            data: Объект для записи

        Returns:
            True в случае успешной записи
        """
        raise NotImplementedError("Метод должен быть реализован в дочернем классе")

    # Дополнительные методы из FileSystemManager
    def get_directory_size(self, directory_path: str) -> int:
        """Вычисляет размер директории.

        Args:
            directory_path: Путь к директории

        Returns:
            Размер директории в байтах или -1 в случае ошибки
        """
        raise NotImplementedError("Метод должен быть реализован в дочернем классе")

    def is_path_exists(self, path: str) -> bool:
        """Проверяет существование пути.

        Args:
            path: Путь для проверки

        Returns:
            True, если путь существует (файл или директория)
        """
        raise NotImplementedError("Метод должен быть реализован в дочернем классе")

    def get_absolute_path(self, path: str) -> str:
        """Получает абсолютный путь.

        Args:
            path: Относительный или абсолютный путь

        Returns:
            Абсолютный путь
        """
        raise NotImplementedError("Метод должен быть реализован в дочернем классе")

    def join_paths(self, *paths: str) -> str:
        """Объединяет пути.

        Args:
            *paths: Части пути для объединения

        Returns:
            Объединенный путь
        """
        raise NotImplementedError("Метод должен быть реализован в дочернем классе")

    def get_parent_directory(self, path: str) -> str:
        """Получает родительскую директорию.

        Args:
            path: Путь к файлу или директории

        Returns:
            Путь к родительской директории
        """
        raise NotImplementedError("Метод должен быть реализован в дочернем классе")

    def get_file_name(self, path: str) -> str:
        """Получает имя файла из пути.

        Args:
            path: Путь к файлу

        Returns:
            Имя файла с расширением
        """
        raise NotImplementedError("Метод должен быть реализован в дочернем классе")

    def get_file_name_without_extension(self, path: str) -> str:
        """Получает имя файла без расширения.

        Args:
            path: Путь к файлу

        Returns:
            Имя файла без расширения
        """
        raise NotImplementedError("Метод должен быть реализован в дочернем классе")

    # Методы для работы с временными файлами
    def create_temp_file(
        self, prefix: str = "", suffix: str = "", content: str = ""
    ) -> Tuple[str, bool]:
        """Создает временный файл.

        Args:
            prefix: Префикс имени файла
            suffix: Суффикс имени файла
            content: Начальное содержимое файла

        Returns:
            Кортеж (путь к временному файлу, успех операции)
        """
        raise NotImplementedError("Метод должен быть реализован в дочернем классе")

    def create_temp_directory(self, prefix: str = "") -> Tuple[str, bool]:
        """Создает временную директорию.

        Args:
            prefix: Префикс имени директории

        Returns:
            Кортеж (путь к временной директории, успех операции)
        """
        raise NotImplementedError("Метод должен быть реализован в дочернем классе")

    # Методы для проверки прав доступа
    def is_readable(self, path: str) -> bool:
        """Проверяет, можно ли прочитать файл или директорию.

        Args:
            path: Путь к файлу или директории

        Returns:
            True, если путь доступен для чтения
        """
        raise NotImplementedError("Метод должен быть реализован в дочернем классе")

    def is_writable(self, path: str) -> bool:
        """Проверяет, можно ли записать в файл или директорию.

        Args:
            path: Путь к файлу или директории

        Returns:
            True, если путь доступен для записи
        """
        raise NotImplementedError("Метод должен быть реализован в дочернем классе")

    def is_executable(self, path: str) -> bool:
        """Проверяет, можно ли выполнить файл.

        Args:
            path: Путь к файлу

        Returns:
            True, если файл доступен для выполнения
        """
        raise NotImplementedError("Метод должен быть реализован в дочернем классе")

    # Платформо-зависимые методы
    def get_drive_info(self) -> Dict[str, Dict[str, Union[str, int, float]]]:
        """Получает информацию о дисках.

        Returns:
            Словарь с информацией о дисках, где ключи - буквы дисков,
            значения - словари с информацией о диске (размер, свободное место и т.д.)
        """
        raise NotImplementedError("Метод должен быть реализован в дочернем классе")

    def get_home_directory(self) -> str:
        """Получает путь к домашней директории пользователя.

        Returns:
            Путь к домашней директории
        """
        raise NotImplementedError("Метод должен быть реализован в дочернем классе")

    def get_temp_directory(self) -> str:
        """Получает путь к временной директории.

        Returns:
            Путь к временной директории
        """
        raise NotImplementedError("Метод должен быть реализован в дочернем классе")

    def get_current_directory(self) -> str:
        """Получает путь к текущей рабочей директории.

        Returns:
            Путь к текущей директории
        """
        raise NotImplementedError("Метод должен быть реализован в дочернем классе")

    def set_current_directory(self, path: str) -> bool:
        """Устанавливает текущую рабочую директорию.

        Args:
            path: Путь к директории

        Returns:
            True в случае успешного изменения директории
        """
        raise NotImplementedError("Метод должен быть реализован в дочернем классе")

    # Методы для проверки и манипуляции символическими ссылками
    def is_symlink(self, path: str) -> bool:
        """Проверяет, является ли путь символической ссылкой.

        Args:
            path: Путь для проверки

        Returns:
            True, если путь является символической ссылкой
        """
        raise NotImplementedError("Метод должен быть реализован в дочернем классе")

    def create_symlink(self, source: str, link_name: str) -> bool:
        """Создает символическую ссылку.

        Args:
            source: Путь к исходному файлу/директории
            link_name: Путь к создаваемой символической ссылке

        Returns:
            True в случае успешного создания ссылки
        """
        raise NotImplementedError("Метод должен быть реализован в дочернем классе")

    def read_symlink(self, path: str) -> Optional[str]:
        """Читает цель символической ссылки.

        Args:
            path: Путь к символической ссылке

        Returns:
            Путь, на который указывает ссылка, или None в случае ошибки
        """
        raise NotImplementedError("Метод должен быть реализован в дочернем классе")
