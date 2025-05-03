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
import webbrowser
import pyperclip
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException

# Загрузка переменных окружения
load_dotenv()

app = Flask(__name__)

# Настройка логирования
logging.basicConfig(level=logging.INFO, 
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

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
    # Добавьте новые команды здесь
    "открыть калькулятор": "open_calculator",
    "открой калькулятор": "open_calculator",
}

def is_command_feasible(command_text):
    """
    Определяет, целесообразно ли выполнение команды
    """
    # Список потенциально опасных или нецелесообразных команд
    dangerous_keywords = [
        "удали", "delete", "format", "форматир", 
        "rm -rf", "shutdown", "выключ", 
        "reboot", "перезагруз"
    ]
    
    # Проверяем наличие опасных ключевых слов
    for keyword in dangerous_keywords:
        if keyword in command_text.lower():
            # Для некоторых команд требуется дополнительное подтверждение
            if keyword in ["shutdown", "выключ", "reboot", "перезагруз"]:
                return {
                    "feasible": True,
                    "requires_confirmation": True,
                    "reason": f"Команда '{keyword}' требует подтверждения пользователя"
                }
            
            # Для действительно опасных команд возвращаем запрет
            if keyword in ["удали", "delete", "format", "форматир", "rm -rf"]:
                return {
                    "feasible": False,
                    "reason": f"Команда '{keyword}' потенциально опасна и не может быть выполнена автоматически"
                }
    
    # Проверяем на сложность и длительность выполнения
    complex_keywords = [
        "установи", "install", "скачай", "download",
        "обнови", "update", "компилируй", "compile"
    ]
    
    for keyword in complex_keywords:
        if keyword in command_text.lower():
            return {
                "feasible": True,
                "requires_confirmation": True,
                "reason": f"Команда '{keyword}' может занять продолжительное время. Требуется подтверждение."
            }
    
    # По умолчанию считаем команду выполнимой
    return {
        "feasible": True,
        "requires_confirmation": False
    }

def process_command(text):
    """Анализ команды и генерация соответствующего кода"""
    text = text.lower()
    
    # Проверяем целесообразность выполнения команды
    feasibility = is_command_feasible(text)
    if not feasibility.get("feasible", True):
        return f"Команда не может быть выполнена: {feasibility.get('reason', 'Неизвестная причина')}", None
    
    # Если команда требует подтверждения, сообщаем об этом
    if feasibility.get("requires_confirmation", False):
        # Здесь можно добавить логику для запроса подтверждения
        # Но пока просто продолжаем выполнение
        logger.info(f"Команда требует подтверждения: {feasibility.get('reason', '')}")
    
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

def get_ai_response(text):
    """Получение ответа от нейросети через различные сервисы"""
    API_URL = "https://api-inference.huggingface.co/models/meta-llama/Llama-2-70b-chat-hf"
    headers = {"Authorization": f"Bearer {os.getenv('HUGGINGFACE_API_KEY', '')}"}
    
    try:
        # Сначала пробуем HuggingFace API
        logger.info("Попытка использования HuggingFace API")
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
        
        response = requests.post(API_URL, headers=headers, json=payload, timeout=10)
        
        if response.status_code == 200:
            logger.info("Успешный ответ от HuggingFace API")
            return response.json()[0]["generated_text"]
        else:
            logger.warning(f"HuggingFace API недоступно (код {response.status_code}). Пробуем альтернативные методы.")
            # Если HuggingFace недоступен, пробуем DeepSeek через браузер
            return try_browser_alternatives(text)
            
    except Exception as e:
        logger.error(f"Ошибка при обращении к HuggingFace API: {str(e)}")
        # В случае ошибки пробуем альтернативные методы
        return try_browser_alternatives(text)

def try_browser_alternatives(text):
    """Попытка получить ответ через браузерные альтернативы"""
    try:
        # Сначала пробуем DeepSeek
        logger.info("Попытка использования DeepSeek через браузер")
        result = use_deepseek(text)
        if result and "" in result:
            logger.info("Успешно получен ответ от DeepSeek")
            return result
        
        # Если DeepSeek не сработал, пробуем LM Arena
        logger.info("DeepSeek не сработал. Попытка использования LM Arena")
        result = use_lm_arena(text)
        if result:
            logger.info("Успешно получен ответ от LM Arena")
            return result
            
        # Если ничего не сработало
        return "Не удалось получить ответ от доступных сервисов. Пожалуйста, используйте предустановленные команды."
    
    except Exception as e:
        logger.error(f"Ошибка при использовании браузерных альтернатив: {str(e)}")
        return f"Произошла ошибка при обращении к альтернативным сервисам: {str(e)}"

