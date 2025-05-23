from core.system_initializer import SystemInitializer


class TestApplicationWorkflow:
    def test_basic_application_flow(self):
        """
        Проверяет базовый рабочий процесс приложения от запуска до выполнения простой задачи.
        Этот тест будет изначально не проходить и поможет определить, что нужно реализовать.
        """
        # Инициализация системы
        system_initializer = SystemInitializer()
        system = system_initializer.initialize()

        # Проверяем, что система успешно инициализирована
        assert system is not False, "Не удалось инициализировать систему"

        # Проверка готовности основных подсистем
        assert system.is_component_registered("filesystem")
        assert system.is_component_registered("input")
        assert system.is_component_registered("vision")

        # Создание простой задачи (например, открытие файла)
        task = system.create_task("Открыть текстовый файл test.txt")

        # Запуск задачи и проверка результата
        result = task.execute()
        assert result.success
        assert "test.txt" in result.details
