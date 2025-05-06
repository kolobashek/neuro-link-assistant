import pytest
from unittest.mock import MagicMock

@pytest.fixture
def mock_component():
    """Фикстура для создания мок-компонента"""
    return MagicMock()

@pytest.fixture
def empty_registry():
    """Фикстура для создания пустого реестра компонентов"""
    try:
        from core.component_registry import ComponentRegistry
        return ComponentRegistry()
    except ImportError:
        # Заглушка, если модуль еще не реализован
        class ComponentRegistry:
            def __init__(self):
                self.components = {}
            
            def register(self, name, component):
                self.components[name] = component
                return True
            
            def get(self, name):
                return self.components.get(name)
        
        return ComponentRegistry()