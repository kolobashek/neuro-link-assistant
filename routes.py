from flask import render_template, request, jsonify, Blueprint
from app import app, command_interrupt_flag
from services.command_service import process_command, execute_command_with_steps, execute_command_with_error_handling
from utils.logging_utils import log_execution_summary
from commands import COMMANDS

# Создаем Blueprint для основных маршрутов
main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def index():
    # Группируем команды по функциям
    commands_grouped = {}
    for command_text, function_name in COMMANDS.items():
        if function_name not in commands_grouped:
            commands_grouped[function_name] = []
        commands_grouped[function_name].append(command_text)
    
    # Создаем список команд для отображения
    # Для каждой функции берем первую команду как основную и остальные как альтернативные
    display_commands = []
    for function_name, command_list in commands_grouped.items():
        main_command = command_list[0]
        alt_commands = command_list[1:] if len(command_list) > 1 else []
        display_commands.append({
            'main': main_command,
            'alternatives': alt_commands,
            'function': function_name
        })
    
    return render_template('index.html', commands=display_commands)

# Создаем Blueprint для API маршрутов
api_bp = Blueprint('api', __name__)

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
            result = execute_command_with_error_handling(user_input, code)
            
            return jsonify({
                'response': response,
                'code': code,
                'execution_result': result.get("execution_result"),
                'is_compound': False,
                'overall_status': result.get("success", False) and "completed" or "failed",
                'completion_percentage': 100.0 if result.get("success", False) else 0.0,
                'accuracy_percentage': 90.0 if result.get("success", False) else 0.0,
                'message': result.get("message", "")
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

@api_bp.route('/interrupt', methods=['POST'])
def interrupt_command():
    """Прерывает выполнение текущей команды"""
    global command_interrupt_flag
    
    # Устанавливаем флаг прерывания
    command_interrupt_flag = True
    
    return jsonify({
        'success': True,
        'message': 'Команда прервана'
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

@api_bp.route('/ai_models', methods=['GET'])
def get_ai_models():
    """Возвращает информацию о доступных нейросетях"""
    # Здесь будет логика получения информации о нейросетях
    # Пока возвращаем заглушку
    models = [
        {
            'id': 'huggingface',
            'name': 'HuggingFace (Llama-2-70b)',
            'status': 'Ready',
            'is_current': True,
            'error': None
        },
        {
            'id': 'deepseek',
            'name': 'DeepSeek Chat',
            'status': 'Ready',
            'is_current': False,
            'error': None
        },
        {
            'id': 'lmarena',
            'name': 'LM Arena',
            'status': 'Unavailable',
            'is_current': False,
            'error': 'Требуется авторизация'
        }
    ]
    
    return jsonify({
        'models': models
    })

@api_bp.route('/check_ai_models', methods=['POST'])
def check_ai_models():
    """Проверяет доступность всех нейросетей"""
    # Здесь будет логика проверки доступности нейросетей
    # Пока возвращаем заглушку
    return jsonify({
        'success': True,
        'message': 'Проверка нейросетей запущена'
    })

@api_bp.route('/check_ai_model/<model_id>', methods=['POST'])
def check_ai_model(model_id):
    """Проверяет доступность конкретной нейросети"""
    # Здесь будет логика проверки доступности конкретной нейросети
    # Пока возвращаем заглушку
    model_names = {
        'huggingface': 'HuggingFace (Llama-2-70b)',
        'deepseek': 'DeepSeek Chat',
        'lmarena': 'LM Arena'
    }
    
    return jsonify({
        'success': True,
        'model_id': model_id,
        'model_name': model_names.get(model_id, model_id)
    })

@api_bp.route('/select_ai_model/<model_id>', methods=['POST'])
def select_ai_model(model_id):
    """Выбирает нейросеть для использования"""
    # Здесь будет логика выбора нейросети
    # Пока возвращаем заглушку
    model_names = {
        'huggingface': 'HuggingFace (Llama-2-70b)',
        'deepseek': 'DeepSeek Chat',
        'lmarena': 'LM Arena'
    }
    
    return jsonify({
        'success': True,
        'model_id': model_id,
        'model_name': model_names.get(model_id, model_id)
    })