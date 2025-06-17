# 🎯 План UI разработки (TDD "сверху вниз")

## ✅ Выполнено:
- [x] Перемещение `tests/system/test_authorization.py` → `tests/integration/test_system_initializer_auth.py`
- [x] Настройка Chrome WebDriver для UI тестов
- [x] Добавлены новые роуты: `/models`, `/history`, `/settings`, `/logs`, `/help`
- [x] Улучшены фикстуры и управление портами в `conftest.py`
- [x] **КРИТИЧНО ИСПРАВЛЕНО**: UI тесты AI моделей теперь работают ✅
- [x] **Гибридный подход**: Статические + динамические элементы в тестах
- [x] **Безопасная очистка портов**: Избегание завершения системных процессов
- [x] **Стабильный Chrome WebDriver**: Оптимизация для Windows + старые GPU
- [x] **App Manager**: Улучшенная логика запуска/остановки приложения
- [x] **Базовые HTML шаблоны**: Созданы templates для всех основных страниц
- [x] **Навигация**: Обновлена base.html с полной навигацией

## 🔄 В работе:

### 🚨 **НОВАЯ КРИТИЧЕСКАЯ ПРОБЛЕМА:**
**UI тест `test_history_item_routing` падает** - JavaScript не работает с элементами `.history-item`

**Причины:**
- Отсутствует JavaScript обработчик для кликов по истории
- Элементы истории статичные, нет `data-history-id`
- Нет интеграции с реальными данными истории

**Требуется:**
1. ✅ Создать `static/js/history.js` с обработчиками кликов
2. ✅ Обновить `templates/components/command_history.html` с data-атрибутами
3. ✅ Создать `templates/history_details.html` для детальной страницы
4. 🔄 Добавить API для получения истории команд
5. 🔄 Интегрировать с БД для реальных данных

### 🎯 **Следующие шаги:**

1. **ИСПРАВИТЬ test_history_item_routing**
2. **Проверить остальные UI тесты в test_routing.py**
3. **Создать недостающие шаблоны** (tasks.html, history_details.html и др.)

**Команды для проверки:**
```bash
# Исправить конкретный тест
poetry run pytest tests/ui/e2e/ui/test_routing.py::TestRouting::test_history_item_routing -v -s

# Проверить все роутинг тесты
poetry run pytest tests/ui/e2e/ui/test_routing.py -v --tb=short

# Проверить все UI тесты
poetry run pytest tests/ui/e2e/ui/ -v --tb=short
```

## 📋 План файлов (обновлено):

### 1. **HTML шаблоны** - ЧАСТИЧНО ГОТОВО ✅
```
templates/
├── base.html                        # ✅ ОБНОВЛЕН - полная навигация
├── index.html                       # ✅ ГОТОВ
├── models.html                      # ✅ ГОТОВ
├── history.html                     # ✅ СОЗДАН
├── settings.html                    # ✅ СОЗДАН
├── logs.html                        # ✅ СОЗДАН
├── help.html                        # ✅ СОЗДАН
├── tasks.html                       # 🔄 СОЗДАТЬ
├── task_details.html                # 🔄 СОЗДАТЬ
├── task_create.html                 # 🔄 СОЗДАТЬ
├── history_details.html             # 🔄 СОЗДАТЬ
├── model_settings.html              # 🔄 СОЗДАТЬ
└── components/
    ├── ai_models.html               # ✅ РАБОТАЕТ (гибрид статика+динамика)
    ├── command_history.html         # 🔄 ОБНОВИТЬ - добавить data-history-id
    ├── command_form.html            # ✅ ГОТОВ
    └── modals.html                  # ✅ ГОТОВ
```

### 2. **JavaScript компоненты** - В РАБОТЕ 🔄
```
static/js/
├── main.js                          # ✅ ГОТОВ
├── ai_models.js                     # ✅ РАБОТАЕТ
├── history.js                       # 🔄 СОЗДАТЬ - обработчики кликов
├── command_form.js                  # ✅ ГОТОВ
├── fixes.js                         # ✅ ГОТОВ
└── utils.js                         # ✅ ГОТОВ
```

### 3. **Routes** - ЧАСТИЧНО ГОТОВО ✅
```
routes/
├── main_routes.py                   # ✅ ОБНОВЛЕН - все роуты добавлены
└── api_routes.py                    # 🔄 РАСШИРИТЬ - API для истории
```

### 4. UI тесты - ИСПРАВИТЬ 🚨
```
tests/ui/e2e/ui/
├── test_routing.py                  # 🚨 1 тест падает: test_history_item_routing
├── test_ai_models.py                # ✅ ИСПРАВЛЕН - все тесты проходят
├── test_command_form.py             # 🔄 ПРОВЕРИТЬ
├── test_command_history.py          # 🔄 ПРОВЕРИТЬ
├── test_navigation.py               # 🔄 ПРОВЕРИТЬ
└── другие тесты...                  # 🔄 ПРОВЕРИТЬ
```

