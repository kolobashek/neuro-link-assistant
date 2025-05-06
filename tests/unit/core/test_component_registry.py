import pytest
from unittest.mock import MagicMock

class TestComponentRegistry:
    """Тесты реестра компонентов"""
    
    @pytest.fixture
    def registry(self):
        """Создает экземпляр ComponentRegistry"""
        from core.component_registry import ComponentRegistry
        return ComponentRegistry()
    
    def test_register_component(self, registry):
        """Тест регистрации компонента"""
        # Создаем тестовый компонент
        test_component = MagicMock()
        
        # Регистрируем компонент
        registry.register("test_component", test_component)
        
        # Проверяем, что компонент зарегистрирован
        assert registry.get("test_component") == test_component
    
    def test_register_duplicate_component(self, registry):
        """Тест регистрации дубликата компонента"""
        # Создаем тестовые компоненты
        component1 = MagicMock()
        component2 = MagicMock()
        
        # Регистрируем первый компонент
        registry.register("test_component", component1)
        
        # Регистрируем второй компонент с тем же именем
        with pytest.raises(ValueError):
            registry.register("test_component", component2)
    
    def test_get_nonexistent_component(self, registry):
        """Тест получения несуществующего компонента"""
        # Пытаемся получить несуществующий компонент
        with pytest.raises(KeyError):
            registry.get("nonexistent_component")
    
    def test_get_component_with_default(self, registry):
        """Тест получения компонента с значением по умолчанию"""
        # Создаем тестовый компонент
        test_component = MagicMock()
        
        # Регистрируем компонент
        registry.register("test_component", test_component)
        
        # Получаем существующий компонент с значением по умолчанию
        component = registry.get("test_component", default=None)
        assert component == test_component
        
        # Получаем несуществующий компонент с значением по умолчанию
        default_value = MagicMock()
        component = registry.get("nonexistent_component", default=default_value)
        assert component == default_value
    
    def test_has_component(self, registry):
        """Тест проверки наличия компонента"""
        # Создаем тестовый компонент
        test_component = MagicMock()
        
        # Регистрируем компонент
        registry.register("test_component", test_component)
        
        # Проверяем наличие компонента
        assert registry.has("test_component") is True
        assert registry.has("nonexistent_component") is False
    
    def test_remove_component(self, registry):
        """Тест удаления компонента"""
        # Создаем тестовый компонент
        test_component = MagicMock()
        
        # Регистрируем компонент
        registry.register("test_component", test_component)
        
        # Удаляем компонент
        registry.remove("test_component")
        
        # Проверяем, что компонент удален
        assert registry.has("test_component") is False
        
        # Проверяем, что получение удаленного компонента вызывает исключение
        with pytest.raises(KeyError):
            registry.get("test_component")
    
    def test_remove_nonexistent_component(self, registry):
        """Тест удаления несуществующего компонента"""
        # Пытаемся удалить несуществующий компонент
        with pytest.raises(KeyError):
            registry.remove("nonexistent_component")
    
    def test_get_all_components(self, registry):
        """Тест получения всех компонентов"""
        # Создаем тестовые компоненты
        component1 = MagicMock()
        component2 = MagicMock()
        
        # Регистрируем компоненты
        registry.register("component1", component1)
        registry.register("component2", component2)
        
        # Получаем все компоненты
        components = registry.get_all()
        
        assert isinstance(components, dict)
        assert len(components) == 2
        assert components["component1"] == component1
        assert components["component2"] == component2