from core.system_initializer import SystemInitializer


class TestFileOperations:
    def test_file_operations_workflow(self):
        """Проверяет работу с файловой системой: создание, чтение, запись, удаление файлов."""
        # Инициализация системы
        system_initializer = SystemInitializer()
        system = system_initializer.initialize()
        assert system is not False, "Не удалось инициализировать систему"

        # Создание задачи для работы с файлами
        task = system.create_task("Создать файл test.txt с текстом 'Hello World'")
        result = task.execute()
        assert result.success

        # Проверка чтения файла
        read_task = system.create_task("Прочитать содержимое файла test.txt")
        read_result = read_task.execute()
        assert read_result.success
        assert "Hello World" in read_result.details

        # Удаление файла
        delete_task = system.create_task("Удалить файл test.txt")
        delete_result = delete_task.execute()
        assert delete_result.success
