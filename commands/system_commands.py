import logging
import os
import time
import traceback

import pyautogui
import pyttsx3

from config import Config

# import win32con
# import win32gui


logger = logging.getLogger("neuro_assistant")


def minimize_all_windows():
    """Свернуть все окна (Win+D)"""
    logger.info("Начало выполнения функции minimize_all_windows()")
    try:
        # Метод с использованием PowerShell
        logger.info("Попытка использования PowerShell для сворачивания всех окон")
        os.system('powershell -command "(New-Object -ComObject Shell.Application).MinimizeAll()"')
        logger.info("Команда PowerShell выполнена")

        return "Все окна свернуты"
    except Exception as e:
        logger.error(f"Ошибка в функции minimize_all_windows(): {str(e)}")
        logger.error(traceback.format_exc())
        return f"Ошибка при сворачивании окон: {str(e)}"


def open_browser():
    """Открыть браузер по умолчанию"""
    os.system("start https://www.google.com")
    return "Браузер открыт"


def take_screenshot(path=None):
    """Сделать скриншот и сохранить по указанному пути"""
    screenshot_path = path or Config.SCREENSHOT_DIR
    os.makedirs(screenshot_path, exist_ok=True)
    filename = f"screenshot_{int(time.time())}.png"
    full_path = os.path.join(screenshot_path, filename)
    pyautogui.screenshot(full_path)
    return f"Скриншот сохранен: {filename}"


def volume_up(steps=5):
    """Увеличить громкость системы"""
    for _ in range(steps):  # Увеличиваем на заданное количество шагов
        pyautogui.press("volumeup")
    return "Громкость увеличена"


def volume_down(steps=5):
    """Уменьшить громкость системы"""
    for _ in range(steps):  # Уменьшаем на заданное количество шагов
        pyautogui.press("volumedown")
    return "Громкость уменьшена"


def set_volume(level):
    """Установить уровень громкости (0-100%)"""
    pyautogui.press("volumemute")
    for _ in range(level):  # Увеличиваем на заданное количество шагов
        pyautogui.press("volumeup")


def open_notepad():
    """Открыть блокнот"""
    os.system("notepad")
    return "Блокнот открыт"


def speak_text(text):
    """Озвучить текст"""
    engine = pyttsx3.init()
    engine.say(text)
    engine.runAndWait()
    return f"Текст '{text}' озвучен"


def shutdown_computer(timeout=30):
    """Выключение компьютера с опциональной задержкой"""
    os.system(f"shutdown /s /t {timeout}")
    return f"Компьютер будет выключен через {timeout} секунд"


def restart_computer(timeout=30):
    """Перезагрузка компьютера с опциональной задержкой"""
    os.system(f"shutdown /r /t {timeout}")
    return f"Компьютер будет перезагружен через {timeout} секунд"


# Управление окнами
def maximize_window(title=None):
    """Развернуть окно"""


def restore_window(title=None):
    """Восстановить окно"""


def close_window(title=None):
    """Закрыть активное окно или окно с указанным заголовком"""


# Управление системой


def sleep_computer():
    """Перевести компьютер в спящий режим"""


def lock_computer():
    """Заблокировать компьютер"""


def logout_user():
    """Выйти из системы"""


def mute_sound():
    """Выключить звук"""


def unmute_sound():
    """Включить звук"""


# Скриншоты и запись экрана
def start_screen_recording(path=None):
    """Начать запись экрана"""


def stop_screen_recording():
    """Остановить запись экрана"""


# Буфер обмена
def copy_to_clipboard(text):
    """Скопировать текст в буфер обмена"""


def paste_from_clipboard():
    """Вставить текст из буфера обмена"""


def clear_clipboard():
    """Очистить буфер обмена"""


def show_notification(title, message):
    """Показать уведомление"""


# Система
def get_system_info():
    """Получить информацию о системе"""


def list_running_processes():
    """Показать список запущенных процессов"""


def kill_process(process_name_or_id):
    """Завершить процесс по имени или ID"""


def get_commands():
    return {
        "свернуть все окна": minimize_all_windows,
        "развернуть окно": maximize_window,
        "закрыть окно": close_window,
        "выключить компьютер": shutdown_computer,
        "перезагрузить компьютер": restart_computer,
        "спящий режим": sleep_computer,
        "заблокировать компьютер": lock_computer,
        "выйти из системы": logout_user,
        "увеличить громкость": volume_up,
        "уменьшить громкость": volume_down,
        "установить громкость": set_volume,
        "выключить звук": mute_sound,
        "включить звук": unmute_sound,
        "сделать скриншот": take_screenshot,
        "начать запись экрана": start_screen_recording,
        "остановить запись экрана": stop_screen_recording,
        "скопировать текст": copy_to_clipboard,
        "вставить текст": paste_from_clipboard,
        "очистить буфер обмена": clear_clipboard,
        "сказать": speak_text,
        "показать уведомление": show_notification,
        "системная информация": get_system_info,
        "запущенные процессы": list_running_processes,
        "завершить процесс": kill_process,
        "открыть браузер": open_browser,
    }


def get_aliases():
    return {
        "скрин": "сделать скриншот",
        "снимок экрана": "сделать скриншот",
        "скриншот": "сделать скриншот",
        "выключить пк": "выключить компьютер",
        "перезагрузить пк": "перезагрузить компьютер",
        "громче": "увеличить громкость",
        "тише": "уменьшить громкость",
        "заблокировать": "заблокировать компьютер",
        "выйти": "выйти из системы",
        "спать": "спящий режим",
        "записывать экран": "начать запись экрана",
        "стоп запись": "остановить запись экрана",
    }


def get_intents():
    return {
        "управление_окнами": ["свернуть все окна", "развернуть окно", "закрыть окно"],
        "управление_системой": [
            "выключить компьютер",
            "перезагрузить компьютер",
            "спящий режим",
            "заблокировать компьютер",
            "выйти из системы",
        ],
        "управление_звуком": [
            "увеличить громкость",
            "уменьшить громкость",
            "установить громкость",
            "выключить звук",
            "включить звук",
        ],
        "скриншоты_запись": [
            "сделать скриншот",
            "начать запись экрана",
            "остановить запись экрана",
        ],
        "буфер_обмена": [
            "скопировать текст",
            "вставить текст",
            "очистить буфер обмена",
        ],
        "информация_система": [
            "системная информация",
            "запущенные процессы",
            "завершить процесс",
        ],
    }


def get_categories():
    return {
        "Система": [
            "управление_окнами",
            "управление_системой",
            "управление_звуком",
            "скриншоты_запись",
            "буфер_обмена",
            "информация_система",
        ]
    }