## 🚀 Приоритетный порядок (TDD):

### Этап 1: КРИТИЧНО - Исправить падающий тест 🔥
1. **Создать `static/js/history.js`** с обработчиками кликов
2. **Обновить `templates/components/command_history.html`** - добавить статичные элементы с data-history-id
3. **Создать `templates/history_details.html`** для детальной страницы
4. **Проверить** что `test_history_item_routing` проходит

### Этап 2: Завершить остальные UI тесты
5. **Создать недостающие шаблоны** (tasks.html, task_details.html и др.)
6. **Проверить все тесты** в `test_routing.py`
7. **Исправить падающие тесты** в других файлах

### Этап 3: Интеграция с данными
8. **API для истории команд** - `/api/history`
9. **Динамическая загрузка** элементов истории
10. **Интеграция с БД** для реальных данных

## 🎯 Текущие задачи (по приоритету):

### 🚨 **ЗАДАЧА 1: Исправить test_history_item_routing** (КРИТИЧНО)

**Создать файлы:**
```javascript
// static/js/history.js - обработчики кликов
document.addEventListener('DOMContentLoaded', function() {
    const historyItems = document.querySelectorAll('.history-item');
    historyItems.forEach(item => {
        item.addEventListener('click', function() {
            const historyId = this.getAttribute('data-history-id');
            if (historyId) {
                window.location.href = `/history/${historyId}`;
            }
        });
    });
});
```

```html
<!-- templates/components/command_history.html - добавить data-history-id -->
<div class="history-item" data-history-id="cmd_001">...</div>
<div class="history-item" data-history-id="cmd_002">...</div>
```

```html
<!-- templates/history_details.html - страница деталей -->
{% extends "base.html" %}
{% block content %}
<h1>Детали команды {{ command.id }}</h1>
<p>Команда: {{ command.command }}</p>
<p>Статус: {{ command.status }}</p>
{% endblock %}
```

### 🔄 **ЗАДАЧА 2: Проверить остальные UI тесты**
```bash
poetry run pytest tests/ui/e2e/ui/test_routing.py -v --tb=line
```

### 🔄 **ЗАДАЧА 3: Создать недостающие шаблоны**
- templates/tasks.html
- templates/task_details.html
- templates/task_create.html
- templates/model_settings.html

## 📊 Прогресс по файлам:

| Файл | Статус | Приоритет | Комментарий |
|------|--------|-----------|-------------|
| `static/js/history.js` | 🔴 Не существует | **КРИТИЧНО** | Нужен для test_history_item_routing |
| `templates/history_details.html` | 🔴 Не существует | **КРИТИЧНО** | Детальная страница истории |
| `templates/components/command_history.html` | 🟡 Обновить | **Высокий** | Добавить data-history-id |
| `test_routing.py` | 🔴 1 тест падает | **Критично** | test_history_item_routing |
| Остальные UI тесты | 🟡 Не проверены | **Высокий** | Могут падать |
| API для истории | 🔴 Не существует | **Средний** | После исправления тестов |

## 🔧 Команды для выполнения:

### Проверить падающий тест:
```bash
poetry run pytest tests/ui/e2e/ui/test_routing.py::TestRouting::test_history_item_routing -v -s
```

### Проверить все роутинг тесты:
```bash
poetry run pytest tests/ui/e2e/ui/test_routing.py -v --tb=short -x
```

### После исправления - проверить все UI тесты:
```bash
poetry run pytest tests/ui/e2e/ui/ -v --tb=short -x
```

## 🎉 **ПОСЛЕДНИЕ ДОСТИЖЕНИЯ:**

### 17.06.2025 - Создание базовой инфраструктуры ✅
- **HTML шаблоны**: Созданы все основные страницы
- **Навигация**: Обновлена base.html с полными роутами
- **Routes**: Добавлены все недостающие роуты в main_routes.py
- **Архитектурный анализ**: Выявлены проблемы с командами

### Техническая статистика:
- **Созданных шаблонов**: 6 (history.html, settings.html, logs.html, help.html и др.)
- **Обновленных файлов**: 2 (base.html, main_routes.py)
- **Новых роутов**: 4 (/history, /settings, /logs, /help)

### Следующий milestone:
🎯 **Исправить падающий UI тест** → **Проверить остальные тесты** → **API интеграция**

---

**Текущий фокус:** 🔥 Исправление test_history_item_routing через создание JavaScript обработчиков
**Ответственный:** TDD подход - тест должен проходить в первую очередь
**Срок:** Критично - нужно исправить сегодня
**Последнее обновление:** 17.06.2025
```
