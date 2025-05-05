import os
import json
import logging
from config import Config
from services.huggingface_service import HuggingFaceService
from huggingface_hub import HfApi

logger = logging.getLogger('neuro_assistant')

# Инициализируем сервис Hugging Face
hf_service = HuggingFaceService()

# Путь к файлу с информацией о моделях
MODELS_INFO_FILE = os.path.join(Config.DATA_DIR, 'ai_models.json')

def get_ai_models():
    """
    Получает список доступных AI-моделей
    
    Returns:
        Словарь с информацией о моделях
    """
    try:
        # Проверяем существование файла с информацией о моделях
        if not os.path.exists(MODELS_INFO_FILE):
            # Если файла нет, создаем его с базовыми моделями
            create_default_models_file()
        
        # Читаем информацию о моделях из файла
        with open(MODELS_INFO_FILE, 'r', encoding='utf-8') as f:
            models_data = json.load(f)
        
        # Получаем текущую модель
        current_model = get_current_ai_model()
        
        # Обновляем статус "текущая модель"
        for model in models_data.get('models', []):
            model['is_current'] = (current_model and model['id'] == current_model['id'])
        
        return models_data
    except Exception as e:
        logger.error(f"Ошибка при получении списка AI-моделей: {str(e)}")
        return {'error': f"Ошибка при получении списка AI-моделей: {str(e)}", 'models': []}

def get_current_ai_model():
    """
    Получает информацию о текущей выбранной AI-модели
    
    Returns:
        Словарь с информацией о текущей модели или None
    """
    try:
        # Проверяем существование файла с информацией о моделях
        if not os.path.exists(MODELS_INFO_FILE):
            return None
        
        # Читаем информацию о моделях из файла
        with open(MODELS_INFO_FILE, 'r', encoding='utf-8') as f:
            models_data = json.load(f)
        
        # Ищем текущую модель
        for model in models_data.get('models', []):
            if model.get('is_current', False):
                return model
        
        return None
    except Exception as e:
        logger.error(f"Ошибка при получении текущей AI-модели: {str(e)}")
        return None

def check_ai_model_availability(model_id=None):
    """

    Проверяет доступность нейросетей
    
    Args:

        model_id: ID конкретной модели для проверки (опционально)
        
    Returns:

        dict: Результат проверки
    """
    try:
        # Получаем список моделей
        models_data = get_ai_models()
        models = models_data.get("models", [])
        





        # Если указан конкретный ID модели
        if model_id:


            # Находим модель по ID
            model = next((m for m in models if m["id"] == model_id), None)
            
            if not model:

                return {
                    "success": False,
                    "message": f"Модель с ID {model_id} не найдена"
                }
            


            # Проверяем, является ли это моделью OpenAI
            if model.get("api_type") == "openai" or "openai" in model.get("huggingface_id", "").lower():
                # Проверяем наличие API ключа OpenAI
                if not os.environ.get("OPENAI_API_KEY"):
                    model["status"] = "unavailable"
                    model["error"] = "API ключ OpenAI не найден. Установите переменную окружения OPENAI_API_KEY."
                    
                    # Сохраняем обновленный статус
                    save_ai_models(models_data)
                    
                    return {
                        "success": False,
                        "model_name": model["name"],
                        "message": model["error"]
                    }
                
                # Здесь можно добавить тестовый запрос к API OpenAI
                # Для простоты просто отметим модель как доступную
                model["status"] = "ready"
                model["error"] = None
                
                # Сохраняем обновленный статус
                save_ai_models(models_data)
                
                return {
                    "success": True,
                    "model_name": model["name"],
                    "message": f"Модель {model['name']} доступна через API OpenAI"
                }
            












            # Для моделей Hugging Face Hub
            try:
                # Проверяем доступность модели
                from huggingface_hub import model_info
                
                # Получаем информацию о модели
                info = model_info(model["huggingface_id"])
                
                if info:
                    model["status"] = "ready"
                    model["error"] = None
                else:
                    model["status"] = "unavailable"
                    model["error"] = "Модель не найдена на Hugging Face Hub"
                
                # Сохраняем обновленный статус
                save_ai_models(models_data)
                
                return {
                    "success": True,
                    "model_name": model["name"],
                    "message": f"Модель {model['name']} {'доступна' if model['status'] == 'ready' else 'недоступна'}"
                }
            except Exception as e:
                model["status"] = "unavailable"
                model["error"] = str(e)
                
                # Сохраняем обновленный статус
                save_ai_models(models_data)
                
                return {
                    "success": False,
                    "model_name": model["name"],
                    "message": f"Ошибка при проверке модели {model['name']}: {str(e)}"
                }
        
        # Если ID не указан, проверяем все модели
        results = {
            "success": True,
            "message": "Проверка моделей выполнена",
            "models_checked": 0,
            "models_available": 0,
            "models_unavailable": 0
        }
        
        for model in models:
            try:
                # Проверяем модели OpenAI
                if model.get("api_type") == "openai" or "openai" in model.get("huggingface_id", "").lower():
                    if not os.environ.get("OPENAI_API_KEY"):
                        model["status"] = "unavailable"
                        model["error"] = "API ключ OpenAI не найден"
                        results["models_unavailable"] += 1
                    else:
                        model["status"] = "ready"
                        model["error"] = None
                        results["models_available"] += 1
                
                # Проверяем модели Hugging Face Hub
                else:
                    try:
                        from huggingface_hub import model_info
                        
                        # Получаем информацию о модели
                        info = model_info(model["huggingface_id"])
                        
                        if info:
                            model["status"] = "ready"
                            model["error"] = None
                            results["models_available"] += 1
                        else:
                            model["status"] = "unavailable"
                            model["error"] = "Модель не найдена на Hugging Face Hub"
                            results["models_unavailable"] += 1
                    except Exception as e:
                        model["status"] = "unavailable"
                        model["error"] = str(e)
                        results["models_unavailable"] += 1
                
                results["models_checked"] += 1
            except Exception as e:
                logger.error(f"Ошибка при проверке модели {model.get('name', 'unknown')}: {str(e)}")
                model["status"] = "unavailable"
                model["error"] = str(e)
                results["models_unavailable"] += 1
                results["models_checked"] += 1
        
        # Сохраняем обновленный статус
        save_ai_models(models_data)
        
        return results
    except Exception as e:
        logger.error(f"Ошибка при проверке доступности моделей: {str(e)}")
        return {
            "success": False,
            "message": f"Ошибка при проверке доступности моделей: {str(e)}"
        }

