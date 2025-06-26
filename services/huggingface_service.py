"""
Сервис для интеграции с HuggingFace Hub.
"""

import asyncio
import logging
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Union

import requests
from sqlalchemy.orm import Session

from config import Config

# ✅ ИСПРАВЛЕНИЕ: Добавляем необходимые импорты
from core.db.connection import get_db
from core.db.models import AIModel

logger = logging.getLogger(__name__)


@dataclass
class HFModelInfo:
    """Информация о модели с HuggingFace."""

    id: str
    author: str
    sha: str
    created_at: str
    last_modified: str
    pipeline_tag: Optional[str]
    tags: List[str]
    downloads: int
    likes: int
    library_name: Optional[str]
    model_size: Optional[str]
    description: Optional[str]
    language: List[str]
    license: Optional[str]


# Добавляем импорт
try:
    from huggingface_hub import HfApi

    HF_API_AVAILABLE = True
except ImportError:
    HF_API_AVAILABLE = False


class HuggingFaceService:
    """Сервис для работы с HuggingFace Hub API."""

    def __init__(self, api_token: Optional[str] = None):
        self.api_token = api_token or getattr(Config, "HUGGINGFACE_API_TOKEN", None)
        self.base_url = "https://huggingface.co/api"
        self.headers = {"User-Agent": "Neuro-Link-Assistant/1.0"}
        if self.api_token:
            self.headers["Authorization"] = f"Bearer {self.api_token}"

        # ✅ НОВОЕ: Используем официальную библиотеку если доступна
        if HF_API_AVAILABLE:
            self.hf_api = HfApi(token=self.api_token)
        else:
            self.hf_api = None

    # ✅ ДОБАВЛЯЕМ: Метод тестирования подключения
    def test_connection(self) -> Dict[str, Any]:
        """Тестирует соединение с HuggingFace Hub."""
        try:
            # Пробуем получить одну популярную модель
            models = self.get_models(limit=1, sort="downloads")

            if models:
                return {
                    "success": True,
                    "message": "Соединение с HuggingFace Hub работает",
                    "test_model": models[0].id,
                    "downloads": models[0].downloads,
                }
            else:
                return {"success": False, "message": "Не удалось получить модели с HuggingFace Hub"}

        except Exception as e:
            logger.error(f"Ошибка тестирования соединения с HF: {e}")
            return {
                "success": False,
                "error": str(e),
                "message": "Ошибка соединения с HuggingFace Hub",
            }

    # ✅ ДОБАВЛЯЕМ: Метод получения популярных моделей
    def get_popular_models(self, limit: int = 10, task: Optional[str] = None) -> List[HFModelInfo]:
        """Получает популярные модели с HuggingFace Hub."""
        return self.get_models(limit=limit, task=task, sort="downloads", direction="desc")

    def get_models(
        self,
        limit: int = 10,
        task: Optional[str] = None,
        sort: str = "downloads",
        direction: str = "desc",
        search: Optional[str] = None,
    ) -> List[HFModelInfo]:
        """Получает список моделей с HuggingFace Hub."""
        try:
            # ✅ ИСПРАВЛЕНО: Простые параметры, которые точно работают
            params = {
                "limit": limit,
                "sort": sort,  # HF API поддерживает: downloads, lastModified, etc.
            }

            if task:
                params["filter"] = task

            if search:
                params["search"] = search

            logger.info(f"Запрос к HF API: {self.base_url}/models с параметрами: {params}")

            response = requests.get(f"{self.base_url}/models", params=params, headers=self.headers)

            if response.status_code == 200:
                models_data = response.json()
                logger.info(f"Получено {len(models_data)} моделей от HF API")

                # ✅ ИСПРАВЛЕНО: Простая обработка без лишних манипуляций
                parsed_models = []
                for model_dict in models_data:
                    try:
                        parsed_model = self._parse_model_info(model_dict)
                        parsed_models.append(parsed_model)
                    except Exception as e:
                        logger.warning(
                            f"Ошибка парсинга модели {model_dict.get('id', 'unknown')}: {e}"
                        )
                        continue

                logger.info(f"Успешно обработано {len(parsed_models)} моделей")
                return parsed_models
            else:
                logger.error(
                    f"Ошибка запроса к HuggingFace API: {response.status_code} {response.text}"
                )
                return []

        except Exception as e:
            logger.error(f"Ошибка получения моделей: {e}")
            return []

    def get_model_details(self, model_id: str) -> Optional[HFModelInfo]:
        """Получает детальную информацию о конкретной модели."""
        try:
            url = f"{self.base_url}/models/{model_id}"
            response = requests.get(url, headers=self.headers, timeout=30)
            response.raise_for_status()

            model_data = response.json()
            return HFModelInfo(
                id=model_data.get("id", ""),
                author=model_data.get("author", ""),
                sha=model_data.get("sha", ""),
                created_at=model_data.get("createdAt", ""),
                last_modified=model_data.get("lastModified", ""),
                pipeline_tag=model_data.get("pipeline_tag"),
                tags=model_data.get("tags", []),
                downloads=model_data.get("downloads", 0),
                likes=model_data.get("likes", 0),
                library_name=model_data.get("library_name"),
                model_size=self._extract_model_size(model_data.get("tags", [])),
                description=(
                    model_data.get("description", "")[:1000]
                    if model_data.get("description")
                    else ""
                ),
                language=self._extract_languages(model_data.get("tags", [])),
                license=model_data.get("license"),
            )

        except requests.RequestException as e:
            logger.error(f"Ошибка получения деталей модели {model_id}: {e}")
            return None

    def search_models(self, query: str, limit: int = 50) -> List[HFModelInfo]:
        """Поиск моделей по запросу."""
        try:
            url = f"{self.base_url}/models"
            params = {"search": query, "limit": limit, "full": True}

            response = requests.get(url, headers=self.headers, params=params, timeout=30)
            response.raise_for_status()

            models_data = response.json()
            models = []

            for model_data in models_data:
                try:
                    model_info = HFModelInfo(
                        id=model_data.get("id", ""),
                        author=model_data.get("author", ""),
                        sha=model_data.get("sha", ""),
                        created_at=model_data.get("createdAt", ""),
                        last_modified=model_data.get("lastModified", ""),
                        pipeline_tag=model_data.get("pipeline_tag"),
                        tags=model_data.get("tags", []),
                        downloads=model_data.get("downloads", 0),
                        likes=model_data.get("likes", 0),
                        library_name=model_data.get("library_name"),
                        model_size=self._extract_model_size(model_data.get("tags", [])),
                        description=(
                            model_data.get("description", "")[:1000]
                            if model_data.get("description")
                            else ""
                        ),
                        language=self._extract_languages(model_data.get("tags", [])),
                        license=model_data.get("license"),
                    )
                    models.append(model_info)
                except Exception as e:
                    logger.warning(f"Ошибка обработки модели в поиске: {e}")
                    continue

            return models

        except Exception as e:
            logger.error(f"Ошибка поиска моделей: {e}")
            return []

    def _parse_model_info(self, model_data: Dict[str, Any]) -> HFModelInfo:
        """Парсит информацию о модели из ответа API."""
        try:
            # ✅ ИСПРАВЛЕНО: Безопасное извлечение данных из словаря
            model_id = model_data.get("id", "unknown")
            author = model_id.split("/")[0] if "/" in model_id else "unknown"

            return HFModelInfo(
                id=model_id,
                author=author,
                sha=model_data.get("sha", ""),
                created_at=model_data.get("createdAt", ""),
                last_modified=model_data.get("lastModified", ""),
                pipeline_tag=model_data.get("pipeline_tag"),
                tags=model_data.get("tags", []) or [],  # Защита от None
                downloads=model_data.get("downloads", 0) or 0,  # Защита от None
                likes=model_data.get("likes", 0) or 0,  # Защита от None
                library_name=model_data.get("library_name"),
                model_size=self._extract_model_size(model_data.get("tags", []) or []),
                description=(
                    str(model_data.get("description", ""))[:1000]
                    if model_data.get("description")
                    else ""
                ),
                language=self._extract_languages(model_data.get("tags", []) or []),
                license=model_data.get("license"),
            )
        except Exception as e:
            logger.error(f"Ошибка парсинга модели {model_data.get('id', 'unknown')}: {e}")
            # Возвращаем минимальную модель
            return HFModelInfo(
                id=model_data.get("id", "unknown"),
                author="unknown",
                sha="",
                created_at="",
                last_modified="",
                pipeline_tag=None,
                tags=[],
                downloads=0,
                likes=0,
                library_name=None,
                model_size=None,
                description="",
                language=[],
                license=None,
            )

    def _parse_model_info_from_api(self, model) -> HFModelInfo:
        """Парсит информацию о модели из официального API."""
        try:
            return HFModelInfo(
                id=getattr(model, "modelId", "unknown"),
                author=(
                    getattr(model, "modelId", "").split("/")[0]
                    if "/" in getattr(model, "modelId", "")
                    else "unknown"
                ),
                sha=getattr(model, "sha", ""),
                created_at=str(getattr(model, "createdAt", "")),
                last_modified=str(getattr(model, "lastModified", "")),
                pipeline_tag=getattr(model, "pipeline_tag", None),
                tags=getattr(model, "tags", []),
                downloads=getattr(model, "downloads", 0),
                likes=getattr(model, "likes", 0),
                library_name=getattr(model, "library_name", None),
                model_size=self._extract_model_size(getattr(model, "tags", [])),
                description=getattr(model, "description", ""),
                language=self._extract_languages(getattr(model, "tags", [])),
                license=getattr(model, "license", None),
            )
        except Exception as e:
            logger.error(f"Ошибка парсинга модели из API: {e}")
            return HFModelInfo(
                id="unknown",
                author="unknown",
                sha="",
                created_at="",
                last_modified="",
                pipeline_tag=None,
                tags=[],
                downloads=0,
                likes=0,
                library_name=None,
                model_size=None,
                description="",
                language=[],
                license=None,
            )

    def _extract_model_size(self, tags: List[str]) -> Optional[str]:
        """Извлекает размер модели из тегов."""
        if not tags or not isinstance(tags, list):
            return None

        size_tags = [
            tag
            for tag in tags
            if isinstance(tag, str)
            and any(size in tag.lower() for size in ["b", "billion", "million", "m"])
        ]
        return size_tags[0] if size_tags else None

    def _extract_languages(self, tags: List[str]) -> List[str]:
        """Извлекает языки из тегов."""
        if not tags or not isinstance(tags, list):
            return []

        language_tags = [
            tag
            for tag in tags
            if isinstance(tag, str)
            and any(lang in tag.lower() for lang in ["en", "ru", "fr", "de", "es", "zh", "ja"])
        ]
        return language_tags


