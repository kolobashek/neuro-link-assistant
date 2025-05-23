# API ядра системы

## Общий обзор

Ядро системы Neuro-Link Assistant состоит из нескольких основных классов, обеспечивающих базовую функциональность:

- `System` - основной класс, предоставляющий высокоуровневый API для работы с системой
- `SystemInitializer` - отвечает за инициализацию и завершение работы системы
- `ComponentRegistry` - реестр компонентов, обеспечивающий их регистрацию и поиск
- `PluginManager` - управляет плагинами системы
- `Task` - представляет задачу для выполнения системой

## System

Основной класс системы, предоставляющий API для работы с системой.

### Методы

#### `__init__(registry)`
Инициализирует систему с указанным реестром компонентов.

```python
def __init__(self, registry):
    """
    Инициализирует систему.

    Args:
        registry (ComponentRegistry): Реестр компонентов
    """
```

#### `is_component_registered(name)`
Проверяет наличие компонента в системе.

```python
def is_component_registered(self, name):
    """
    Проверяет, зарегистрирован ли компонент в системе.

    Args:
        name (str): Имя компонента

    Returns:
        bool: True, если компонент зарегистрирован, иначе False
    """
```

#### `create_task(description)`
Создает задачу на основе описания.

```python
def create_task(self, description):
    """
    Создает задачу на основе текстового описания.

    Args:
        description (str): Описание задачи

    Returns:
        Task: Созданная задача
    """
```

#### `get_component(name)`
Получает компонент из реестра по имени.

```python
def get_component(self, name):
    """
    Возвращает компонент по имени.

    Args:
        name (str): Имя компонента

    Returns:
        object: Компонент или None, если компонент не найден
    """
```

## SystemInitializer

Отвечает за инициализацию системы и регистрацию базовых компонентов.

### Методы

#### `__init__(registry=None)`
Создает инициализатор с указанным реестром.

```python
def __init__(self, registry=None):
    """
    Инициализирует инициализатор системы.

    Args:
        registry (ComponentRegistry, optional): Реестр компонентов.
            Если не указан, создается новый.
    """
```

#### `initialize()`
Инициализирует систему.

```python
def initialize(self):
    """
    Инициализирует систему.

    Returns:
        System: Инициализированная система
    """
```

#### `register_core_components()`
Регистрирует основные компоненты системы.

```python
def register_core_components(self):
    """
    Регистрирует основные компоненты системы.

    Returns:
        bool: True в случае успешной регистрации
    """
```

#### `shutdown()`
Завершает работу системы.

```python
def shutdown(self):
    """
    Завершает работу системы.

    Returns:
        bool: True в случае успешного завершения
    """
```

## ComponentRegistry

Реестр компонентов, обеспечивающий их регистрацию и поиск.

### Методы

#### `register(name, component)`
Регистрирует компонент в реестре.

```python
def register(self, name, component):
    """
    Регистрирует компонент в реестре.

    Args:
        name (str): Имя компонента
        component (object): Экземпляр компонента

    Returns:
        bool: True в случае успешной регистрации
    """
```

#### `get(name, default=None)`
Возвращает компонент по имени.

```python
def get(self, name, default=None):
    """
    Возвращает компонент по имени.

    Args:
        name (str): Имя компонента
        default (object, optional): Значение по умолчанию,
            возвращаемое если компонент не найден

    Returns:
        object: Компонент или default, если компонент не найден
    """
```

#### `has(name)`
Проверяет наличие компонента в реестре.

```python
def has(self, name):
    """
    Проверяет наличие компонента в реестре.

    Args:
        name (str): Имя компонента

    Returns:
        bool: True, если компонент зарегистрирован, иначе False
    """
```

## Task

Представляет задачу для выполнения системой.

### Методы

#### `__init__(description, registry)`
Инициализирует задачу.

```python
def __init__(self, description, registry):
    """
    Инициализирует задачу.

    Args:
        description (str): Описание задачи
        registry (ComponentRegistry): Реестр компонентов
    """
```

#### `execute()`
Выполняет задачу.

```python
def execute(self):
    """
    Выполняет задачу.

    Returns:
        TaskResult: Результат выполнения задачи
    """
```

## PluginManager

Управляет плагинами системы.

### Методы

#### `__init__(registry=None)`
Инициализирует менеджер плагинов.

```python
def __init__(self, registry=None):
    """
    Инициализирует менеджер плагинов.

    Args:
        registry (ComponentRegistry, optional): Реестр компонентов
    """
```

#### `discover_plugins()`
Обнаруживает доступные плагины.

```python
def discover_plugins(self):
    """
    Обнаруживает доступные плагины.

    Returns:
        list: Список имен файлов плагинов
    """
```

#### `load_plugin(plugin_name)`
Загружает плагин по имени.

```python
def load_plugin(self, plugin_name):
    """
    Загружает плагин.

    Args:
        plugin_name (str): Имя плагина

    Returns:
        object: Экземпляр плагина или None в случае ошибки
    """
```

#### `load_plugins()`
Загружает все доступные плагины.

```python
def load_plugins(self):
    """
    Загружает все доступные плагины.

    Returns:
        int: Количество успешно загруженных плагинов
    """
```

#### `unload_plugin(plugin_name)`
Выгружает плагин.

```python
def unload_plugin(self, plugin_name):
    """
    Выгружает плагин.

    Args:
        plugin_name (str): Имя плагина

    Returns:
        bool: True в случае успешной выгрузки
    """
```

## Примеры использования

### Инициализация системы

```python
# Создание и инициализация системы
initializer = SystemInitializer()
system = initializer.initialize()

# Проверка наличия компонентов
if system.is_component_registered("filesystem"):
    fs = system.get_component("filesystem")
    content = fs.read_file("config.txt")
```

### Создание и выполнение задачи

```python
# Создание задачи
task = system.create_task("Открыть файл example.txt")

# Выполнение задачи
result = task.execute()

# Проверка результата
if result.success:
    print(f"Задача выполнена успешно: {result.details}")
else:
    print(f"Ошибка выполнения задачи: {result.error}")
```

### Работа с плагинами

```python
# Получение менеджера плагинов
plugin_manager = system.get_component("plugin_manager")

# Загрузка плагинов
loaded_count = plugin_manager.load_plugins()
print(f"Загружено плагинов: {loaded_count}")

# Использование конкретного плагина
plugin = plugin_manager.get_plugin("image_processor")
if plugin:
    plugin.process_image("image.jpg")
```
