# Настройка среды разработки

Это руководство поможет вам настроить среду разработки для проекта Neuro-Link Assistant.

## Системные требования

- Windows 10 или новее (проект ориентирован на Windows)
- Python 3.8.1 или новее
- Poetry для управления зависимостями
- Docker и Docker Compose (для базы данных)
- Git

## Установка базовых инструментов

### 1. Python

Скачайте и установите Python с [официального сайта](https://www.python.org/downloads/).

Проверьте установку:
```bash
python --version
```

### 2. Poetry

Установите Poetry следуя [официальной инструкции](https://python-poetry.org/docs/#installation):

#### Windows PowerShell:
```bash
(Invoke-WebRequest -Uri https://install.python-poetry.org -UseBasicParsing).Content | python -
```

Добавьте Poetry в PATH и настройте оболочку:
```bash
$Env:Path += ";$Env:APPDATA\Python\Scripts"
poetry config virtualenvs.in-project true
```

## Настройка проекта

### 1. Клонирование репозитория

```bash
git clone https://github.com/kolobashek/neuro-link-assistant.git
cd neuro-link-assistant
```

### 2. Установка зависимостей с Poetry

```bash
# Установка всех зависимостей
poetry install

# Активация виртуального окружения
poetry shell
```

## Настройка базы данных

Проект использует PostgreSQL через Docker для работы с данными.

### 1. Запуск базы данных

```bash
# Запуск контейнеров PostgreSQL и pgAdmin
docker-compose up -d postgres pgadmin
```

### 2. Проверка состояния

```bash
docker-compose ps
```

### 3. Подключение к pgAdmin

1. Откройте в браузере http://localhost:5050
2. Войдите с учетными данными:
   - Email: admin@example.com
   - Пароль: admin_password
3. Добавьте сервер:
   - Имя: NeuroLink DB
   - Хост: postgres
   - Порт: 5432
   - База данных: neurolink_db
   - Пользователь: neurolink
   - Пароль: secure_password

### 4. Применение миграций

```bash
# С использованием скрипта из Poetry
poetry run db-migrate
```

## Настройка IDE

### Visual Studio Code

1. Установите VS Code с [официального сайта](https://code.visualstudio.com/)
2. Установите рекомендуемые расширения:
   - Python
   - Pylance
   - Python Test Explorer
   - Python Docstring Generator
   - Docker

3. Настройте Python интерпретатор:
   - Нажмите F1 → "Python: Select Interpreter"
   - Выберите интерпретатор из .venv проекта

4. Настройка линтера и форматтера:
   ```json
   // settings.json
   {
     "python.linting.enabled": true,
     "python.linting.pylintEnabled": true,
     "python.linting.mypyEnabled": true,
     "python.formatting.provider": "black",
     "python.formatting.blackArgs": ["--line-length", "100"],
     "editor.formatOnSave": true
   }
   ```

## Проверка установки

```bash
# Запуск тестов
poetry run pytest

# Проверка системных тестов
poetry run pytest tests/system

# Проверка с покрытием
poetry run pytest --cov=core
```

## Запуск приложения (при наличии веб-интерфейса)

```bash
# Запуск Flask сервера
poetry run python app.py
```

## Работа с Docker

```bash
# Запуск базы данных
poetry run db-up

# Остановка базы данных
poetry run db-down

# Просмотр логов
poetry run db-logs
```

## Устранение типичных проблем

### Проблемы с Poetry

**Ошибка**: Poetry не может разрешить зависимости

**Решение**:
```bash
poetry update
poetry install --no-cache
```

### Проблемы с Docker

**Ошибка**: Не удается подключиться к базе данных

**Решение**:
```bash
# Проверьте состояние контейнеров
docker-compose ps

# Перезапустите контейнеры
poetry run db-restart

# Проверьте логи
poetry run db-logs
```

### Проблемы с зависимостями Windows

**Ошибка**: Не устанавливаются пакеты pywin32 или WMI

**Решение**:
```bash
# Установите вручную через pip внутри виртуального окружения
poetry shell
pip install pywin32==301
pip install WMI==1.5.1
```

## Дополнительные ресурсы

- [Документация Poetry](https://python-poetry.org/docs/)
- [Документация Docker Compose](https://docs.docker.com/compose/)
- [Руководство по PyTest](https://docs.pytest.org/)
