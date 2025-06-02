"""Сервис для работы с AI моделями."""

import logging
from typing import Any, Dict, List, Optional

from sqlalchemy.orm import Session

from core.db.models import AIModel

logger = logging.getLogger(__name__)


class AIModelService:
    """Сервис управления AI моделями."""

    def __init__(self, db_session: Session):
        """
        Инициализирует сервис AI моделей.

        Args:
            db_session: Сессия базы данных
        """
        self.db = db_session

    def create_model(
        self,
        name: str,
        provider: str,
        is_api: bool = True,
        base_url: Optional[str] = None,
        api_key_name: Optional[str] = None,
        configuration: Optional[Dict[str, Any]] = None,
    ) -> Optional[AIModel]:
        """Создание новой AI модели."""
        try:
            model = AIModel(
                name=name,
                provider=provider,
                is_api=is_api,
                base_url=base_url,
                api_key_name=api_key_name,
                configuration=configuration or {},
            )
            self.db.add(model)
            self.db.commit()
            self.db.refresh(model)
            logger.info(f"Создана модель: {model.name}")
            return model
        except Exception as e:
            logger.error(f"Ошибка создания модели: {e}")
            self.db.rollback()
            return None

    def get_model(self, model_id: int) -> Optional[AIModel]:
        """Получение модели по ID."""
        return self.db.query(AIModel).filter(AIModel.id == model_id).first()

    def get_model_by_name(self, name: str) -> Optional[AIModel]:
        """Получение модели по имени."""
        return self.db.query(AIModel).filter(AIModel.name == name).first()

    def list_models(self, active_only: bool = True) -> List[AIModel]:
        """Список всех моделей."""
        query = self.db.query(AIModel)
        if active_only:
            query = query.filter(AIModel.is_active == True)
        return query.all()

    def update_model(self, model_id: int, **kwargs) -> Optional[AIModel]:
        """Обновление модели."""
        try:
            model = self.get_model(model_id)
            if not model:
                return None

            for key, value in kwargs.items():
                if hasattr(model, key):
                    setattr(model, key, value)

            self.db.commit()
            self.db.refresh(model)
            logger.info(f"Обновлена модель: {model.name}")
            return model
        except Exception as e:
            logger.error(f"Ошибка обновления модели: {e}")
            self.db.rollback()
            return None

    def delete_model(self, model_id: int) -> bool:
        """Удаление модели."""
        try:
            model = self.get_model(model_id)
            if not model:
                return False

            self.db.delete(model)
            self.db.commit()
            logger.info(f"Удалена модель: {model.name}")
            return True
        except Exception as e:
            logger.error(f"Ошибка удаления модели: {e}")
            self.db.rollback()
            return False

    def activate_model(self, model_id: int) -> bool:
        """Активация модели."""
        return self.update_model(model_id, is_active=True) is not None

    def deactivate_model(self, model_id: int) -> bool:
        """Деактивация модели."""
        return self.update_model(model_id, is_active=False) is not None

    def register_model(self, **kwargs) -> Optional[AIModel]:
        """Алиас для create_model для совместимости с тестами."""
        return self.create_model(**kwargs)

    def get_model_by_id(self, model_id: int) -> Optional[AIModel]:
        """Алиас для get_model для совместимости с тестами."""
        return self.get_model(model_id)

    def get_active_models(self) -> List[AIModel]:
        """Алиас для list_models для совместимости с тестами."""
        return self.list_models(active_only=True)

    def update_model_configuration(
        self, model_id: int, configuration: Dict[str, Any]
    ) -> Optional[AIModel]:
        """Обновление конфигурации модели."""
        return self.update_model(model_id, configuration=configuration)