def select_ai_model(model_id):
    """
    Выбирает AI-модель для использования
    
    Args:
        model_id: Идентификатор модели
        
    Returns:
        Словарь с результатом операции
    """
    try:
        # Получаем список моделей
        models_data = get_ai_models()
        
        if 'error' in models_data:
            return {'success': False, 'message': models_data['error']}
        
        models = models_data.get('models', [])
        
        # Ищем модель с указанным ID
        model = next((m for m in models if m['id'] == model_id), None)
        
        if not model:
            return {'success': False, 'message': f"Модель с ID {model_id} не найдена"}
        
        # Проверяем доступность модели
        availability = hf_service.check_model_availability(model['huggingface_id'])
        
        if not availability['available']:
            return {
                'success': False, 
                'message': f"Модель {model['name']} недоступна: {availability.get('error', 'Неизвестная ошибка')}"
            }
        
        # Обновляем статус всех моделей
        for m in models:
            m['is_current'] = (m['id'] == model_id)
        
        # Сохраняем обновленную информацию
        models_data['models'] = models
        with open(MODELS_INFO_FILE, 'w', encoding='utf-8') as f:
            json.dump(models_data, f, ensure_ascii=False, indent=2)
        
        # Предзагружаем модель и токенизатор
        try:
            hf_service.load_model(model['huggingface_id'])
            hf_service.load_tokenizer(model['huggingface_id'])
        except Exception as e:
            logger.warning(f"Предзагрузка модели {model['name']} не удалась: {str(e)}")
        
        return {
            'success': True,
            'model_id': model_id,
            'model_name': model['name'],
            'message': f"Модель {model['name']} выбрана для использования"
        }
    except Exception as e:
        logger.error(f"Ошибка при выборе AI-модели: {str(e)}")
        return {'success': False, 'message': f"Ошибка при выборе AI-модели: {str(e)}"}

