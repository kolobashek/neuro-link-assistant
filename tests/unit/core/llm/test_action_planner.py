import pytest
from unittest.mock import MagicMock, patch

# Предполагаем, что у нас есть класс ActionPlanner в core/llm/action_planner.py
# Если его нет, нужно будет создать этот файл
try:
    from core.llm.action_planner import ActionPlanner
    HAS_ACTION_PLANNER = True
except ImportError:
    HAS_ACTION_PLANNER = False

# Пропускаем тесты, если модуль не найден
pytestmark = pytest.mark.skipif(not HAS_ACTION_PLANNER, reason="ActionPlanner not implemented yet")

class TestActionPlanner:
    """Тесты для планировщика действий"""
    
    @pytest.fixture
    def action_planner(self):
        """Фикстура для создания экземпляра ActionPlanner"""
        # Создаем мок для обработчика ошибок
        error_handler = MagicMock()
        
        # Создаем мок для API-коннектора
        api_connector = MagicMock()
        
        # Создаем планировщик действий
        planner = ActionPlanner(
            api_connector=api_connector,
            error_handler=error_handler
        )
        
        return planner
    
    def test_plan_actions(self, action_planner):
        """Тест планирования действий на основе запроса"""
        import json
        
        # Настраиваем мок API-коннектора для возврата плана действий
        action_planner.api_connector.send_request.return_value = {
            "choices": [
                {
                    "message": {
                        "content": json.dumps([
                            {"action": "open_file", "params": {"path": "example.txt"}},
                            {"action": "read_content", "params": {}},
                            {"action": "close_file", "params": {}}
                        ])
                    }
                }
            ]
        }
        
        # Планируем действия
        actions = action_planner.plan_actions("Открой файл example.txt и прочитай его содержимое")
        
        # Проверяем, что запрос был отправлен
        action_planner.api_connector.send_request.assert_called_once()
        
        # Проверяем результат
        assert len(actions) == 3
        assert actions[0] == {"action": "open_file", "params": {"path": "example.txt"}}
        assert actions[1] == {"action": "read_content", "params": {}}
        assert actions[2] == {"action": "close_file", "params": {}}    
    def test_plan_actions_api_error(self, action_planner):
        """Тест обработки ошибки API при планировании действий"""
        # Настраиваем мок API-коннектора для имитации ошибки
        action_planner.api_connector.send_request.return_value = None
        
        # Планируем действия
        actions = action_planner.plan_actions("Открой файл example.txt и прочитай его содержимое")
        
        # Проверяем, что запрос был отправлен
        action_planner.api_connector.send_request.assert_called_once()
        
        # Проверяем, что ошибка была обработана
        action_planner.error_handler.handle_error.assert_called_once()
        
        # Проверяем, что возвращается пустой список при ошибке
        assert actions == []
    
    def test_execute_plan(self, action_planner):
        """Тест выполнения плана действий"""
        # Создаем мок для исполнителя действий
        action_executor = MagicMock()
        action_planner.action_executor = action_executor
        
        # Настраиваем мок исполнителя для возврата результатов
        action_executor.execute_action.side_effect = [
            {"status": "success", "result": "Файл открыт"},
            {"status": "success", "result": "Содержимое: Hello, World!"},
            {"status": "success", "result": "Файл закрыт"}
        ]
        
        # План действий
        plan = [
            {"action": "open_file", "params": {"path": "example.txt"}},
            {"action": "read_content", "params": {}},
            {"action": "close_file", "params": {}}
        ]
        
        # Выполняем план
        results = action_planner.execute_plan(plan)
        
        # Проверяем, что все действия были выполнены
        assert action_executor.execute_action.call_count == 3
        
        # Проверяем результаты
        assert len(results) == 3
        assert results[0] == {"status": "success", "result": "Файл открыт"}
        assert results[1] == {"status": "success", "result": "Содержимое: Hello, World!"}
        assert results[2] == {"status": "success", "result": "Файл закрыт"}