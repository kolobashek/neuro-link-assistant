import requests
import os
import json
import time
import logging
import traceback
from config import Config
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
import webbrowser
import pyperclip

# Настройка логирования
logger = logging.getLogger('neuro_assistant')

# Глобальная переменная для хранения информации о нейросетях
AI_MODELS = [
    {
        'id': 'huggingface',
        'name': 'HuggingFace API',
        'method': 'api',
        'status': 'unknown',
        'error_message': None,
        'priority': 1,
        'url': 'https://api-inference.huggingface.co/models/meta-llama/Llama-2-70b-chat-hf'
    },
    {
        'id': 'deepseek',
        'name': 'DeepSeek Chat',
        'method': 'browser',
        'status': 'unknown',
        'error_message': None,
        'priority': 2,
        'url': 'https://chat.deepseek.com/'
    },
    {
        'id': 'lmarena',
        'name': 'LM Arena',
        'method': 'browser',
        'status': 'unknown',
        'error_message': None,
        'priority': 3,
        'url': 'https://lmarena.ai/'
    }
]

# Текущая модель (по умолчанию - первая в списке)
current_ai_model = AI_MODELS[0]

def get_ai_models():
    """Возвращает список доступных нейросетей"""
    return AI_MODELS

def get_current_ai_model():
    """Возвращает текущую нейросеть"""
    return current_ai_model

def set_ai_model_status(model_id, status, error_message=None):
    """Устанавливает статус нейросети"""
    global AI_MODELS
    
    for model in AI_MODELS:
        if model['id'] == model_id:
            model['status'] = status
            model['error_message'] = error_message
            break

def get_ai_response(text):
    """Получение ответа от нейросети через различные сервисы"""
    global current_ai_model
    
    # Пробуем получить ответ от текущей нейросети
    try:
        logger.info(f"Попытка использования {current_ai_model['name']}")
        
        if current_ai_model['method'] == 'api':
            response = get_api_response(current_ai_model, text)
        elif current_ai_model['method'] == 'browser':
            response = get_browser_response(current_ai_model, text)
        else:
            logger.error(f"Неизвестный метод: {current_ai_model['method']}")
            response = None
        
        # Если получили ответ, возвращаем его
        if response:
            set_ai_model_status(current_ai_model['id'], 'ready')
            return response
        
        # Если не получили ответ, пробуем другие нейросети
        logger.warning(f"Не удалось получить ответ от {current_ai_model['name']}. Пробуем альтернативные методы.")
        set_ai_model_status(current_ai_model['id'], 'unavailable')
        
    except Exception as e:
        logger.error(f"Ошибка при обращении к {current_ai_model['name']}: {str(e)}")
        set_ai_model_status(current_ai_model['id'], 'error', str(e))
    
    # Пробуем другие нейросети в порядке приоритета
    for model in sorted(AI_MODELS, key=lambda x: x['priority']):
        # Пропускаем текущую модель и недоступные модели
        if model['id'] == current_ai_model['id'] or model['status'] in ['unavailable', 'error']:
            continue
        
        try:
            logger.info(f"Попытка использования альтернативной нейросети: {model['name']}")
            
            if model['method'] == 'api':
                response = get_api_response(model, text)
            elif model['method'] == 'browser':
                response = get_browser_response(model, text)
            else:
                logger.error(f"Неизвестный метод: {model['method']}")
                response = None
            
            # Если получили ответ, возвращаем его
            if response:
                set_ai_model_status(model['id'], 'ready')
                # Устанавливаем эту модель как текущую
                current_ai_model = model
                return response
                
        except Exception as e:
            logger.error(f"Ошибка при обращении к {model['name']}: {str(e)}")
            set_ai_model_status(model['id'], 'error', str(e))
    
    # Если ни одна нейросеть не сработала, используем запасной вариант
    logger.warning("Все нейросети недоступны. Использование запасного варианта.")
    return fallback_browser_method(text)

