import os
import time
import logging
import traceback
import pyautogui
import win32gui
import win32con
import pyttsx3
from config import Config

logger = logging.getLogger('neuro_assistant')

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

def take_screenshot():
    """Сделать скриншот и сохранить в папку проекта"""
    screenshot_path = Config.SCREENSHOT_DIR
    os.makedirs(screenshot_path, exist_ok=True)
    filename = f"screenshot_{int(time.time())}.png"
    full_path = os.path.join(screenshot_path, filename)
    pyautogui.screenshot(full_path)
    return f"Скриншот сохранен: {filename}"

def volume_up():
    """Увеличить громкость системы"""
    for _ in range(5):  # Увеличиваем на 5 шагов
        pyautogui.press('volumeup')
    return "Громкость увеличена"

def volume_down():
    """Уменьшить громкость системы"""
    for _ in range(5):  # Уменьшаем на 5 шагов
        pyautogui.press('volumedown')
    return "Громкость уменьшена"

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

def shutdown_computer():
    """Выключение компьютера (с задержкой 10 секунд)"""
    os.system("shutdown /s /t 10")
    return "Компьютер будет выключен через 10 секунд"

def restart_computer():
    """Перезагрузка компьютера (с задержкой 10 секунд)"""
    os.system("shutdown /r /t 10")
    return "Компьютер будет перезагружен через 10 секунд"