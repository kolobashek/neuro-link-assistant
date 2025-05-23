from core.system_initializer import SystemInitializer


class TestWebAutomation:
    def test_web_search_automation(self):
        """Проверяет автоматизацию веб-поиска."""
        system_initializer = SystemInitializer()
        system = system_initializer.initialize()
        assert system is not False, "Не удалось инициализировать систему"

        # Создание задачи для веб-поиска
        task = system.create_task(
            "Открыть браузер, найти в поисковике 'Python TDD' и сохранить первые 3 результата"
        )
        result = task.execute()
        assert result.success
        assert len(result.details.split("\n")) >= 3  # Проверка наличия как минимум 3 результатов
