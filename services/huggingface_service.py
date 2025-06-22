import logging
import os

from huggingface_hub import HfApi, HfFolder, Repository
from huggingface_hub.errors import RepositoryNotFoundError, RevisionNotFoundError
from transformers.models.auto.configuration_auto import AutoConfig
from transformers.models.auto.modeling_auto import AutoModelForCausalLM
from transformers.models.auto.tokenization_auto import AutoTokenizer

from config import Config

logger = logging.getLogger("neuro_assistant")


class HuggingFaceService:
    def __init__(self):
        self.api = HfApi()
        self.token = os.environ.get("HUGGINGFACE_TOKEN") or Config.HUGGINGFACE_TOKEN
        self.models_cache = {}
        self.tokenizers_cache = {}

        # Установка токена для доступа к приватным моделям
        if self.token:
            HfFolder.save_token(self.token)
            logger.info("Hugging Face токен установлен")
        else:
            logger.warning(
                "Hugging Face токен не найден. Доступ к приватным моделям будет ограничен"
            )

    def list_available_models(self, filter_criteria=None):
        """
        Получает список доступных моделей с Hugging Face Hub

        Args:
            filter_criteria: Критерии фильтрации моделей (например, по тегам)

        Returns:
            Список моделей
        """
        try:
            # Получаем список моделей
            models = self.api.list_models(filter=filter_criteria)

            # Форматируем результат
            result = []
            for model in models:
                result.append(
                    {
                        "id": model.id,
                        "name": model.id.split("/")[-1],
                        "author": model.id.split("/")[0] if "/" in model.id else "Unknown",
                        "tags": model.tags,
                        "downloads": model.downloads,
                        "likes": model.likes,
                    }
                )

            return result
        except Exception as e:
            logger.error(f"Ошибка при получении списка моделей с Hugging Face: {str(e)}")
            return []

    def check_model_availability(self, model_id):
        """
        Проверяет доступность модели на Hugging Face Hub

        Args:
            model_id: Идентификатор модели

        Returns:
            Словарь с информацией о доступности модели
        """
        try:
            # Проверяем существование модели
            model_info = self.api.model_info(model_id)

            # Пробуем загрузить конфигурацию модели
            config = AutoConfig.from_pretrained(model_id, token=self.token)

            return {
                "available": True,
                "model_id": model_id,
                "model_name": model_id.split("/")[-1],
                "author": model_id.split("/")[0] if "/" in model_id else "Unknown",
                "tags": model_info.tags,
                "size": model_info.siblings[0].size if model_info.siblings else None,
                "config": {
                    "model_type": config.model_type,
                    "vocab_size": config.vocab_size if hasattr(config, "vocab_size") else None,
                    "hidden_size": config.hidden_size if hasattr(config, "hidden_size") else None,
                },
            }
        except (RepositoryNotFoundError, RevisionNotFoundError) as e:
            logger.error(f"Модель {model_id} не найдена на Hugging Face Hub: {str(e)}")
            return {
                "available": False,
                "model_id": model_id,
                "error": f"Модель не найдена: {str(e)}",
            }
        except Exception as e:
            logger.error(f"Ошибка при проверке доступности модели {model_id}: {str(e)}")
            return {
                "available": False,
                "model_id": model_id,
                "error": f"Ошибка при проверке модели: {str(e)}",
            }

    def load_model(self, model_id, force_reload=False):
        """
        Загружает модель с Hugging Face Hub

        Args:
            model_id: Идентификатор модели
            force_reload: Принудительная перезагрузка модели

        Returns:
            Загруженная модель или None в случае ошибки
        """
        try:
            # Проверяем, есть ли модель в кеше
            if model_id in self.models_cache and not force_reload:
                logger.info(f"Модель {model_id} загружена из кеша")
                return self.models_cache[model_id]

            # Загружаем модель
            logger.info(f"Загрузка модели {model_id} с Hugging Face Hub...")
            model = AutoModelForCausalLM.from_pretrained(model_id, token=self.token)

            # Сохраняем в кеш
            self.models_cache[model_id] = model

            logger.info(f"Модель {model_id} успешно загружена")
            return model
        except Exception as e:
            logger.error(f"Ошибка при загрузке модели {model_id}: {str(e)}")
            return None

    def load_tokenizer(self, model_id, force_reload=False):
        """
        Загружает токенизатор для модели с Hugging Face Hub

        Args:
            model_id: Идентификатор модели
            force_reload: Принудительная перезагрузка токенизатора

        Returns:
            Загруженный токенизатор или None в случае ошибки
        """
        try:
            # Проверяем, есть ли токенизатор в кеше
            if model_id in self.tokenizers_cache and not force_reload:
                logger.info(f"Токенизатор для модели {model_id} загружен из кеша")
                return self.tokenizers_cache[model_id]

            # Загружаем токенизатор
            logger.info(f"Загрузка токенизатора для модели {model_id} с Hugging Face Hub...")
            tokenizer = AutoTokenizer.from_pretrained(model_id, token=self.token)

            # ИСПРАВЛЕНИЕ: Устанавливаем pad_token если его нет
            if tokenizer.pad_token is None:
                tokenizer.pad_token = tokenizer.eos_token
                logger.info(f"Установлен pad_token = eos_token для модели {model_id}")

            # Сохраняем в кеш
            self.tokenizers_cache[model_id] = tokenizer

            logger.info(f"Токенизатор для модели {model_id} успешно загружен")
            return tokenizer
        except Exception as e:
            logger.error(f"Ошибка при загрузке токенизатора для модели {model_id}: {str(e)}")
            return None

    def download_model(self, model_id, local_dir):
        """
        Скачивает модель с Hugging Face Hub в локальную директорию

        Args:
            model_id: Идентификатор модели
            local_dir: Локальная директория для сохранения

        Returns:
            Путь к скачанной модели или None в случае ошибки
        """
        try:
            # Создаем директорию, если она не существует
            os.makedirs(local_dir, exist_ok=True)

            # Формируем путь для сохранения
            model_name = model_id.split("/")[-1]
            model_path = os.path.join(local_dir, model_name)

            # Скачиваем модель
            logger.info(f"Скачивание модели {model_id} в {model_path}...")

            # Клонируем репозиторий
            repo = Repository(local_dir=model_path, clone_from=model_id, token=self.token)

            # Проверяем, что репозиторий был клонирован
            if os.path.exists(os.path.join(repo.local_dir, ".git")):
                logger.info(f"Репозиторий успешно клонирован в {repo.local_dir}")

            logger.info(f"Модель {model_id} успешно скачана в {model_path}")
            return model_path
        except Exception as e:
            logger.error(f"Ошибка при скачивании модели {model_id}: {str(e)}")
            return None
