# Подход к тестированию

## Философия тестирования

В Neuro-Link Assistant применяется подход TDD (Test-Driven Development) с особенностью "сверху вниз":

1. Сначала создаются **системные тесты** ("гранд-тесты"), проверяющие работу системы в целом
2. На основе системных тестов определяются необходимые компоненты и их интерфейсы
3. Далее создаются **интеграционные тесты** для проверки взаимодействия компонентов
4. Наконец разрабатываются **модульные тесты** для детальной проверки отдельных компонентов

Такой подход позволяет:
- Получить раннее представление о работе системы в целом
- Выявить проблемы интеграции на ранних этапах
- Естественным образом определить необходимые компоненты и их интерфейсы

## Уровни тестирования

### 1. Системные тесты (гранд-тесты)

Проверяют полный рабочий процесс приложения:

```python
def test_basic_application_flow(self):
    # Инициализация системы
    system = SystemInitializer().initialize()

    # Проверка готовности подсистем
    assert system.is_component_registered("filesystem")

    # Создание и выполнение задачи
    task = system.create_task("Открыть файл test.txt")
    result = task.execute()
    assert result.success
```

Расположение: `tests/system/`

### 2. Интеграционные тесты

Проверяют взаимодействие между компонентами:

```python
def test_filesystem_task_integration(self):
    registry = ComponentRegistry()
    registry.register("filesystem", MockFileSystem())

    task = FileTask("test.txt", registry)
    result = task.execute()

    fs = registry.get("filesystem")
    assert fs.was_accessed("test.txt")
```

Расположение: `tests/integration/`

### 3. Модульные тесты

Проверяют отдельные компоненты в изоляции:

```python
def test_file_system_operations(self):
    fs = Win32FileSystem()

    fs.write_file("test.txt", "Hello, World!")
    assert fs.file_exists("test.txt")
    content = fs.read_file("test.txt")
    assert content == "Hello, World!"
```

Расположение: `tests/unit/`

## Использование моков

Для изоляции тестируемых компонентов:

```python
# Создание мока
mock_filesystem = MagicMock()
mock_filesystem.file_exists.return_value = True
mock_filesystem.read_file.return_value = "mock content"

# Использование мока
registry.register("filesystem", mock_filesystem)
task = Task("Read test.txt", registry)
result = task.execute()

# Проверка вызовов
mock_filesystem.read_file.assert_called_once_with("test.txt")
```

## Фикстуры pytest

Для переиспользования тестовых объектов:

```python
@pytest.fixture
def component_registry():
    registry = ComponentRegistry()
    registry.register("error_handler", ErrorHandler())
    return registry

@pytest.fixture
def system(component_registry):
    initializer = SystemInitializer(component_registry)
    return initializer.initialize()

def test_system_component_access(system):
    assert system.is_component_registered("error_handler")
```

## Запуск тестов

```bash
# Запуск всех тестов
pytest

# Запуск системных тестов
pytest tests/system/

# Запуск с отчетом о покрытии
pytest --cov=core

# Запуск конкретного теста
pytest tests/system/test_application_workflow.py::TestApplicationWorkflow::test_basic_application_flow
```

## Текущее состояние тестирования

✅ **Реализованы**:
- Системный тест базового рабочего процесса
- Модульные тесты реестра компонентов и обработчика ошибок
- Тесты подсистемы ввода
- Частичные тесты файловой системы

❌ **В разработке**:
- Интеграционные тесты между подсистемами
- Тесты для компьютерного зрения, веб-взаимодействия, LLM

## Рекомендации

1. **Следуйте процессу TDD**:
   - Красный: сначала напишите тест, который не проходит
   - Зеленый: реализуйте минимальный код для прохождения теста
   - Рефакторинг: улучшите код, сохраняя его функциональность

2. **Изолируйте тесты**:
   - Каждый тест должен быть независимым
   - Используйте моки для внешних зависимостей
   - Очищайте тестовое окружение после каждого теста

3. **Пишите ясные тесты**:
   - Следуйте паттерну Arrange-Act-Assert
   - Давайте тестам говорящие имена
   - Проверяйте только одну концепцию в каждом тесте
