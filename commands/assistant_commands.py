import logging

import pyautogui

logger = logging.getLogger("neuro_assistant")


# Электронная почта
def send_email(to, subject, body, attachments=None):
    """Отправить электронное письмо"""


def check_email():
    """Проверить электронную почту"""


def open_email_client():
    """Открыть почтовый клиент"""


# Мессенджеры
def open_messenger(messenger_name):
    """Открыть мессенджер (WhatsApp, Telegram, и т.д.)"""
    pyautogui.press("win")
    pyautogui.write(messenger_name)
    pyautogui.press("enter")


def send_message(messenger, recipient, message):
    """Отправить сообщение через мессенджер"""


def make_voice_call(messenger, recipient):
    """Сделать голосовой вызов"""


def make_video_call(messenger, recipient):
    """Сделать видеозвонок"""