class ModelSyncService:
    """Сервис для синхронизации моделей с базой данных."""

    def __init__(self, hf_service: HuggingFaceService):
        self.hf_service = hf_service

    def sync_popular_models(self, limit: int = 200) -> Dict[str, Any]:
        """Синхронизирует популярные модели с базой данных."""
        try:
            # ✅ ИСПРАВЛЕНИЕ: Используем правильный контекстный менеджер
            db = next(get_db())
            try:
                # Получаем популярные модели разных типов
                tasks = [
                    "text-generation",
                    "text-classification",
                    "translation",
                    "summarization",
                    "question-answering",
                    "text2text-generation",
                ]

                total_synced = 0
                total_updated = 0
                total_errors = 0

                for task in tasks:
                    try:
                        models = self.hf_service.get_models(
                            limit=limit // len(tasks), task=task, sort="downloads"
                        )

                        for model_info in models:
                            try:
                                synced, updated = self._sync_model_to_db(db, model_info)
                                if synced:
                                    total_synced += 1
                                if updated:
                                    total_updated += 1

                            except Exception as e:
                                logger.error(f"Ошибка синхронизации модели {model_info.id}: {e}")
                                total_errors += 1

                    except Exception as e:
                        logger.error(f"Ошибка получения моделей для задачи {task}: {e}")
                        total_errors += 1

                db.commit()

                result = {
                    "success": True,
                    "total_synced": total_synced,
                    "total_updated": total_updated,
                    "total_errors": total_errors,
                    "timestamp": datetime.now().isoformat(),
                }

                logger.info(f"Синхронизация завершена: {result}")
                return result
            finally:
                db.close()

        except Exception as e:
            logger.error(f"Критическая ошибка синхронизации: {e}")
            return {"success": False, "error": str(e), "timestamp": datetime.now().isoformat()}

    def _sync_model_to_db(self, db: Session, model_info: HFModelInfo) -> tuple[bool, bool]:
        """Синхронизирует конкретную модель с базой данных."""
        try:
            if not model_info or not model_info.id:
                logger.warning("model_info или model_info.id отсутствует")
                return False, False

            # Ищем существующую модель
            existing_model = db.query(AIModel).filter(AIModel.hf_model_id == model_info.id).first()

            if existing_model:
                # ✅ ПРОСТОЙ ПОДХОД: Создаем словарь изменений напрямую
                update_data = {}

                # Обновляем без сравнения - просто обновляем все поля
                update_data.update(
                    {
                        "downloads": model_info.downloads,
                        "likes": model_info.likes,
                        "description": model_info.description or "",
                        "tags": model_info.tags or [],
                        "is_featured": model_info.downloads > 10000,
                        "last_sync_at": datetime.now(),
                        "sync_status": "synced",
                        "sync_error": None,
                    }
                )

                # Обновляем дату изменения HF
                hf_last_modified = self._parse_hf_datetime(model_info.last_modified)
                if hf_last_modified:
                    update_data["last_modified_hf"] = hf_last_modified

                # Обновляем через query.update()
                db.query(AIModel).filter(AIModel.id == existing_model.id).update(update_data)
                return False, True
            else:
                # Создаем новую модель
                new_model = self._create_model_from_hf(model_info)
                db.add(new_model)
                return True, False

        except Exception as e:
            logger.error(f"Ошибка синхронизации модели: {e}")
            return False, False

    def _create_model_from_hf(self, model_info: HFModelInfo) -> AIModel:
        """Создает новую модель в БД из HF данных."""
        if not model_info:
            raise ValueError("model_info не может быть None")

        # ✅ ДОБАВЛЕНО: Безопасная обрезка данных
        return AIModel(
            name=(model_info.id.split("/")[-1] if "/" in model_info.id else model_info.id)[:255],
            full_name=model_info.id[:255],
            hf_model_id=model_info.id[:255],
            hf_url=f"https://huggingface.co/{model_info.id}"[:500],
            author=(model_info.author or "")[:255],
            description=(model_info.description or "")[:1000],
            tags=model_info.tags,
            pipeline_tag=(model_info.pipeline_tag or "")[:200],  # ✅ Увеличенный лимит
            language=model_info.language,
            downloads=model_info.downloads,
            likes=model_info.likes,
            model_size=(model_info.model_size or "")[:200],  # ✅ ИСПРАВЛЕНО: увеличен лимит
            license=(model_info.license or "")[:100],
            library_name=(model_info.library_name or "")[:100],
            created_at_hf=self._parse_hf_datetime(model_info.created_at),
            last_modified_hf=self._parse_hf_datetime(model_info.last_modified),
            sync_status="synced",
            last_sync_at=datetime.now(),
            is_active=True,
            is_featured=model_info.downloads > 10000,
            provider="huggingface",
            model_type=(model_info.pipeline_tag or "unknown")[:100],
        )

    def _parse_hf_datetime(self, date_str: Optional[str]) -> Optional[datetime]:
        """Парсит дату из HF формата."""
        if not date_str:
            return None

        try:
            # HF использует ISO формат
            return datetime.fromisoformat(date_str.replace("Z", "+00:00"))
        except Exception as e:
            logger.warning(f"Ошибка парсинга даты HF: {date_str}, ошибка: {e}")
            return None