def get_api_response(model, text):
    """Получение ответа от нейросети через API"""
    if model['id'] == 'huggingface':
        API_URL = model['url']
        headers = {"Authorization": f"Bearer {os.getenv('HUGGINGFACE_API_KEY', '')}"}
        
        prompt = f"""Напиши Python код для выполнения следующей команды на Windows: "{text}".
        Используй доступные библиотеки: pyautogui, os, win32gui, win32con, pyttsx3.
        Оформи код в формате Python между тройными обратными кавычками с указанием языка python.
        Примеры доступных функций:
        - pyautogui.hotkey('win', 'd') - нажатие комбинации клавиш
        - os.system("start notepad") - запуск программы
        - pyautogui.press('volumeup') - нажатие на кнопку
        - pyautogui.screenshot('filename.png') - создание скриншота
        """
        
        payload = {
            "inputs": prompt,
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
            logger.warning(f"HuggingFace API недоступно (код {response.status_code})")
            return None
    
    # Для других API можно добавить здесь
    
    return None

def get_browser_response(model, text):
    """Получение ответа от нейросети через браузер"""
    if model['id'] == 'deepseek':
        return use_deepseek(text)
    elif model['id'] == 'lmarena':
        return use_lm_arena(text)
    
    return None

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
    from commands.system_commands import speak_text
    speak_text("Открыт браузер с DeepSeek. Запрос скопирован в буфер обмена. Вставьте его и получите ответ.")
    
    return "Открыт браузер с DeepSeek. Запрос скопирован в буфер обмена. Пожалуйста, вставьте его и получите ответ."

def check_ai_model_availability(model_id=None):
    """
    Проверяет доступность нейросети
    
    Args:
        model_id: ID нейросети для проверки. Если None, проверяются все нейросети.
        
    Returns:
        Словарь с результатами проверки
    """
    global AI_MODELS
    
    results = {
        'checked_at': time.time(),
        'models': []
    }
    
    # Определяем, какие модели проверять
    models_to_check = []
    if model_id:
        # Проверяем только указанную модель
        for model in AI_MODELS:
            if model['id'] == model_id:
                models_to_check.append(model)
                break
    else:
        # Проверяем все модели
        models_to_check = AI_MODELS
    
    # Проверяем каждую модель
    for model in models_to_check:
        logger.info(f"Проверка доступности нейросети: {model['name']}")
        
        result = {
            'id': model['id'],
            'name': model['name'],
            'available': False,
            'response_time': None,
            'error': None
        }
        
        start_time = time.time()
        
        try:
            # Проверяем в зависимости от метода
            if model['method'] == 'api':
                available = check_api_model_availability(model)
            elif model['method'] == 'browser':
                available = check_browser_model_availability(model)
            else:
                available = False
                result['error'] = f"Неизвестный метод: {model['method']}"
            
            result['available'] = available
            
            # Если модель доступна, обновляем её статус
            if available:
                set_ai_model_status(model['id'], 'ready')
            else:
                set_ai_model_status(model['id'], 'unavailable')
                
        except Exception as e:
            result['available'] = False
            result['error'] = str(e)
            set_ai_model_status(model['id'], 'error', str(e))
            logger.error(f"Ошибка при проверке нейросети {model['name']}: {str(e)}")
        
        # Вычисляем время ответа
        result['response_time'] = time.time() - start_time
        
        results['models'].append(result)
    
    return results

def check_api_model_availability(model):
    """Проверяет доступность API-модели"""
    if model['id'] == 'huggingface':
        API_URL = model['url']
        headers = {"Authorization": f"Bearer {os.getenv('HUGGINGFACE_API_KEY', '')}"}
        
        try:
            # Отправляем простой запрос для проверки доступности
            response = requests.get(API_URL, headers=headers, timeout=5)
            
            # Проверяем код ответа
            if response.status_code in [200, 401, 403]:  # Даже если нет доступа, API работает
                return True
            else:
                logger.warning(f"HuggingFace API недоступно (код {response.status_code})")
                return False
                
        except Exception as e:
            logger.error(f"Ошибка при проверке HuggingFace API: {str(e)}")
            return False
    
    # По умолчанию считаем недоступным
    return False

def check_browser_model_availability(model):
    """Проверяет доступность браузерной модели"""
    # Для браузерных моделей просто проверяем доступность сайта
    if model['id'] in ['deepseek', 'lmarena']:
        url = model.get('url', '')
        if not url:
            return False
        
        try:
            # Проверяем доступность сайта
            response = requests.get(url, timeout=5)
            return response.status_code == 200
        except Exception as e:
            logger.error(f"Ошибка при проверке доступности {url}: {str(e)}")
            return False
    
    # По умолчанию считаем недоступным
    return False

def select_ai_model(model_id):
    """
    Выбирает нейросеть для использования
    
    Args:
        model_id: ID нейросети для использования
        
    Returns:
        Словарь с результатом операции
    """
    global AI_MODELS, current_ai_model
    
    for model in AI_MODELS:
        if model['id'] == model_id:
            # Проверяем, доступна ли модель
            if model['status'] == 'unavailable':
                return {
                    'success': False,
                    'message': f"Нейросеть {model['name']} недоступна"
                }
            
            # Устанавливаем модель как текущую
            current_ai_model = model
            logger.info(f"Выбрана нейросеть: {model['name']}")
            
            return {
                'success': True,
                'message': f"Выбрана нейросеть: {model['name']}"
            }
    
    return {
        'success': False,
        'message': f"Нейросеть с ID {model_id} не найдена"
    }