def update_model_status(model_id, status, error=None):
    """
    Обновляет статус модели в файле конфигурации
    
    Args:
        model_id: Идентификатор модели
        status: Новый статус (ready, busy, error, unavailable)
        error: Сообщение об ошибке (если есть)
    """
    try:
        # Получаем список моделей
        models_data = get_ai_models()
        
        if 'error' in models_data:
            logger.error(f"Ошибка при обновлении статуса модели: {models_data['error']}")
            return
        
        models = models_data.get('models', [])
        
        # Обновляем статус модели
        for model in models:
            if model['id'] == model_id:
                model['status'] = status
                if error:
                    model['error'] = error
                elif 'error' in model:
                    del model['error']
                break
        
        # Сохраняем обновленную информацию
        models_data['models'] = models
        with open(MODELS_INFO_FILE, 'w', encoding='utf-8') as f:
            json.dump(models_data, f, ensure_ascii=False, indent=2)
    except Exception as e:
        logger.error(f"Ошибка при обновлении статуса модели {model_id}: {str(e)}")

def create_default_models_file():
    """
    Создает файл с информацией о моделях по умолчанию
    """
    try:
        # Создаем директорию, если она не существует
        os.makedirs(os.path.dirname(MODELS_INFO_FILE), exist_ok=True)
        
        # Базовый список моделей
        default_models = {
            "models": [
                {
                    "id": "gpt-3.5-turbo",
                    "name": "GPT-3.5 Turbo",
                    "description": "Модель OpenAI GPT-3.5 Turbo (требует API ключ OpenAI)",
                    "huggingface_id": "openai/gpt-3.5-turbo",
                    "type": "chat",
                    "status": "unavailable",
                    "is_current": True,
                    "api_type": "openai"  # Добавляем тип API
                },
                {
                    "id": "llama-2-7b",
                    "name": "Llama 2 (7B)",
                    "description": "Модель Meta Llama 2 (7B параметров)",
                    "huggingface_id": "meta-llama/Llama-2-7b-hf",
                    "type": "completion",
                    "status": "unavailable",
                    "is_current": False
                },
                {
                    "id": "mistral-7b",
                    "name": "Mistral 7B",
                    "description": "Модель Mistral AI (7B параметров)",
                    "huggingface_id": "mistralai/Mistral-7B-v0.1",
                    "type": "completion",
                    "status": "unavailable",
                    "is_current": False
                },
                {
                    "id": "gemma-7b",
                    "name": "Gemma 7B",
                    "description": "Модель Google Gemma (7B параметров)",
                    "huggingface_id": "google/gemma-7b",
                    "type": "completion",
                    "status": "unavailable",
                    "is_current": False
                }
            ]
        }
        
        # Пытаемся получить популярные модели с Hugging Face Hub
        try:
            huggingface_models = get_available_huggingface_models(limit=5)
            
            # Добавляем модели в список, если они не дублируют существующие
            existing_ids = {model["huggingface_id"] for model in default_models["models"]}
            
            for model in huggingface_models:
                if model["huggingface_id"] not in existing_ids:
                    default_models["models"].append(model)
        except Exception as e:
            logger.warning(f"Не удалось получить модели с Hugging Face Hub: {str(e)}")
        
        # Записываем в файл
        with open(MODELS_INFO_FILE, 'w', encoding='utf-8') as f:
            json.dump(default_models, f, ensure_ascii=False, indent=4)
            
        logger.info(f"Создан файл с информацией о моделях: {MODELS_INFO_FILE}")
        return True
    except Exception as e:
        logger.error(f"Ошибка при создании файла с моделями: {str(e)}")
        return False