# ✅ ИСПРАВЛЕНИЕ: Глобальные функции (не методы класса)
def get_hf_service() -> HuggingFaceService:
    """Возвращает экземпляр HuggingFace сервиса."""
    return HuggingFaceService()


def sync_models_from_hf(limit: int = 200) -> Dict[str, Any]:
    """Синхронизирует модели с HuggingFace Hub."""
    hf_service = get_hf_service()
    sync_service = ModelSyncService(hf_service)
    return sync_service.sync_popular_models(limit)


def get_model_details_from_hf(model_id: str) -> Optional[HFModelInfo]:
    """Получает детали модели с HuggingFace Hub."""
    hf_service = get_hf_service()
    return hf_service.get_model_details(model_id)


def search_hf_models(query: str, limit: int = 50) -> List[HFModelInfo]:
    """Поиск моделей на HuggingFace Hub."""
    hf_service = get_hf_service()
    return hf_service.search_models(query, limit)


def search_models_for_ui(query: str, limit: int = 20) -> Dict[str, Any]:
    """Поиск моделей для отображения в UI."""
    try:
        hf_service = get_hf_service()
        models = hf_service.search_models(query, limit)

        # Форматируем для UI
        formatted_models = []
        for model in models[:limit]:  # Дополнительная защита
            formatted_models.append(
                {
                    "id": model.id,
                    "name": model.id.split("/")[-1] if "/" in model.id else model.id,
                    "author": model.author,
                    "downloads": model.downloads,
                    "likes": model.likes,
                    "description": (
                        (model.description or "")[:200] + "..."
                        if len(model.description or "") > 200
                        else (model.description or "")
                    ),
                    "pipeline_tag": model.pipeline_tag,
                    "url": f"https://huggingface.co/{model.id}",
                }
            )

        return {
            "success": True,
            "models": formatted_models,
            "total": len(formatted_models),
            "query": query,
        }

    except Exception as e:
        logger.error(f"Ошибка поиска моделей: {e}")
        return {"success": False, "error": str(e), "models": []}


