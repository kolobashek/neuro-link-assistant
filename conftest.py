import os
import sys

# Добавляем корневой каталог проекта в путь поиска модулей
project_root = os.path.abspath(os.path.dirname(__file__))
sys.path.insert(0, project_root)

# Убеждаемся, что все основные модули доступны
sys.path.insert(0, os.path.join(project_root, "core"))
sys.path.insert(0, os.path.join(project_root, "routes"))
sys.path.insert(0, os.path.join(project_root, "services"))
sys.path.insert(0, os.path.join(project_root, "utils"))

# Настройки для тестовой среды
os.environ.setdefault("TESTING", "true")
os.environ.setdefault("FLASK_ENV", "testing")

# Отключаем логирование в файлы для тестов
os.environ.setdefault("DISABLE_FILE_LOGGING", "true")