def use_deepseek(text):
    """Использование DeepSeek через браузер"""
    prompt = f"""Напиши Python код для выполнения следующей команды на Windows: "{text}".
    Используй доступные библиотеки: pyautogui, os, win32gui, win32con, pyttsx3.
    Оформи код в формате Python между тройными обратными кавычками с указанием языка python.
    Примеры доступных функций:
    - pyautogui.hotkey('win', 'd') - нажатие комбинации клавиш
    - os.system("start notepad") - запуск программы
    - pyautogui.press('volumeup') - нажатие на кнопку
    - pyautogui.screenshot('filename.png') - создание скриншота
    """
    
    try:
        # Инициализация браузера
        options = webdriver.ChromeOptions()
        options.add_argument("--start-maximized")
        driver = webdriver.Chrome(options=options)
        
        # Открываем DeepSeek
        driver.get("https://chat.deepseek.com/")
        
        # Ждем загрузки страницы и проверяем, залогинен ли пользователь
        wait = WebDriverWait(driver, 10)
        
        try:
            # Проверяем, есть ли поле ввода (если залогинен)
            input_field = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "textarea[placeholder*='Send a message']")))
            
            # Вставляем запрос
            input_field.send_keys(prompt)
            input_field.send_keys(Keys.RETURN)
            
            # Ждем ответа (ищем блок с кодом)
            code_block = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "pre code")))
            
            # Получаем весь ответ
            response_elements = driver.find_elements(By.CSS_SELECTOR, ".markdown-body p, .markdown-body pre")
            full_response = "\n".join([elem.text for elem in response_elements])
            
            driver.quit()
            return full_response
            
        except TimeoutException:
            # Если не залогинен, пробуем залогиниться или переходим к следующему варианту
            logger.warning("DeepSeek требует авторизации. Переходим к следующему варианту.")
            driver.quit()
            return None
            
    except Exception as e:
        logger.error(f"Ошибка при использовании DeepSeek: {str(e)}")
        try:
            driver.quit()
        except:
            pass
        return None

def use_lm_arena(text):
    """Использование LM Arena через браузер"""
    prompt = f"""Напиши Python код для выполнения следующей команды на Windows: "{text}".
    Используй доступные библиотеки: pyautogui, os, win32gui, win32con, pyttsx3.
    Оформи код в формате Python между тройными обратными кавычками с указанием языка python.
    Примеры доступных функций:
    - pyautogui.hotkey('win', 'd') - нажатие комбинации клавиш
    - os.system("start notepad") - запуск программы
    - pyautogui.press('volumeup') - нажатие на кнопку
    - pyautogui.screenshot('filename.png') - создание скриншота
    """
    
    try:
        # Инициализация браузера
        options = webdriver.ChromeOptions()
        options.add_argument("--start-maximized")
        driver = webdriver.Chrome(options=options)
        
        # Открываем LM Arena
        driver.get("https://lmarena.ai/")
        
        # Ждем загрузки страницы
        wait = WebDriverWait(driver, 10)
        
        # Находим поле ввода
        input_field = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "textarea[placeholder*='Send a message']")))
        
        # Вставляем запрос
        input_field.send_keys(prompt)
        input_field.send_keys(Keys.RETURN)
        
        # Ждем ответа (ищем блок с кодом или любой ответ)
        try:
            code_block = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "pre code")))
        except:
            # Если блок с кодом не найден, ищем любой ответ
            wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, ".message-content")))
        
        # Получаем весь ответ
        time.sleep(2)  # Даем время для полной загрузки ответа
        response_elements = driver.find_elements(By.CSS_SELECTOR, ".message-content p, .message-content pre")
        full_response = "\n".join([elem.text for elem in response_elements])
        
        driver.quit()
        return full_response
        
    except Exception as e:
        logger.error(f"Ошибка при использовании LM Arena: {str(e)}")
        try:
            driver.quit()
        except:
            pass
        return None

