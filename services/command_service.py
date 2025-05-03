import re
import os
import time
import logging
import traceback
import datetime
import win32gui
from globals import command_interrupt_flag  # Импортируем из globals
from config import Config
from utils.helpers import extract_code_from_response, add_interrupt_checks, extract_math_expression
from utils.logging_utils import log_execution_summary
from models.command_models import CommandStep, CommandExecution
from services.ai_service import get_ai_response

logger = logging.getLogger('neuro_assistant')
detailed_logger = logging.getLogger('detailed_log')

# Словарь с командами и соответствующими функциями
from commands import COMMANDS

def is_command_feasible(command_text):
    """
    Определяет, целесообразно ли выполнение команды
    """
    # Список потенциально опасных или нецелесообразных команд
    dangerous_keywords = [
        "удали", "delete", "format", "форматир", 
        "rm -rf", "shutdown", "выключ", 
        "reboot", "перезагруз"
    ]
    
    # Проверяем наличие опасных ключевых слов
    for keyword in dangerous_keywords:
        if keyword in command_text.lower():
            # Для некоторых команд требуется дополнительное подтверждение
            if keyword in ["shutdown", "выключ", "reboot", "перезагруз"]:
                return {
                    "feasible": True,
                    "requires_confirmation": True,
                    "reason": f"Команда '{keyword}' требует подтверждения пользователя"
                }
            
            # Для действительно опасных команд возвращаем запрет
            if keyword in ["удали", "delete", "format", "форматир", "rm -rf"]:
                return {
                    "feasible": False,
                    "reason": f"Команда '{keyword}' потенциально опасна и не может быть выполнена автоматически"
                }
    
    # Проверяем на сложность и длительность выполнения
    complex_keywords = [
        "установи", "install", "скачай", "download",
        "обнови", "update", "компилируй", "compile"
    ]
    
    for keyword in complex_keywords:
        if keyword in command_text.lower():
            return {
                "feasible": True,
                "requires_confirmation": True,
                "reason": f"Команда '{keyword}' может занять продолжительное время. Требуется подтверждение."
            }
    
    # По умолчанию считаем команду выполнимой
    return {
        "feasible": True,
        "requires_confirmation": False
    }

def process_command(text):
    """Анализ команды и генерация соответствующего кода"""
    text = text.lower()
    
    # Проверяем целесообразность выполнения команды
    feasibility = is_command_feasible(text)
    if not feasibility.get("feasible", True):
        return f"Команда не может быть выполнена: {feasibility.get('reason', 'Неизвестная причина')}", None
    
    # Если команда требует подтверждения, сообщаем об этом
    if feasibility.get("requires_confirmation", False):
        # Здесь можно добавить логику для запроса подтверждения
        # Но пока просто продолжаем выполнение
        logger.info(f"Команда требует подтверждения: {feasibility.get('reason', '')}")
    
    # Простое сопоставление с известными командами
    for command_text, function_name in COMMANDS.items():
        if command_text in text:
            code = f"{function_name}()"
            
            # Особая обработка для команды "сказать"
            if function_name == "speak_text":
                # Извлекаем текст после слова "сказать"
                speak_content = ""
                if "сказать" in text:
                    speak_content = text.split("сказать", 1)[1].strip()
                elif "скажи" in text:
                    speak_content = text.split("скажи", 1)[1].strip()
                
                if speak_content:
                    code = f"speak_text('{speak_content}')"
            
            return f"Выполняю команду: {command_text}", code
    
    # Если команда не распознана, отправляем запрос к нейросети
    # для генерации кода на основе текста
    response = get_ai_response(text)
    code = extract_code_from_response(response)
    
    return response, code

