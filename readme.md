# Neuro-Link Assistant

Платформа для оркестрации моделей искусственного интеллекта и автоматизации задач на Windows.

## Обзор

Neuro-Link Assistant интегрирует различные модели AI и предоставляет единый интерфейс для выполнения сложных задач автоматизации с использованием компьютерного зрения, управления вводом и взаимодействия с веб.

## Текущее состояние

- ✅ Базовая архитектура и ядро системы
- ✅ Проходит системный тест рабочего процесса
- 🚧 В разработке: файловая система и подсистема ввода

## Быстрый старт

```bash
git clone https://github.com/kolobashek/neuro-link-assistant.git
cd neuro-link-assistant
python -m venv venv
venv\Scripts\activate  # Windows
pip install -r requirements.txt
pytest  # Запуск тестов
```

## Документация

- **Архитектура**: [Обзор](docs/architecture/overview.md), [Компоненты](docs/architecture/components.md), [Подсистемы](docs/architecture/subsystems.md), [Интерфейсы](docs/architecture/interfaces.md)
- **Разработка**: [Методология](docs/development/methodology.md), [Тестирование](docs/development/testing.md), [Стандарты](docs/development/standards.md), [Рабочий процесс](docs/development/workflow.md)
- **Руководства**: [Настройка](docs/guides/setup.md), [Контрибьюция](docs/guides/contribution.md)
- **API**: [Ядро системы](docs/api/core.md), [Компоненты](docs/api/components.md), [Подсистемы](docs/api/subsystems.md)

## Требования

- Python 3.8 или выше
- Windows 10 или выше
- Дополнительные зависимости в [pyproject.toml](pyproject.toml)

## Архитектура

Проект построен на модульной архитектуре с центральным реестром компонентов. Ключевые подсистемы:

- **Файловая система**: операции с файлами и директориями
- **Подсистема ввода**: эмуляция клавиатуры и мыши
- **Компьютерное зрение**: анализ экрана и распознавание элементов
- **Веб-взаимодействие**: автоматизация браузера и работа с веб
- **LLM-интеграция**: взаимодействие с языковыми моделями

## Разработка

Проект следует методологии TDD с подходом "сверху вниз", начиная с системных тестов и постепенно детализируя компоненты. Для участия в разработке ознакомьтесь с [руководством по контрибьюции](docs/guides/contribution.md).

## Лицензия

[Apache License 2.0](LICENSE)
