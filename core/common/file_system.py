# Абстрактный класс файловой системы
# Позволяет унифицировать работу с локальной-удаленной инфраструктурой


class AbstractFileSystem:
    """Абстрактный класс для работы с файловой системой"""

    def list_directory(self, path):
        """Получить список файлов в директории"""
        raise NotImplementedError("Метод должен быть реализован в дочернем классе")

    def file_exists(self, path):
        """Проверить существование файла"""
        raise NotImplementedError("Метод должен быть реализован в дочернем классе")

    def create_directory(self, path):
        """Создать директорию"""
        raise NotImplementedError("Метод должен быть реализован в дочернем классе")

    def read_file(self, path):
        """Прочитать содержимое файла"""
        raise NotImplementedError("Метод должен быть реализован в дочернем классе")

    def write_file(self, path, content):
        """Записать содержимое в файл"""
        raise NotImplementedError("Метод должен быть реализован в дочернем классе")

    def delete_file(self, path):
        """Удалить файл"""
        raise NotImplementedError("Метод должен быть реализован в дочернем классе")

    def get_file_size(self, path):
        """Получить размер файла"""
        raise NotImplementedError("Метод должен быть реализован в дочернем классе")

    def get_file_modification_time(self, path):
        """Получить время последнего изменения файла"""
        raise NotImplementedError("Метод должен быть реализован в дочернем классе")