def execute_python_code(code):
    """Выполнить Python код и вернуть результат"""
    global command_interrupt_flag
    
    try:
        # Импортируем все доступные команды
        from commands.system_commands import (
            minimize_all_windows, open_browser, take_screenshot, 
            volume_up, volume_down, open_notepad, speak_text,
            shutdown_computer, restart_computer
        )
        from commands.media_commands import media_pause, media_next
        from commands.app_commands import open_calculator
        
        # Создаем локальный словарь с разрешенными функциями
        import pyautogui
        import os
        import time
        import win32gui
        import win32con
        import win32api
        import pyttsx3
        import re
        import pyperclip
        
        local_dict = {
            "pyautogui": pyautogui,
            "os": os,
            "time": time,
            "win32gui": win32gui,
            "win32con": win32con,
            "win32api": win32api,
            "pyttsx3": pyttsx3,
            "re": re,
            "pyperclip": pyperclip,
            "minimize_all_windows": minimize_all_windows,
            "open_browser": open_browser,
            "take_screenshot": take_screenshot,
            "volume_up": volume_up,
            "volume_down": volume_down,
            "open_notepad": open_notepad,
            "speak_text": speak_text,
            "open_calculator": open_calculator,
            "shutdown_computer": shutdown_computer,
            "restart_computer": restart_computer,
            "media_pause": media_pause,
            "media_next": media_next,
            "extract_math_expression": extract_math_expression,
            # Добавляем логгеры для отчетов о выполнении
            "detailed_logger": detailed_logger,
            # Добавляем функцию для проверки прерывания
            "check_interrupt": lambda: command_interrupt_flag
        }
        
        # Модифицируем код, добавляя проверки прерывания
        modified_code = add_interrupt_checks(code)
        
        # Выполняем код в изолированном пространстве
        result = {}
        exec(modified_code, {"__builtins__": {}}, local_dict)
        
        # Проверяем, был ли возвращен результат из кода
        if 'result' in local_dict:
            return local_dict['result']
        
        # Проверяем, было ли прерывание
        if command_interrupt_flag:
            return "Выполнение прервано пользователем"
        
        return "Код успешно выполнен"
    except Exception as e:
        traceback_str = traceback.format_exc()
        detailed_logger.error(f"Ошибка при выполнении кода: {str(e)}\n{traceback_str}")
        return f"Ошибка при выполнении кода: {str(e)}\n{traceback_str}"

def execute_command_with_error_handling(command_text, code):
    """
    Выполняет команду с обработкой ошибок, анализом и автоматическим восстановлением
    """
    logger.info(f"Начало выполнения команды: {command_text}")
    
    # Выполнение кода
    execution_result = execute_python_code(code)
    
    # Если есть функция проверки, используем её
    if 'verify_command_execution' in globals():
        verification_result = verify_command_execution(code, command_text)
        
        # Если команда выполнена успешно
        if verification_result.get("verified", False):
            logger.info(f"Команда '{command_text}' успешно выполнена")
            return {
                "success": True,
                "execution_result": execution_result,
                "verification_result": verification_result,
                "message": "Команда успешно выполнена"
            }
        else:
            # Если команда не выполнена успешно, возвращаем информацию об ошибке
            logger.warning(f"Команда '{command_text}' не выполнена успешно")
            return {
                "success": False,
                "execution_result": execution_result,
                "verification_result": verification_result,
                "message": verification_result.get("message", "Команда не выполнена успешно")
            }
    else:
        # Если функция проверки не определена, просто возвращаем результат выполнения
        return {
            "success": True,
            "execution_result": execution_result,
            "message": "Команда выполнена, но проверка не производилась"
        }

def parse_compound_command(text):
    """
    Разбирает составную команду на отдельные шаги
    Возвращает список шагов и общее описание команды
    """
    text = text.lower()
    steps = []
    
    # Ищем разделители составных команд
    separators = [" и ", " затем ", " после этого ", " потом ", ", "]
    
    # Пытаемся разбить команду по разделителям
    command_parts = [text]
    for separator in separators:
        new_parts = []
        for part in command_parts:
            if separator in part:
                new_parts.extend(part.split(separator))
            else:
                new_parts.append(part)
        command_parts = new_parts
    
    # Удаляем дубликаты и пустые строки
    command_parts = [part.strip() for part in command_parts if part.strip()]
    command_parts = list(dict.fromkeys(command_parts))
    
    # Создаем шаги для каждой части команды
    for i, part in enumerate(command_parts):
        steps.append(CommandStep(
            step_number=i+1,
            description=part,
            status='pending',
            completion_percentage=0.0
        ))
    
    return steps, text

