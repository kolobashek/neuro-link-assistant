from core.system_initializer import SystemInitializer


class TestComputerVision:
    def test_screen_capture_and_analysis(self):
        """Проверяет функциональность компьютерного зрения: захват экрана и распознавание элементов."""
        system_initializer = SystemInitializer()
        system = system_initializer.initialize()
        assert system is not False, "Не удалось инициализировать систему"

        # Создание задачи для захвата экрана
        task = system.create_task("Сделать снимок экрана и найти иконку проводника")
        result = task.execute()
        assert result.success
        assert "координаты" in result.details.lower()  # Должны быть найдены координаты элемента