def generate_text(prompt, max_length=1000, model_id=None):
    """
    Генерирует текст с использованием выбранной модели
    
    Args:
        prompt: Запрос для генерации
        max_length: Максимальная длина генерируемого текста
        model_id: Идентификатор модели (если None, используется текущая)
        
    Returns:
        Сгенерированный текст
    """
    try:
        # Получаем модель
        if model_id:
            # Ищем модель с указанным ID
            models_data = get_ai_models()
            models = models_data.get('models', [])
            model = next((m for m in models if m['id'] == model_id), None)
            
            if not model:
                raise ValueError(f"Модель с ID {model_id} не найдена")
            
            huggingface_id = model['huggingface_id']
        else:
            # Используем текущую модель
            current_model = get_current_ai_model()
            
            if not current_model:
                raise ValueError("Текущая модель не выбрана")
            
            huggingface_id = current_model['huggingface_id']
            model_id = current_model['id']
        
        # Обновляем статус модели
        update_model_status(model_id, 'busy')
        
        try:
            # Загружаем модель и токенизатор
            model = hf_service.load_model(huggingface_id)
            tokenizer = hf_service.load_tokenizer(huggingface_id)
            
            if not model or not tokenizer:
                raise ValueError(f"Не удалось загрузить модель или токенизатор для {huggingface_id}")
            
            # Кодируем запрос
            inputs = tokenizer(prompt, return_tensors="pt", padding=True, truncation=True)
            
            # Генерируем ответ
            outputs = model.generate(
                inputs.input_ids,
                max_length=max_length,
                num_return_sequences=1,
                do_sample=True,
                temperature=0.7,
                top_p=0.9
            )
            
            # Декодируем ответ
            generated_text = tokenizer.decode(outputs[0], skip_special_tokens=True)
            
            # Обновляем статус модели
            update_model_status(model_id, 'ready')
            
            return generated_text
        except Exception as e:
            # В случае ошибки обновляем статус модели
            update_model_status(model_id, 'error', str(e))
            raise
    except Exception as e:
        logger.error(f"Ошибка при генерации текста: {str(e)}")
        return f"Ошибка при генерации текста: {str(e)}"

def generate_chat_response(messages, max_length=1000, model_id=None):
    """
    Генерирует ответ в формате чата с использованием выбранной модели
    
    Args:
        messages: Список сообщений в формате [{"role": "user", "content": "..."}, ...]
        max_length: Максимальная длина генерируемого текста
        model_id: Идентификатор модели (если None, используется текущая)
        
    Returns:
        Сгенерированный ответ
    """
    try:
        # Получаем модель
        if model_id:
            # Ищем модель с указанным ID
            models_data = get_ai_models()
            models = models_data.get('models', [])
            model = next((m for m in models if m['id'] == model_id), None)
            
            if not model:
                raise ValueError(f"Модель с ID {model_id} не найдена")
            
            huggingface_id = model['huggingface_id']
        else:
            # Используем текущую модель
            current_model = get_current_ai_model()
            
            if not current_model:
                raise ValueError("Текущая модель не выбрана")
            
            huggingface_id = current_model['huggingface_id']
            model_id = current_model['id']
        
        # Обновляем статус модели
        update_model_status(model_id, 'busy')
        
        try:
            # Загружаем модель и токенизатор
            model = hf_service.load_model(huggingface_id)
            tokenizer = hf_service.load_tokenizer(huggingface_id)
            
            if not model or not tokenizer:
                raise ValueError(f"Не удалось загрузить модель или токенизатор для {huggingface_id}")
            
            # Форматируем сообщения в текстовый запрос
            prompt = ""
            for message in messages:
                role = message.get("role", "user")
                content = message.get("content", "")
                
                if role == "system":
                    prompt += f"System: {content}\n\n"
                elif role == "user":
                    prompt += f"User: {content}\n\n"
                elif role == "assistant":
                    prompt += f"Assistant: {content}\n\n"
            
            prompt += "Assistant: "
            
            # Кодируем запрос
            inputs = tokenizer(prompt, return_tensors="pt", padding=True, truncation=True)
            
            # Генерируем ответ
            outputs = model.generate(
                inputs.input_ids,
                max_length=max_length,
                num_return_sequences=1,
                do_sample=True,
                temperature=0.7,
                top_p=0.9
            )
            
            # Декодируем ответ
            generated_text = tokenizer.decode(outputs[0], skip_special_tokens=True)
            
            # Извлекаем только ответ ассистента
            assistant_response = generated_text.split("Assistant: ")[-1].strip()
            
            # Обновляем статус модели
            update_model_status(model_id, 'ready')
            
            return assistant_response
        except Exception as e:
            # В случае ошибки обновляем статус модели
            update_model_status(model_id, 'error', str(e))
            raise
    except Exception as e:
        logger.error(f"Ошибка при генерации ответа в чате: {str(e)}")
        return f"Ошибка при генерации ответа: {str(e)}"

