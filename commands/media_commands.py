import pyautogui
import logging

logger = logging.getLogger('neuro_assistant')

def media_pause():
    """Пауза/воспроизведение медиа"""
    pyautogui.press('playpause')
    return "Управление воспроизведением"

def media_next():
    """Следующий трек"""
    pyautogui.press('nexttrack')
    return "Переключение на следующий трек"