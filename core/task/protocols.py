from typing import Any, Protocol

from core.task.base import TaskResult


class TaskProtocol(Protocol):
    """Протокол для класса Task."""

    description: str
    _registry: Any

    def _extract_filename(self) -> str | None:
        """Извлекает имя файла из описания задачи."""
        ...

    def _extract_content(self) -> str:
        """Извлекает содержимое для записи в файл."""
        ...

    def _extract_search_query(self) -> str | None:
        """Извлекает поисковый запрос из описания задачи."""
        ...

    def _extract_application_name(self) -> str | None:
        """Извлекает имя приложения из описания задачи."""
        ...


class WebTaskProtocol(TaskProtocol, Protocol):
    """Протокол для веб-операций Task."""

    def _perform_duckduckgo_search(self, browser_controller: Any) -> TaskResult:
        """Выполняет поиск в DuckDuckGo."""
        ...

    def _perform_web_search_with_protection(self, browser_controller: Any) -> TaskResult:
        """Выполняет поиск с защитой от ботов."""
        ...

    def _check_bot_protection(self, browser_controller: Any) -> TaskResult:
        """Проверяет защиту от ботов."""
        ...

    def _open_browser_safely(self, browser_controller: Any) -> TaskResult:
        """Безопасно открывает браузер."""
        ...

    def _perform_search_safely(self, browser_controller: Any, search_query: str) -> TaskResult:
        """Безопасно выполняет поиск."""
        ...

    def _detect_bot_protection(self, browser_controller: Any) -> bool:
        """Определяет наличие защиты от ботов."""
        ...

    def _human_like_typing(self, element_finder: Any, element: Any, text: str) -> None:
        """Имитирует человеческий ввод."""
        ...

    def _extract_duckduckgo_results(self, element_finder: Any) -> list[str]:
        """Извлекает результаты DuckDuckGo."""
        ...

    def _extract_search_results(self, element_finder: Any) -> list[str]:
        """Извлекает результаты поиска."""
        ...


class WindowsTaskProtocol(TaskProtocol, Protocol):
    """Протокол для Windows-операций Task."""

    def _launch_calculator(self) -> TaskResult:
        """Запускает калькулятор."""
        ...

    def _launch_notepad(self) -> TaskResult:
        """Запускает блокнот."""
        ...

    def _launch_application(self, app_name: str) -> TaskResult:
        """Запускает приложение."""
        ...


class FileTaskProtocol(TaskProtocol, Protocol):
    """Протокол для файловых операций Task."""

    def _create_file(self, filesystem: Any) -> TaskResult:
        """Создает файл."""
        ...

    def _read_file(self, filesystem: Any) -> TaskResult:
        """Читает файл."""
        ...

    def _delete_file(self, filesystem: Any) -> TaskResult:
        """Удаляет файл."""
        ...
