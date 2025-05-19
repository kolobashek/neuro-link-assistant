import sys
from unittest.mock import MagicMock, patch

import pytest

from scripts.docker import restart_db, run_command, show_db_logs, start_db, stop_db


@pytest.fixture
def mock_subprocess_popen():
    """Фикстура для мокирования subprocess.Popen"""
    with patch("subprocess.Popen") as mock_popen:
        # Настройка мок-объекта
        process_mock = MagicMock()
        process_mock.stdout = ["Output line 1\n", "Output line 2\n"]
        process_mock.stderr = MagicMock()
        process_mock.stderr.read.return_value = "Error message"
        process_mock.wait.return_value = 0  # Успешное завершение по умолчанию
        mock_popen.return_value = process_mock
        yield mock_popen, process_mock


class TestDockerScripts:

    def test_run_command_success(self, mock_subprocess_popen):
        """Тест успешного выполнения команды"""
        mock_popen, process_mock = mock_subprocess_popen

        # Вызов функции
        run_command("docker-compose up -d")

        # Проверка, что Popen был вызван с правильными аргументами
        mock_popen.assert_called_once()
        args, kwargs = mock_popen.call_args
        assert "docker-compose up -d" in args[0]
        assert kwargs["shell"] is True

        # Проверка обработки вывода
        process_mock.wait.assert_called_once()

    def test_run_command_error(self, mock_subprocess_popen):
        """Тест обработки ошибок при выполнении команды"""
        mock_popen, process_mock = mock_subprocess_popen
        process_mock.wait.return_value = 1  # Имитация ошибки

        # Проверка, что при ошибке вызывается sys.exit
        with pytest.raises(SystemExit) as excinfo:
            run_command("docker-compose invalid")

        assert excinfo.value.code == 1
        process_mock.stderr.read.assert_called_once()

    def test_start_db(self, mock_subprocess_popen):
        """Тест запуска БД"""
        with patch("scripts.docker.run_command") as mock_run_command:
            start_db()
            mock_run_command.assert_called_once_with("docker-compose up -d")

    def test_stop_db(self, mock_subprocess_popen):
        """Тест остановки БД"""
        with patch("scripts.docker.run_command") as mock_run_command:
            stop_db()
            mock_run_command.assert_called_once_with("docker-compose down")

    def test_restart_db(self, mock_subprocess_popen):
        """Тест перезапуска БД"""
        with patch("scripts.docker.stop_db") as mock_stop:
            with patch("scripts.docker.start_db") as mock_start:
                restart_db()
                mock_stop.assert_called_once()
                mock_start.assert_called_once()

    def test_show_db_logs(self, mock_subprocess_popen):
        """Тест просмотра логов БД"""
        with patch("scripts.docker.run_command") as mock_run_command:
            show_db_logs()
            mock_run_command.assert_called_once_with("docker-compose logs -f")

    def test_main_function(self, mock_subprocess_popen):
        """Тест вызова функций из main"""
        test_cases = [
            ("start", "scripts.docker.start_db"),
            ("stop", "scripts.docker.stop_db"),
            ("restart", "scripts.docker.restart_db"),
            ("logs", "scripts.docker.show_db_logs"),
        ]

        for arg, expected_func in test_cases:
            with patch(expected_func) as mock_func:
                with patch.object(sys, "argv", ["docker.py", arg]):
                    # Импортируем модуль заново для запуска __main__
                    import importlib

                    import scripts.docker

                    importlib.reload(scripts.docker)
                    mock_func.assert_called_once()

    def test_main_invalid_command(self, mock_subprocess_popen):
        """Тест обработки неверной команды"""
        with patch.object(sys, "argv", ["docker.py", "invalid"]):
            with pytest.raises(SystemExit) as excinfo:
                import importlib

                import scripts.docker

                importlib.reload(scripts.docker)
            assert excinfo.value.code == 1
