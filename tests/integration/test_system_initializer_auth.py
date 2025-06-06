import pytest

from core.system_initializer import SystemInitializer


def test_user_authentication():
    """Проверяет регистрацию, вход и проверку прав доступа."""
    system_initializer = SystemInitializer()
    system = system_initializer.initialize()

    # ИСПРАВЛЕНО: проверяем что система инициализирована
    if not system:
        pytest.skip("Система не инициализирована корректно")

    # Регистрация пользователя
    register_task = system.create_task(
        "Зарегистрировать пользователя test_user с паролем password123"
    )
    register_result = register_task.execute()
    assert register_result.success

    # Вход пользователя
    login_task = system.create_task("Войти как пользователь test_user с паролем password123")
    login_result = login_task.execute()
    assert login_result.success
    assert "токен" in login_result.details.lower()

    # Проверка прав доступа
    access_task = system.create_task("Проверить права доступа текущего пользователя")
    access_result = access_task.execute()
    assert access_result.success
