#!/usr/bin/env python3
"""Скрипт для исправления проблемы с токеном HuggingFace"""

import os
import sys
from pathlib import Path

import requests
from dotenv import load_dotenv


def main():
    print("🔧 Исправление проблемы с токеном HuggingFace...")

    # Загружаем .env файл
    env_path = Path(".env")
    if not env_path.exists():
        print("❌ Файл .env не найден!")
        return False

    print("📄 Загружаем .env файл...")
    load_dotenv(env_path)

    # Проверяем токен
    token = os.getenv("HUGGINGFACE_TOKEN")
    if not token:
        print("❌ HUGGINGFACE_TOKEN не найден в .env файле")
        return False

    print(f"✅ Токен найден, длина: {len(token)}")

    # Проверяем валидность токена
    try:
        print("🌐 Проверяем валидность токена...")
        headers = {"Authorization": f"Bearer {token}"}
        response = requests.get("https://huggingface.co/api/whoami", headers=headers, timeout=10)

        if response.status_code == 200:
            data = response.json()
            print(f"✅ Токен валиден! Пользователь: {data.get('name', 'Unknown')}")

            # Обновляем переменную окружения для текущей сессии
            os.environ["HUGGINGFACE_TOKEN"] = token
            print("✅ Токен установлен в переменную окружения")

            return True
        else:
            print(f"❌ Токен невалиден! Статус: {response.status_code}")
            print(f"Ответ: {response.text[:200]}")
            return False

    except Exception as e:
        print(f"❌ Ошибка при проверке токена: {e}")
        return False


if __name__ == "__main__":
    success = main()
    if success:
        print("\n🎉 Токен исправлен! Теперь можно тестировать AI.")
    else:
        print("\n❌ Не удалось исправить проблему с токеном.")
