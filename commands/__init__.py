# Словарь с командами и соответствующими функциями
COMMANDS = {
    "свернуть все окна": "minimize_all_windows",
    "сверни все окна": "minimize_all_windows",
    "открыть браузер": "open_browser",
    "открой браузер": "open_browser",
    "сделать скриншот": "take_screenshot",
    "сделай скриншот": "take_screenshot",
    "громкость выше": "volume_up",
    "увеличь громкость": "volume_up",
    "громкость ниже": "volume_down",
    "уменьши громкость": "volume_down",
    "открыть блокнот": "open_notepad",
    "открой блокнот": "open_notepad",
    "сказать": "speak_text",
    "скажи": "speak_text",
    "выключить компьютер": "shutdown_computer",
    "выключи компьютер": "shutdown_computer",
    "перезагрузить компьютер": "restart_computer",
    "перезагрузи компьютер": "restart_computer",
    "поставить на паузу": "media_pause",
    "поставь на паузу": "media_pause",
    "следующий трек": "media_next",
    "следующая песня": "media_next",
    "открыть калькулятор": "open_calculator",
    "открой калькулятор": "open_calculator",
}

# Импортируем все команды для удобства использования
from commands.system_commands import (
    minimize_all_windows, open_browser, take_screenshot, 
    volume_up, volume_down, open_notepad, speak_text,
    shutdown_computer, restart_computer
)
from commands.media_commands import media_pause, media_next
from commands.app_commands import open_calculator