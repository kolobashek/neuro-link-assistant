from core.system_initializer import SystemInitializer


class TestWindowsAutomation:
    def test_windows_application_automation(self):
        """Проверяет автоматизацию работы с приложениями Windows."""
        system_initializer = SystemInitializer()
        system = system_initializer.initialize()
        assert system is not False, "Не удалось инициализировать систему"

        # Создание задачи для работы с калькулятором
        task = system.create_task("Открыть калькулятор, выполнить операцию 2+2 и вернуть результат")
        result = task.execute()
        assert result.success
        assert "4" in result.details
