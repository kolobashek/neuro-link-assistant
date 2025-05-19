# scripts/docker.py
import subprocess
import sys
from pathlib import Path

# Получаем путь к корневой директории проекта
PROJECT_ROOT = Path(__file__).parent.parent


def run_command(command, cwd=PROJECT_ROOT):
    """Запускает shell-команду и выводит результат"""
    print(f"Выполняем: {command}")
    process = subprocess.Popen(
        command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, cwd=cwd
    )

    # Выводим вывод команды в реальном времени
    if process.stdout:  # Проверяем, что stdout не None
        for line in process.stdout:
            print(line.strip())

    # Дожидаемся завершения команды
    exit_code = process.wait()

    # Если команда завершилась с ошибкой, выводим сообщение
    if exit_code != 0:
        stderr_output = ""
        if process.stderr:  # Проверяем, что stderr не None
            stderr_output = process.stderr.read()
        print(f"Ошибка выполнения команды: {stderr_output}")
        sys.exit(exit_code)


def start_db():
    """Запускает контейнеры базы данных"""
    run_command("docker-compose up -d")
    print("База данных запущена!")
    print("pgAdmin доступен по адресу: http://localhost:5050")
    print("Данные для входа в pgAdmin: admin@example.com / admin_password")


def stop_db():
    """Останавливает контейнеры базы данных"""
    run_command("docker-compose down")
    print("База данных остановлена")


def restart_db():
    """Перезапускает контейнеры базы данных"""
    stop_db()
    start_db()


def show_db_logs():
    """Показывает логи базы данных"""
    run_command("docker-compose logs -f")


if __name__ == "__main__":
    # Для возможности запуска напрямую из командной строки
    if len(sys.argv) > 1:
        command = sys.argv[1]
        if command == "start":
            start_db()
        elif command == "stop":
            stop_db()
        elif command == "restart":
            restart_db()
        elif command == "logs":
            show_db_logs()
        else:
            print(f"Неизвестная команда: {command}")
            print("Доступные команды: start, stop, restart, logs")
            sys.exit(1)
    else:
        print("Укажите команду: start, stop, restart, logs")
        sys.exit(1)
