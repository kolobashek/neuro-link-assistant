class ActionPlanner:
    """
    Планировщик действий на основе запросов пользователя.
    Использует языковую модель для создания плана действий.
    """
    
    def __init__(self, llm_client, prompt_processor, response_parser):
        """
        Инициализация планировщика действий.
        
        Args:
            llm_client (LLMApiClient): Клиент API языковой модели
            prompt_processor (PromptProcessor): Процессор промптов
            response_parser (ResponseParser): Парсер ответов
        """
        self.llm_client = llm_client
        self.prompt_processor = prompt_processor
        self.response_parser = response_parser
        
        # Добавляем базовый шаблон для планирования действий
        self.prompt_processor.add_template(
            "action_planning",
            """
            You are an AI assistant that helps users by creating action plans.
            The user has the following request:
            
            {user_request}
            
            Create a detailed plan of actions to fulfill this request.
            Return your plan as a JSON object with the following structure:
            {
                "actions": [
                    {"type": "action_type", "parameter1": "value1", ...},
                    ...
                ]
            }
            """
        )
    
    def plan_actions(self, user_request):
        """
        Создает план действий на основе запроса пользователя.
        
        Args:
            user_request (str): Запрос пользователя
            
        Returns:
            dict: План действий в формате JSON
        """
        try:
            # Создаем промпт для планирования действий
            prompt = self.prompt_processor.process_prompt(
                "action_planning", 
                {"user_request": user_request}
            )
            
            # Отправляем запрос к языковой модели
            response = self.llm_client.send_request(prompt)
            
            # Парсим ответ
            parsed_response = self.response_parser.parse_response(response)
            
            # Извлекаем план действий в формате JSON
            action_plan = self.response_parser.extract_json(parsed_response)
            
            # Если план действий не удалось извлечь, возвращаем пустой план
            if not action_plan or "actions" not in action_plan:
                return {"actions": []}
                
            return action_plan
            
        except Exception as e:
            # В случае ошибки возвращаем пустой план действий
            return {"actions": [], "error": str(e)}