import re
import os
import time
from config import Config

def extract_code_from_response(response):
    """Извлекает код Python из ответа нейросети"""
    code_start = response.find("")
    if code_start != -1:
        code_start += 9  # длина "python"
        code_end = response.find("```", code_start)
        if code_end != -1:
            return response[code_start:code_end].strip()
    return None

def extract_math_expression(text):
    """Извлекает математическое выражение из текста"""
    import re
    
    # Ищем числа и математические операторы
    pattern = r'(\d+\s*[\+\-\*\/]\s*\d+)'
    matches = re.findall(pattern, text)
    
    if matches:
        return matches[0].replace(' ', '')
    
    return None

def add_interrupt_checks(code):
    """
    Добавляет проверки прерывания в код
    """
    # Разбиваем код на строки
    lines = code.split('\n')
    modified_lines = []
    
    # Добавляем импорт time в начало, если его нет
    if not any('import time' in line for line in lines):
        modified_lines.append('import time')
    
    # Добавляем проверку прерывания перед каждым циклом и после каждой операции ожидания
    for line in lines:
        modified_lines.append(line)
        
        # Добавляем проверку после time.sleep
        if 'time.sleep' in line:
            indent = len(line) - len(line.lstrip())
            check_line = ' ' * indent + 'if check_interrupt(): return "Выполнение прервано пользователем"'
            modified_lines.append(check_line)
        
        # Добавляем проверку в начало циклов
        if any(keyword in line for keyword in ['for ', 'while ']):
            if not line.strip().startswith('#'):  # Игнорируем комментарии
                indent = len(line) - len(line.lstrip())
                next_indent = indent + 4  # Стандартный отступ Python
                check_line = ' ' * next_indent + 'if check_interrupt(): return "Выполнение прервано пользователем"'
                modified_lines.append(check_line)
    
    # Собираем модифицированный код
    return '\n'.join(modified_lines)

def check_interrupt_during_operation(operation_name, interval=0.5, max_time=30):
    """
    Выполняет проверку прерывания во время длительных операций
    
    Args:
        operation_name: Название операции для логирования
        interval: Интервал проверки в секундах
        max_time: Максимальное время выполнения в секундах
        
    Returns:
        True, если операция должна быть прервана, False в противном случае
    """
    from app import command_interrupt_flag
    from utils.logging_utils import detailed_logger
    
    start_time = time.time()
    elapsed_time = 0
    
    while elapsed_time < max_time:
        # Проверяем флаг прерывания
        if command_interrupt_flag:
            detailed_logger.info(f"Операция '{operation_name}' прервана пользователем после {elapsed_time:.1f} секунд")
            return True
        
        # Ждем указанный интервал
        time.sleep(interval)
        
        # Обновляем прошедшее время
        elapsed_time = time.time() - start_time
    
    # Если превышено максимальное время
    detailed_logger.warning(f"Операция '{operation_name}' превысила максимальное время выполнения ({max_time} секунд)")
    return False