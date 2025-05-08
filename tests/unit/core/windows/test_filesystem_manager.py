import pytest
import os
import shutil
import tempfile
from unittest.mock import patch, MagicMock
from core.windows.filesystem_manager import FileSystemManager

class TestFileSystemManager:
    """Тесты класса управления файловой системой Windows"""
    
    @pytest.fixture
    def temp_dir(self):
        """Создает временную директорию для тестов"""
        temp_dir = tempfile.mkdtemp()
        yield temp_dir
        # Очистка после тестов
        if os.path.exists(temp_dir):
            shutil.rmtree(temp_dir)
    
    @pytest.fixture
    def filesystem_manager(self):
        """Создает экземпляр FileSystemManager"""
        return FileSystemManager()    
    def test_list_directory(self, temp_dir, filesystem_manager):
        """Тест получения списка файлов и директорий"""
        # Создаем тестовые файлы и директории
        os.makedirs(os.path.join(temp_dir, "subdir"))
        with open(os.path.join(temp_dir, "file1.txt"), "w") as f:
            f.write("Test content")
        with open(os.path.join(temp_dir, "file2.txt"), "w") as f:
            f.write("More test content")
        
        # Получаем список файлов и директорий
        items = filesystem_manager.list_directory(temp_dir)
        
        # Проверяем результат
        assert len(items) == 3
        assert any(item["name"] == "subdir" and item["type"] == "directory" for item in items)
        assert any(item["name"] == "file1.txt" and item["type"] == "file" for item in items)
        assert any(item["name"] == "file2.txt" and item["type"] == "file" for item in items)
    
    def test_list_directory_not_found(self, filesystem_manager):
        """Тест получения списка файлов из несуществующей директории"""
        # Получаем список файлов из несуществующей директории
        items = filesystem_manager.list_directory("non_existent_directory")
        
        # Проверяем результат
        assert items == []
    
    def test_create_directory(self, temp_dir, filesystem_manager):
        """Тест создания директории"""
        # Создаем директорию
        new_dir = os.path.join(temp_dir, "new_directory")
        result = filesystem_manager.create_directory(new_dir)
        
        # Проверяем результат
        assert result is True
        assert os.path.exists(new_dir)
        assert os.path.isdir(new_dir)
    
    def test_create_directory_already_exists(self, temp_dir, filesystem_manager):
        """Тест создания уже существующей директории"""
        # Создаем директорию
        new_dir = os.path.join(temp_dir, "existing_directory")
        os.makedirs(new_dir)
        
        # Пытаемся создать ту же директорию
        result = filesystem_manager.create_directory(new_dir)
        
        # Проверяем результат
        assert result is True
        assert os.path.exists(new_dir)
        assert os.path.isdir(new_dir)
    
    def test_create_directory_error(self, filesystem_manager):
        """Тест создания директории с ошибкой"""
        # Пытаемся создать директорию в недоступном месте
        result = filesystem_manager.create_directory("C:\\Windows\\System32\\InaccessibleDir")
        
        # Проверяем результат
        assert result is False
    
    def test_delete_directory(self, temp_dir, filesystem_manager):
        """Тест удаления директории"""
        # Создаем директорию
        new_dir = os.path.join(temp_dir, "directory_to_delete")
        os.makedirs(new_dir)
        
        # Удаляем директорию
        result = filesystem_manager.delete_directory(new_dir)
        
        # Проверяем результат
        assert result is True
        assert not os.path.exists(new_dir)
    
    def test_delete_directory_not_found(self, filesystem_manager):
        """Тест удаления несуществующей директории"""
        # Удаляем несуществующую директорию
        result = filesystem_manager.delete_directory("non_existent_directory")
        
        # Проверяем результат
        assert result is False
    
    def test_delete_directory_with_contents(self, temp_dir, filesystem_manager):
        """Тест удаления директории с содержимым"""
        # Создаем директорию с файлами
        new_dir = os.path.join(temp_dir, "directory_with_contents")
        os.makedirs(new_dir)
        with open(os.path.join(new_dir, "file.txt"), "w") as f:
            f.write("Test content")
        
        # Удаляем директорию
        result = filesystem_manager.delete_directory(new_dir, recursive=True)
        
        # Проверяем результат
        assert result is True
        assert not os.path.exists(new_dir)
    
    def test_read_file(self, temp_dir, filesystem_manager):
        """Тест чтения файла"""
        # Создаем тестовый файл
        file_path = os.path.join(temp_dir, "test_file.txt")
        with open(file_path, "w") as f:
            f.write("Test content")
        
        # Читаем файл
        content = filesystem_manager.read_file(file_path)
        
        # Проверяем результат
        assert content == "Test content"
    
    def test_read_file_not_found(self, filesystem_manager):
        """Тест чтения несуществующего файла"""
        # Читаем несуществующий файл
        content = filesystem_manager.read_file("non_existent_file.txt")
        
        # Проверяем результат
        assert content is None
    
    def test_write_file(self, temp_dir, filesystem_manager):
        """Тест записи в файл"""
        # Записываем в файл
        file_path = os.path.join(temp_dir, "new_file.txt")
        result = filesystem_manager.write_file(file_path, "New content")
        
        # Проверяем результат
        assert result is True
        assert os.path.exists(file_path)
        
        # Проверяем содержимое файла
        with open(file_path, "r") as f:
            content = f.read()
        assert content == "New content"
    
    def test_write_file_error(self, filesystem_manager):
        """Тест записи в файл с ошибкой"""
        # Пытаемся записать в файл в недоступном месте
        result = filesystem_manager.write_file("C:\\Windows\\System32\\InaccessibleFile.txt", "Content")
        
        # Проверяем результат
        assert result is False
    
    def test_append_to_file(self, temp_dir, filesystem_manager):
        """Тест добавления в файл"""
        # Создаем тестовый файл
        file_path = os.path.join(temp_dir, "append_file.txt")
        with open(file_path, "w") as f:
            f.write("Initial content")
        
        # Добавляем в файл
        result = filesystem_manager.append_to_file(file_path, "\nAppended content")
        
        # Проверяем результат
        assert result is True
        
        # Проверяем содержимое файла
        with open(file_path, "r") as f:
            content = f.read()
        assert content == "Initial content\nAppended content"
    
    def test_append_to_file_not_found(self, temp_dir, filesystem_manager):
        """Тест добавления в несуществующий файл"""
        # Добавляем в несуществующий файл
        file_path = os.path.join(temp_dir, "non_existent_file.txt")
        result = filesystem_manager.append_to_file(file_path, "Content")
        
        # Проверяем результат
        assert result is True
        assert os.path.exists(file_path)
        
        # Проверяем содержимое файла
        with open(file_path, "r") as f:
            content = f.read()
        assert content == "Content"
    
    def test_delete_file(self, temp_dir, filesystem_manager):
        """Тест удаления файла"""
        # Создаем тестовый файл
        file_path = os.path.join(temp_dir, "file_to_delete.txt")
        with open(file_path, "w") as f:
            f.write("Test content")
        
        # Удаляем файл
        result = filesystem_manager.delete_file(file_path)
        
        # Проверяем результат
        assert result is True
        assert not os.path.exists(file_path)
    
    def test_delete_file_not_found(self, filesystem_manager):
        """Тест удаления несуществующего файла"""
        # Удаляем несуществующий файл
        result = filesystem_manager.delete_file("non_existent_file.txt")
        
        # Проверяем результат
        assert result is False
    
    def test_copy_file(self, temp_dir, filesystem_manager):
        """Тест копирования файла"""
        # Создаем тестовый файл
        source_path = os.path.join(temp_dir, "source_file.txt")
        with open(source_path, "w") as f:
            f.write("Test content")
        
        # Копируем файл
        dest_path = os.path.join(temp_dir, "dest_file.txt")
        result = filesystem_manager.copy_file(source_path, dest_path)
        
        # Проверяем результат
        assert result is True
        assert os.path.exists(dest_path)
        
        # Проверяем содержимое файла
        with open(dest_path, "r") as f:
            content = f.read()
        assert content == "Test content"
    
    def test_copy_file_source_not_found(self, temp_dir, filesystem_manager):
        """Тест копирования несуществующего файла"""
        # Копируем несуществующий файл
        source_path = os.path.join(temp_dir, "non_existent_file.txt")
        dest_path = os.path.join(temp_dir, "dest_file.txt")
        result = filesystem_manager.copy_file(source_path, dest_path)
        
        # Проверяем результат
        assert result is False
        assert not os.path.exists(dest_path)
    
    def test_move_file(self, temp_dir, filesystem_manager):
        """Тест перемещения файла"""
        # Создаем тестовый файл
        source_path = os.path.join(temp_dir, "source_file.txt")
        with open(source_path, "w") as f:
            f.write("Test content")
        
        # Перемещаем файл
        dest_path = os.path.join(temp_dir, "moved_file.txt")
        result = filesystem_manager.move_file(source_path, dest_path)
        
        # Проверяем результат
        assert result is True
        assert not os.path.exists(source_path)
        assert os.path.exists(dest_path)
        
        # Проверяем содержимое файла
        with open(dest_path, "r") as f:
            content = f.read()
        assert content == "Test content"
    
    def test_move_file_source_not_found(self, temp_dir, filesystem_manager):
        """Тест перемещения несуществующего файла"""
        # Перемещаем несуществующий файл
        source_path = os.path.join(temp_dir, "non_existent_file.txt")
        dest_path = os.path.join(temp_dir, "moved_file.txt")
        result = filesystem_manager.move_file(source_path, dest_path)
        
        # Проверяем результат
        assert result is False
        assert not os.path.exists(dest_path)
    
    def test_get_file_info(self, temp_dir, filesystem_manager):
        """Тест получения информации о файле"""
        # Создаем тестовый файл
        file_path = os.path.join(temp_dir, "info_file.txt")
        with open(file_path, "w") as f:
            f.write("Test content")
        
        # Получаем информацию о файле
        info = filesystem_manager.get_file_info(file_path)
        
        # Проверяем результат
        assert info is not None
        assert info["name"] == "info_file.txt"
        assert info["path"] == file_path
        assert info["size"] > 0
        assert info["is_file"] is True
        assert info["is_directory"] is False
        assert "created" in info
        assert "modified" in info
        assert "accessed" in info
    
    def test_get_file_info_not_found(self, filesystem_manager):
        """Тест получения информации о несуществующем файле"""
        # Получаем информацию о несуществующем файле
        info = filesystem_manager.get_file_info("non_existent_file.txt")
        
        # Проверяем результат
        assert info is None
    
    def test_search_files(self, temp_dir, filesystem_manager):
        """Тест поиска файлов"""
        # Создаем тестовые файлы
        os.makedirs(os.path.join(temp_dir, "subdir"))
        with open(os.path.join(temp_dir, "file1.txt"), "w") as f:
            f.write("Test content")
        with open(os.path.join(temp_dir, "file2.txt"), "w") as f:
            f.write("More test content")
        with open(os.path.join(temp_dir, "subdir", "file3.txt"), "w") as f:
            f.write("Nested test content")
        
        # Ищем файлы по маске
        files = filesystem_manager.search_files(temp_dir, "*.txt", recursive=True)
        
        # Проверяем результат
        assert len(files) == 3
        assert any(file["name"] == "file1.txt" for file in files)
        assert any(file["name"] == "file2.txt" for file in files)
        assert any(file["name"] == "file3.txt" for file in files)
    
    def test_search_files_not_recursive(self, temp_dir, filesystem_manager):
        """Тест поиска файлов без рекурсии"""
        # Создаем тестовые файлы
        os.makedirs(os.path.join(temp_dir, "subdir"))
        with open(os.path.join(temp_dir, "file1.txt"), "w") as f:
            f.write("Test content")
        with open(os.path.join(temp_dir, "file2.txt"), "w") as f:
            f.write("More test content")
        with open(os.path.join(temp_dir, "subdir", "file3.txt"), "w") as f:
            f.write("Nested test content")
        
        # Ищем файлы по маске без рекурсии
        files = filesystem_manager.search_files(temp_dir, "*.txt", recursive=False)
        
        # Проверяем результат
        assert len(files) == 2
        assert any(file["name"] == "file1.txt" for file in files)
        assert any(file["name"] == "file2.txt" for file in files)
        assert not any(file["name"] == "file3.txt" for file in files)