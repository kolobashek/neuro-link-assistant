import datetime
import logging
from flask import Blueprint, request, jsonify, current_app
from globals import command_interrupt_flag  # Импортируем из globals
from services.command_service import (
    process_command, execute_python_code, execute_command_with_error_handling,
    execute_command_with_steps, try_fix_error
)
from utils.helpers import extract_code_from_response
from utils.logging_utils import log_execution_summary
from models.command_models import CommandStep, CommandExecution

api_bp = Blueprint('api', __name__)
logger = logging.getLogger('neuro_assistant')
detailed_logger = logging.getLogger('detailed_log')

@api_bp.route('/query', methods=['POST'])
def query():
    user_input = request.json.get('input', '').lower()
    
    # Проверяем, является ли команда составной
    if any(sep in user_input for sep in [" и ", " затем ", " после этого ", " потом ", ", "]):
        # Обрабатываем составную команду
        execution_result = execute_command_with_steps(user_input)
        
        # Формируем ответ для пользователя
        steps_info = []
        for step in execution_result.steps:
            step_info = {
                'number': step.step_number,
                'description': step.description,
                'status': step.status,
                'result': step.result if step.status == 'completed' else step.error
            }
            steps_info.append(step_info)
        
        return jsonify({
            'response': f"Выполнение команды: {user_input}",
            'is_compound': True,
            'steps': steps_info,
            'overall_status': execution_result.overall_status,
            'completion_percentage': execution_result.completion_percentage,
            'accuracy_percentage': execution_result.accuracy_percentage,
            'message': f"Команда выполнена с точностью {execution_result.accuracy_percentage:.1f}% и завершенностью {execution_result.completion_percentage:.1f}%"
        })
    else:
        # Обрабатываем простую команду
        response, code = process_command(user_input)
        
        # Если есть код для выполнения, выполняем его
        if code:
            execution_result = execute_python_code(code)
            
            # Создаем запись о выполнении команды для логирования
            step = CommandStep(
                step_number=1,
                description=user_input,
                status='completed' if "Ошибка" not in execution_result else 'failed',
                result=execution_result if "Ошибка" not in execution_result else None,
                error=execution_result if "Ошибка" in execution_result else None,
                completion_percentage=100.0 if "Ошибка" not in execution_result else 0.0
            )
            
            execution = CommandExecution(
                command_text=user_input,
                steps=[step],
                start_time=datetime.datetime.now().isoformat(),
                end_time=datetime.datetime.now().isoformat(),
                overall_status='completed' if "Ошибка" not in execution_result else 'failed',
                completion_percentage=100.0 if "Ошибка" not in execution_result else 0.0,
                accuracy_percentage=90.0 if "Ошибка" not in execution_result else 0.0
            )
            
            # Логируем выполнение команды
            log_execution_summary(execution, final=True)
            
            return jsonify({
                'response': response,
                'code': code,
                'execution_result': execution_result,
                'is_compound': False,
                'overall_status': execution.overall_status,
                'completion_percentage': execution.completion_percentage,
                'accuracy_percentage': execution.accuracy_percentage
            })
        else:
            # Если код не был сгенерирован
            return jsonify({
                'response': response,
                'code': None,
                'execution_result': "Не удалось сгенерировать код для выполнения команды",
                'is_compound': False,
                'overall_status': 'failed',
                'completion_percentage': 0.0,
                'accuracy_percentage': 0.0,
                'message': "Пожалуйста, уточните команду или используйте предустановленные команды"
            })

@api_bp.route('/clarify', methods=['POST'])
def clarify():
    """
    Обрабатывает запросы на уточнение информации от пользователя
    """
    user_input = request.json.get('input', '')
    original_command = request.json.get('original_command', '')
    error_context = request.json.get('error_context', {})
    
    logger.info(f"Получено уточнение от пользователя: {user_input}")
    
    # Формируем новый запрос с учетом уточнения
    new_command = f"{original_command} ({user_input})"
    
    # Получаем новый код с учетом уточнения
    response, code = process_command(new_command)
    
    # Если есть код, выполняем его
    if code:
        result = execute_command_with_error_handling(new_command, code)
        
        return jsonify({
            'response': response,
            'code': code,
            'execution_result': result.get("execution_result"),
            'verification_result': result.get("verification_result"),
            'error_analysis': result.get("error_analysis", {}),
            'screenshot': result.get("screenshot"),
            'message': result.get("message")
        })
    else:
        return jsonify({
            'response': "Не удалось сгенерировать код даже с учетом уточнения",
            'code': None,
            'execution_result': "Не удалось сгенерировать код для выполнения команды",
            'message': "Пожалуйста, используйте предустановленные команды или сформулируйте запрос иначе"
        })

