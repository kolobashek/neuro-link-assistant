from core.system_initializer import SystemInitializer


class TestModelOrchestration:
    def test_multi_model_workflow(self):
        """Проверяет оркестрацию нескольких моделей для решения комплексной задачи."""
        system_initializer = SystemInitializer()
        system = system_initializer.initialize()
        assert system is not False, "Не удалось инициализировать систему"

        # Задача, требующая координации нескольких моделей
        task = system.create_task(
            "Найти на рабочем столе документ с текстом, проанализировать его содержимое с помощью LLM и сохранить результат в новый файл"
        )
        result = task.execute()
        assert result.success
        assert "анализ сохранен" in result.details.lower()
