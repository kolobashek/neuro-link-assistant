# -*- coding: utf-8 -*-
"""
Базовые абстрактные классы для работы с процессами.
"""
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional


class AbstractProcessManager(ABC):
    """
    Абстрактный класс для управления процессами.
    Определяет интерфейс для платформо-зависимых реализаций.
    """

    @abstractmethod
    def start_process(
        self,
        executable: str,
        args: Optional[List[str]] = None,
        cwd: Optional[str] = None,
        wait: bool = False,
        shell: bool = False,
        env: Optional[Dict[str, str]] = None,
    ) -> Dict[str, Any]:
        """
        Запускает процесс.

        Args:
            executable (str): Путь к исполняемому файлу
            args (List[str], optional): Список аргументов командной строки
            cwd (str, optional): Рабочая директория
            wait (bool): Ожидать завершения процесса
            shell (bool): Использовать оболочку для запуска
            env (Dict[str, str], optional): Переменные окружения

        Returns:
            Dict[str, Any]: Информация о запущенном процессе
        """
        pass

    @abstractmethod
    def run_command(
        self, command: str, cwd: Optional[str] = None, env: Optional[Dict[str, str]] = None
    ) -> Dict[str, Any]:
        """
        Выполняет команду в оболочке и ожидает завершения.

        Args:
            command (str): Команда для выполнения
            cwd (str, optional): Рабочая директория
            env (Dict[str, str], optional): Переменные окружения

        Returns:
            Dict[str, Any]: Результат выполнения команды
        """
        pass

    @abstractmethod
    def terminate_process(self, pid: Optional[int] = None, name: Optional[str] = None) -> bool:
        """
        Завершает процесс по его PID или имени.

        Args:
            pid (int, optional): Идентификатор процесса
            name (str, optional): Имя процесса

        Returns:
            bool: True в случае успешного завершения
        """
        pass

    @abstractmethod
    def kill_process(self, pid: int) -> bool:
        """
        Принудительно завершает процесс по его PID.

        Args:
            pid (int): Идентификатор процесса

        Returns:
            bool: True в случае успешного завершения
        """
        pass

    @abstractmethod
    def get_process_info(self, pid: int) -> Optional[Dict[str, Any]]:
        """
        Получает подробную информацию о процессе.

        Args:
            pid (int): Идентификатор процесса

        Returns:
            Optional[Dict[str, Any]]: Словарь с информацией о процессе или None, если процесс не найден
        """
        pass

    @abstractmethod
    def find_process_by_name(self, name: str) -> List[Dict[str, Any]]:
        """
        Находит процессы по имени.

        Args:
            name (str): Имя процесса (может быть частичным)

        Returns:
            List[Dict[str, Any]]: Список словарей с информацией о найденных процессах
        """
        pass

    @abstractmethod
    def is_process_running(self, pid: Optional[int] = None, name: Optional[str] = None) -> bool:
        """
        Проверяет, запущен ли процесс.

        Args:
            pid (int, optional): Идентификатор процесса
            name (str, optional): Имя процесса

        Returns:
            bool: True, если процесс запущен
        """
        pass

    @abstractmethod
    def wait_for_process_exit(self, pid: int, timeout: Optional[int] = None) -> bool:
        """
        Ожидает завершения процесса.

        Args:
            pid (int): Идентификатор процесса
            timeout (int, optional): Таймаут в секундах

        Returns:
            bool: True, если процесс завершился, False в случае таймаута
        """
        pass

    @abstractmethod
    def get_all_processes(self) -> List[Dict[str, Any]]:
        """
        Получает список всех запущенных процессов.

        Returns:
            List[Dict[str, Any]]: Список словарей с информацией о процессах
        """
        pass

    @abstractmethod
    def set_process_priority(self, pid: int, priority: str) -> bool:
        """
        Устанавливает приоритет процесса.

        Args:
            pid (int): Идентификатор процесса
            priority (str): Приоритет процесса ('realtime', 'high', 'above_normal',
                        'normal', 'below_normal', 'idle')

        Returns:
            bool: True в случае успешной установки приоритета
        """
        pass
