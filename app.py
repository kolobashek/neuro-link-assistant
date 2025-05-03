from flask import Flask, render_template, request, jsonify, current_app
import requests
import os
import json
import subprocess
import traceback
import pyautogui
import win32gui
import win32con
import win32api
import pyttsx3
import time
import logging
from dotenv import load_dotenv

# Загрузка переменных окружения
load_dotenv()

app = Flask(__name__)

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Словарь с командами и соответствующими функциями
COMMANDS = {
    "свернуть все окна": "minimize_all_windows",
    "открыть браузер": "open_browser",
    "сделать скриншот": "take_screenshot",
    "громкость выше": "volume_up",
    "громкость ниже": "volume_down",
    "открыть блокнот": "open_notepad",
    "сказать": "speak_text",
    "выключить компьютер": "shutdown_computer",
    "перезагрузить компьютер": "restart_computer",
    "поставить на паузу": "media_pause",
    "следующий трек": "media_next",
}

def get_ai_response(text, max_retries=3, retry_delay=2):
    """Получение ответа от нейросети через HuggingFace API с повторными попытками"""
    API_URL = "https://api-inference.huggingface.co/models/google/flan-t5-base"  # Используем меньшую модель
    api_key = os.getenv('HUGGINGFACE_API_KEY', '')
    headers = {"Authorization": f"Bearer {api_key}"}
    
    # Логирование заголовков запроса (маскируем часть API ключа для безопасности)
    masked_key = api_key[:4] + "..." + api_key[-4:] if len(api_key) > 8 else "Ключ не задан"
    logger.info(f"Заголовки запроса к HuggingFace API: Authorization: Bearer {masked_key}")
    
    payload = {
        "inputs": f"""Напиши Python код для выполнения следующей команды на Windows: "{text}".
        Используй доступные библиотеки: pyautogui, os, win32gui, win32con, pyttsx3.
        Оформи код в формате Python между тройными обратными кавычками с указанием языка python.
        Примеры доступных функций:
        - pyautogui.hotkey('win', 'd') - нажатие комбинации клавиш
        - os.system("start notepad") - запуск программы
        - pyautogui.press('volumeup') - нажатие на кнопку
        - pyautogui.screenshot('filename.png') - создание скриншота
        """,
        "parameters": {
            "max_length": 512,
            "temperature": 0.7
        }
    }
    
    for attempt in range(max_retries):
        try:
            logger.info(f"Отправка запроса к HuggingFace API для текста: '{text}' (попытка {attempt+1}/{max_retries})")
            response = requests.post(API_URL, headers=headers, json=payload)
            logger.info(f"Статус ответа от HuggingFace API: {response.status_code}")
            
            if response.status_code == 200:
                logger.info("Успешный ответ от API")
                return response.json()[0]["generated_text"]
            elif response.status_code == 503:
                logger.warning(f"Сервис временно недоступен (503). Попытка {attempt+1}/{max_retries}")
                if attempt < max_retries - 1:
                    time.sleep(retry_delay)
                    continue
                else:
                    return "Сервис генерации кода временно недоступен. Пожалуйста, попробуйте позже или используйте предопределенные команды."
            else:
                logger.error(f"Ошибка API. Тело ответа: {response.text}")
                return f"Ошибка API: {response.status_code}"
        except Exception as e:
            logger.exception(f"Исключение при обращении к API: {str(e)}")
            if attempt < max_retries - 1:
                time.sleep(retry_delay)
                continue
            else:
                return f"Произошла ошибка при обращении к нейросети: {str(e)}"
    
    return "Не удалось получить ответ от сервиса после нескольких попыток."    
