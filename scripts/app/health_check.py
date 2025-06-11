"""Быстрая проверка состояния приложения"""

import sys
from typing import Optional

import requests


def quick_check(url: str = "http://localhost:5000", timeout: int = 3) -> bool:
    """Быстрая проверка приложения"""
    try:
        response = requests.get(url, timeout=timeout)
        if response.status_code == 200:
            print(f"✅ Приложение работает на {url}")
            return True
        else:
            print(f"⚠️ Приложение отвечает с кодом {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print(f"❌ Приложение недоступно на {url}")
        return False
    except requests.exceptions.Timeout:
        print(f"⏰ Таймаут подключения к {url}")
        return False
    except Exception as e:
        print(f"❌ Ошибка проверки: {e}")
        return False


def main():
    """CLI для быстрой проверки"""
    import argparse

    parser = argparse.ArgumentParser(description="Быстрая проверка приложения")
    parser.add_argument("--url", default="http://localhost:5000", help="URL приложения")
    parser.add_argument("--timeout", type=int, default=3, help="Таймаут в секундах")

    args = parser.parse_args()

    success = quick_check(args.url, args.timeout)
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
