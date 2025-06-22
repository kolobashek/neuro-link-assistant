#!/usr/bin/env python3
"""Тест подключения к HuggingFace API"""

import os
import sys

sys.path.append(".")

from services.ai_service import check_ai_model_availability, get_ai_models
from services.huggingface_service import HuggingFaceService


def test_huggingface_connection():
    """Тестируем подключение к HuggingFace"""
    print("🤖 Тестирование HuggingFace подключения...")

    # Инициализируем сервис
    hf_service = HuggingFaceService()

    # Проверяем токен
    if hf_service.token:
        print(f"✅ Токен HuggingFace найден: {hf_service.token[:10]}...")
    else:
        print("❌ Токен HuggingFace не найден!")
        return False

    # Проверяем доступность простой модели
    try:
        print("🔍 Проверяем доступность модели microsoft/DialoGPT-medium...")
        availability = hf_service.check_model_availability("microsoft/DialoGPT-medium")

        if availability["available"]:
            print("✅ Модель доступна!")
            print(f"   - Имя: {availability['model_name']}")
            print(f"   - Автор: {availability['author']}")
            return True
        else:
            print(f"❌ Модель недоступна: {availability.get('error')}")
            return False

    except Exception as e:
        print(f"❌ Ошибка при проверке: {e}")
        return False


def test_ai_models_file():
    """Тестируем файл с AI моделями"""
    print("\n📋 Проверяем файл с AI моделями...")

    try:
        models = get_ai_models()
        if "error" in models:
            print(f"❌ Ошибка: {models['error']}")
            return False

        models_list = models.get("models", [])
        print(f"✅ Найдено {len(models_list)} моделей:")

        for model in models_list:
            status = "🟢" if model.get("status") == "ready" else "🔴"
            current = "⭐" if model.get("is_current") else "  "
            print(f"   {status}{current} {model['name']} ({model['id']})")

        return True

    except Exception as e:
        print(f"❌ Ошибка при чтении моделей: {e}")
        return False


def test_simple_request():
    """Тестируем простой запрос к AI"""
    print("\n🧠 Тестируем простой AI запрос...")

    try:
        # Используем текущую модель из файла
        from services.ai_service import get_current_ai_model

        current_model = get_current_ai_model()
        if not current_model:
            print("❌ Текущая модель не найдена")
            return False

        test_model_id = current_model["id"]
        print(f"🎯 Используем модель: {current_model['name']} ({test_model_id})")

        # Проверяем доступность модели
        availability_result = check_ai_model_availability(test_model_id)

        if availability_result.get("success"):
            print(f"✅ Модель {test_model_id} доступна для тестирования")

            # Пробуем простой запрос
            from services.ai_service import generate_text

            print("📝 Отправляем тестовый запрос...")
            response = generate_text(
                "Hello, how are you today?", max_length=50, model_id=test_model_id
            )

            if response and not response.startswith("Ошибка"):
                print(f"✅ Получен ответ: {response[:100]}...")
                return True
            else:
                print(f"❌ Ошибка в ответе: {response}")
                return False
        else:
            print(f"❌ Модель недоступна: {availability_result.get('message')}")

            # Попробуем добавить простую модель
            print("🔄 Попробуем добавить простую тестовую модель...")
            return add_simple_test_model()

    except Exception as e:
        print(f"❌ Ошибка при тестовом запросе: {e}")
        return False


def add_simple_test_model():
    """Добавляем простую тестовую модель"""
    try:
        from services.ai_service import add_model

        # Добавляем DistilGPT-2 как простую тестовую модель
        model_data = {
            "id": "distilgpt2-test",
            "name": "DistilGPT-2 (Test)",
            "description": "Легкая модель для тестирования",
            "huggingface_id": "distilgpt2",
            "type": "completion",
        }

        result = add_model(model_data)
        if result.get("success"):
            print(f"✅ Тестовая модель добавлена: {model_data['name']}")

            # Выбираем её как текущую
            from services.ai_service import select_ai_model

            select_result = select_ai_model("distilgpt2-test")

            if select_result.get("success"):
                print("✅ Тестовая модель выбрана как текущая")

                # Теперь пробуем запрос
                from services.ai_service import generate_text

                response = generate_text("Hello!", max_length=30, model_id="distilgpt2-test")

                if response and not response.startswith("Ошибка"):
                    print(f"✅ Тестовый запрос успешен: {response[:100]}...")
                    return True
                else:
                    print(f"❌ Ошибка в тестовом запросе: {response}")
                    return False
            else:
                print(f"❌ Ошибка выбора модели: {select_result.get('message')}")
                return False
        else:
            print(f"❌ Ошибка добавления модели: {result.get('message')}")
            return False

    except Exception as e:
        print(f"❌ Ошибка при добавлении тестовой модели: {e}")
        return False


if __name__ == "__main__":
    print("🚀 Начинаем тестирование AI интеграции...\n")

    # Тест 1: HuggingFace подключение
    hf_ok = test_huggingface_connection()

    # Тест 2: AI модели файл
    models_ok = test_ai_models_file()

    # Тест 3: Простой AI запрос (только если первые два прошли)
    request_ok = False
    if hf_ok and models_ok:
        request_ok = test_simple_request()

    print(f"\n📊 Результаты тестирования:")
    print(f"   HuggingFace API: {'✅' if hf_ok else '❌'}")
    print(f"   AI модели файл: {'✅' if models_ok else '❌'}")
    print(f"   Простой запрос: {'✅' if request_ok else '❌'}")

    if hf_ok and models_ok and request_ok:
        print("\n🎉 AI интеграция полностью работает!")
        print("Готово к интеграции с UI!")
    elif hf_ok and models_ok:
        print("\n⚡ Базовая настройка готова, нужно протестировать запросы")
    else:
        print("\n⚠️  Требуется настройка AI компонентов")
