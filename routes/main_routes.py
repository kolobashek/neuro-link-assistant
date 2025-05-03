from flask import Blueprint, render_template
from commands import COMMANDS

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