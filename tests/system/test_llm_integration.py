from core.system_initializer import SystemInitializer


class TestLLMIntegration:
    def test_llm_basic_interaction(self):
        """Проверяет базовое взаимодействие с языковыми моделями."""
        system_initializer = SystemInitializer()
        system = system_initializer.initialize()
        assert system is not False, "Не удалось инициализировать систему"

        # Создание задачи для LLM
        task = system.create_task("Сгенерировать короткое стихотворение о программировании")
        result = task.execute()
        assert result.success
        assert len(result.details) > 50  # Проверка, что получен достаточно длинный ответ