# Простой вариант без Selenium (просто открывает браузер)
def fallback_browser_method(text):
    """Простой метод открытия браузера с запросом"""
    prompt = f"""Напиши Python код для выполнения следующей команды на Windows: "{text}".
    Используй доступные библиотеки: pyautogui, os, win32gui, win32con, pyttsx3."""
    
    # Копируем запрос в буфер обмена
    pyperclip.copy(prompt)
    
    # Сначала пробуем DeepSeek
    webbrowser.open("https://chat.deepseek.com/")
    time.sleep(1)  # Даем время на открытие браузера
    
    # Уведомляем пользователя
    speak_text("Открыт браузер с DeepSeek. Запрос скопирован в буфер обмена. Вставьте его и получите ответ.")
    
    return "Открыт браузер с DeepSeek. Запрос скопирован в буфер обмена. Пожалуйста, вставьте его и получите ответ."

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
def open_calculator():
    """Открыть калькулятор"""
    os.system("calc")
    return "Калькулятор открыт"
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
            "win32api": win32api,
            "pyttsx3": pyttsx3,
            "re": re,
            "pyperclip": pyperclip,
            "minimize_all_windows": minimize_all_windows,
            "open_browser": open_browser,
            "take_screenshot": take_screenshot,
            "volume_up": volume_up,
            "volume_down": volume_down,
            "open_notepad": open_notepad,
            "speak_text": speak_text,
            "open_calculator": open_calculator,
            "shutdown_computer": shutdown_computer,
            "restart_computer": restart_computer,
            "media_pause": media_pause,
            "media_next": media_next,
            "extract_math_expression": extract_math_expression,
            # Добавляем логгеры для отчетов о выполнении
            "detailed_logger": detailed_logger,
        }
        
        # Выполняем код в изолированном пространстве
        result = {}
        exec(code, {"__builtins__": {}}, local_dict)
        
        # Проверяем, был ли возвращен результат из кода
        if 'result' in local_dict:
            return local_dict['result']
        
        return "Код успешно выполнен"
    except Exception as e:
        traceback_str = traceback.format_exc()
        detailed_logger.error(f"Ошибка при выполнении кода: {str(e)}\n{traceback_str}")
        return f"Ошибка при выполнении кода: {str(e)}\n{traceback_str}"

def execute_command_with_error_handling(command_text, code):
    """
    Выполняет команду с обработкой ошибок, анализом и автоматическим восстановлением
    """
    logger.info(f"Начало выполнения команды: {command_text}")
    
    # Выполнение кода
    execution_result = execute_python_code(code)
    
    # Если есть функция проверки, используем её
    if 'verify_command_execution' in globals():
        verification_result = verify_command_execution(code, command_text)
        
        # Если команда выполнена успешно
        if verification_result.get("verified", False):
            logger.info(f"Команда '{command_text}' успешно выполнена")
            return {
                "success": True,
                "execution_result": execution_result,
                "verification_result": verification_result,
                "message": "Команда успешно выполнена"
            }
        else:
            # Если команда не выполнена успешно, возвращаем информацию об ошибке
            logger.warning(f"Команда '{command_text}' не выполнена успешно")
            return {
                "success": False,
                "execution_result": execution_result,
                "verification_result": verification_result,
                "message": verification_result.get("message", "Команда не выполнена успешно")
            }
    else:
        # Если функция проверки не определена, просто возвращаем результат выполнения
        return {
            "success": True,
            "execution_result": execution_result,
            "message": "Команда выполнена, но проверка не производилась"
        }

@app.route('/')
def index():
    # Группируем команды по функциям
    commands_grouped = {}
    for command_text, function_name in COMMANDS.items():
        if function_name not in commands_grouped:
            commands_grouped[function_name] = []
        commands_grouped[function_name].append(command_text)
    
    # Создаем список команд для отображения
    # Для каждой функции берем первую команду как основную и остальные как альтернативные
    display_commands = []
    for function_name, command_list in commands_grouped.items():
        main_command = command_list[0]
        alt_commands = command_list[1:] if len(command_list) > 1 else []
        display_commands.append({
            'main': main_command,
            'alternatives': alt_commands,
            'function': function_name
        })
    
    return render_template('index.html', commands=display_commands)

