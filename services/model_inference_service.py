import logging
import os
from typing import Any, Dict, Optional, Tuple

logger = logging.getLogger("neuro_assistant")

# Опциональные импорты для ML библиотек
try:
    import torch
    from transformers.models.auto.modeling_auto import AutoModelForCausalLM
    from transformers.models.auto.tokenization_auto import AutoTokenizer
    from transformers.pipelines import pipeline

    HF_TRANSFORMERS_AVAILABLE = True
except ImportError:
    HF_TRANSFORMERS_AVAILABLE = False
    logger.warning("Transformers библиотека не установлена. ML функции недоступны.")

# ЗАМЕНИТЬ импорт OpenAI:
try:
    import openai

    # Проверка версии API
    if hasattr(openai, "OpenAI"):
        OPENAI_AVAILABLE = True
        logger.info("OpenAI библиотека (v1.0+) доступна")
    else:
        OPENAI_AVAILABLE = False
        logger.warning("Устаревшая версия OpenAI. Обновите: pip install openai>=1.0.0")
except ImportError:
    OPENAI_AVAILABLE = False
    logger.warning("OpenAI библиотека не установлена.")


class ModelInferenceService:
    """Сервис для загрузки и выполнения инференса моделей"""

    def __init__(self):
        self.loaded_models = {}
        self.loaded_tokenizers = {}
        self.model_cache = {}

    def check_model_availability(self, model_id: str) -> Dict[str, Any]:
        """Проверяет доступность модели для инференса"""
        try:
            # Проверка OpenAI моделей
            if self._is_openai_model(model_id):
                return self._check_openai_availability(model_id)

            # Проверка HuggingFace моделей
            if HF_TRANSFORMERS_AVAILABLE:
                return self._check_hf_model_availability(model_id)
            else:
                return {
                    "available": False,
                    "error": "Transformers библиотека не установлена",
                    "model_id": model_id,
                }

        except Exception as e:
            logger.error(f"Ошибка проверки доступности модели {model_id}: {e}")
            return {"available": False, "error": str(e), "model_id": model_id}

    def load_model(self, model_id: str):
        """Загружает модель для инференса"""
        try:
            if model_id in self.loaded_models:
                return self.loaded_models[model_id]

            # OpenAI модели не требуют локальной загрузки
            if self._is_openai_model(model_id):
                self.loaded_models[model_id] = "openai_api"
                return "openai_api"

            # Загрузка HuggingFace модели
            if HF_TRANSFORMERS_AVAILABLE:
                model = self._load_hf_model(model_id)
                if model:
                    self.loaded_models[model_id] = model
                    return model

            return None

        except Exception as e:
            logger.error(f"Ошибка загрузки модели {model_id}: {e}")
            return None

    def load_tokenizer(self, model_id: str):
        """Загружает токенизатор для модели"""
        try:
            if model_id in self.loaded_tokenizers:
                return self.loaded_tokenizers[model_id]

            # OpenAI модели не требуют локального токенизатора
            if self._is_openai_model(model_id):
                self.loaded_tokenizers[model_id] = "openai_api"
                return "openai_api"

            # Загрузка HuggingFace токенизатора
            if HF_TRANSFORMERS_AVAILABLE:
                tokenizer = self._load_hf_tokenizer(model_id)
                if tokenizer:
                    self.loaded_tokenizers[model_id] = tokenizer
                    return tokenizer

            return None

        except Exception as e:
            logger.error(f"Ошибка загрузки токенизатора {model_id}: {e}")
            return None

    def generate_text(self, model_id: str, prompt: str, max_length: int = 100, **kwargs) -> str:
        """Генерирует текст с использованием загруженной модели"""
        try:
            # OpenAI API
            if self._is_openai_model(model_id):
                return self._generate_openai(model_id, prompt, max_length, **kwargs)

            # HuggingFace модели
            return self._generate_hf(model_id, prompt, max_length, **kwargs)

        except Exception as e:
            logger.error(f"Ошибка генерации текста: {e}")
            return f"Ошибка генерации: {str(e)}"

    def unload_model(self, model_id: str):
        """Выгружает модель из памяти"""
        try:
            if model_id in self.loaded_models:
                del self.loaded_models[model_id]
            if model_id in self.loaded_tokenizers:
                del self.loaded_tokenizers[model_id]
            if model_id in self.model_cache:
                del self.model_cache[model_id]

            # Очистка GPU памяти если доступно
            if HF_TRANSFORMERS_AVAILABLE and torch.cuda.is_available():
                torch.cuda.empty_cache()

            logger.info(f"Модель {model_id} выгружена")
            return True
        except Exception as e:
            logger.error(f"Ошибка выгрузки модели {model_id}: {e}")
            return False

    def get_loaded_models(self) -> Dict[str, Any]:
        """Возвращает список загруженных моделей"""
        return {
            "loaded_models": list(self.loaded_models.keys()),
            "loaded_tokenizers": list(self.loaded_tokenizers.keys()),
            "memory_usage": self._get_memory_usage(),
        }

    # Приватные методы
    def _is_openai_model(self, model_id: str) -> bool:
        """Проверяет, является ли модель OpenAI"""
        openai_models = ["gpt-3.5-turbo", "gpt-4", "text-davinci-003"]
        return any(openai_model in model_id.lower() for openai_model in openai_models)

    def _check_openai_availability(self, model_id: str) -> Dict[str, Any]:
        """Проверяет доступность OpenAI API"""
        api_key = os.environ.get("OPENAI_API_KEY")
        if not api_key:
            return {
                "available": False,
                "error": "OPENAI_API_KEY не установлен",
                "model_id": model_id,
            }

        if not OPENAI_AVAILABLE:
            return {
                "available": False,
                "error": "openai библиотека не установлена",
                "model_id": model_id,
            }

        return {"available": True, "model_id": model_id, "type": "openai_api"}

    def _check_hf_model_availability(self, model_id: str) -> Dict[str, Any]:
        """Проверяет доступность HuggingFace модели"""
        try:
            # Простая проверка - пытаемся получить конфиг модели
            from transformers.models.auto.configuration_auto import AutoConfig

            config = AutoConfig.from_pretrained(model_id)

            return {
                "available": True,
                "model_id": model_id,
                "type": "huggingface",
                "config": str(type(config).__name__),
            }
        except Exception as e:
            return {"available": False, "error": str(e), "model_id": model_id}

    def _load_hf_model(self, model_id: str):
        """Загружает HuggingFace модель"""
        try:
            logger.info(f"Загружаем HF модель: {model_id}")
            model = AutoModelForCausalLM.from_pretrained(
                model_id,
                torch_dtype=torch.float16 if torch.cuda.is_available() else torch.float32,
                device_map="auto" if torch.cuda.is_available() else None,
                trust_remote_code=True,
            )
            logger.info(f"Модель {model_id} успешно загружена")
            return model
        except Exception as e:
            logger.error(f"Не удалось загрузить модель {model_id}: {e}")
            return None

    def _load_hf_tokenizer(self, model_id: str):
        """Загружает HuggingFace токенизатор"""
        try:
            logger.info(f"Загружаем токенизатор: {model_id}")
            tokenizer = AutoTokenizer.from_pretrained(model_id, trust_remote_code=True)
            if tokenizer.pad_token is None:
                tokenizer.pad_token = tokenizer.eos_token
            logger.info(f"Токенизатор {model_id} успешно загружен")
            return tokenizer
        except Exception as e:
            logger.error(f"Не удалось загрузить токенизатор {model_id}: {e}")
            return None

    def _generate_openai(self, model_id: str, prompt: str, max_length: int, **kwargs) -> str:
        """Генерация через OpenAI API"""
        try:
            logger.debug(f"Генерация текста для модели {model_id}, промпт: {prompt[:50]}...")
            if not OPENAI_AVAILABLE:
                return "OpenAI библиотека недоступна"
            api_key = os.environ.get("OPENAI_API_KEY")
            if not api_key:
                return "OPENAI_API_KEY не установлен"

            # Настройка OpenAI API (новый способ)
            import openai

            client = openai.OpenAI(api_key=api_key)

            logger.info(f"Отправляем запрос к OpenAI модели: {model_id}")

            # ✅ НОВЫЙ API OpenAI
            response = client.chat.completions.create(
                model=model_id,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=max_length,
                temperature=kwargs.get("temperature", 0.7),
                top_p=kwargs.get("top_p", 1.0),
                frequency_penalty=kwargs.get("frequency_penalty", 0),
                presence_penalty=kwargs.get("presence_penalty", 0),
            )

            # ✅ Детальная проверка ответа
            if not response:
                return "Пустой ответ от OpenAI API"

            if not response.choices:
                return "Нет вариантов ответа от модели"

            choice = response.choices[0]
            if not choice:
                return "Пустой выбор от модели"

            if not choice.message:
                return "Нет сообщения от модели"

            content = choice.message.content
            if not content:
                return "Пустой контент от модели"

            result = content.strip()
            logger.info(f"Получен ответ от OpenAI (длина: {len(result)})")

            return result if result else "Пустой ответ после обработки"

        except Exception as e:
            logger.error(f"Ошибка OpenAI API: {e}")
            return f"Ошибка OpenAI API: {str(e)}"

    def _generate_hf(self, model_id: str, prompt: str, max_length: int, **kwargs) -> str:
        """Генерация через HuggingFace модель"""
        try:
            model = self.loaded_models.get(model_id)
            tokenizer = self.loaded_tokenizers.get(model_id)

            if not model or not tokenizer:
                return "Модель или токенизатор не загружены"

            # Токенизация
            inputs = tokenizer(prompt, return_tensors="pt", truncation=True)

            # Генерация
            with torch.no_grad():
                outputs = model.generate(
                    inputs.input_ids,
                    max_new_tokens=max_length,
                    temperature=kwargs.get("temperature", 0.7),
                    do_sample=True,
                    pad_token_id=tokenizer.eos_token_id,
                )

            # Декодирование
            generated_text = tokenizer.decode(outputs[0], skip_special_tokens=True)

            # Убираем исходный промпт из ответа
            if generated_text.startswith(prompt):
                generated_text = generated_text[len(prompt) :].strip()

            return generated_text

        except Exception as e:
            logger.error(f"Ошибка HF генерации: {e}")
            return f"Ошибка генерации: {str(e)}"

    def _get_memory_usage(self) -> Dict[str, Any]:
        """Получает информацию об использовании памяти"""
        try:
            memory_info = {
                "loaded_models_count": len(self.loaded_models),
                "loaded_tokenizers_count": len(self.loaded_tokenizers),
            }

            if HF_TRANSFORMERS_AVAILABLE and torch.cuda.is_available():
                memory_info.update(
                    {
                        "gpu_memory_allocated": torch.cuda.memory_allocated(),
                        "gpu_memory_reserved": torch.cuda.memory_reserved(),
                        "gpu_memory_cached": torch.cuda.memory_cached(),
                    }
                )

            return memory_info
        except Exception as e:
            logger.error(f"Ошибка получения информации о памяти: {e}")
            return {}