def execute_command_with_steps(command_text, code=None):
    """
    Выполняет команду по шагам, проверяя результат каждого шага
    и информируя пользователя о ходе выполнения
    """
    global command_interrupt_flag
    
    # Сбрасываем флаг прерывания
    command_interrupt_flag = False
    
    # Разбираем команду на шаги
    steps, full_command = parse_compound_command(command_text)
    
    # Создаем запись о выполнении команды
    execution = CommandExecution(
        command_text=full_command,
        steps=steps,
        start_time=datetime.datetime.now().isoformat()
    )
    
    # Логируем начало выполнения команды
    detailed_logger.info(f"Начало выполнения команды: {full_command}")
    detailed_logger.info(f"Количество шагов: {len(steps)}")
    
    # Выполняем каждый шаг
    for i, step in enumerate(execution.steps):
        # Проверяем, не было ли прерывания
        if command_interrupt_flag:
            step.status = 'interrupted'
            step.error = "Выполнение прервано пользователем"
            detailed_logger.info(f"Шаг {step.step_number} прерван пользователем")
            break
        
        step.status = 'in_progress'
        execution.current_step = i
        
        detailed_logger.info(f"Шаг {step.step_number}: {step.description} - начало выполнения")
        
        # Генерируем код для выполнения шага
        step_response, step_code = process_single_step(step.description)
        
        if step_code:
            # Обновляем информацию о шаге
            detailed_logger.info(f"Сгенерирован код для шага {step.step_number}: {step_code}")
            
            # Выполняем код
            try:
                # Выполняем код с проверкой результата
                execution_result = execute_python_code(step_code)
                
                # Проверяем, не было ли прерывания
                if command_interrupt_flag:
                    step.status = 'interrupted'
                    step.error = "Выполнение прервано пользователем"
                    detailed_logger.info(f"Шаг {step.step_number} прерван пользователем")
                    break
                
                # Проверяем результат выполнения
                if "Ошибка" in execution_result:
                    step.status = 'failed'
                    step.error = execution_result
                    step.completion_percentage = 50.0  # Частичное выполнение
                    detailed_logger.error(f"Шаг {step.step_number} завершился с ошибкой: {execution_result}")
                else:
                    step.status = 'completed'
                    step.result = execution_result
                    step.completion_percentage = 100.0
                    detailed_logger.info(f"Шаг {step.step_number} успешно выполнен: {execution_result}")
                
                # Проверяем результат выполнения шага
                verification_result = verify_step_execution(step.description, execution_result)
                
                # Обновляем точность выполнения на основе проверки
                if verification_result:
                    step.accuracy_percentage = verification_result.get('accuracy', 100.0)
                    detailed_logger.info(f"Точность выполнения шага {step.step_number}: {step.accuracy_percentage}%")
            except Exception as e:
                step.status = 'failed'
                step.error = str(e)
                step.completion_percentage = 0.0
                detailed_logger.error(f"Исключение при выполнении шага {step.step_number}: {str(e)}")
        else:
            step.status = 'failed'
            step.error = "Не удалось сгенерировать код для выполнения шага"
            step.completion_percentage = 0.0
            detailed_logger.error(f"Не удалось сгенерировать код для шага {step.step_number}")
        
        # Обновляем общий прогресс выполнения команды
        update_execution_progress(execution)
        
        # Логируем промежуточный результат
        log_execution_summary(execution)
        
        # Если шаг не выполнен успешно, пытаемся исправить ошибку
        if step.status == 'failed' and not command_interrupt_flag:
            detailed_logger.info(f"Попытка исправить ошибку в шаге {step.step_number}")
            
            # Анализируем ошибку и пытаемся её исправить
            fixed_code = try_fix_error(step.description, step.error)
            
            if fixed_code:
                detailed_logger.info(f"Найдено исправление для шага {step.step_number}: {fixed_code}")
                
                # Выполняем исправленный код
                try:
                    execution_result = execute_python_code(fixed_code)
                    
                    # Проверяем, не было ли прерывания
                    if command_interrupt_flag:
                        step.status = 'interrupted'
                        step.error = "Выполнение прервано пользователем"
                        detailed_logger.info(f"Шаг {step.step_number} прерван пользователем при исправлении")
                        break
                    
                    if "Ошибка" in execution_result:
                        detailed_logger.error(f"Исправление не помогло: {execution_result}")
                    else:
                        step.status = 'completed'
                        step.result = execution_result
                        step.completion_percentage = 100.0
                        step.error = None
                        detailed_logger.info(f"Шаг {step.step_number} успешно исправлен и выполнен")
                        
                        # Обновляем общий прогресс
                        update_execution_progress(execution)
                except Exception as e:
                    detailed_logger.error(f"Исключение при выполнении исправленного кода: {str(e)}")
    
    # Завершаем выполнение команды
    execution.end_time = datetime.datetime.now().isoformat()
    
    # Определяем общий статус выполнения
    if command_interrupt_flag:
        execution.overall_status = 'interrupted'
    elif all(step.status == 'completed' for step in execution.steps):
        execution.overall_status = 'completed'
    else:
        execution.overall_status = 'failed'
    
    # Логируем итоговый результат
    detailed_logger.info(f"Завершение выполнения команды: {full_command}")
    detailed_logger.info(f"Общий статус: {execution.overall_status}")
    detailed_logger.info(f"Процент выполнения: {execution.completion_percentage}%")
    detailed_logger.info(f"Точность выполнения: {execution.accuracy_percentage}%")
    
    # Записываем итоговый результат в краткий журнал
    log_execution_summary(execution, final=True)
    
    return execution

