"""
Модуль для работы с паролями.
"""

import hashlib
import secrets
from typing import Optional, Tuple


def hash_password(password: str, salt: Optional[str] = None) -> Tuple[str, str]:
    """
    Хеширует пароль с солью.

    Args:
        password: Пароль для хеширования
        salt: Соль (если не указана, генерируется автоматически)

    Returns:
        Tuple[str, str]: Кортеж (хеш_пароля, соль)
    """
    salt = salt or secrets.token_hex(16)  # Используем или переданную соль, или генерируем новую
    # Используем SHA-256 для хеширования пароля с солью
    password_hash = hashlib.sha256(f"{password}{salt}".encode()).hexdigest()
    return password_hash, salt


def verify_password(password: str, stored_hash: str, salt: str) -> bool:
    """
    Проверяет пароль против сохраненного хеша.

    Args:
        password: Вводимый пароль
        stored_hash: Сохраненный хеш
        salt: Соль

    Returns:
        bool: True если пароль верный
    """
    password_hash = hashlib.sha256(f"{password}{salt}".encode()).hexdigest()
    return password_hash == stored_hash


def generate_secure_password(length: int = 12) -> str:
    """
    Генерирует безопасный пароль.

    Args:
        length: Длина пароля

    Returns:
        str: Сгенерированный пароль
    """
    import string

    characters = string.ascii_letters + string.digits + "!@#$%^&*"
    return "".join(secrets.choice(characters) for _ in range(length))