def search_models(query, limit=20):
    """
    Поиск моделей на Hugging Face Hub
    
    Args:
        query: Поисковый запрос
        limit: Максимальное количество результатов
        
    Returns:
        list: Список найденных моделей
    """
    try:
        # Инициализируем API
        from huggingface_hub import HfApi
        api = HfApi()
        
        # Выполняем поиск моделей
        models = api.list_models(
            search=query,  # Поисковый запрос
            filter="text-generation",  # Фильтр по типу модели
            sort="downloads",  # Сортировка по количеству загрузок
            direction=-1,  # Сортировка по убыванию
            limit=limit  # Ограничение количества результатов
        )
        
        # Преобразуем результаты в удобный формат
        result = []
        for model in models:
            result.append({
                "id": model.id,
                "name": model.id.split('/')[-1],
                "author": model.id.split('/')[0] if '/' in model.id else "Unknown",
                "description": model.card_data.get("description", "") if model.card_data else "",
                "tags": model.tags,
                "downloads": model.downloads,
                "likes": model.likes
            })
        
        return result
    except Exception as e:
        logger.error(f"Ошибка при поиске моделей: {str(e)}")
        return []

def add_model(model_data):
    """
    Добавляет новую модель в список доступных
    
    Args:
        model_data: Данные о модели (id, name, description, huggingface_id, type)
        
    Returns:
        Словарь с результатом операции
    """
    try:
        # Проверяем обязательные поля
        required_fields = ['id', 'name', 'huggingface_id', 'type']
        for field in required_fields:
            if field not in model_data:
                return {'success': False, 'message': f"Отсутствует обязательное поле: {field}"}
        
        # Получаем список моделей
        models_data = get_ai_models()
        
        if 'error' in models_data:
            return {'success': False, 'message': models_data['error']}
        
        models = models_data.get('models', [])
        
        # Проверяем, что модель с таким ID не существует
        if any(m['id'] == model_data['id'] for m in models):
            return {'success': False, 'message': f"Модель с ID {model_data['id']} уже существует"}
        
        # Проверяем доступность модели на Hugging Face
        availability = hf_service.check_model_availability(model_data['huggingface_id'])
        
        # Создаем новую модель
        new_model = {
            'id': model_data['id'],
            'name': model_data['name'],
            'description': model_data.get('description', ''),
            'huggingface_id': model_data['huggingface_id'],
            'type': model_data['type'],
            'status': 'ready' if availability['available'] else 'unavailable',
            'is_current': False
        }
        
        if not availability['available'] and 'error' in availability:
            new_model['error'] = availability['error']
        
        # Добавляем модель в список
        models.append(new_model)
        models_data['models'] = models
        
        # Сохраняем обновленную информацию
        with open(MODELS_INFO_FILE, 'w', encoding='utf-8') as f:
            json.dump(models_data, f, ensure_ascii=False, indent=2)
        
        return {
            'success': True,
            'model': new_model,
            'message': f"Модель {new_model['name']} успешно добавлена"
        }
    except Exception as e:
        logger.error(f"Ошибка при добавлении модели: {str(e)}")
        return {'success': False, 'message': f"Ошибка при добавлении модели: {str(e)}"}

def remove_model(model_id):
    """
    Удаляет модель из списка доступных
    
    Args:
        model_id: Идентификатор модели
        
    Returns:
        Словарь с результатом операции
    """
    try:
        # Получаем список моделей
        models_data = get_ai_models()
        
        if 'error' in models_data:
            return {'success': False, 'message': models_data['error']}
        
        models = models_data.get('models', [])
        
        # Ищем модель с указанным ID
        model = next((m for m in models if m['id'] == model_id), None)
        
        if not model:
            return {'success': False, 'message': f"Модель с ID {model_id} не найдена"}
        
        # Проверяем, не является ли модель текущей
        if model.get('is_current', False):
            return {'success': False, 'message': f"Нельзя удалить текущую модель. Сначала выберите другую модель."}
        
        # Удаляем модель из списка
        models = [m for m in models if m['id'] != model_id]
        models_data['models'] = models
        
        # Сохраняем обновленную информацию
        with open(MODELS_INFO_FILE, 'w', encoding='utf-8') as f:
            json.dump(models_data, f, ensure_ascii=False, indent=2)
        
        return {
            'success': True,
            'model_id': model_id,
            'message': f"Модель {model['name']} успешно удалена"
        }
    except Exception as e:
        logger.error(f"Ошибка при удалении модели: {str(e)}")
        return {'success': False, 'message': f"Ошибка при удалении модели: {str(e)}"}

