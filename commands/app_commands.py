import os
import time
import logging
import win32gui
import pyautogui

logger = logging.getLogger('neuro_assistant')

def open_calculator():
    """Открыть калькулятор"""
    os.system("calc")
    return "Калькулятор открыт"

def calculate_expression(expression):
    """
    Вычисляет выражение с помощью калькулятора Windows
    
    Args:
        expression: Математическое выражение для вычисления
        
    Returns:
        Строка с результатом вычисления
    """
    # Открываем калькулятор
    os.system("calc")
    time.sleep(1)  # Ждем открытия калькулятора
    
    # Находим окно калькулятора и активируем его
    calc_window = win32gui.FindWindow(None, "Калькулятор")
    if calc_window == 0:  # Если не нашли по русскому названию
        calc_window = win32gui.FindWindow(None, "Calculator")
    
    if calc_window != 0:
        # Активируем окно калькулятора
        win32gui.SetForegroundWindow(calc_window)
        time.sleep(0.5)  # Даем время на активацию окна
        
        # Очищаем калькулятор
        pyautogui.press('escape')
        
        # Вводим выражение
        for char in expression:
            if char == '+':
                pyautogui.press('+')
            elif char == '-':
                pyautogui.press('-')
            elif char == '*':
                pyautogui.press('*')
            elif char == '/':
                pyautogui.press('/')
            else:
                pyautogui.press(char)
        
        # Нажимаем Enter для вычисления
        pyautogui.press('enter')
        
        # Даем время на вычисление
        time.sleep(0.5)
        
        return f"Вычислено выражение {expression} в калькуляторе"
    else:
        return "Не удалось найти окно калькулятора"