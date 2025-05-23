# API компонентов

Этот документ описывает API для работы с компонентами Neuro-Link Assistant.

## Реестр компонентов

### Получение реестра

```python
from core.common.registry.component_registry import ComponentRegistry

# Получение глобального реестра
registry = ComponentRegistry.get_instance()

# Создание нового реестра
custom_registry = ComponentRegistry()
```

### Регистрация компонентов

```python
# Регистрация компонента
registry.register("file_system", file_system_instance)

# Проверка наличия компонента
if registry.has("file_system"):
    print("Файловая система зарегистрирована")
```

### Получение компонентов

```python
# Получение компонента
file_system = registry.get("file_system")

# Получение с значением по умолчанию (если компонент не найден)
input_controller = registry.get("input", default_controller)
```

## Файловая система

### Получение экземпляра

```python
from core.common.filesystem.factory import get_file_system

# Получение файловой системы для текущей платформы
fs = get_file_system()

# Получение конкретной реализации
from core.platform.windows.filesystem.win32_file_system import Win32FileSystem
win_fs = Win32FileSystem()
```

### Основные операции

```python
# Чтение файла
content = fs.read_file("path/to/file.txt")

# Запись файла
fs.write_file("path/to/file.txt", "Содержимое файла")

# Проверка существования
if fs.file_exists("path/to/file.txt"):
    print("Файл существует")

# Получение информации о файле
mod_time = fs.get_file_modification_time("path/to/file.txt")

# Работа с директориями
directories = fs.list_directory_names("path/to/dir")
```

## Подсистема ввода

### Получение контроллера ввода

```python
from core.common.input.factory import get_input_controller

# Получение контроллера ввода для текущей платформы
input_ctrl = get_input_controller()
```

### Работа с клавиатурой

```python
# Доступ к контроллеру клавиатуры
keyboard = input_ctrl.keyboard

# Нажатие клавиши
keyboard.press_key("a")

# Ввод текста
keyboard.type_text("Hello, World!")

# Комбинации клавиш
keyboard.hotkey("ctrl", "c")  # Копировать
```

### Работа с мышью

```python
# Доступ к контроллеру мыши
mouse = input_ctrl.mouse

# Перемещение курсора
mouse.move_to(100, 200)

# Клики
mouse.click()
mouse.right_click()
mouse.double_click()

# Перетаскивание
mouse.drag_to(300, 400)
```

## Создание собственных компонентов

### Создание реализации интерфейса

```python
from core.common.filesystem.base import AbstractFileSystem

class CustomFileSystem(AbstractFileSystem):
    def file_exists(self, path: str) -> bool:
        # Реализация метода
        return True

    def read_file(self, path: str, encoding: str = "utf-8") -> str:
        # Реализация метода
        return "File content"

    # Реализация остальных методов абстрактного класса
```

### Регистрация компонента

```python
# Получение реестра
registry = ComponentRegistry.get_instance()

# Создание экземпляра компонента
custom_fs = CustomFileSystem()

# Регистрация компонента
registry.register("custom_file_system", custom_fs)
```

### Использование компонента

```python
# Получение компонента через реестр
fs = registry.get("custom_file_system")

# Использование компонента
content = fs.read_file("some/path.txt")
```

## Требования к компонентам

1. Компоненты должны реализовывать соответствующие абстрактные интерфейсы
2. Компоненты должны быть потокобезопасными, если используются из разных потоков
3. Компоненты должны корректно обрабатывать ошибки и исключения
4. Компоненты должны освобождать ресурсы при удалении или завершении работы