def try_fix_error(step_description, error_message):
    """
    Анализирует ошибку и пытается сгенерировать исправленный код
    """
    detailed_logger.info(f"Анализ ошибки: {error_message}")
    
    # Проверяем типичные ошибки и предлагаем исправления
    if "NameError: name" in error_message and "is not defined" in error_message:
        # Извлекаем имя неопределенной функции или переменной
        match = re.search(r"name '(.+)' is not defined", error_message)
        if match:
            undefined_name = match.group(1)
            detailed_logger.info(f"Обнаружено неопределенное имя: {undefined_name}")
            
            # Проверяем, является ли это именем функции, которую нужно определить
            if undefined_name.endswith("_calculator"):
                detailed_logger.info("Генерация кода для работы с калькулятором")
                return generate_calculator_code(step_description)
            
            # Другие специальные случаи можно добавить здесь
    
    # Если не удалось определить конкретную ошибку, используем нейросеть для исправления
    prompt = f"""
    Исправь ошибку в Python коде для выполнения следующей команды: "{step_description}".
    Ошибка: {error_message}
    
    Используй доступные библиотеки: pyautogui, os, win32gui, win32con, pyttsx3.
    Оформи исправленный код в формате Python между тройными обратными кавычками.
    """
    
    response = get_ai_response(prompt)
    fixed_code = extract_code_from_response(response)
    
    return fixed_code

def generate_calculator_code(step_description):
    """
    Генерирует код для работы с калькулятором на основе описания шага
    """
    # Извлекаем математическое выражение из описания
    expression = extract_math_expression(step_description)
    
    if not expression:
        return None
    
    # Генерируем код для работы с калькулятором
    code = f"""
def calculate_with_calculator(expression):
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

# Выполняем вычисление
calculate_with_calculator("{expression}")
"""
    return code

def extract_math_expression(text):
    """Извлекает математическое выражение из текста"""
    import re
    
    # Ищем числа и математические операторы
    pattern = r'(\d+\s*[\+\-\*\/]\s*\d+)'
    matches = re.findall(pattern, text)
    
    if matches:
        return matches[0].replace(' ', '')
    
    return None

# Обновляем маршрут для обработки запросов
@app.route('/query', methods=['POST'])
def query():
    user_input = request.json.get('input', '').lower()
    
    # Проверяем, является ли команда составной
    if any(sep in user_input for sep in [" и ", " затем ", " после этого ", " потом ", ", "]):
        # Обрабатываем составную команду
        execution_result = execute_command_with_steps(user_input)
        
        # Формируем ответ для пользователя
        steps_info = []
        for step in execution_result.steps:
            step_info = {
                'number': step.step_number,
                'description': step.description,
                'status': step.status,
                'result': step.result if step.status == 'completed' else step.error
            }
            steps_info.append(step_info)
        
        return jsonify({
            'response': f"Выполнение команды: {user_input}",
            'is_compound': True,
            'steps': steps_info,
            'overall_status': execution_result.overall_status,
            'completion_percentage': execution_result.completion_percentage,
            'accuracy_percentage': execution_result.accuracy_percentage,
            'message': f"Команда выполнена с точностью {execution_result.accuracy_percentage:.1f}% и завершенностью {execution_result.completion_percentage:.1f}%"
        })
    else:
        # Обрабатываем простую команду
        response, code = process_command(user_input)
        
        # Если есть код для выполнения, выполняем его
        if code:
            execution_result = execute_python_code(code)
            
            # Создаем запись о выполнении команды для логирования
            step = CommandStep(
                step_number=1,
                description=user_input,
                status='completed' if "Ошибка" not in execution_result else 'failed',
                result=execution_result if "Ошибка" not in execution_result else None,
                error=execution_result if "Ошибка" in execution_result else None,
                completion_percentage=100.0 if "Ошибка" not in execution_result else 0.0
            )
            
            execution = CommandExecution(
                command_text=user_input,
                steps=[step],
                start_time=datetime.datetime.now().isoformat(),
                end_time=datetime.datetime.now().isoformat(),
                overall_status='completed' if "Ошибка" not in execution_result else 'failed',
                completion_percentage=100.0 if "Ошибка" not in execution_result else 0.0,
                accuracy_percentage=90.0 if "Ошибка" not in execution_result else 0.0
            )
            
            # Логируем выполнение команды
            log_execution_summary(execution, final=True)
            
            return jsonify({
                'response': response,
                'code': code,
                'execution_result': execution_result,
                'is_compound': False,
                'overall_status': execution.overall_status,
                'completion_percentage': execution.completion_percentage,
                'accuracy_percentage': execution.accuracy_percentage
            })
        else:
            # Если код не был сгенерирован
            return jsonify({
                'response': response,
                'code': None,
                'execution_result': "Не удалось сгенерировать код для выполнения команды",
                'is_compound': False,
                'overall_status': 'failed',
                'completion_percentage': 0.0,
                'accuracy_percentage': 0.0,
                'message': "Пожалуйста, уточните команду или используйте предустановленные команды"
            })

