#!/usr/bin/env python3
"""Быстрая проверка состояния приложения"""

import sys

import requests


def quick_check(url="http://localhost:5000", timeout=1):
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


if __name__ == "__main__":
    if quick_check():
        sys.exit(0)
    else:
        sys.exit(1)
