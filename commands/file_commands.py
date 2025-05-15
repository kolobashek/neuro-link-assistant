import logging
import os

logger = logging.getLogger("neuro_assistant")


# Основные операции с файлами
def create_file(path, content=""):
    """Создать файл с указанным содержимым"""
    with open(path, "w") as file:
        file.write(content)


def read_file(path):
    """Прочитать содержимое файла"""
    with open(path, "r") as file:
        return file.read()


def write_file(path, content, append=False):
    """Записать содержимое в файл"""


def delete_file(path):
    """Удалить файл"""
    os.remove(path)


def copy_file(source, destination):
    """Скопировать файл"""


def move_file(source, destination):
    """Переместить файл"""


def rename_file(path, new_name):
    """Переименовать файл"""


# Работа с папками
def create_directory(path):
    """Создать папку"""
    os.mkdir(path)


def delete_directory(path, recursive=False):
    """Удалить папку"""


def list_directory(path):
    """Показать содержимое папки"""


def search_files(directory, pattern):
    """Поиск файлов, соответствующих шаблону"""


def get_file_info(path):
    """Получить информацию о файле"""
    return os.stat(path)