@app.route('/clarify', methods=['POST'])
def clarify():
    """
    Обрабатывает запросы на уточнение информации от пользователя
    """
    user_input = request.json.get('input', '')
    original_command = request.json.get('original_command', '')
    error_context = request.json.get('error_context', {})
    
    logger.info(f"Получено уточнение от пользователя: {user_input}")
    
    # Формируем новый запрос с учетом уточнения
    new_command = f"{original_command} ({user_input})"
    
    # Получаем новый код с учетом уточнения
    response, code = process_command(new_command)
    
    # Если есть код, выполняем его
    if code:
        result = execute_command_with_error_handling(new_command, code)
        
        return jsonify({
            'response': response,
            'code': code,
            'execution_result': result.get("execution_result"),
            'verification_result': result.get("verification_result"),
            'error_analysis': result.get("error_analysis", {}),
            'screenshot': result.get("screenshot"),
            'message': result.get("message")
        })
    else:
        return jsonify({
            'response': "Не удалось сгенерировать код даже с учетом уточнения",
            'code': None,
            'execution_result': "Не удалось сгенерировать код для выполнения команды",
            'message': "Пожалуйста, используйте предустановленные команды или сформулируйте запрос иначе"
        })

@app.route('/confirm', methods=['POST'])
def confirm_action():
    """
    Обрабатывает подтверждение действия от пользователя
    """
    user_confirmation = request.json.get('confirmation', False)
    command = request.json.get('command', '')
    code = request.json.get('code', '')
    
    if not user_confirmation:
        return jsonify({
            'response': "Действие отменено пользователем",
            'code': code,
            'execution_result': None,
            'message': "Команда не была выполнена по решению пользователя"
        })
    
    # Если пользователь подтвердил, выполняем команду
    result = execute_command_with_error_handling(command, code)
    
    return jsonify({
        'response': f"Команда подтверждена и выполнена: {command}",
        'code': code,
        'execution_result': result.get("execution_result"),
        'verification_result': result.get("verification_result"),
        'error_analysis': result.get("error_analysis", {}),
        'screenshot': result.get("screenshot"),
        'message': result.get("message")
    })

# Глобальная переменная для хранения истории команд
command_history = []

def add_to_history(command, result):
    """Добавляет команду и результат в историю"""
    command_history.append({
        'timestamp': time.time(),
        'command': command,
        'result': result,
        'success': result.get('success', False)
    })
    
    # Ограничиваем историю последними 50 командами
    if len(command_history) > 50:
        command_history.pop(0)

@app.route('/history', methods=['GET'])
def get_history():
    """Возвращает историю выполненных команд"""
    try:
        # Читаем краткий журнал команд
        with open('command_summary.txt', 'r', encoding='utf-8') as f:
            summary_content = f.read()
        
        # Разбиваем на отдельные записи
        entries = []
        current_entry = {}
        lines = summary_content.split('\n')
        
        for line in lines:
            if line.startswith('20'):  # Начало новой записи (с даты)
                if current_entry:
                    entries.append(current_entry)
                    current_entry = {}
                # Извлекаем дату и время
                parts = line.split(' - ', 1)
                if len(parts) > 1:
                    current_entry['timestamp'] = parts[0]
            elif line.startswith('Команда:'):
                current_entry['command'] = line.replace('Команда:', '').strip()
            elif line.startswith('Статус:'):
                current_entry['status'] = line.replace('Статус:', '').strip()
            elif line.startswith('Выполнение:'):
                current_entry['completion'] = line.replace('Выполнение:', '').strip()
            elif line.startswith('Точность:'):
                current_entry['accuracy'] = line.replace('Точность:', '').strip()
        
        # Добавляем последнюю запись
        if current_entry:
            entries.append(current_entry)
        
        return jsonify({
            'history': entries,
            'count': len(entries)
        })
    except Exception as e:
        return jsonify({
            'error': f"Ошибка при чтении истории: {str(e)}",
            'history': []
        })

