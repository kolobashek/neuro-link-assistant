import os

import requests
from dotenv import load_dotenv

from config import Config

load_dotenv()


def test_manual_request():
    """Тест как в документации (рабочий)"""
    token = os.getenv("HUGGINGFACE_TOKEN")

    headers = {"Authorization": f"Bearer {token}"}
    payload = {
        "messages": [{"role": "user", "content": "Test manual"}],
        "model": "deepseek/deepseek-v3-0324",
        "stream": False,
    }

    response = requests.post(
        "https://router.huggingface.co/novita/v3/openai/chat/completions",
        headers=headers,
        json=payload,
        timeout=30,
    )

    print("=== РУЧНОЙ ЗАПРОС ===")
    print(f"Статус: {response.status_code}")
    print(f"Config токен: {Config.HUGGINGFACE_TOKEN[:10]}...")
    print(f"Ручной токен: {token[:10]}...")
    print(f"Токены равны: {Config.HUGGINGFACE_TOKEN == token}")

    if response.status_code == 200:
        result = response.json()
        print("✅ Успех:", result["choices"][0]["message"]["content"][:100])
    else:
        print("❌ Ошибка:", response.text[:200])


def test_config_request():
    """Тест через Config (не рабочий?)"""
    api_key = Config.HUGGINGFACE_TOKEN

    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}

    payload = {
        "messages": [{"role": "user", "content": "Test config"}],
        "model": "deepseek/deepseek-v3-0324",
        "stream": False,
    }

    response = requests.post(
        "https://router.huggingface.co/novita/v3/openai/chat/completions",
        headers=headers,
        json=payload,
        timeout=30,
    )

    print("\n=== ЗАПРОС ЧЕРЕЗ CONFIG ===")
    print(f"Статус: {response.status_code}")
    print(f"Токен из Config: {api_key[:10] if api_key else 'НЕТ'}...")

    if response.status_code == 200:
        result = response.json()
        print("✅ Успех:", result["choices"][0]["message"]["content"][:100])
    else:
        print("❌ Ошибка:", response.text[:200])


if __name__ == "__main__":
    test_manual_request()
    test_config_request()
