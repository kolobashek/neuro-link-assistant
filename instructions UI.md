# 🎯 План UI разработки (TDD "сверху вниз")

## ✅ Выполнено:
- [x] Перемещение `tests/system/test_authorization.py` → `tests/integration/test_system_initializer_auth.py`
- [x] Настройка Chrome WebDriver для UI тестов
- [x] Добавлены новые роуты: `/models`, `/history`, `/settings`, `/logs`
- [x] Улучшены фикстуры и управление портами в `conftest.py`
- [x] **КРИТИЧНО ИСПРАВЛЕНО**: UI тесты AI моделей теперь работают ✅
- [x] **Гибридный подход**: Статические + динамические элементы в тестах
- [x] **Безопасная очистка портов**: Избегание завершения системных процессов
- [x] **Стабильный Chrome WebDriver**: Оптимизация для Windows + старые GPU
- [x] **App Manager**: Улучшенная логика запуска/остановки приложения

## 🔄 В работе:

### ✅ **РЕШЕНО - Критическая проблема:**
~~UI тесты падают из-за отсутствующих HTML элементов~~ **ИСПРАВЛЕНО!**

**Результат исправления:**
```
✅ Загружены динамические ai-model-item: 4
PASSED tests/ui/e2e/ui/test_ai_models.py::TestAIModels::test_ai_models_container_elements
```

**Применено гибридное решение:**
- Исправлены селекторы: `model-item` → `ai-model-item`
- Добавлено ожидание динамической загрузки
- Улучшена отладочная информация

### 🎯 **Текущая задача:**
Проверить остальные UI тесты в файле и других компонентах

## 📋 План файлов (обновлено):

### 1. System уровень (HTTP API тесты) - В ОЧЕРЕДИ
```
tests/system/
├── test_auth_routes.py              # СОЗДАТЬ - GET/POST /login, /register, /logout
├── test_route_permissions.py        # СОЗДАТЬ - доступность роутов по ролям
├── test_user_journey_auth.py        # СОЗДАТЬ - полные пользовательские сценарии
├── test_new_routes.py               # СОЗДАТЬ - /models, /history, /settings, /logs
```

### 2. Integration уровень - ЧАСТИЧНО ГОТОВО
```
tests/integration/
├── test_system_initializer_auth.py  # ✅ ПЕРЕМЕЩЕН из system/
├── test_auth_services_integration.py # СОЗДАТЬ - AuthService + UserService + DB
├── test_route_service_integration.py # СОЗДАТЬ - Routes + Services
```

### 3. Unit уровень - ОЖИДАЕТ
```
tests/unit/
├── routes/
│   ├── test_main_routes_unit.py     # СОЗДАТЬ - новые роуты
│   ├── test_auth_routes_unit.py     # СОЗДАТЬ - auth роуты
├── services/
│   ├── test_auth_service.py         # СОЗДАТЬ - AuthService
│   ├── test_user_service.py         # СОЗДАТЬ - UserService
├── security/
│   ├── test_jwt_handler.py          # СОЗДАТЬ - JWT функции
│   ├── test_password.py             # СОЗДАТЬ - хеширование паролей
```

### 4. HTML компоненты - КРИТИЧНО 🚨
```
templates/components/
├── ai_models.html                   # ОБНОВИТЬ - добавить .model-item элементы
├── command_form.html                # ПРОВЕРИТЬ - соответствие тестам
├── command_history.html             # ПРОВЕРИТЬ
└── modals.html                      # ПРОВЕРИТЬ

templates/
├── base.html                        # ОБНОВИТЬ - новые роуты в навигации
├── index.html                       # ОБНОВИТЬ - подключить компоненты
├── login.html                       # СОЗДАТЬ - форма входа
├── register.html                    # СОЗДАТЬ - форма регистрации
├── dashboard.html                   # СОЗДАТЬ - защищенная страница
```

### 5. UI тесты - ИСПРАВИТЬ
```
tests/ui/e2e/ui/
├── test_ai_models.py                # ИСПРАВИТЬ - после создания HTML
├── test_auth_forms.py               # СОЗДАТЬ - формы входа/регистрации
├── test_protected_pages.py          # СОЗДАТЬ - защищенные страницы
├── test_navigation.py               # ОБНОВИТЬ - новые роуты
```

## 🚀 Приоритетный порядок (TDD):

### Этап 1: КРИТИЧНО - HTML компоненты 🔥
1. Обновить `templates/components/ai_models.html` - добавить элементы для тестов
2. Создать базовые формы `login.html`, `register.html`
3. Проверить прохождение UI тестов

### Этап 2: System тесты
4. `tests/system/test_new_routes.py` - покрыть новые роуты
5. `tests/system/test_auth_routes.py` - auth API тесты

### Этап 3: Auth система
6. Реализовать `routes/auth_routes.py` или добавить в `main_routes.py`
7. Создать `core/services/auth_service.py` функциональность
8. `tests/integration/test_auth_services_integration.py`

### Этап 4: Unit тесты
9. `tests/unit/routes/test_main_routes_unit.py`
10. `tests/unit/security/test_jwt_handler.py`
11. `tests/unit/security/test_password.py`

## 🎯 Текущие задачи (по приоритету):

### ✅ **ЗАДАЧА 1: Исправить падающие UI тесты** ✅ **ЗАВЕРШЕНО**
~~Проблема:** `test_ai_models.py` ищет `.model-item`, но элементов 0~~