# ✅ Дополнительные функции для простого AI тестирования
def get_simple_ai_response(prompt: str, max_length: int = 100) -> str:
    """
    Простой AI ответ без сложных зависимостей.

    Args:
        prompt: Входной промпт
        max_length: Максимальная длина ответа

    Returns:
        Сгенерированный ответ
    """
    try:
        # ✅ Используем простую эвристику для быстрого тестирования
        responses = {
            "привет": "Привет! Как дела?",
            "hello": "Hello! How can I help you?",
            "как дела": "Дела хорошо, спасибо! А у вас?",
            "что делаешь": "Я готов помочь вам с различными задачами!",
            "помощь": "Я могу помочь с текстом, кодом, вопросами и многим другим.",
            "спасибо": "Пожалуйста! Рад помочь!",
            "пока": "До свидания! Удачного дня!",
        }

        prompt_lower = prompt.lower().strip()

        # Ищем подходящий ответ
        for key, response in responses.items():
            if key in prompt_lower:
                return response

        # Если точного совпадения нет, генерируем простой ответ
        if "?" in prompt:
            return f"Интересный вопрос! Вы спрашиваете: '{prompt[:50]}...'"
        elif len(prompt) > 50:
            return f"Вы написали длинный текст. Могу ли я помочь с чем-то конкретным?"
        else:
            return f"Понял ваш запрос: '{prompt}'. Как могу помочь дальше?"

    except Exception as e:
        logger.error(f"Ошибка генерации простого ответа: {e}")
        return "Извините, произошла ошибка при обработке вашего запроса."


