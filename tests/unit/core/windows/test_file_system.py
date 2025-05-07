import pytest
import os
import shutil
from unittest.mock import patch, MagicMock

class TestFileSystem:
    """Тесты класса файловой системы Windows"""
    
    @pytest.fixture
    def file_system(self):
        """Создает экземпляр FileSystem с мок-зависимостями"""
        from core.filesystem import get_file_system FileSystem
        return FileSystem()
    
    @pytest.fixture
    def test_dir(self, tmp_path):
        """Создает временную директорию для тестов"""
        return tmp_path
    
    def test_create_directory(self, file_system, test_dir):
        """Тест создания директории"""
        # Создаем путь к новой директории
        new_dir = test_dir / "test_create_dir"
        
        # Создаем директорию
        result = file_system.create_directory(str(new_dir))
        
        # Проверяем результат
        assert result is True
        assert os.path.exists(new_dir)
        assert os.path.isdir(new_dir)
    
    def test_create_directory_exists(self, file_system, test_dir):
        """Тест создания директории, которая уже существует"""
        # Создаем директорию
        new_dir = test_dir / "test_exists_dir"
        os.makedirs(new_dir, exist_ok=True)
        
        # Пытаемся создать ту же директорию
        result = file_system.create_directory(str(new_dir))
        
        # Проверяем результат (должен быть True, так как директория существует)
        assert result is True
        assert os.path.exists(new_dir)
        assert os.path.isdir(new_dir)
    
    def test_delete_directory(self, file_system, test_dir):
        """Тест удаления директории"""
        # Создаем директорию
        new_dir = test_dir / "test_delete_dir"
        os.makedirs(new_dir, exist_ok=True)
        
        # Удаляем директорию
        result = file_system.delete_directory(str(new_dir))
        
        # Проверяем результат
        assert result is True
        assert not os.path.exists(new_dir)
    
    def test_delete_directory_not_exists(self, file_system, test_dir):
        """Тест удаления несуществующей директории"""
        # Создаем путь к несуществующей директории
        non_existent_dir = test_dir / "non_existent_dir"
        
        # Удаляем директорию
        result = file_system.delete_directory(str(non_existent_dir))
        
        # Проверяем результат (должен быть False, так как директория не существует)
        assert result is False
    
    def test_list_directory(self, file_system, test_dir):
        """Тест получения списка файлов и директорий"""
        # Создаем директорию с файлами и поддиректориями
        test_subdir = test_dir / "test_list_dir"
        os.makedirs(test_subdir, exist_ok=True)
        
        # Создаем файлы
        (test_subdir / "file1.txt").write_text("Test file 1")
        (test_subdir / "file2.txt").write_text("Test file 2")
        
        # Создаем поддиректорию
        os.makedirs(test_subdir / "subdir", exist_ok=True)
        
        # Получаем список файлов и директорий
        result = file_system.list_directory(str(test_subdir))
        
        # Проверяем результат
        assert len(result) == 3
        assert "file1.txt" in result
        assert "file2.txt" in result
        assert "subdir" in result
    
    def test_list_directory_not_exists(self, file_system, test_dir):
        """Тест получения списка файлов из несуществующей директории"""
        # Создаем путь к несуществующей директории
        non_existent_dir = test_dir / "non_existent_dir"
        
        # Получаем список файлов и директорий
        result = file_system.list_directory(str(non_existent_dir))
        
        # Проверяем результат (должен быть пустой список)
        assert result == []
    
    def test_create_file(self, file_system, test_dir):
        """Тест создания файла"""
        # Создаем путь к новому файлу
        new_file = test_dir / "test_create_file.txt"
        
        # Создаем файл с содержимым
        content = "Test file content"
        result = file_system.create_file(str(new_file), content)
        
        # Проверяем результат
        assert result is True
        assert os.path.exists(new_file)
        assert os.path.isfile(new_file)
        assert new_file.read_text() == content
    
    def test_read_file(self, file_system, test_dir):
        """Тест чтения файла"""
        # Создаем файл с содержимым
        test_file = test_dir / "test_read_file.txt"
        content = "Test file content for reading"
        test_file.write_text(content)
        
        # Читаем файл
        result = file_system.read_file(str(test_file))
        
        # Проверяем результат
        assert result == content
    
    def test_read_file_not_exists(self, file_system, test_dir):
        """Тест чтения несуществующего файла"""
        # Создаем путь к несуществующему файлу
        non_existent_file = test_dir / "non_existent_file.txt"
        
        # Читаем файл
        result = file_system.read_file(str(non_existent_file))
        
        # Проверяем результат (должен быть None)
        assert result is None
    
    def test_write_file(self, file_system, test_dir):
        """Тест записи в файл"""
        # Создаем путь к файлу
        test_file = test_dir / "test_write_file.txt"
        
        # Записываем содержимое в файл
        content = "Test file content for writing"
        result = file_system.write_file(str(test_file), content)
        
        # Проверяем результат
        assert result is True
        assert os.path.exists(test_file)
        assert test_file.read_text() == content
    
    def test_append_file(self, file_system, test_dir):
        """Тест добавления в файл"""
        # Создаем файл с начальным содержимым
        test_file = test_dir / "test_append_file.txt"
        initial_content = "Initial content\n"
        test_file.write_text(initial_content)
        
        # Добавляем содержимое в файл
        append_content = "Appended content"
        result = file_system.append_file(str(test_file), append_content)
        
        # Проверяем результат
        assert result is True
        assert test_file.read_text() == initial_content + append_content
    
    def test_delete_file(self, file_system, test_dir):
        """Тест удаления файла"""
        # Создаем файл
        test_file = test_dir / "test_delete_file.txt"
        test_file.write_text("Test file for deletion")
        
        # Удаляем файл
        result = file_system.delete_file(str(test_file))
        
        # Проверяем результат
        assert result is True
        assert not os.path.exists(test_file)
    
    def test_delete_file_not_exists(self, file_system, test_dir):
        """Тест удаления несуществующего файла"""
        # Создаем путь к несуществующему файлу
        non_existent_file = test_dir / "non_existent_file.txt"
        
        # Удаляем файл
        result = file_system.delete_file(str(non_existent_file))
        
        # Проверяем результат (должен быть False)
        assert result is False
    
    def test_copy_file(self, file_system, test_dir):
        """Тест копирования файла"""
        # Создаем исходный файл
        source_file = test_dir / "source_file.txt"
        content = "Test file for copying"
        source_file.write_text(content)
        
        # Создаем путь к целевому файлу
        target_file = test_dir / "target_file.txt"
        
        # Копируем файл
        result = file_system.copy_file(str(source_file), str(target_file))
        
        # Проверяем результат
        assert result is True
        assert os.path.exists(target_file)
        assert target_file.read_text() == content
    
    def test_move_file(self, file_system, test_dir):
        """Тест перемещения файла"""
        # Создаем исходный файл
        source_file = test_dir / "source_move_file.txt"
        content = "Test file for moving"
        source_file.write_text(content)
        
        # Создаем путь к целевому файлу
        target_file = test_dir / "target_move_file.txt"
        
        # Перемещаем файл
        result = file_system.move_file(str(source_file), str(target_file))
        
        # Проверяем результат
        assert result is True
        assert not os.path.exists(source_file)
        assert os.path.exists(target_file)
        assert target_file.read_text() == content
    
    def test_get_file_info(self, file_system, test_dir):
        """Тест получения информации о файле"""
        # Создаем файл
        test_file = test_dir / "test_info_file.txt"
        content = "Test file for info"
        test_file.write_text(content)
        
        # Получаем информацию о файле
        info = file_system.get_file_info(str(test_file))
        
        # Проверяем результат
        assert info is not None
        assert "size" in info
        assert info["size"] == len(content)
        assert "created" in info
        assert "modified" in info
        assert "is_directory" in info
        assert info["is_directory"] is False
    
    def test_get_file_info_directory(self, file_system, test_dir):
        """Тест получения информации о директории"""
        # Создаем директорию
        test_subdir = test_dir / "test_info_dir"
        os.makedirs(test_subdir, exist_ok=True)
        
        # Получаем информацию о директории
        info = file_system.get_file_info(str(test_subdir))
        
        # Проверяем результат
        assert info is not None
        assert "is_directory" in info
        assert info["is_directory"] is True
    
    def test_search_files(self, file_system, test_dir):
        """Тест поиска файлов по шаблону"""
        # Создаем директорию с файлами
        test_search_dir = test_dir / "test_search_dir"
        os.makedirs(test_search_dir, exist_ok=True)
        
        # Создаем файлы
        (test_search_dir / "file1.txt").write_text("Test file 1")
        (test_search_dir / "file2.txt").write_text("Test file 2")
        (test_search_dir / "document.doc").write_text("Test document")
        
        # Создаем поддиректорию с файлами
        os.makedirs(test_search_dir / "subdir", exist_ok=True)
        (test_search_dir / "subdir" / "file3.txt").write_text("Test file 3")
        
        # Ищем файлы по шаблону *.txt
        result = file_system.search_files(str(test_search_dir), "*.txt", recursive=True)
        
        # Проверяем результат
        assert len(result) == 3
        assert any("file1.txt" in path for path in result)
        assert any("file2.txt" in path for path in result)
        assert any("file3.txt" in path for path in result)
        assert not any("document.doc" in path for path in result)
    
    def test_get_drive_info(self, file_system):
        """Тест получения информации о дисках"""
        # Получаем информацию о дисках
        drives = file_system.get_drive_info()
        
        # Проверяем результат
        assert isinstance(drives, dict)
        # На Windows должен быть хотя бы один диск (C:)
        assert len(drives) > 0
        
        # Проверяем структуру информации о диске
        for drive, info in drives.items():
            assert "total" in info
            assert "free" in info
            assert "used" in info