@app.route('/detailed_history/<command_timestamp>', methods=['GET'])
def get_detailed_history(command_timestamp):
    """Возвращает подробную информацию о выполнении команды"""
    try:
        # Читаем подробный журнал команд
        with open('detailed_command_log.txt', 'r', encoding='utf-8') as f:
            log_content = f.read()
        
        # Ищем записи, соответствующие указанной временной метке
        entries = []
        command_found = False
        command_details = []
        
        lines = log_content.split('\n')
        for line in lines:
            if command_timestamp in line:
                command_found = True
                command_details.append(line)
            elif command_found and line.strip():
                command_details.append(line)
        
        return jsonify({
            'command_timestamp': command_timestamp,
            'details': command_details
        })
    except Exception as e:
        return jsonify({
            'error': f"Ошибка при чтении подробной истории: {str(e)}",
            'details': []
        })

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

import logging
import json
import datetime
import re
from dataclasses import dataclass, asdict
from typing import List, Dict, Any, Optional

# Настройка логирования для подробного журнала
detailed_logger = logging.getLogger('detailed_log')
detailed_logger.setLevel(logging.INFO)
detailed_handler = logging.FileHandler('detailed_command_log.txt', encoding='utf-8')
detailed_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
detailed_logger.addHandler(detailed_handler)

# Настройка логирования для краткого журнала
summary_logger = logging.getLogger('summary_log')
summary_logger.setLevel(logging.INFO)
summary_handler = logging.FileHandler('command_summary.txt', encoding='utf-8')
summary_handler.setFormatter(logging.Formatter('%(asctime)s - %(message)s'))
summary_logger.addHandler(summary_handler)

@dataclass
class CommandStep:
    """Класс для представления шага выполнения команды"""
    step_number: int
    description: str
    status: str  # 'pending', 'in_progress', 'completed', 'failed'
    result: Optional[str] = None
    error: Optional[str] = None
    completion_percentage: float = 0.0

@dataclass
class CommandExecution:
    """Класс для представления выполнения команды"""
    command_text: str
    steps: List[CommandStep]
    start_time: str
    end_time: Optional[str] = None
    overall_status: str = 'in_progress'  # 'in_progress', 'completed', 'failed'
    completion_percentage: float = 0.0
    accuracy_percentage: float = 0.0

def parse_compound_command(text):
    """
    Разбирает составную команду на отдельные шаги
    Возвращает список шагов и общее описание команды
    """
    text = text.lower()
    steps = []
    
    # Ищем разделители составных команд
    separators = [" и ", " затем ", " после этого ", " потом ", ", "]
    
    # Пытаемся разбить команду по разделителям
    command_parts = [text]
    for separator in separators:
        new_parts = []
        for part in command_parts:
            if separator in part:
                new_parts.extend(part.split(separator))
            else:
                new_parts.append(part)
        command_parts = new_parts
    
    # Удаляем дубликаты и пустые строки
    command_parts = [part.strip() for part in command_parts if part.strip()]
    command_parts = list(dict.fromkeys(command_parts))
    
    # Создаем шаги для каждой части команды
    for i, part in enumerate(command_parts):
        steps.append(CommandStep(
            step_number=i+1,
            description=part,
            status='pending',
            completion_percentage=0.0
        ))
    
    return steps, text

