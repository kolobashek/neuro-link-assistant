# Рабочий процесс разработки

## Общий цикл разработки

Рабочий процесс Neuro-Link Assistant следует принципам TDD "сверху вниз" и состоит из следующих этапов:

### 1. Планирование и анализ

- Изучение требований из дорожной карты
- Создание задачи в системе отслеживания задач
- Определение критериев приемки

### 2. Создание тестов

- Начало с системного теста, определяющего новую функциональность
- Создание интеграционных тестов для взаимодействия компонентов
- Написание модульных тестов для отдельных компонентов

### 3. Реализация функциональности

- Минимальная реализация для прохождения тестов
- Запуск тестов для проверки прогресса
- Рефакторинг кода при сохранении работоспособности тестов

### 4. Проверка и документирование

- Запуск полного набора тестов
- Проверка соответствия стандартам кодирования
- Обновление документации

### 5. Отправка изменений

- Создание pull/merge request
- Прохождение code review
- Слияние кода в основную ветку

## Работа с Git

### Ветвление

```
main
  ├── feature/file-system-tests
  ├── feature/input-subsystem
  ├── bugfix/task-execution
  └── refactor/component-registry
```

- `main`: Стабильная ветка с рабочим кодом
- `feature/*`: Новая функциональность
- `bugfix/*`: Исправление ошибок
- `refactor/*`: Улучшение существующего кода

### Коммиты

Используйте содержательные сообщения коммитов:

```
feat: Добавлена реализация Win32FileSystem
test: Созданы тесты для подсистемы ввода
fix: Исправлена ошибка в компонентном реестре
refactor: Улучшена обработка ошибок
docs: Обновлена документация подсистем
```

## Создание новой функциональности

1. **Создание ветки**
   ```bash
   git checkout -b feature/new-feature
   ```

2. **Создание системного теста**
   ```bash
   # Создание нового файла теста
   touch tests/system/test_new_feature.py

   # Реализация теста для новой функциональности
   # Запуск теста (должен не проходить)
   pytest tests/system/test_new_feature.py -v
   ```

3. **Создание модульных тестов**
   ```bash
   # Создание тестов для компонентов
   touch tests/unit/core/test_component.py

   # Реализация модульных тестов
   # Запуск тестов (должны не проходить)
   pytest tests/unit/core/test_component.py -v
   ```

4. **Минимальная реализация**
   ```bash
   # Создание необходимых файлов
   touch core/component.py

   # Реализация кода для прохождения тестов
   # Запуск тестов (должны проходить)
   pytest tests/unit/core/test_component.py -v
   ```

5. **Рефакторинг и документирование**
   ```bash
   # Улучшение кода
   # Добавление документации
   # Запуск всех тестов
   pytest
   ```

6. **Отправка изменений**
   ```bash
   git add .
   git commit -m "feat: Добавлена новая функциональность"
   git push origin feature/new-feature
   ```

## Проверка перед отправкой

- ✅ Все тесты проходят успешно
- ✅ Код соответствует стандартам форматирования
- ✅ Документация обновлена
- ✅ Типизация добавлена
- ✅ Нет дублирования кода
- ✅ Изменения минимальны и целенаправленны

## Code Review

При проверке кода коллег обращайте внимание на:

1. **Соответствие TDD**: тесты созданы до реализации
2. **Качество тестов**: тесты проверяют правильные аспекты
3. **Чистота кода**: соответствие принципам SOLID
4. **Документация**: все публичные API документированы
5. **Обработка ошибок**: исключения обрабатываются правильно
