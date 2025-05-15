import logging
import time
import webbrowser

import pyperclip
from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from commands.system_commands import speak_text

logger = logging.getLogger("neuro_assistant")


def use_browser_automation(
    url, prompt, css_selector_input, css_selector_response, browser_name="DeepSeek"
):
    """
    Общая функция для автоматизации браузера

    Args:
        url: URL сервиса
        prompt: Текст запроса
        css_selector_input: CSS-селектор для поля ввода
        css_selector_response: CSS-селектор для получения ответа
        browser_name: Название сервиса для логирования

    Returns:
        Текст ответа или None в случае ошибки
    """
    try:
        # Инициализация браузера
        options = webdriver.ChromeOptions()
        options.add_argument("--start-maximized")
        driver = webdriver.Chrome(options=options)

        # Открываем сервис
        driver.get(url)

        # Ждем загрузки страницы
        wait = WebDriverWait(driver, 10)

        try:
            # Находим поле ввода
            input_field = wait.until(
                EC.presence_of_element_located((By.CSS_SELECTOR, css_selector_input))
            )

            # Вставляем запрос
            input_field.send_keys(prompt)
            input_field.send_keys(Keys.RETURN)

            # Ждем ответа
            wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, css_selector_response)))

            # Даем время для полной загрузки ответа
            time.sleep(2)

            # Получаем ответ
            response_elements = driver.find_elements(By.CSS_SELECTOR, css_selector_response)
            full_response = "\n".join([elem.text for elem in response_elements])

            driver.quit()
            return full_response

        except TimeoutException:
            logger.warning(f"{browser_name} требует авторизации или не отвечает")
            driver.quit()
            return None

    except Exception as e:
        logger.error(f"Ошибка при использовании {browser_name}: {str(e)}")
        try:
            driver.quit()
        except Exception:
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
    speak_text(
        "Открыт браузер с DeepSeek. Запрос скопирован в буфер обмена. Вставьте его и получите ответ."
    )

    return "Открыт браузер с DeepSeek. Запрос скопирован в буфер обмена. Пожалуйста, вставьте его и получите ответ."
