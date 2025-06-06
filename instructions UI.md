🎯 План файлов (по приоритету TDD):
1. Перемещение существующих файлов
# Действие: mv
tests/system/test_authorization.py → tests/integration/test_system_initializer_auth.py

Copy

Execute

2. System уровень (HTTP API тесты)
tests/system/
├── test_auth_routes.py              # СОЗДАТЬ - GET/POST /login, /register, /logout
├── test_route_permissions.py        # СОЗДАТЬ - доступность роутов по ролям
├── test_user_journey_auth.py        # СОЗДАТЬ - полные пользовательские сценарии

Copy

Apply

3. Integration уровень (компоненты + сервисы)
tests/integration/
├── test_system_initializer_auth.py  # ПЕРЕМЕСТИТЬ - из system/
├── test_auth_services_integration.py # СОЗДАТЬ - AuthService + UserService + DB
├── test_route_service_integration.py # СОЗДАТЬ - Routes + Services

Copy

Apply

4. Unit уровень (изолированные компоненты)
tests/unit/
├── routes/
│   ├── test_auth_routes_unit.py     # СОЗДАТЬ - изолированные роуты
├── services/
│   ├── test_auth_service.py         # СОЗДАТЬ - AuthService
│   ├── test_user_service.py         # СОЗДАТЬ - UserService
│   ├── test_permission_service.py   # СОЗДАТЬ - PermissionService
├── security/
│   ├── test_jwt_handler.py          # СОЗДАТЬ - JWT функции
│   ├── test_password.py             # СОЗДАТЬ - хеширование паролей

Copy

Apply

5. Contract тесты (новая категория)
tests/contract/
├── api/
│   ├── test_auth_api_contracts.py   # СОЗДАТЬ - API контракты auth

Copy

Apply

6. Обновление фикстур
tests/conftest.py                    # ДОПОЛНИТЬ - auth фикстуры

Copy

Apply

7. UI тесты (исправить существующие)
tests/ui/e2e/ui/
├── test_auth_forms.py               # СОЗДАТЬ - формы входа/регистрации
├── test_protected_pages.py          # СОЗДАТЬ - защищенные страницы

Copy

Apply

🚀 Порядок создания (TDD "сверху вниз"):
Этап 1: System тесты (основа)
tests/system/test_auth_routes.py
tests/system/test_route_permissions.py
Перемещение: test_authorization.py → test_system_initializer_auth.py
Этап 2: Integration тесты
tests/integration/test_auth_services_integration.py
tests/integration/test_route_service_integration.py
Этап 3: Unit тесты
tests/unit/services/test_auth_service.py
tests/unit/security/test_jwt_handler.py
tests/unit/security/test_password.py
Этап 4: Фикстуры и поддержка
Обновление tests/conftest.py
tests/contract/api/test_auth_api_contracts.py
✅ Проверка на дублирование:
НЕ создаем (уже есть похожие):

❌ test_authorization.py уже переместили в integration
❌ Дублирующие фикстуры в conftest.py
Создаем новые (отсутствуют):

✅ HTTP API тесты для auth
✅ Unit тесты для security компонентов
✅ Integration тесты сервисов