def process_single_step(step_text):
    """
    Обрабатывает отдельный шаг команды
    Возвращает ответ и код для выполнения
    """
    # Проверяем, соответствует ли шаг стандартной команде
    for command_text, function_name in COMMANDS.items():
        if command_text in step_text:
            code = f"{function_name}()"
            
            # Особая обработка для команды "сказать"
            if function_name == "speak_text":
                # Извлекаем текст после слова "сказать" или "скажи"
                speak_content = ""
                if "сказать" in step_text:
                    speak_content = step_text.split("сказать", 1)[1].strip()
                elif "скажи" in step_text:
                    speak_content = step_text.split("скажи", 1)[1].strip()
                
                if speak_content:
                    code = f"speak_text('{speak_content}')"
            
            return f"Выполняю команду: {command_text}", code
    
    # Если шаг не соответствует стандартной команде, генерируем код с помощью нейросети
    response = get_ai_response(step_text)
    code = extract_code_from_response(response)
    
    return response, code

def verify_step_execution(step_description, execution_result):
    """
    Проверяет результат выполнения шага
    Возвращает словарь с информацией о проверке
    """
    global command_interrupt_flag
    
    # Проверяем, было ли прерывание
    if command_interrupt_flag or "прервано пользователем" in execution_result:
        return {
            'verified': False,
            'accuracy': 0.0,
            'message': "Выполнение прервано пользователем"
        }
    
    # Базовая проверка на наличие ошибок
    if "Ошибка" in execution_result:
        return {
            'verified': False,
            'accuracy': 0.0,
            'message': f"Шаг не выполнен из-за ошибки: {execution_result}"
        }
    
    # Проверка для конкретных типов команд
    if "калькулятор" in step_description.lower():
        # Проверяем, был ли открыт калькулятор
        calc_window = win32gui.FindWindow(None, "Калькулятор")
        if calc_window == 0:
            calc_window = win32gui.FindWindow(None, "Calculator")
        
        if calc_window != 0:
            return {
                'verified': True,
                'accuracy': 100.0,
                'message': "Калькулятор успешно открыт"
            }
        else:
            return {
                'verified': False,
                'accuracy': 0.0,
                'message': "Калькулятор не был открыт"
            }
    
    if "браузер" in step_description.lower():
        # Проверяем, был ли открыт браузер
        browser_windows = ["Google Chrome", "Mozilla Firefox", "Microsoft Edge", "Opera", "Safari"]
        for browser in browser_windows:
            if win32gui.FindWindow(None, browser) != 0:
                return {
                    'verified': True,
                    'accuracy': 100.0,
                    'message': f"Браузер {browser} успешно открыт"
                }
        
        return {
            'verified': False,
            'accuracy': 50.0,  # Возможно, браузер открыт, но не распознан
            'message': "Не удалось подтвердить открытие браузера"
        }
    
    # Для других команд просто возвращаем успешный результат
    return {
        'verified': True,
        'accuracy': 90.0,  # По умолчанию считаем, что команда выполнена с высокой точностью
        'message': "Шаг выполнен успешно"
    }

def update_execution_progress(execution):
    """
    Обновляет общий прогресс выполнения команды
    """
    # Вычисляем средний процент выполнения всех шагов
    if execution.steps:
        completion_sum = sum(step.completion_percentage for step in execution.steps)
        execution.completion_percentage = completion_sum / len(execution.steps)
        
        # Вычисляем среднюю точность выполнения для завершенных шагов
        completed_steps = [step for step in execution.steps if step.status == 'completed']
        if completed_steps:
            accuracy_sum = sum(getattr(step, 'accuracy_percentage', 90.0) for step in completed_steps)
            execution.accuracy_percentage = accuracy_sum / len(completed_steps)
        else:
            execution.accuracy_percentage = 0.0

