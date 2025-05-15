import logging

import pyautogui

logger = logging.getLogger("neuro_assistant")


# IDE и инструменты
def open_vscode(path=None):
    """Открыть Visual Studio Code"""
    pyautogui.press("win")
    pyautogui.write("code")
    pyautogui.press("enter")


def open_pycharm(path=None):
    """Открыть PyCharm"""


def open_github_desktop():
    """Открыть GitHub Desktop"""


def open_terminal():
    """Открыть терминал"""


# Git и контроль версий
def git_clone(repo_url, path=None):
    """Клонировать Git-репозиторий"""


def git_pull():
    """Выполнить git pull в текущем репозитории"""


def git_commit(message):
    """Сделать коммит с указанным сообщением"""


def git_push():
    """Отправить изменения на удаленный репозиторий"""


# Тестирование и отладка
def run_tests(path=None):
    """Запустить тесты"""


def run_script(path):
    """Выполнить скрипт"""


def debug_script(path):
    """Запустить скрипт в режиме отладки"""


def check_code_quality(path):
    """Проверить качество кода"""