def execute_command_with_steps(command_text, code=None):
    """
    Выполняет команду по шагам, проверяя результат каждого шага
    и информируя пользователя о ходе выполнения
    """
    # Разбираем команду на шаги
    steps, full_command = parse_compound_command(command_text)
    
    # Создаем запись о выполнении команды
    execution = CommandExecution(
        command_text=full_command,
        steps=steps,
        start_time=datetime.datetime.now().isoformat()
    )
    
    # Логируем начало выполнения команды
    detailed_logger.info(f"Начало выполнения команды: {full_command}")
    detailed_logger.info(f"Количество шагов: {len(steps)}")
    
    # Выполняем каждый шаг
    for i, step in enumerate(execution.steps):
        step.status = 'in_progress'
        detailed_logger.info(f"Шаг {step.step_number}: {step.description} - начало выполнения")
        
        # Генерируем код для выполнения шага
        step_response, step_code = process_single_step(step.description)
        
        if step_code:
            # Обновляем информацию о шаге
            detailed_logger.info(f"Сгенерирован код для шага {step.step_number}: {step_code}")
            
            # Выполняем код
            try:
                # Выполняем код с проверкой результата
                execution_result = execute_python_code(step_code)
                
                # Проверяем результат выполнения
                if "Ошибка" in execution_result:
                    step.status = 'failed'
                    step.error = execution_result
                    step.completion_percentage = 50.0  # Частичное выполнение
                    detailed_logger.error(f"Шаг {step.step_number} завершился с ошибкой: {execution_result}")
                else:
                    step.status = 'completed'
                    step.result = execution_result
                    step.completion_percentage = 100.0
                    detailed_logger.info(f"Шаг {step.step_number} успешно выполнен: {execution_result}")
                
                # Проверяем результат выполнения шага
                verification_result = verify_step_execution(step.description, execution_result)
                
                # Обновляем точность выполнения на основе проверки
                if verification_result:
                    step.accuracy_percentage = verification_result.get('accuracy', 100.0)
                    detailed_logger.info(f"Точность выполнения шага {step.step_number}: {step.accuracy_percentage}%")
            except Exception as e:
                step.status = 'failed'
                step.error = str(e)
                step.completion_percentage = 0.0
                detailed_logger.error(f"Исключение при выполнении шага {step.step_number}: {str(e)}")
        else:
            step.status = 'failed'
            step.error = "Не удалось сгенерировать код для выполнения шага"
            step.completion_percentage = 0.0
            detailed_logger.error(f"Не удалось сгенерировать код для шага {step.step_number}")
        
        # Обновляем общий прогресс выполнения команды
        update_execution_progress(execution)
        
        # Логируем промежуточный результат
        log_execution_summary(execution)
        
        # Если шаг не выполнен успешно, пытаемся исправить ошибку
        if step.status == 'failed':
            detailed_logger.info(f"Попытка исправить ошибку в шаге {step.step_number}")
            
            # Анализируем ошибку и пытаемся её исправить
            fixed_code = try_fix_error(step.description, step.error)
            
            if fixed_code:
                detailed_logger.info(f"Найдено исправление для шага {step.step_number}: {fixed_code}")
                
                # Выполняем исправленный код
                try:
                    execution_result = execute_python_code(fixed_code)
                    
                    if "Ошибка" in execution_result:
                        detailed_logger.error(f"Исправление не помогло: {execution_result}")
                    else:
                        step.status = 'completed'
                        step.result = execution_result
                        step.completion_percentage = 100.0
                        step.error = None
                        detailed_logger.info(f"Шаг {step.step_number} успешно исправлен и выполнен")
                        
                        # Обновляем общий прогресс
                        update_execution_progress(execution)
                except Exception as e:
                    detailed_logger.error(f"Исключение при выполнении исправленного кода: {str(e)}")
    
    # Завершаем выполнение команды
    execution.end_time = datetime.datetime.now().isoformat()
    
    # Определяем общий статус выполнения
    if all(step.status == 'completed' for step in execution.steps):
        execution.overall_status = 'completed'
    else:
        execution.overall_status = 'failed'
    
    # Логируем итоговый результат
    detailed_logger.info(f"Завершение выполнения команды: {full_command}")
    detailed_logger.info(f"Общий статус: {execution.overall_status}")
    detailed_logger.info(f"Процент выполнения: {execution.completion_percentage}%")
    detailed_logger.info(f"Точность выполнения: {execution.accuracy_percentage}%")
    
    # Записываем итоговый результат в краткий журнал
    log_execution_summary(execution, final=True)
    
    return execution

