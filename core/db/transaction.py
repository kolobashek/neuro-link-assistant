"""
Модуль для управления транзакциями базы данных.
"""

from contextlib import contextmanager
from functools import wraps
from typing import Any, Callable, Generator, TypeVar

from sqlalchemy.orm import Session

T = TypeVar("T")


class TransactionManager:
    """
    Менеджер транзакций для управления операциями базы данных.
    """

    def __init__(self, db_session: Session):
        """
        Инициализирует менеджер транзакций.

        Args:
            db_session (Session): Сессия SQLAlchemy.
        """
        self.session = db_session

    @contextmanager
    def begin(self) -> Generator[Session, None, None]:
        """
        Контекстный менеджер для выполнения операций внутри транзакции.

        Yields:
            Session: Сессия SQLAlchemy.

        Raises:
            Exception: Если произошла ошибка внутри транзакции.
        """
        # Создаем вложенную транзакцию (savepoint)
        try:
            # Начинаем транзакцию
            yield self.session
            # Если исключений не возникло, фиксируем изменения
            self.session.commit()
        except Exception:
            # В случае ошибки откатываем все изменения
            self.session.rollback()
            raise


def transaction(db_session: Session) -> Callable[[Callable[..., T]], Callable[..., T]]:
    """
    Декоратор для выполнения функции внутри транзакции.

    Args:
        db_session (Session): Сессия SQLAlchemy.

    Returns:
        Callable: Декорированная функция.
    """

    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        @wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> T:
            # Создаем менеджер транзакций
            tx = TransactionManager(db_session)
            # Выполняем функцию внутри транзакции
            with tx.begin():
                return func(*args, **kwargs)

        return wrapper

    return decorator