def try_fix_error(step_description, error_message):
    """
    Анализирует ошибку и пытается сгенерировать исправленный код
    """
    detailed_logger.info(f"Анализ ошибки: {error_message}")
    
    # Проверяем типичные ошибки и предлагаем исправления
    if "NameError: name" in error_message and "is not defined" in error_message:
        # Извлекаем имя неопределенной функции или переменной
        match = re.search(r"name '(.+)' is not defined", error_message)
        if match:
            undefined_name = match.group(1)
            detailed_logger.info(f"Обнаружено неопределенное имя: {undefined_name}")
            
            # Проверяем, является ли это именем функции, которую нужно определить
            if undefined_name.endswith("_calculator"):
                detailed_logger.info("Генерация кода для работы с калькулятором")
                return generate_calculator_code(step_description)
            
            # Другие специальные случаи можно добавить здесь
    
    # Если не удалось определить конкретную ошибку, используем нейросеть для исправления
    prompt = f"""
    Исправь ошибку в Python коде для выполнения следующей команды: "{step_description}".
    Ошибка: {error_message}
    
    Используй доступные библиотеки: pyautogui, os, win32gui, win32con, pyttsx3.
    Оформи исправленный код в формате Python между тройными обратными кавычками.
    """
    
    response = get_ai_response(prompt)
    fixed_code = extract_code_from_response(response)
    
    return fixed_code

def generate_calculator_code(step_description):
    """
    Генерирует код для работы с калькулятором на основе описания шага
    """
    # Извлекаем математическое выражение из описания
    expression = extract_math_expression(step_description)
    
    if not expression:
        return None
    
    # Генерируем код для работы с калькулятором
    code = f"""
def calculate_with_calculator(expression):
    # Открываем калькулятор
    os.system("calc")
    time.sleep(1)  # Ждем открытия калькулятора
    
    # Находим окно калькулятора и активируем его
    calc_window = win32gui.FindWindow(None, "Калькулятор")
    if calc_window == 0:  # Если не нашли по русскому названию
        calc_window = win32gui.FindWindow(None, "Calculator")
    
    if calc_window != 0:
        # Активируем окно калькулятора
        win32gui.SetForegroundWindow(calc_window)
        time.sleep(0.5)  # Даем время на активацию окна
        
        # Очищаем калькулятор
        pyautogui.press('escape')
        
        # Вводим выражение
        for char in expression:
            if char == '+':
                pyautogui.press('+')
            elif char == '-':
                pyautogui.press('-')
            elif char == '*':
                pyautogui.press('*')
            elif char == '/':
                pyautogui.press('/')
            else:
                pyautogui.press(char)
        
        # Нажимаем Enter для вычисления
        pyautogui.press('enter')
        
        # Даем время на вычисление
        time.sleep(0.5)
        
        return f"Вычислено выражение {expression} в калькуляторе"
    else:
        return "Не удалось найти окно калькулятора"

# Выполняем вычисление
calculate_with_calculator("{expression}")
"""
    return code

def verify_command_execution(code, command_text):
    """
    Проверяет результат выполнения команды
    
    Args:
        code: Выполненный код
        command_text: Текст команды
        
    Returns:
        Словарь с информацией о проверке
    """
    # Проверка для конкретных типов команд
    if "калькулятор" in command_text.lower():
        # Проверяем, был ли открыт калькулятор
        calc_window = win32gui.FindWindow(None, "Калькулятор")
        if calc_window == 0:
            calc_window = win32gui.FindWindow(None, "Calculator")
        
        if calc_window != 0:
            return {
                'verified': True,
                'accuracy': 100.0,
                'message': "Калькулятор успешно открыт"
            }
        else:
            return {
                'verified': False,
                'accuracy': 0.0,
                'message': "Калькулятор не был открыт"
            }
    
    if "браузер" in command_text.lower():
        # Проверяем, был ли открыт браузер
        browser_windows = ["Google Chrome", "Mozilla Firefox", "Microsoft Edge", "Opera", "Safari"]
        for browser in browser_windows:
            if win32gui.FindWindow(None, browser) != 0:
                return {
                    'verified': True,
                    'accuracy': 100.0,
                    'message': f"Браузер {browser} успешно открыт"
                }
        
        return {
            'verified': False,
            'accuracy': 50.0,  # Возможно, браузер открыт, но не распознан
            'message': "Не удалось подтвердить открытие браузера"
        }
    
    # Для других команд просто возвращаем успешный результат
    return {
        'verified': True,
        'accuracy': 90.0,  # По умолчанию считаем, что команда выполнена с высокой точностью
        'message': "Команда выполнена успешно"
    }