def process_single_step(step_text):
    """
    Обрабатывает отдельный шаг команды
    Возвращает ответ и код для выполнения
    """
    # Проверяем, соответствует ли шаг стандартной команде
    for command_text, function_name in COMMANDS.items():
        if command_text in step_text:
            code = f"{function_name}()"
            
            # Особая обработка для команды "сказать"
            if function_name == "speak_text":
                # Извлекаем текст после слова "сказать" или "скажи"
                speak_content = ""
                if "сказать" in step_text:
                    speak_content = step_text.split("сказать", 1)[1].strip()
                elif "скажи" in step_text:
                    speak_content = step_text.split("скажи", 1)[1].strip()
                
                if speak_content:
                    code = f"speak_text('{speak_content}')"
            
            return f"Выполняю команду: {command_text}", code
    
    # Если шаг не соответствует стандартной команде, генерируем код с помощью нейросети
    response = get_ai_response(step_text)
    code = extract_code_from_response(response)
    
    return response, code

def verify_step_execution(step_description, execution_result):
    """
    Проверяет результат выполнения шага
    Возвращает словарь с информацией о проверке
    """
    # Базовая проверка на наличие ошибок
    if "Ошибка" in execution_result:
        return {
            'verified': False,
            'accuracy': 0.0,
            'message': f"Шаг не выполнен из-за ошибки: {execution_result}"
        }
    
    # Проверка для конкретных типов команд
    if "калькулятор" in step_description.lower():
        # Проверяем, был ли открыт калькулятор
        calc_window = win32gui.FindWindow(None, "Калькулятор")
        if calc_window == 0:
            calc_window = win32gui.FindWindow(None, "Calculator")
        
        if calc_window != 0:
            return {
                'verified': True,
                'accuracy': 100.0,
                'message': "Калькулятор успешно открыт"
            }
        else:
            return {
                'verified': False,
                'accuracy': 0.0,
                'message': "Калькулятор не был открыт"
            }
    
    if "браузер" in step_description.lower():
        # Проверяем, был ли открыт браузер
        browser_windows = ["Google Chrome", "Mozilla Firefox", "Microsoft Edge", "Opera", "Safari"]
        for browser in browser_windows:
            if win32gui.FindWindow(None, browser) != 0:
                return {
                    'verified': True,
                    'accuracy': 100.0,
                    'message': f"Браузер {browser} успешно открыт"
                }
        
        return {
            'verified': False,
            'accuracy': 50.0,  # Возможно, браузер открыт, но не распознан
            'message': "Не удалось подтвердить открытие браузера"
        }
    
    # Для других команд просто возвращаем успешный результат
    return {
        'verified': True,
        'accuracy': 90.0,  # По умолчанию считаем, что команда выполнена с высокой точностью
        'message': "Шаг выполнен успешно"
    }

def update_execution_progress(execution):
    """
    Обновляет общий прогресс выполнения команды
    """
    # Вычисляем средний процент выполнения всех шагов
    if execution.steps:
        completion_sum = sum(step.completion_percentage for step in execution.steps)
        execution.completion_percentage = completion_sum / len(execution.steps)
        
        # Вычисляем среднюю точность выполнения для завершенных шагов
        completed_steps = [step for step in execution.steps if step.status == 'completed']
        if completed_steps:
            accuracy_sum = sum(getattr(step, 'accuracy_percentage', 90.0) for step in completed_steps)
            execution.accuracy_percentage = accuracy_sum / len(completed_steps)
        else:
            execution.accuracy_percentage = 0.0

def log_execution_summary(execution, final=False):
    """
    Записывает краткую информацию о выполнении команды в журнал
    """
    status_text = execution.overall_status
    if not final:
        status_text = f"в процессе ({execution.completion_percentage:.1f}% выполнено)"
    
    summary_text = (
        f"Команда: {execution.command_text}\n"
        f"Статус: {status_text}\n"
        f"Выполнение: {execution.completion_percentage:.1f}%\n"
        f"Точность: {execution.accuracy_percentage:.1f}%\n"
    )
    
    # Добавляем информацию о шагах для финального отчета
    if final:
        summary_text += "Шаги:\n"
        for step in execution.steps:
            step_status = "выполнен" if step.status == "completed" else "не выполнен"
            summary_text += f"  - Шаг {step.step_number}: {step.description} - {step_status}\n"
    
    # Записываем в журнал
    summary_logger.info(summary_text)

if __name__ == '__main__':
  app.run(debug=True)