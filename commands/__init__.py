import importlib
import logging
import os
from typing import Callable, Dict, List, Optional

logger = logging.getLogger("neuro_assistant")

# Инициализируем словари
COMMANDS: Dict[str, Callable] = {}
COMMAND_ALIASES: Dict[str, str] = {}
COMMAND_INTENTS: Dict[str, List[str]] = {}
COMMAND_CATEGORIES: Dict[str, List[str]] = {}


def load_command_modules():
    """
    Динамически загружает все модули команд из директории commands
    """
    # Получаем путь к текущей директории
    current_dir = os.path.dirname(os.path.abspath(__file__))

    # Получаем список файлов в директории
    files = [
        f
        for f in os.listdir(current_dir)
        if os.path.isfile(os.path.join(current_dir, f))
        and f.endswith("_commands.py")
        and f != "__init__.py"
    ]

    for file in files:
        module_name = file[:-3]  # Убираем расширение .py
        try:
            # Импортируем модуль
            module = importlib.import_module(f"commands.{module_name}")

            # Добавляем команды из модуля
            if hasattr(module, "get_commands"):
                COMMANDS.update(module.get_commands())

            # Добавляем псевдонимы команд
            if hasattr(module, "get_aliases"):
                COMMAND_ALIASES.update(module.get_aliases())

            # Добавляем намерения команд
            if hasattr(module, "get_intents"):
                COMMAND_INTENTS.update(module.get_intents())

            # Добавляем категории команд
            if hasattr(module, "get_categories"):
                COMMAND_CATEGORIES.update(module.get_categories())

            logger.info(f"Загружен модуль команд: {module_name}")
        except Exception as e:
            logger.error(f"Ошибка при загрузке модуля {module_name}: {str(e)}")


def get_command_function(command_text: str) -> Optional[Callable]:
    """
    Получить функцию команды по тексту.

    Args:
        command_text (str): Текст команды

    Returns:
        Optional[Callable]: Функция команды или None, если команда не найдена
    """
    # Проверяем, есть ли команда в основном словаре
    if command_text in COMMANDS:
        return COMMANDS[command_text]

    # Проверяем, есть ли команда в синонимах
    if command_text in COMMAND_ALIASES:
        original_command = COMMAND_ALIASES[command_text]
        return COMMANDS.get(original_command)

    return None


# Загружаем модули при импорте пакета
load_command_modules()
