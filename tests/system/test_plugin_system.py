import pytest

from core.system_initializer import SystemInitializer


class TestPluginSystem:
    def test_plugin_loading_and_execution(self):
        """Проверяет загрузку и выполнение плагинов."""
        system_initializer = SystemInitializer()
        system = system_initializer.initialize()
        assert system is not False, "Не удалось инициализировать систему"

        # Получение списка плагинов
        plugins = system.get_plugin_manager().get_loaded_plugins()

        if plugins:
            # Если есть хотя бы один плагин, проверяем его
            plugin_name = next(iter(plugins.keys()))
            task = system.create_task(f"Выполнить операцию с использованием плагина {plugin_name}")
            result = task.execute()
            assert result.success
        else:
            # Если плагинов нет, этот тест пропускается
            pytest.skip("No plugins available for testing")