def test_hf_connection() -> Dict[str, Any]:
    """Тестирует соединение с HuggingFace Hub."""
    try:
        hf_service = get_hf_service()

        # Пробуем получить одну популярную модель
        models = hf_service.get_models(limit=1, sort="downloads")

        if models:
            return {
                "success": True,
                "message": "Соединение с HuggingFace Hub работает",
                "test_model": models[0].id,
                "downloads": models[0].downloads,
            }
        else:
            return {"success": False, "message": "Не удалось получить модели с HuggingFace Hub"}

    except Exception as e:
        logger.error(f"Ошибка тестирования соединения с HF: {e}")
        return {"success": False, "error": str(e), "message": "Ошибка соединения с HuggingFace Hub"}


def add_single_model_to_db(model_id: str) -> Dict[str, Any]:
    """Добавляет одну конкретную модель в базу данных по её ID."""
    try:
        hf_service = get_hf_service()

        # Получаем детали модели
        model_info = hf_service.get_model_details(model_id)
        if not model_info:
            return {"success": False, "error": f"Модель {model_id} не найдена на HuggingFace"}

        db = next(get_db())
        try:
            # Проверяем, есть ли уже такая модель
            existing = db.query(AIModel).filter(AIModel.hf_model_id == model_id).first()
            if existing:
                return {"success": False, "error": f"Модель {model_id} уже существует в базе"}

            # Создаем новую модель
            sync_service = ModelSyncService(hf_service)
            new_model = sync_service._create_model_from_hf(model_info)
            db.add(new_model)
            db.commit()

            return {
                "success": True,
                "message": f"Модель {model_id} успешно добавлена",
                "model_name": new_model.name,
                "downloads": new_model.downloads,
            }

        finally:
            db.close()

    except Exception as e:
        logger.error(f"Ошибка добавления модели {model_id}: {e}")
        return {"success": False, "error": str(e)}
