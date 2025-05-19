# scripts/db.py
import subprocess
import sys
from pathlib import Path

# Получаем путь к корневой директории проекта
PROJECT_ROOT = Path(__file__).parent.parent


def run_command(command, cwd=PROJECT_ROOT):
    """Запускает shell-команду и выводит результат"""
    print(f"Выполняем: {command}")
    process = subprocess.run(
        command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, cwd=cwd
    )

    print(process.stdout)

    if process.returncode != 0:
        print(f"Ошибка: {process.stderr}")
        sys.exit(process.returncode)


def run_migrations():
    """Запускает миграции Alembic"""
    run_command("alembic upgrade head")
    print("Миграции успешно применены!")


def seed_database():
    """Заполняет базу данных начальными данными"""
    # Этот скрипт должен быть создан в вашем проекте
    run_command("python -m core.db.seed")
    print("База данных заполнена начальными данными!")


if __name__ == "__main__":
    if len(sys.argv) > 1:
        command = sys.argv[1]
        if command == "migrate":
            run_migrations()
        elif command == "seed":
            seed_database()
        else:
            print(f"Неизвестная команда: {command}")
            print("Доступные команды: migrate, seed")
            sys.exit(1)
    else:
        print("Укажите команду: migrate, seed")
        sys.exit(1)
