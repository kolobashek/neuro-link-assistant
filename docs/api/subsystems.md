# API подсистем Neuro-Link Assistant

## Обзор

В этом документе описаны программные интерфейсы (API) основных подсистем Neuro-Link Assistant, предоставляющие доступ к функциональности системы.

## Файловая подсистема

### Получение файловой системы

```python
from core.common.filesystem.factory import get_file_system

# Получение платформо-зависимой реализации
file_system = get_file_system()
```

### Основные операции

```python
# Проверка существования файла
if file_system.file_exists("path/to/file.txt"):
    print("Файл существует")

# Чтение файла
content = file_system.read_file("path/to/file.txt")

# Запись файла
file_system.write_file("output.txt", "Hello, World!")

# Работа с директориями
dirs = file_system.list_directory_names("/path/to/dir")
```

## Подсистема ввода

### Получение контроллера ввода

```python
from core.common.input.factory import get_input_controller

# Получение контроллера ввода
input_ctrl = get_input_controller()
```

### Работа с клавиатурой

```python
# Доступ к клавиатуре
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
# Доступ к мыши
mouse = input_ctrl.mouse

# Перемещение курсора
mouse.move_to(100, 200)

# Клик
mouse.click()

# Правый клик
mouse.right_click()

# Двойной клик
mouse.double_click()

# Перетаскивание
mouse.drag_to(300, 400)
```

## Подсистема компьютерного зрения

### Получение компонентов

```python
from core.vision.screen_capture import ScreenCapture
from core.vision.element_recognition import ElementRecognition

# Создание компонентов
screen_capture = ScreenCapture()
element_recognition = ElementRecognition()
```

### Основные операции

```python
# Захват скриншота
screenshot = screen_capture.capture_screen()

# Поиск элемента по шаблону
template = screen_capture.load_image("button_template.png")
location = element_recognition.find_element(screenshot, template)
if location:
    x, y, width, height = location
    print(f"Элемент найден на позиции ({x}, {y})")

# Распознавание текста на экране
text_regions = element_recognition.find_text(screenshot, "Найти этот текст")
```

## Подсистема веб-взаимодействия

### Инициализация браузера

```python
from core.web.browser_controller import BrowserController
from core.web.element_finder import ElementFinder

# Создание контроллера
browser = BrowserController()
browser.initialize("chrome")  # или "firefox", "edge"

# Создание компонента поиска элементов
finder = ElementFinder(browser)
```

### Основные операции

```python
# Навигация
browser.navigate("https://example.com")

# Поиск элементов
element = finder.find_element_by_id("login-button")
elements = finder.find_elements_by_class("item")

# Взаимодействие с элементами
element.click()
element.type_text("Hello")

# Извлечение данных
page_title = browser.get_title()
page_text = browser.get_page_text()
element_text = element.get_text()
```

## Подсистема LLM

### Инициализация клиента

```python
from core.llm.api_client import LLMClient
from core.llm.prompt_processor import PromptProcessor

# Создание клиента для выбранной модели
llm_client = LLMClient(model="gpt-4")

# Создание процессора промптов
prompt_processor = PromptProcessor()
```

### Основные операции

```python
# Создание и оптимизация промпта
prompt = prompt_processor.create_prompt(
    task="Суммаризация текста",
    content="Длинный текст для обработки...",
    max_tokens=100
)

# Генерация текста
response = llm_client.generate_text(prompt)

# Чат-формат взаимодействия
messages = [
    {"role": "system", "content": "Вы полезный ассистент."},
    {"role": "user", "content": "Объясните концепцию машинного обучения"}
]
response = llm_client.chat_completion(messages)
```

## Подсистема базы данных

### Инициализация

```python
from core.db.connection import DBConnection
from core.db.repository.task_repository import TaskRepository

# Подключение к базе данных
db_connection = DBConnection("postgresql://user:password@localhost/dbname")

# Создание репозитория
task_repo = TaskRepository(db_connection)
```

### Основные операции

```python
# Создание записи
task_id = task_repo.create_task({
    "name": "Пример задачи",
    "description": "Описание задачи",
    "status": "pending"
})

# Получение записи
task = task_repo.get_task(task_id)

# Обновление записи
task_repo.update_task(task_id, {"status": "completed"})

# Получение списка записей
tasks = task_repo.list_tasks(filters={"status": "pending"}, limit=10)

# Удаление записи
task_repo.delete_task(task_id)
```

## Текущее состояние разработки подсистем

| Подсистема | Состояние | Тестовое покрытие |
|------------|-----------|-------------------|
| Файловая | В разработке | Частично |
| Ввод | В разработке | Частично |
| Комп. зрение | Требуется рефакторинг | Отсутствует |
| Веб | Требуется рефакторинг | Отсутствует |
| LLM | Требуется рефакторинг | Отсутствует |
| БД | Требуется рефакторинг | Отсутствует |
