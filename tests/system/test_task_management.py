from core.system_initializer import SystemInitializer


class TestTaskManagement:
    def test_task_lifecycle(self):
        """Проверяет полный жизненный цикл задачи: создание, выполнение, сохранение в истории."""
        system_initializer = SystemInitializer()
        system = system_initializer.initialize()
        assert system is not False, "Не удалось инициализировать систему"

        # Создание задачи
        task = system.create_task("Тестовая задача для проверки жизненного цикла")

        # Сохранение и получение задачи из базы данных
        task_id = system.task_manager.save_task(task)
        retrieved_task = system.task_manager.get_task(task_id)
        assert retrieved_task.description == task.description

        # Выполнение задачи
        result = retrieved_task.execute()
        assert result.success

        # Проверка истории задач
        history = system.task_manager.get_task_history()
        assert any(t.id == task_id for t in history)
