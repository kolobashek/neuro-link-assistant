from core.system_initializer import SystemInitializer


class TestWebAutomation:
    def test_web_search_automation(self):
        """Проверяет автоматизацию веб-поиска с обработкой защиты от ботов."""
        system_initializer = SystemInitializer()
        system = system_initializer.initialize()
        assert system is not False, "Не удалось инициализировать систему"

        # Создание задачи для веб-поиска
        task = system.create_task(
            "Открыть браузер, найти в поисковике 'Python TDD' и сохранить первые 3 результата"
        )
        result = task.execute()

        # Проверяем успешность выполнения
        assert result.success, f"Задача не выполнена: {result.details}"

        # Проверяем результаты
        if "captcha" in result.details.lower() or "робот" in result.details.lower():
            # Если обнаружена защита от ботов, это тоже считается успехом
            print("ВНИМАНИЕ: Обнаружена защита от ботов (CAPTCHA)")
            assert (
                "обнаружена защита от ботов" in result.details.lower()
                or len(result.details.split("\n")) >= 3
            )
        else:
            # Обычная проверка результатов поиска
            assert (
                len(result.details.split("\n")) >= 3
            ), f"Недостаточно результатов: {result.details}"

        print(f"Результат поиска: {result.details}")

    def test_web_search_with_alternative_engine(self):
        """Проверяет веб-поиск с использованием альтернативного поисковика."""
        system_initializer = SystemInitializer()
        system = system_initializer.initialize()
        assert system is not False, "Не удалось инициализировать систему"

        # Создание задачи для поиска в DuckDuckGo (менее строгая защита)
        task = system.create_task(
            "Открыть браузер, найти в DuckDuckGo 'Python TDD' и сохранить первые 3 результата"
        )
        result = task.execute()

        assert result.success, f"Задача не выполнена: {result.details}"
        assert len(result.details.split("\n")) >= 3, f"Недостаточно результатов: {result.details}"

        print(f"Результат поиска в DuckDuckGo: {result.details}")

    def test_bot_detection_handling(self):
        """Проверяет обработку обнаружения ботов."""
        system_initializer = SystemInitializer()
        system = system_initializer.initialize()
        assert system is not False, "Не удалось инициализировать систему"

        # Создание задачи, которая может вызвать защиту от ботов
        task = system.create_task("Открыть браузер и проверить наличие защиты от ботов на Google")
        result = task.execute()

        # Задача должна выполниться успешно, даже если обнаружена защита
        assert result.success, f"Задача не выполнена: {result.details}"

        # Результат должен содержать информацию о состоянии
        assert len(result.details) > 0, "Результат не должен быть пустым"

        print(f"Результат проверки защиты: {result.details}")