def get_ai_response(prompt, system_message=None):
    """
    Получает ответ от AI-модели
    
    Args:
        prompt: Запрос пользователя
        system_message: Системное сообщение (опционально)
        
    Returns:
        Ответ от AI-модели
    """
    try:
        # Получаем текущую модель
        current_model = get_current_ai_model()
        
        if not current_model:
            return "Ошибка: Не выбрана модель AI. Пожалуйста, выберите модель в настройках."
        
        # Формируем сообщения для чата
        messages = []
        
        if system_message:
            messages.append({
                "role": "system",
                "content": system_message
            })
        
        messages.append({
            "role": "user",
            "content": prompt
        })
        
        # Определяем тип модели и вызываем соответствующую функцию
        if current_model.get('type') == 'chat':
            return generate_chat_response(messages)
        else:
            # Для моделей типа completion формируем запрос по-другому
            full_prompt = ""
            if system_message:
                full_prompt += f"{system_message}\n\n"
            full_prompt += f"User: {prompt}\nAssistant: "
            
            return generate_text(full_prompt)
    except Exception as e:
        logger.error(f"Ошибка при получении ответа от AI: {str(e)}")
        return f"Ошибка при получении ответа от AI: {str(e)}"

def get_available_huggingface_models(filter_criteria=None, limit=20):
    """
    Получает список доступных моделей с Hugging Face Hub
    
    Args:
        filter_criteria: Критерии фильтрации моделей (опционально)
        limit: Максимальное количество моделей для получения
        
    Returns:
        Список моделей
    """
    try:
        # Инициализируем API
        api = HfApi()
        
        # Получаем список моделей
        models = api.list_models(
            filter=filter_criteria or "text-generation",  # Фильтр по типу модели
            sort="downloads",  # Сортировка по количеству загрузок
            direction=-1,  # Сортировка по убыванию
            limit=limit  # Ограничение количества результатов
        )
        
        # Преобразуем результаты в удобный формат
        result = []
        for model in models:
            model_id = model.id.replace('/', '-').lower()  # Создаем безопасный ID
            result.append({
                "id": model_id,
                "name": model.id.split('/')[-1],
                "description": model.card_data.get("description", "") if model.card_data else f"Модель {model.id}",
                "huggingface_id": model.id,
                "type": "completion",  # По умолчанию считаем, что это модель для завершения текста
                "status": "unavailable",
                "is_current": False
            })
        
        return result
    except Exception as e:
        logger.error(f"Ошибка при получении списка моделей с Hugging Face Hub: {str(e)}")
        return []

def update_models_from_huggingface():
    """
    Обновляет список моделей, добавляя популярные модели с Hugging Face Hub
    
    Returns:
        dict: Результат операции
    """
    try:
        # Проверяем существование файла с моделями
        if not os.path.exists(MODELS_INFO_FILE):
            create_default_models_file()
        
        # Получаем текущий список моделей
        with open(MODELS_INFO_FILE, 'r', encoding='utf-8') as f:
            models_data = json.load(f)
        
        current_models = models_data.get("models", [])
        
        # Получаем список популярных моделей с Hugging Face Hub
        huggingface_models = get_available_huggingface_models(limit=10)
        
        # Создаем словарь существующих моделей для быстрого поиска
        existing_models = {model["huggingface_id"]: True for model in current_models}
        
        # Добавляем новые модели, если их еще нет в списке
        added_count = 0
        for hf_model in huggingface_models:
            if hf_model["huggingface_id"] not in existing_models:
                current_models.append(hf_model)
                added_count += 1
        
        # Сохраняем обновленный список моделей
        with open(MODELS_INFO_FILE, 'w', encoding='utf-8') as f:
            json.dump({"models": current_models}, f, ensure_ascii=False, indent=4)
        
        return {
            "success": True,
            "message": f"Список моделей обновлен. Добавлено {added_count} новых моделей.",
            "added_count": added_count,
            "total_models": len(current_models)
        }
    except Exception as e:
        logger.error(f"Ошибка при обновлении списка моделей: {str(e)}")
        return {
            "success": False,
            "message": f"Ошибка при обновлении списка моделей: {str(e)}"
        }

def save_ai_models(models_data):
    """
    Сохраняет информацию о моделях в файл
    
    Args:
        models_data: Данные о моделях для сохранения
    
    Returns:
        bool: Результат операции
    """
    try:
        with open(MODELS_INFO_FILE, 'w', encoding='utf-8') as f:
            json.dump(models_data, f, ensure_ascii=False, indent=4)
        return True
    except Exception as e:
        logger.error(f"Ошибка при сохранении информации о моделях: {str(e)}")
        return False