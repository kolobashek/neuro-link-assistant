import os
import pytest
import tempfile
import shutil
import json
import csv
from unittest.mock import patch, mock_open

class TestFileManager:
    """Тесты менеджера файловой системы"""
    
    @pytest.fixture
    def file_manager(self):
        """Создает экземпляр FileManager"""
        from core.filesystem import get_file_system
        return get_file_system()
    
    @pytest.fixture
    def temp_dir(self):
        """Создает временную директорию для тестов"""
        temp_dir = tempfile.mkdtemp()
        yield temp_dir
        # Очищаем после тестов
        shutil.rmtree(temp_dir, ignore_errors=True)
    
    def test_create_file(self, file_manager, temp_dir):
        """Тест создания файла"""
        test_file = os.path.join(temp_dir, "test.txt")
        content = "Test content"
        
        result = file_manager.create_file(test_file, content)
        
        assert result is True
        assert os.path.exists(test_file)
        
        # Проверяем содержимое файла
        with open(test_file, 'r') as f:
            assert f.read() == content
    
    def test_read_file(self, file_manager, temp_dir):
        """Тест чтения файла"""
        test_file = os.path.join(temp_dir, "test.txt")
        content = "Test content"
        
        # Создаем файл для теста
        with open(test_file, 'w') as f:
            f.write(content)
        
        result = file_manager.read_file(test_file)
        
        assert result == content
    
    def test_append_to_file(self, file_manager, temp_dir):
        """Тест добавления в файл"""
        test_file = os.path.join(temp_dir, "test.txt")
        initial_content = "Initial content\n"
        append_content = "Appended content"
        
        # Создаем файл с начальным содержимым
        with open(test_file, 'w') as f:
            f.write(initial_content)
        
        result = file_manager.append_to_file(test_file, append_content)
        
        assert result is True
        
        # Проверяем содержимое файла
        with open(test_file, 'r') as f:
            assert f.read() == initial_content + append_content
    
    def test_delete_file(self, file_manager, temp_dir):
        """Тест удаления файла"""
        test_file = os.path.join(temp_dir, "test.txt")
        
        # Создаем файл для теста
        with open(test_file, 'w') as f:
            f.write("Test content")
        
        result = file_manager.delete_file(test_file)
        
        assert result is True
        assert not os.path.exists(test_file)
    
    def test_create_directory(self, file_manager, temp_dir):
        """Тест создания директории"""
        test_dir = os.path.join(temp_dir, "test_dir")
        
        result = file_manager.create_directory(test_dir)
        
        assert result is True
        assert os.path.exists(test_dir)
        assert os.path.isdir(test_dir)
    
    def test_delete_directory(self, file_manager, temp_dir):
        """Тест удаления директории"""
        test_dir = os.path.join(temp_dir, "test_dir")
        
        # Создаем директорию для теста
        os.makedirs(test_dir)
        
        result = file_manager.delete_directory(test_dir)
        
        assert result is True
        assert not os.path.exists(test_dir)
    
    def test_list_directory(self, file_manager, temp_dir):
        """Тест получения списка файлов в директории"""
        # Создаем тестовые файлы
        test_files = ["file1.txt", "file2.txt", "file3.log"]
        for file_name in test_files:
            with open(os.path.join(temp_dir, file_name), 'w') as f:
                f.write("Test content")
        
        # Получаем список всех файлов
        result = file_manager.list_directory(temp_dir)
        
        assert set(result) == set(test_files)
        
        # Получаем список файлов по шаблону
        result = file_manager.list_directory(temp_dir, "*.txt")
        
        assert set(result) == {"file1.txt", "file2.txt"}
    
    def test_copy_file(self, file_manager, temp_dir):
        """Тест копирования файла"""
        source_file = os.path.join(temp_dir, "source.txt")
        dest_file = os.path.join(temp_dir, "dest.txt")
        content = "Test content"
        
        # Создаем исходный файл
        with open(source_file, 'w') as f:
            f.write(content)
        
        result = file_manager.copy_file(source_file, dest_file)
        
        assert result is True
        assert os.path.exists(dest_file)
        
        # Проверяем содержимое скопированного файла
        with open(dest_file, 'r') as f:
            assert f.read() == content
    
    def test_move_file(self, file_manager, temp_dir):
        """Тест перемещения файла"""
        source_file = os.path.join(temp_dir, "source.txt")
        dest_file = os.path.join(temp_dir, "dest.txt")
        content = "Test content"
        
        # Создаем исходный файл
        with open(source_file, 'w') as f:
            f.write(content)
        
        result = file_manager.move_file(source_file, dest_file)
        
        assert result is True
        assert not os.path.exists(source_file)
        assert os.path.exists(dest_file)
        
        # Проверяем содержимое перемещенного файла
        with open(dest_file, 'r') as f:
            assert f.read() == content
    
    def test_rename_file(self, file_manager, temp_dir):
        """Тест переименования файла"""
        old_name = os.path.join(temp_dir, "old.txt")
        new_name = "new.txt"
        content = "Test content"
        
        # Создаем исходный файл
        with open(old_name, 'w') as f:
            f.write(content)
        
        result = file_manager.rename_file(old_name, new_name)
        
        assert result is True
        assert not os.path.exists(old_name)
        assert os.path.exists(os.path.join(temp_dir, new_name))
        
        # Проверяем содержимое переименованного файла
        with open(os.path.join(temp_dir, new_name), 'r') as f:
            assert f.read() == content
    
    def test_get_file_info(self, file_manager, temp_dir):
        """Тест получения информации о файле"""
        test_file = os.path.join(temp_dir, "test.txt")
        content = "Test content"
        
        # Создаем файл для теста
        with open(test_file, 'w') as f:
            f.write(content)
        
        info = file_manager.get_file_info(test_file)
        
        assert info is not None
        assert info["name"] == "test.txt"
        assert info["path"] == os.path.abspath(test_file)
        assert info["size"] == len(content)
        assert info["is_file"] is True
        assert info["is_directory"] is False
        assert info["extension"] == ".txt"
    
    def test_zip_and_unzip_files(self, file_manager, temp_dir):
        """Тест создания и распаковки ZIP-архива"""
        # Создаем тестовые файлы
        file1 = os.path.join(temp_dir, "file1.txt")
        file2 = os.path.join(temp_dir, "file2.txt")
        with open(file1, 'w') as f:
            f.write("Content 1")
        with open(file2, 'w') as f:
            f.write("Content 2")
        
        zip_path = os.path.join(temp_dir, "archive.zip")
        extract_dir = os.path.join(temp_dir, "extracted")
        
        # Создаем архив
        result = file_manager.zip_files([file1, file2], zip_path)
        assert result is True
        assert os.path.exists(zip_path)
        
        # Распаковываем архив
        result = file_manager.unzip_file(zip_path, extract_dir)
        assert result is True
        assert os.path.exists(extract_dir)
        assert os.path.exists(os.path.join(extract_dir, "file1.txt"))
        assert os.path.exists(os.path.join(extract_dir, "file2.txt"))
        
        # Проверяем содержимое распакованных файлов
        with open(os.path.join(extract_dir, "file1.txt"), 'r') as f:
            assert f.read() == "Content 1"
        with open(os.path.join(extract_dir, "file2.txt"), 'r') as f:
            assert f.read() == "Content 2"
    
    def test_read_write_json(self, file_manager, temp_dir):
        """Тест чтения и записи JSON-файла"""
        json_file = os.path.join(temp_dir, "test.json")
        data = {"name": "Test", "value": 123, "items": [1, 2, 3]}
        
        # Записываем JSON
        result = file_manager.write_json(json_file, data)
        assert result is True
        assert os.path.exists(json_file)
        
        # Читаем JSON
        read_data = file_manager.read_json(json_file)
        assert read_data == data
    
    def test_read_write_csv(self, file_manager, temp_dir):
        """Тест чтения и записи CSV-файла"""
        csv_file = os.path.join(temp_dir, "test.csv")
        data = [
            ["Name", "Age", "City"],
            ["John", "30", "New York"],
            ["Alice", "25", "London"]
        ]
        
        # Записываем CSV
        result = file_manager.write_csv(csv_file, data)
        assert result is True
        assert os.path.exists(csv_file)
        
        # Читаем CSV
        read_data = file_manager.read_csv(csv_file)
        assert read_data == data
    
    def test_read_write_binary(self, file_manager, temp_dir):
        """Тест чтения и записи бинарного файла"""
        binary_file = os.path.join(temp_dir, "test.bin")
        data = b'\x00\x01\x02\x03\x04'
        
        # Записываем бинарные данные
        result = file_manager.write_binary(binary_file, data)
        assert result is True
        assert os.path.exists(binary_file)
        
        # Читаем бинарные данные
        read_data = file_manager.read_binary(binary_file)
        assert read_data == data
    
    def test_read_write_pickle(self, file_manager, temp_dir):
        """Тест чтения и записи объекта pickle"""
        pickle_file = os.path.join(temp_dir, "test.pkl")
        data = {"complex": "object", "with": [1, 2, 3], "nested": {"data": True}}
        
        # Записываем объект
        result = file_manager.write_pickle(pickle_file, data)
        assert result is True
        assert os.path.exists(pickle_file)
        
        # Читаем объект
        read_data = file_manager.read_pickle(pickle_file)
        assert read_data == data
    
    def test_search_files(self, file_manager, temp_dir):
        """Тест поиска файлов"""
        # Создаем структуру файлов для теста
        os.makedirs(os.path.join(temp_dir, "subdir"))
        files = [
            os.path.join(temp_dir, "file1.txt"),
            os.path.join(temp_dir, "file2.txt"),
            os.path.join(temp_dir, "document.doc"),
            os.path.join(temp_dir, "subdir", "file3.txt")
        ]
        
        for file_path in files:
            with open(file_path, 'w') as f:
                f.write("Test content")
        
        # Поиск без рекурсии
        result = file_manager.search_files(temp_dir, "*.txt", recursive=False)
        assert len(result) == 2
        assert os.path.join(temp_dir, "file1.txt") in result
        assert os.path.join(temp_dir, "file2.txt") in result
        assert os.path.join(temp_dir, "subdir", "file3.txt") not in result
        
        # Поиск с рекурсией
        result = file_manager.search_files(temp_dir, "*.txt", recursive=True)
        assert len(result) == 3
        assert os.path.join(temp_dir, "file1.txt") in result
        assert os.path.join(temp_dir, "file2.txt") in result
        assert os.path.join(temp_dir, "subdir", "file3.txt") in result
    
    def test_file_exists(self, file_manager, temp_dir):
        """Тест проверки существования файла"""
        test_file = os.path.join(temp_dir, "test.txt")
        
        # Файл не существует
        assert file_manager.is_file_exists(test_file) is False
        
        # Создаем файл
        with open(test_file, 'w') as f:
            f.write("Test content")
        
        # Файл существует
        assert file_manager.is_file_exists(test_file) is True
    
    def test_directory_exists(self, file_manager, temp_dir):
        """Тест проверки существования директории"""
        test_dir = os.path.join(temp_dir, "test_dir")
        
        # Директория не существует
        assert file_manager.is_directory_exists(test_dir) is False
        
        # Создаем директорию
        os.makedirs(test_dir)
        
        # Директория существует
        assert file_manager.is_directory_exists(test_dir) is True
    
    def test_get_file_size(self, file_manager, temp_dir):
        """Тест получения размера файла"""
        test_file = os.path.join(temp_dir, "test.txt")
        content = "Test content"
        
        # Создаем файл
        with open(test_file, 'w') as f:
            f.write(content)
        
        # Проверяем размер
        assert file_manager.get_file_size(test_file) == len(content)
    
    def test_get_file_extension(self, file_manager):
        """Тест получения расширения файла"""
        assert file_manager.get_file_extension("test.txt") == ".txt"
        assert file_manager.get_file_extension("document.pdf") == ".pdf"
        assert file_manager.get_file_extension("archive.tar.gz") == ".gz"
        assert file_manager.get_file_extension("noextension") == ""