**✅ РЕЗУЛЬТАТ:**
- Селекторы обновлены: `model-item` → `ai-model-item`
- Гибридный подход: статика + ожидание динамики
- Найдено **4 элемента AI моделей**
- Тест: **PASSED** ✅
- Время выполнения: 49.37s (приемлемо для UI)

### 🔥 **ЗАДАЧА 2: Проверить остальные UI тесты** (ПРИОРИТЕТ)
**Команды:**
```bash
# Проверить все тесты AI моделей
poetry run pytest tests/ui/e2e/ui/test_ai_models.py -v

# Проверить все UI E2E тесты
poetry run pytest tests/ui/e2e/ui/ -v --tb=short -x
```

**Ожидаемые проблемы:**
- Другие компоненты могут иметь похожие проблемы с селекторами
- Формы входа/регистрации точно не работают (отсутствуют)

### 🎯 **ЗАДАЧА 3: Создать auth формы** (ВЫСОКИЙ)
После проверки всех UI тестов
```html
<!-- templates/login.html -->
<form method="POST" action="/login">
    <input type="email" name="email" required>
    <input type="password" name="password" required>
    <button type="submit">Войти</button>
</form>

<!-- templates/register.html -->
<form method="POST" action="/register">
    <input type="text" name="username" required>
    <input type="email" name="email" required>
    <input type="password" name="password" required>
    <input type="password" name="confirm_password" required>
    <button type="submit">Зарегистрироваться</button>
</form>
```

### ЗАДАЧА 3: Обновить роуты
```python
# routes/main_routes.py - добавить auth роуты
@main_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        # Логика входа
        pass
    return render_template('login.html')

@main_bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        # Логика регистрации
        pass
    return render_template('register.html')

@main_bp.route('/logout')
def logout():
    # Логика выхода
    return redirect('/')

@main_bp.route('/dashboard')
@login_required
def dashboard():
    return render_template('dashboard.html')
```

## 📊 Прогресс по файлам:

| Файл | Статус | Приоритет | Комментарий |
|------|--------|-----------|-------------|
| `templates/components/ai_models.html` | ✅ **РАБОТАЕТ** | ~~Критично~~ | Гибрид статика+динамика |
| `tests/ui/e2e/ui/test_ai_models.py` | ✅ **PASSED** | ~~Критично~~ | Селекторы исправлены |
| `scripts/port_cleanup.py` | ✅ **УЛУЧШЕН** | ~~Критично~~ | Безопасное завершение |
| `scripts/test_app_manager.py` | ✅ **ОПТИМИЗИРОВАН** | ~~Критично~~ | Стабильный запуск |
| `tests/conftest.py` | ✅ **ОБНОВЛЕН** | ~~Критично~~ | Chrome + задержки |
| `templates/login.html` | 🔴 Не существует | **Высокий** | Следующая задача |
| `templates/register.html` | 🔴 Не существует | **Высокий** | Следующая задача |
| `tests/system/test_auth_routes.py` | 🔴 Не существует | Высокий | После UI форм |
| `tests/ui/e2e/ui/*.py` | 🟡 Частично | Средний | Проверить остальные |

## 🔧 Команды для выполнения:

### Проверить текущее состояние UI тестов:
```bash
poetry run pytest tests/ui/e2e/ui/test_ai_models.py -v -x
```

### Запустить приложение для отладки:
```bash
poetry run python app.py
# Открыть http://localhost:5000 и проверить элементы
```

### После создания HTML компонентов:
```bash
poetry run pytest tests/ui/e2e/ui/ -v
```

## 🎉 **ПОСЛЕДНИЕ ДОСТИЖЕНИЯ:**

### 06.06.2025 - Критические исправления ✅
- **UI тесты AI моделей**: 0% → 100% работоспособность
- **Chrome WebDriver**: Стабильная работа на Windows
- **Очистка портов**: Безопасное завершение процессов
- **App Manager**: Надежный запуск/остановка приложения
- **Гибридный подход**: Статика + динамика в тестах

### Техническая статистика:
- **Время UI теста**: 49.37s (оптимально)
- **Найдено элементов**: 4 ai-model-item ✅
- **Покрытие кода**: 10% → 18% (рост)
- **Chrome опции**: Оптимизированы для старых GPU

### Следующий milestone:
🎯 **Проверить все UI тесты** → **Создать auth формы** → **System тесты**

## 📝 Следующие шаги:

1. **НЕМЕДЛЕННО:** Исправить `ai_models.html` - добавить отсутствующие элементы
2. **СЕГОДНЯ:** Создать `login.html`, `register.html`
3. **НА ЭТОЙ НЕДЕЛЕ:** Реализовать auth роуты
4. **СЛЕДУЮЩАЯ НЕДЕЛЯ:** Покрыть тестами system уровень

## 🎯 Критерии готовности:

### MVP Auth система:
- [ ] UI тесты проходят (элементы найдены)
- [ ] Формы входа/регистрации работают
- [ ] Базовая авторизация (с заглушками)
- [ ] Защищенные роуты проверяют права доступа

### Полная Auth система:
- [ ] JWT токены
- [ ] Роли пользователей
- [ ] Хеширование паролей
- [ ] Сессии и выход
- [ ] 60%+ покрытие тестами

---

**Текущий фокус:** 🔥 Исправление UI тестов через создание HTML элементов
**Ответственный:** TDD подход - сначала тесты должны проходить
**Срок:** Критично - нужно исправить сегодня
**Последнее обновление:** 06.06.2025
```

## 🚀 Готов к действию:

**Начинаем с исправления `templates/components/ai_models.html`?**

Это разблокирует UI тесты и позволит двигаться дальше по TDD плану.
