# Ключевые интерфейсы

## Роль интерфейсов в системе

Интерфейсы (абстрактные базовые классы) в Neuro-Link Assistant обеспечивают:
- Чёткое разделение между абстракциями и реализациями
- Возможность замены компонентов без изменения остального кода
- Определение контрактов взаимодействия между подсистемами
- Облегчение тестирования через возможность мокирования

## Основные интерфейсы системы

### Файловая подсистема

```python
class AbstractFileSystem(ABC):
    @abstractmethod
    def file_exists(self, path: str) -> bool:
        """Проверяет существование файла."""
        pass

    @abstractmethod
    def read_file(self, path: str, encoding: str = "utf-8") -> str:
        """Читает содержимое файла."""
        pass

    @abstractmethod
    def write_file(self, path: str, content: str, encoding: str = "utf-8") -> bool:
        """Записывает содержимое в файл."""
        pass

    @abstractmethod
    def delete_file(self, path: str) -> bool:
        """Удаляет файл."""
        pass

    @abstractmethod
    def list_files(self, directory: str, pattern: str = "*") -> List[str]:
        """Возвращает список файлов в директории по шаблону."""
        pass
```

### Подсистема ввода

```python
class AbstractKeyboard(ABC):
    @abstractmethod
    def press_key(self, key: str) -> bool:
        """Нажимает клавишу."""
        pass

    @abstractmethod
    def release_key(self, key: str) -> bool:
        """Отпускает клавишу."""
        pass

    @abstractmethod
    def type_text(self, text: str, interval: float = 0.0) -> bool:
        """Печатает текст."""
        pass

    @abstractmethod
    def hotkey(self, *keys: str) -> bool:
        """Нажимает комбинацию клавиш."""
        pass

class AbstractMouse(ABC):
    @abstractmethod
    def move_to(self, x: int, y: int) -> bool:
        """Перемещает курсор мыши."""
        pass

    @abstractmethod
    def click(self, button: str = "left") -> bool:
        """Выполняет клик мышью."""
        pass

    @abstractmethod
    def double_click(self, button: str = "left") -> bool:
        """Выполняет двойной клик мышью."""
        pass

    @abstractmethod
    def drag_to(self, x: int, y: int, button: str = "left") -> bool:
        """Перетаскивает с зажатой кнопкой мыши."""
        pass
```

### Подсистема компьютерного зрения

```python
class AbstractScreenCapture(ABC):
    @abstractmethod
    def capture_screen(self, region: Optional[Tuple[int, int, int, int]] = None) -> Any:
        """Захватывает изображение экрана."""
        pass

    @abstractmethod
    def save_screenshot(self, path: str, region: Optional[Tuple[int, int, int, int]] = None) -> bool:
        """Сохраняет скриншот в файл."""
        pass

class AbstractElementRecognition(ABC):
    @abstractmethod
    def find_element(self, template: Any, confidence: float = 0.9) -> Optional[Tuple[int, int, int, int]]:
        """Находит элемент на экране по шаблону."""
        pass

    @abstractmethod
    def find_text(self, text: str) -> Optional[Tuple[int, int, int, int]]:
        """Находит текст на экране."""
        pass
```

### Подсистема веб-взаимодействия

```python
class AbstractBrowser(ABC):
    @abstractmethod
    def navigate(self, url: str) -> bool:
        """Переходит по указанному URL."""
        pass

    @abstractmethod
    def find_element_by_selector(self, selector: str) -> Any:
        """Находит элемент по CSS-селектору."""
        pass

    @abstractmethod
    def find_element_by_xpath(self, xpath: str) -> Any:
        """Находит элемент по XPath."""
        pass

    @abstractmethod
    def get_page_content(self) -> str:
        """Возвращает HTML-содержимое страницы."""
        pass
```

### Подсистема интеграции с LLM

```python
class AbstractLLMClient(ABC):
    @abstractmethod
    def generate_text(self, prompt: str, max_tokens: int = 100) -> str:
        """Генерирует текст по промпту."""
        pass

    @abstractmethod
    def chat_completion(self, messages: List[Dict[str, str]]) -> str:
        """Выполняет завершение чата по списку сообщений."""
        pass
```

## Применение интерфейсов

### Пример использования

```python
# Код, зависящий от абстракции, а не от конкретной реализации
def save_text_to_file(text: str, file_path: str, fs: AbstractFileSystem) -> bool:
    try:
        return fs.write_file(file_path, text)
    except Exception as e:
        error_handler.handle_error(e, f"Failed to save text to {file_path}")
        return False

# Использование с конкретной реализацией
def process_document(document_path: str):
    registry = get_component_registry()
    fs = registry.get("filesystem")  # Получаем реализацию через реестр

    content = fs.read_file(document_path)
    # Обработка содержимого...
    processed_content = content.upper()

    # Сохранение результата
    save_text_to_file(processed_content, f"processed_{document_path}", fs)
```

### Создание мока для тестирования

```python
# Мок для тестирования
class MockFileSystem(AbstractFileSystem):
    def __init__(self):
        self.files = {}

    def file_exists(self, path: str) -> bool:
        return path in self.files

    def read_file(self, path: str, encoding: str = "utf-8") -> str:
        if not self.file_exists(path):
            raise FileNotFoundError(f"File not found: {path}")
        return self.files[path]

    def write_file(self, path: str, content: str, encoding: str = "utf-8") -> bool:
        self.files[path] = content
        return True

    # Реализация остальных методов...

# Использование в тестах
def test_save_text_to_file():
    mock_fs = MockFileSystem()
    result = save_text_to_file("Test content", "test.txt", mock_fs)

    assert result is True
    assert mock_fs.file_exists("test.txt")
    assert mock_fs.read_file("test.txt") == "Test content"
```

## Рекомендации по созданию новых интерфейсов

1. **Принцип единственной ответственности**: Интерфейс должен представлять одну связную функциональность
2. **Принцип разделения интерфейсов**: Предпочитайте несколько специализированных интерфейсов одному общему
3. **Абстрактные методы**: Включайте только те методы, которые обязательны для всех реализаций
4. **Документирование контрактов**: Четко описывайте ожидаемое поведение методов, включая исключения
5. **Согласованность имен**: Используйте последовательные имена методов между интерфейсами