@api_bp.route('/confirm', methods=['POST'])
def confirm_action():
    """
    Обрабатывает подтверждение действия от пользователя
    """
    user_confirmation = request.json.get('confirmation', False)
    command = request.json.get('command', '')
    code = request.json.get('code', '')
    
    if not user_confirmation:
        return jsonify({
            'response': "Действие отменено пользователем",
            'code': code,
            'execution_result': None,
            'message': "Команда не была выполнена по решению пользователя"
        })
    
    # Если пользователь подтвердил, выполняем команду
    result = execute_command_with_error_handling(command, code)
    
    return jsonify({
        'response': f"Команда подтверждена и выполнена: {command}",
        'code': code,
        'execution_result': result.get("execution_result"),
        'verification_result': result.get("verification_result"),
        'error_analysis': result.get("error_analysis", {}),
        'screenshot': result.get("screenshot"),
        'message': result.get("message")
    })

@api_bp.route('/interrupt', methods=['POST'])
def interrupt_command():
    """
    Прерывает выполнение текущей команды
    """
    global command_interrupt_flag
    
    # Устанавливаем флаг прерывания
    command_interrupt_flag = True
    
    logger.info("Получен запрос на прерывание команды")
    detailed_logger.info("Получен запрос на прерывание команды")
    
    return jsonify({
        'success': True,
        'message': "Запрос на прерывание команды получен. Выполнение будет остановлено при первой возможности."
    })

@api_bp.route('/history', methods=['GET'])
def get_history():
    """Возвращает историю выполненных команд"""
    try:
        # Читаем краткий журнал команд
        with open('command_summary.txt', 'r', encoding='utf-8') as f:
            summary_content = f.read()
        
        # Разбиваем на отдельные записи
        entries = []
        current_entry = {}
        lines = summary_content.split('\n')
        
        for line in lines:
            if line.startswith('20'):  # Начало новой записи (с даты)
                if current_entry:
                    entries.append(current_entry)
                    current_entry = {}
                # Извлекаем дату и время
                parts = line.split(' - ', 1)
                if len(parts) > 1:
                    current_entry['timestamp'] = parts[0]
            elif line.startswith('Команда:'):
                current_entry['command'] = line.replace('Команда:', '').strip()
            elif line.startswith('Статус:'):
                current_entry['status'] = line.replace('Статус:', '').strip()
            elif line.startswith('Выполнение:'):
                current_entry['completion'] = line.replace('Выполнение:', '').strip()
            elif line.startswith('Точность:'):
                current_entry['accuracy'] = line.replace('Точность:', '').strip()
        
        # Добавляем последнюю запись
        if current_entry:
            entries.append(current_entry)
        
        return jsonify({
            'history': entries,
            'count': len(entries)
        })
    except Exception as e:
        return jsonify({
            'error': f"Ошибка при чтении истории: {str(e)}",
            'history': []
        })

@api_bp.route('/detailed_history/<command_timestamp>', methods=['GET'])
def get_detailed_history(command_timestamp):
    """Возвращает подробную информацию о выполнении команды"""
    try:
        # Читаем подробный журнал команд
        with open('detailed_command_log.txt', 'r', encoding='utf-8') as f:
            log_content = f.read()
        
        # Ищем записи, соответствующие указанной временной метке
        entries = []
        command_found = False
        command_details = []
        
        lines = log_content.split('\n')
        for line in lines:
            if command_timestamp in line:
                command_found = True
                command_details.append(line)
            elif command_found and line.strip():
                command_details.append(line)
        
        return jsonify({
            'command_timestamp': command_timestamp,
            'details': command_details
        })
    except Exception as e:
        return jsonify({
            'error': f"Ошибка при чтении подробной истории: {str(e)}",
            'details': []
        })