def minimize_all_windows():
    """Свернуть все окна (Win+D)"""
    logger.info("Начало выполнения функции minimize_all_windows()")
    try:
        # Проверим, что pyautogui доступен и работает
        logger.info("Текущая позиция курсора: " + str(pyautogui.position()))
        
        # Добавим небольшую задержку перед нажатием клавиш
        logger.info("Ожидание 1 секунду перед нажатием клавиш...")
        time.sleep(1)
        
        # Попробуем нажать комбинацию клавиш
        logger.info("Попытка нажатия комбинации Win+D")
        pyautogui.hotkey('win', 'd')
        logger.info("Комбинация клавиш Win+D нажата")
        
        # Добавим еще одну задержку после нажатия
        time.sleep(0.5)
        logger.info("Функция minimize_all_windows() завершена успешно")
        
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
    screenshot_path = os.path.join(os.getcwd(), "static", "screenshots")
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

# Выполнение произвольного кода Python (с осторожностью)
def execute_python_code(code):
    """Выполнить Python код и вернуть результат"""
    try:
        # Создаем локальный словарь с разрешенными функциями
        local_dict = {
            "pyautogui": pyautogui,
            "os": os,
            "time": time,
            "win32gui": win32gui,
            "win32con": win32con,
            "pyttsx3": pyttsx3,
            "minimize_all_windows": minimize_all_windows,
            "open_browser": open_browser,
            "take_screenshot": take_screenshot,
            "volume_up": volume_up,
            "volume_down": volume_down,
            "open_notepad": open_notepad,
            "speak_text": speak_text,
        }
        
        # Выполняем код в изолированном пространстве
        result = {}
        exec(code, {"__builtins__": {}}, local_dict)
        return "Код успешно выполнен"
    except Exception as e:
        traceback_str = traceback.format_exc()
        return f"Ошибка при выполнении кода: {str(e)}\n{traceback_str}"

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/query', methods=['POST'])
def query():
    user_input = request.json.get('input', '').lower()
    # user_input = request.json[0].get('input', '').lower()
    
    # Определение типа команды и генерация ответа
    response, code = process_command(user_input)
    
    # Если есть код для выполнения, выполняем его
    execution_result = None
    if code:
        execution_result = execute_python_code(code)
    
    return jsonify({
        'response': response,
        'code': code,
        'execution_result': execution_result
    })

def process_command(text):
    """Анализ команды и генерация соответствующего кода"""
    text = text.lower()
    
    # Простое сопоставление с известными командами
    for command_text, function_name in COMMANDS.items():
        if command_text in text:
            code = f"{function_name}()"
            
            # Особая обработка для команды "сказать"
            if function_name == "speak_text":
                # Извлекаем текст после слова "сказать"
                speak_content = text.split("сказать", 1)[1].strip()
                if speak_content:
                    code = f"speak_text('{speak_content}')"
            
            return f"Выполняю команду: {command_text}", code
    
    # Если команда не распознана, отправляем запрос к нейросети
    # для генерации кода на основе текста
    response = get_ai_response(text)
    code = extract_code_from_response(response)
    
    return response, code

def extract_code_from_response(response):
    """Извлекает код Python из ответа нейросети"""
    code_start = response.find("```python")
    if code_start != -1:
        code_start += 9  # длина "```python"
        code_end = response.find("```", code_start)
        if code_end != -1:
            return response[code_start:code_end].strip()
    return None

# И реализовать функции
def shutdown_computer():
    """Выключение компьютера (с задержкой 10 секунд)"""
    os.system("shutdown /s /t 10")
    return "Компьютер будет выключен через 10 секунд"

def restart_computer():
    """Перезагрузка компьютера (с задержкой 10 секунд)"""
    os.system("shutdown /r /t 10")
    return "Компьютер будет перезагружен через 10 секунд"

def media_pause():
    """Пауза/воспроизведение медиа"""
    pyautogui.press('playpause')
    return "Управление воспроизведением"

def media_next():
    """Следующий трек"""
    pyautogui.press('nexttrack')
    return "Переключение на следующий трек"

if __name__ == '__main__':
  app.run(debug=True)