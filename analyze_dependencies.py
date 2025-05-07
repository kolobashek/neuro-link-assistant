import os
import re
import sys
from collections import defaultdict

def find_python_files(directory):
    """Найти все Python файлы в указанной директории рекурсивно"""
    python_files = []
    for root, dirs, files in os.walk(directory):
        # Исключаем venv и __pycache__
        if '/venv/' in root or '\\venv\\' in root or '__pycache__' in root:
            continue
        for file in files:
            if file.endswith('.py'):
                python_files.append(os.path.join(root, file))
    return python_files

def parse_imports(file_path):
    """Извлечь все импорты из Python файла"""
    imports = []
    with open(file_path, 'r', encoding='utf-8') as file:
        try:
            content = file.read()
            # Регулярные выражения для поиска импортов
            import_patterns = [
                r'^\s*import\s+([\w\.]+)(?:\s+as\s+\w+)?',
                r'^\s*from\s+([\w\.]+)\s+import\s+.+'
            ]
            
            for pattern in import_patterns:
                for match in re.finditer(pattern, content, re.MULTILINE):
                    imports.append(match.group(1))
        except Exception as e:
            print(f"Ошибка при чтении файла {file_path}: {e}")
    return imports

def analyze_dependencies(project_root):
    """Анализ зависимостей в проекте"""
    python_files = find_python_files(project_root)
    
    # Карта "файл -> его импорты"
    file_imports = {}
    
    # Карта "модуль -> файлы, которые его импортируют"
    module_dependents = defaultdict(list)
    
    for file_path in python_files:
        rel_path = os.path.relpath(file_path, project_root)
        imports = parse_imports(file_path)
        file_imports[rel_path] = imports
        
        # Заполняем информацию о зависимостях
        for imported_module in imports:
            if imported_module.startswith(('core.', 'utils.', 'services.', 'models.', 'routes.')):
                module_dependents[imported_module].append(rel_path)
    
    return file_imports, module_dependents

def find_unused_modules(file_imports, module_dependents, project_root):
    """Найти неиспользуемые модули"""
    python_files = find_python_files(project_root)
    
    # Создаем множество всех модулей проекта
    all_modules = set()
    for file_path in python_files:
        rel_path = os.path.relpath(file_path, project_root)
        # Преобразуем путь к файлу в имя модуля
        if rel_path.endswith('__init__.py'):
            module_name = os.path.dirname(rel_path).replace('/', '.').replace('\\', '.')
            all_modules.add(module_name)
        else:
            module_name = rel_path[:-3].replace('/', '.').replace('\\', '.')
            all_modules.add(module_name)
    
    # Модули, которые никто не импортирует
    unused_modules = []
    for module in all_modules:
        if module not in module_dependents and not module.endswith('__init__'):
            # Проверяем, что это не точка входа приложения
            if module != 'app' and not module.startswith('test_'):
                unused_modules.append(module)
    
    return unused_modules

def find_duplicated_functionality(project_root):
    """Поиск потенциально дублирующей функциональности по именам файлов"""
    potential_duplicates = []
    file_paths = find_python_files(project_root)
    
    # Группируем файлы по их базовым именам
    file_groups = defaultdict(list)
    for file_path in file_paths:
        base_name = os.path.basename(file_path).lower()
        if base_name != '__init__.py':
            file_groups[base_name].append(file_path)
    
    # Находим группы с более чем одним файлом
    for base_name, paths in file_groups.items():
        if len(paths) > 1:
            potential_duplicates.append((base_name, paths))
    
    # Поиск по похожим именам
    similarity_groups = []
    checked = set()
    
    for file_path in file_paths:
        base_name = os.path.basename(file_path).lower()
        if base_name in checked or base_name == '__init__.py':
            continue
            
        checked.add(base_name)
        similar_files = []
        
        # Проверяем ключевые слова
        keywords = ['file', 'system', 'keyboard', 'mouse', 'manager', 'controller', 'emulator']
        for keyword in keywords:
            if keyword in base_name:
                for other_file in file_paths:
                    other_base = os.path.basename(other_file).lower()
                    if other_base != base_name and keyword in other_base and other_file != file_path:
                        similar_files.append(other_file)
        
        if similar_files:
            similarity_groups.append((base_name, [file_path] + similar_files))
    
    return potential_duplicates, similarity_groups

if __name__ == "__main__":
    project_root = os.path.dirname(os.path.abspath(__file__))
    
    print("Анализ зависимостей в проекте...")
    file_imports, module_dependents = analyze_dependencies(project_root)
    
    print("\nМодули с наибольшим количеством зависимостей:")
    sorted_dependencies = sorted(module_dependents.items(), key=lambda x: len(x[1]), reverse=True)
    for module, dependents in sorted_dependencies[:10]:
        print(f"{module}: {len(dependents)} зависимых файлов")
    
    print("\nПоиск неиспользуемых модулей...")
    unused_modules = find_unused_modules(file_imports, module_dependents, project_root)
    for module in sorted(unused_modules):
        print(f"Неиспользуемый модуль: {module}")
    
    print("\nПоиск потенциального дублирования...")
    duplicates, similar_files = find_duplicated_functionality(project_root)
    
    if duplicates:
        print("\nФайлы с одинаковыми именами в разных директориях:")
        for base_name, paths in duplicates:
            print(f"  {base_name}:")
            for path in paths:
                print(f"    - {os.path.relpath(path, project_root)}")
    
    if similar_files:
        print("\nФайлы с похожей функциональностью (по названиям):")
        for base_name, paths in similar_files:
            print(f"  Связано с '{base_name}':")
            for path in paths:
                print(f"    - {os.path.relpath(path, project_root)}")

    print("\nАнализ завершен.")