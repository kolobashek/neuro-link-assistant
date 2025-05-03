import os
import requests
import logging
from config import Config
from services.browser_service import use_browser_automation, fallback_browser_method

logger = logging.getLogger('neuro_assistant')

def get_ai_response(text, service="huggingface"):
    """
    Получение ответа от нейросети через различные сервисы
    
    Args:
        text: Текст запроса
        service: Сервис для использования (huggingface, deepseek, lmarena)
    
    Returns:
        Ответ от сервиса
    """
    prompt = f"""Напиши Python код для выполнения следующей команды на Windows: "{text}".
    Используй доступные библиотеки: pyautogui, os, win32gui, win32con, pyttsx3.
    Оформи код в формате Python между тройными обратными кавычками с указанием языка python.
    Примеры доступных функций:
    - pyautogui.hotkey('win', 'd') - нажатие комбинации клавиш
    - os.system("start notepad") - запуск программы
    - pyautogui.press('volumeup') - нажатие на кнопку
    - pyautogui.screenshot('filename.png') - создание скриншота
    """
    
    if service == "huggingface":
        try:
            logger.info("Попытка использования HuggingFace API")
            API_URL = "https://api-inference.huggingface.co/models/meta-llama/Llama-2-70b-chat-hf"
            headers = {"Authorization": f"Bearer {Config.HUGGINGFACE_API_KEY}"}
            
            payload = {"inputs": prompt, "parameters": {"max_length": 512, "temperature": 0.7}}
            response = requests.post(API_URL, headers=headers, json=payload, timeout=10)
            
            if response.status_code == 200:
                logger.info("Успешный ответ от HuggingFace API")
                return response.json()[0]["generated_text"]
            else:
                logger.warning(f"HuggingFace API недоступно (код {response.status_code})")
                return get_ai_response(text, "deepseek")
        except Exception as e:
            logger.error(f"Ошибка при обращении к HuggingFace API: {str(e)}")
            return get_ai_response(text, "deepseek")
    
    elif service == "deepseek":
        logger.info("Попытка использования DeepSeek через браузер")
        result = use_browser_automation(
            url="https://chat.deepseek.com/",
            prompt=prompt,
            css_selector_input="textarea[placeholder*='Send a message']",
            css_selector_response=".markdown-body p, .markdown-body pre",
            browser_name="DeepSeek"
        )
        
        if result:
            logger.info("Успешно получен ответ от DeepSeek")
            return result
        else:
            logger.info("DeepSeek не сработал. Попытка использования LM Arena")
            return get_ai_response(text, "lmarena")
    
    elif service == "lmarena":
        logger.info("Попытка использования LM Arena")
        result = use_browser_automation(
            url="https://lmarena.ai/",
            prompt=prompt,
            css_selector_input="textarea[placeholder*='Send a message']",
            css_selector_response=".message-content p, .message-content pre",
            browser_name="LM Arena"
        )
        
        if result:
            logger.info("Успешно получен ответ от LM Arena")
            return result
        else:
            return fallback_browser_method(text)
    
    else:
        return "Неизвестный сервис AI. Пожалуйста, используйте предустановленные команды."