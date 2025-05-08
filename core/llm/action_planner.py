import json
from typing import Dict, Any, List, Optional

class ActionPlanner:
    """
    Планировщик действий на основе запросов к нейросети.
    """
    
    def __init__(self, api_connector, error_handler=None, action_executor=None):
        """
        Инициализация планировщика действий.
        
        Args:
            api_connector (object): Коннектор API нейросети
            error_handler (object, optional): Обработчик ошибок
            action_executor (object, optional): Исполнитель действий
        """
        self.api_connector = api_connector
        self.error_handler = error_handler
        self.action_executor = action_executor
    
    def plan_actions(self, user_request: str) -> List[Dict[str, Any]]:
        """
        Планирование действий на основе запроса пользователя.
        
        Args:
            user_request (str): Запрос пользователя
        
        Returns:
            List[Dict[str, Any]]: Список действий для выполнения
        """
        try:
            # Формируем запрос к API
            payload = {
                "model": "gpt-4",
                "messages": [
                    {"role": "system", "content": "You are an AI assistant that helps plan actions to fulfill user requests. Return a JSON array of actions."},
                    {"role": "user", "content": user_request}
                ],
                "temperature": 0.7
            }
            
            # Отправляем запрос
            response = self.api_connector.send_request("/v1/chat/completions", payload)
            
            # Проверяем ответ
            if not response or "choices" not in response or not response["choices"]:
                if self.error_handler:
                    self.error_handler.handle_error(
                        Exception("Invalid API response"),
                        "Invalid API response for action planning"
                    )
                return []
            
            # Извлекаем план действий из ответа
            content = response["choices"][0]["message"]["content"]
            
            # Парсим JSON
            try:
                actions = json.loads(content)
                if not isinstance(actions, list):
                    actions = []
            except json.JSONDecodeError as e:
                if self.error_handler:
                    self.error_handler.handle_error(e, "Error parsing action plan")
                actions = []
            
            return actions
        
        except Exception as e:
            # Обрабатываем ошибку
            if self.error_handler:
                self.error_handler.handle_error(e, "Error planning actions")
            else:
                print(f"Error planning actions: {e}")
            
            return []
    
    def execute_plan(self, plan: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Выполнение плана действий.
        
        Args:
            plan (List[Dict[str, Any]]): План действий
        
        Returns:
            List[Dict[str, Any]]: Результаты выполнения действий
        """
        if not self.action_executor:
            if self.error_handler:
                self.error_handler.handle_error(
                    Exception("Action executor not set"),
                    "Cannot execute plan: action executor not set"
                )
            return []
        
        results = []
        
        # Выполняем каждое действие в плане
        for action in plan:
            action_type = action.get("action")
            params = action.get("params", {})
            
            # Выполняем действие
            result = self.action_executor.execute_action(action_type, params)
            results.append(result)
            
            # Если действие завершилось с ошибкой, прерываем выполнение плана
            if result.get("status") == "error":
                if self.error_handler:
                    self.error_handler.handle_warning(
                        f"Plan execution stopped due to error in action {action_type}",
                        "action_planner"
                    )
                break
        
        return results