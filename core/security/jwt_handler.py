"""
Обработчик JWT токенов.
"""

import hashlib
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, Optional

import jwt

SECRET_KEY = "neuro-link-secret-key-change-in-production"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30


def create_access_token(data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
    """
    Создает JWT токен доступа.

    Args:
        data: Данные для включения в токен
        expires_delta: Время жизни токена

    Returns:
        str: JWT токен
    """
    to_encode = data.copy()

    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)

    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def verify_token(token: str) -> Dict[str, Any]:
    """
    Проверяет JWT токен.

    Args:
        token: JWT токен для проверки

    Returns:
        Dict[str, Any]: Декодированные данные из токена

    Raises:
        jwt.InvalidTokenError: Если токен невалидный
        jwt.ExpiredSignatureError: Если токен истек
        jwt.InvalidSignatureError: Если подпись невалидная
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        raise jwt.ExpiredSignatureError("Токен истек")
    except jwt.InvalidSignatureError:
        raise jwt.InvalidSignatureError("Невалидная подпись токена")
    except jwt.InvalidTokenError:
        raise jwt.InvalidTokenError("Невалидный токен")


def decode_token(token: str) -> Dict[str, Any]:
    """
    Декодирует JWT токен без проверки.

    Args:
        token: JWT токен для декодирования

    Returns:
        Dict[str, Any]: Декодированные данные из токена
    """
    try:
        # Декодируем без проверки подписи для тестирования
        payload = jwt.decode(token, options={"verify_signature": False})
        return payload
    except Exception as e:
        raise jwt.InvalidTokenError(f"Ошибка декодирования токена: {str(e)}")


def create_refresh_token(user_id: int) -> str:
    """
    Создает refresh токен.

    Args:
        user_id: ID пользователя

    Returns:
        str: Refresh токен
    """
    data = {"user_id": user_id, "type": "refresh"}
    expire = datetime.now(timezone.utc) + timedelta(days=7)  # Refresh токен на 7 дней
    data.update({"exp": expire})
    return jwt.encode(data, SECRET_KEY, algorithm=ALGORITHM)


def generate_token_signature(token: str, secret: str) -> str:
    """
    Генерирует подпись для токена.

    Args:
        token: Токен для подписи
        secret: Секретный ключ

    Returns:
        str: Подпись токена
    """
    return hashlib.sha256(f"{token}{secret}".encode()).hexdigest()
