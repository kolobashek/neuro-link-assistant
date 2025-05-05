from dataclasses import dataclass, asdict
from typing import List, Dict, Any, Optional
import datetime

@dataclass
class CommandStep:
    """Класс для представления шага выполнения команды"""
    step_number: int
    description: str
    status: str  # 'pending', 'in_progress', 'completed', 'failed', 'interrupted'
    result: Optional[str] = None
    error: Optional[str] = None
    completion_percentage: float = 0.0
    accuracy_percentage: float = 90.0  # По умолчанию считаем, что команда выполнена с высокой точностью

@dataclass
class CommandExecution:
    """Класс для представления выполнения команды"""
    command_text: str
    steps: List[CommandStep]
    start_time: str
    end_time: Optional[str] = None
    overall_status: str = 'in_progress'  # 'in_progress', 'completed', 'failed', 'interrupted'
    completion_percentage: float = 0.0
    accuracy_percentage: float = 0.0
    current_step: int = 0  # Индекс текущего выполняемого шага
    
    def to_dict(self):
        """Преобразует объект в словарь для JSON-сериализации"""
        result = asdict(self)
        return result
    
    @classmethod
    def from_dict(cls, data):
        """Создает объект из словаря"""
        steps = [CommandStep(**step_data) for step_data in data.get('steps', [])]
        return cls(
            command_text=data.get('command_text', ''),
            steps=steps,
            start_time=data.get('start_time', datetime.datetime.now().isoformat()),
            end_time=data.get('end_time'),
            overall_status=data.get('overall_status', 'in_progress'),
            completion_percentage=data.get('completion_percentage', 0.0),
            accuracy_percentage=data.get('accuracy_percentage', 0.0),
            current_step=data.get('current_step', 0)
        )