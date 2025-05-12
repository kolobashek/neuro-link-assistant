# План тестирования ИИ-агента для Windows

## 1. Модульные тесты (Unit Tests)

```bash
python -m pytest tests/unit/ -v
```

### 1.1 Тесты ядра системы

```bash
python -m pytest tests/unit/core/ -v
```

#### 1.1.1 Тесты архитектуры

```bash
python -m pytest tests/unit/core/test_component_registry.py tests/unit/core/test_system_initializer.py tests/unit/core/test_error_handler.py tests/unit/core/test_plugin_manager.py -v
```

- [x] Тест регистрации и получения компонентов
  ```bash
  python -m pytest tests/unit/core/test_component_registry.py -v
  ```
- [x] Тест инициализации системы
  ```bash
  python -m pytest tests/unit/core/test_system_initializer.py -v
  ```
- [x] Тест обработки ошибок и логирования
  ```bash
  python -m pytest tests/unit/core/test_error_handler.py -v
  ```
- [x] Тест расширяемости через плагины
  ```bash
  python -m pytest tests/unit/core/test_plugin_manager.py -v
  ```

#### 1.1.2 Тесты LLM-интеграции

```bash
python -m pytest tests/unit/core/llm/ -v
```

- [ ] Тест подключения к LLM API
  ```bash
  python -m pytest tests/unit/core/llm/test_api_connector.py -v
  ```
- [ ] Тест обработки промптов
  ```bash
  python -m pytest tests/unit/core/llm/test_prompt_processor.py -v
  ```
- [ ] Тест парсинга ответов модели
  ```bash
  python -m pytest tests/unit/core/llm/test_response_parser.py -v
  ```
- [ ] Тест планирования действий на основе запросов
  ```bash
  python -m pytest tests/unit/core/llm/test_action_planner.py -v
  ```
- [ ] Тест обработки ошибок API
  ```bash
  python -m pytest tests/unit/core/llm/test_error_handling.py -v
  ```

#### 1.1.3 Тесты взаимодействия с Windows

```bash
python -m pytest tests/unit/core/windows/ -v
```

- [x] Тест управления окнами (поиск, активация, закрытие)
  ```bash
  python -m pytest tests/unit/core/windows/test_window_manager.py -v
  ```
- [x] Тест операций с файловой системой (создание, чтение, запись)
  ```bash
  python -m pytest tests/unit/core/windows/test_file_system.py -v
  ```
- [x] Тест управления процессами (запуск, завершение)
  ```bash
  python -m pytest tests/unit/core/windows/test_process_manager.py -v
  ```
- [x] Тест получения системной информации
  ```bash
  python -m pytest tests/unit/core/windows/test_system_info.py -v
  ```
- [x] Тест работы с реестром Windows
  ```bash
  python -m pytest tests/unit/core/windows/test_registry_manager.py -v
  ```

### 1.2 Тесты функциональных модулей

```bash
python -m pytest tests/unit/core/vision/ tests/unit/core/web/ tests/unit/core/input/ -v
```

#### 1.2.1 Тесты компьютерного зрения

```bash
python -m pytest tests/unit/core/vision/ -v
```

- [ ] Тест захвата скриншотов
  ```bash
  python -m pytest tests/unit/core/vision/test_screen_capture.py -v
  ```
- [x] Тест распознавания элементов интерфейса
  ```bash
  python -m pytest tests/unit/core/vision/test_element_recognition.py -v
  ```
- [x] Тест локализации элементов на экране
  ```bash
  python -m pytest tests/unit/core/vision/test_element_localization.py -v
  ```
- [x] Тест сравнения изображений
  ```bash
  python -m pytest tests/unit/core/vision/test_image_comparison.py -v
  ```
- [x] Тест обработки изменений на экране
  ```bash
  python -m pytest tests/unit/core/vision/test_screen_changes.py -v
  ```

#### 1.2.2 Тесты веб-взаимодействия

```bash
python -m pytest tests/unit/core/web/ -v
```

- [x] Тест инициализации браузера
  ```bash
  python -m pytest tests/unit/core/web/test_browser_init.py -v
  ```
- [x] Тест навигации по веб-страницам
  ```bash
  python -m pytest tests/unit/core/web/test_navigation.py -v
  ```
- [x] Тест поиска элементов DOM
  ```bash
  python -m pytest tests/unit/core/web/test_dom_search.py -v
  ```
- [x] Тест взаимодействия с формами
  ```bash
  python -m pytest tests/unit/core/web/test_form_interaction.py -v
  ```
- [x] Тест обработки JavaScript-событий
  ```bash
  python -m pytest tests/unit/core/web/test_js_events.py -v
  ```
- [x] Тест извлечения данных со страницы
  ```bash
  python -m pytest tests/unit/core/web/test_data_extraction.py -v
  ```

#### 1.2.3 Тесты эмуляции пользовательского ввода

```bash
python -m pytest tests/unit/core/input/ -v
```

- [ ] Тест эмуляции клавиатуры (нажатия клавиш, комбинации)
  ```bash
  python -m pytest tests/unit/core/input/test_keyboard_controller.py -v
  ```
- [ ] Тест эмуляции мыши (движение, клики, перетаскивание)
  ```bash
  python -m pytest tests/unit/core/input/test_mouse_controller.py -v
  ```
- [ ] Тест имитации человеческого поведения (задержки, неточности)
  ```bash
  python -m pytest tests/unit/core/input/test_human_simulation.py -v
  ```
- [ ] Тест взаимодействия с системными диалогами
  ```bash
  python -m pytest tests/unit/core/input/test_dialog_interaction.py -v
  ```

### 1.3 Тесты специализированных возможностей

```bash
python -m pytest tests/unit/core/installation/ tests/unit/core/files/ tests/unit/core/decision/ -v
```

#### 1.3.1 Тесты установки программ

```bash
python -m pytest tests/unit/core/installation/ -v
```

- [ ] Тест работы с пакетными менеджерами
  ```bash
  python -m pytest tests/unit/core/installation/test_package_managers.py -v
  ```
- [ ] Тест автоматизации установщиков
  ```bash
  python -m pytest tests/unit/core/installation/test_installer_automation.py -v
  ```
- [ ] Тест проверки успешности установки
  ```bash
  python -m pytest tests/unit/core/installation/test_installation_verification.py -v
  ```
- [ ] Тест обработки ошибок установки
  ```bash
  python -m pytest tests/unit/core/installation/test_error_handling.py -v
  ```

#### 1.3.2 Тесты работы с файлами и документами

```bash
python -m pytest tests/unit/core/files/ -v
```

- [ ] Тест операций с различными типами файлов
  ```bash
  python -m pytest tests/unit/core/files/test_file_operations.py -v
  ```
- [ ] Тест работы с документами (текст, таблицы)
  ```bash
  python -m pytest tests/unit/core/files/test_document_processing.py -v
  ```
- [ ] Тест поиска информации в файлах
  ```bash
  python -m pytest tests/unit/core/files/test_file_search.py -v
  ```
- [ ] Тест обработки больших файлов
  ```bash
  python -m pytest tests/unit/core/files/test_large_file_handling.py -v
  ```

#### 1.3.3 Тесты системы принятия решений

```bash
python -m pytest tests/unit/core/decision/ -v
```

- [ ] Тест выбора оптимального способа взаимодействия
  ```bash
  python -m pytest tests/unit/core/decision/test_interaction_selection.py -v
  ```
- [ ] Тест адаптации к результатам действий
  ```bash
  python -m pytest tests/unit/core/decision/test_action_adaptation.py -v
  ```
- [ ] Тест обработки неожиданных ситуаций
  ```bash
  python -m pytest tests/unit/core/decision/test_unexpected_handling.py -v
  ```
- [ ] Тест приоритизации действий
  ```bash
  python -m pytest tests/unit/core/decision/test_action_prioritization.py -v
  ```

## 2. Интеграционные тесты (Integration Tests)

```bash
python -m pytest tests/integration/ -v
```

### 2.1 Тесты взаимодействия компонентов

```bash
python -m pytest tests/integration/llm_actions/ tests/integration/vision_input/ tests/integration/web_system/ -v
```

#### 2.1.1 Тесты интеграции LLM и системы действий

```bash
python -m pytest tests/integration/llm_actions/ -v
```

- [ ] Тест преобразования намерений в конкретные действия
  ```bash
  python -m pytest tests/integration/llm_actions/test_intent_to_action.py -v
  ```
- [ ] Тест обратной связи от действий к LLM
  ```bash
  python -m pytest tests/integration/llm_actions/test_action_feedback.py -v
  ```
- [ ] Тест обработки сложных многошаговых инструкций
  ```bash
  python -m pytest tests/integration/llm_actions/test_multistep_instructions.py -v
  ```

#### 2.1.2 Тесты интеграции компьютерного зрения и ввода

```bash
python -m pytest tests/integration/vision_input/ -v
```

- [ ] Тест распознавания и взаимодействия с элементами
  ```bash
  python -m pytest tests/integration/vision_input/test_element_interaction.py -v
  ```
- [ ] Тест адаптации к изменениям интерфейса
  ```bash
  python -m pytest tests/integration/vision_input/test_interface_adaptation.py -v
  ```
- [ ] Тест точности позиционирования на основе распознавания
  ```bash
  python -m pytest tests/integration/vision_input/test_positioning_accuracy.py -v
  ```

#### 2.1.3 Тесты интеграции веб и системных компонентов

```bash
python -m pytest tests/integration/web_system/ -v
```

- [ ] Тест загрузки файлов из веб в систему
  ```bash
  python -m pytest tests/integration/web_system/test_file_download.py -v
  ```
- [ ] Тест передачи данных между веб и локальными приложениями
  ```bash
  python -m pytest tests/integration/web_system/test_data_transfer.py -v
  ```
- [ ] Тест автоматизации веб-установщиков
  ```bash
  python -m pytest tests/integration/web_system/test_web_installers.py -v
  ```

### 2.2 Тесты гибридной системы

```bash
python -m pytest tests/integration/hybrid/ tests/integration/programming/ -v
```

#### 2.2.1 Тесты переключения методов взаимодействия

```bash
python -m pytest tests/integration/hybrid/ -v
```

- [ ] Тест выбора между DOM и CV для веб-страниц
  ```bash
  python -m pytest tests/integration/hybrid/test_dom_cv_selection.py -v
  ```
- [ ] Тест переключения между API и эмуляцией ввода
  ```bash
  python -m pytest tests/integration/hybrid/test_api_input_switching.py -v
  ```
- [ ] Тест восстановления после сбоев взаимодействия
  ```bash
  python -m pytest tests/integration/hybrid/test_interaction_recovery.py -v
  ```

#### 2.2.2 Тесты программирования и отладки

```bash
python -m pytest tests/integration/programming/ -v
```

- [ ] Тест генерации кода
  ```bash
  python -m pytest tests/integration/programming/test_code_generation.py -v
  ```
- [ ] Тест запуска и анализа результатов выполнения
  ```bash
  python -m pytest tests/integration/programming/test_execution_analysis.py -v
  ```
- [ ] Тест базовой отладки и исправления ошибок
  ```bash
  python -m pytest tests/integration/programming/test_debugging.py -v
  ```

## 3. Системные тесты (System Tests)

```bash
python -m pytest tests/system/ -v
```

### 3.1 Тесты сценариев использования

```bash
python -m pytest tests/system/basic/ tests/system/complex/ -v
```

#### 3.1.1 Тесты базовых задач

```bash
python -m pytest tests/system/basic/ -v
```

- [ ] Тест работы с файлами и папками
  ```bash
  python -m pytest tests/system/basic/test_file_operations.py -v
  ```
- [ ] Тест поиска информации в интернете
  ```bash
  python -m pytest tests/system/basic/test_web_search.py -v
  ```
- [ ] Тест установки простых программ
  ```bash
  python -m pytest tests/system/basic/test_program_installation.py -v
  ```
- [ ] Тест базовой работы с приложениями
  ```bash
  python -m pytest tests/system/basic/test_app_interaction.py -v
  ```

#### 3.1.2 Тесты сложных сценариев

```bash
python -m pytest tests/system/complex/ -v
```

- [ ] Тест установки и настройки среды разработки
  ```bash
  python -m pytest tests/system/complex/test_dev_environment_setup.py -v
  ```
- [ ] Тест автоматизации рабочего процесса
  ```bash
  python -m pytest tests/system/complex/test_workflow_automation.py -v
  ```
- [ ] Тест решения проблем на основе поиска информации
  ```bash
  python -m pytest tests/system/complex/test_problem_solving.py -v
  ```
- [ ] Тест создания и редактирования документов
  ```bash
  python -m pytest tests/system/complex/test_document_editing.py -v
  ```

### 3.2 Тесты производительности и надежности

#### 3.2.1 Тесты производительности

- [ ] Тест времени отклика системы
  ```bash
  python -m pytest tests/system/performance/test_response_time.py -v
  ```
- [ ] Тест использования ресурсов (CPU, память)
  ```bash
  python -m pytest tests/system/performance/test_resource_usage.py -v
  ```
- [ ] Тест скорости выполнения типовых задач
  ```bash
  python -m pytest tests/system/performance/test_task_speed.py -v
  ```
- [ ] Тест масштабируемости при сложных задачах
  ```bash
  python -m pytest tests/system/performance/test_scalability.py -v
  ```

#### 3.2.2 Тесты надежности

- [ ] Тест восстановления после сбоев
  ```bash
  python -m pytest tests/system/reliability/test_recovery.py -v
  ```
- [ ] Тест длительной работы (стабильность)
  ```bash
  python -m pytest tests/system/reliability/test_stability.py -v
  ```
- [ ] Тест обработки граничных случаев
  ```bash
  python -m pytest tests/system/reliability/test_edge_cases.py -v
  ```
- [ ] Тест работы при ограниченных ресурсах
  ```bash
  python -m pytest tests/system/reliability/test_limited_resources.py -v
  ```

### 3.3 Тесты безопасности

#### 3.3.1 Тесты контроля доступа

- [ ] Тест ограничений доступа к системным ресурсам
  ```bash
  python -m pytest tests/system/security/test_resource_restrictions.py -v
  ```
- [ ] Тест подтверждения потенциально опасных действий
  ```bash
  python -m pytest tests/system/security/test_dangerous_actions.py -v
  ```
- [ ] Тест соблюдения политик безопасности
  ```bash
  python -m pytest tests/system/security/test_security_policies.py -v
  ```

## 4. Приемочные тесты (Acceptance Tests)

### 4.1 Тесты пользовательских историй

#### 4.1.1 Тесты основных пользовательских сценариев

- [ ] Тест "Установка и настройка Python с виртуальным окружением"
  ```bash
  python -m pytest tests/acceptance/user_stories/test_python_setup.py -v
  ```
- [ ] Тест "Поиск и обработка информации из интернета"
  ```bash
  python -m pytest tests/acceptance/user_stories/test_web_research.py -v
  ```
- [ ] Тест "Автоматизация рутинных задач Windows"
  ```bash
  python -m pytest tests/acceptance/user_stories/test_windows_automation.py -v
  ```
- [ ] Тест "Помощь в программировании и отладке"
  ```bash
  python -m pytest tests/acceptance/user_stories/test_programming_assistance.py -v
  ```

### 4.2 Тесты удобства использования

#### 4.2.1 Тесты пользовательского интерфейса

- [ ] Тест понятности интерфейса
  ```bash
  python -m pytest tests/acceptance/usability/test_interface_clarity.py -v
  ```
- [ ] Тест обратной связи о действиях агента
  ```bash
  python -m pytest tests/acceptance/usability/test_agent_feedback.py -v
  ```
- [ ] Тест естественно-языкового взаимодействия
  ```bash
  python -m pytest tests/acceptance/usability/test_natural_language.py -v
  ```

## 5. Инфраструктура тестирования

### 5.1 Инструменты и фреймворки

- [ ] Настройка pytest для модульных и интеграционных тестов
  ```bash
  python -m pytest tests/infrastructure/test_pytest_setup.py -v
  ```
- [ ] Настройка моков и стабов для внешних зависимостей
  ```bash
  python -m pytest tests/infrastructure/test_mocks_setup.py -v
  ```
- [ ] Создание фикстур для типовых сценариев тестирования
  ```bash
  python -m pytest tests/infrastructure/test_fixtures_setup.py -v
  ```

### 5.2 Автоматизация тестирования

- [ ] Настройка CI/CD для автоматического запуска тестов
  ```bash
  python -m pytest tests/infrastructure/test_ci_cd_setup.py -v
  ```
- [ ] Создание отчетов о покрытии кода тестами
  ```bash
  python -m pytest tests/infrastructure/test_coverage_reports.py -v
  ```
- [ ] Интеграция с системой отслеживания ошибок
  ```bash
  python -m pytest tests/infrastructure/test_issue_tracking.py -v
  ```

### 5.3 Тестовые среды

- [ ] Создание изолированных виртуальных машин для тестирования
  ```bash
  python -m pytest tests/infrastructure/test_vm_setup.py -v
  ```
- [ ] Настройка снимков состояния для быстрого восстановления
  ```bash
  python -m pytest tests/infrastructure/test_snapshot_setup.py -v
  ```
- [ ] Подготовка тестовых данных и сценариев
  ```bash
  python -m pytest tests/infrastructure/test_data_preparation.py -v
  ```

## Приоритизация тестов

### Критические тесты (выполнять в первую очередь)

- Тесты ядра системы (1.1)
  ```bash
  python -m pytest tests/unit/core/ -v
  ```
- Тесты базовых функциональных модулей (1.2)
  ```bash
  python -m pytest tests/unit/core/vision/ tests/unit/core/input/ tests/unit/core/web/ -v
  ```
- Тесты интеграции ключевых компонентов (2.1)
  ```bash
  python -m pytest tests/integration/llm_actions/ tests/integration/vision_input/ -v
  ```

### Высокоприоритетные тесты

- Тесты специализированных возможностей (1.3)
  ```bash
  python -m pytest tests/unit/core/installation/ tests/unit/core/files/ tests/unit/core/decision/ -v
  ```
- Тесты гибридной системы (2.2)
  ```bash
  python -m pytest tests/integration/hybrid/ tests/integration/programming/ -v
  ```
- Тесты базовых задач (3.1.1)
  ```bash
  python -m pytest tests/system/basic/ -v
  ```

### Среднеприоритетные тесты

- Тесты сложных сценариев (3.1.2)
  ```bash
  python -m pytest tests/system/complex/ -v
  ```
- Тесты производительности и надежности (3.2)
  ```bash
  python -m pytest tests/system/performance/ tests/system/reliability/ -v
  ```
- Тесты пользовательских историй (4.1)
  ```bash
  python -m pytest tests/acceptance/user_stories/ -v
  ```

### Низкоприоритетные тесты

- Тесты безопасности (3.3)
  ```bash
  python -m pytest tests/system/security/ -v
  ```
- Тесты удобства использования (4.2)
  ```bash
  python -m pytest tests/acceptance/usability/ -v
  ```

## Методология выполнения тестов

### Подход TDD (Test-Driven Development)

1. Сначала пишем тест, определяющий ожидаемое поведение компонента
2. Запускаем тест и убеждаемся, что он не проходит (так как компонент еще не реализован)
3. Реализуем минимальный код, необходимый для прохождения теста
4. Запускаем тест снова и убеждаемся, что он проходит
5. Рефакторим код, сохраняя прохождение теста

### Порядок выполнения

1. Начинаем с тестов ядра системы (1.1)
   ```bash
   python -m pytest tests/unit/core/ -v
   ```
2. Переходим к тестам функциональных модулей (1.2)
   ```bash
   python -m pytest tests/unit/core/vision/ tests/unit/core/input/ tests/unit/core/web/ -v
   ```
3. Реализуем интеграционные тесты (2.1, 2.2)
   ```bash
   python -m pytest tests/integration/ -v
   ```
4. Добавляем системные тесты (3.1, 3.2, 3.3)
   ```bash
   python -m pytest tests/system/ -v
   ```
5. Завершаем приемочными тестами (4.1, 4.2)
   ```bash
   python -m pytest tests/acceptance/ -v
   ```

### Критерии успешности

- Все тесты проходят успешно
  ```bash
  python -m pytest tests/
  ```
- Покрытие кода тестами не менее 80%
  ```bash
  python -m pytest --cov=core tests/ --cov-report=html
  ```
- Время выполнения всех тестов не превышает 10 минут
  ```bash
  time python -m pytest tests/
  ```
- Отсутствие ложноположительных и ложноотрицательных результатов
  ```bash
  python -m pytest tests/ -v --no-header --no-summary
  ```

## Отчеты о состоянии тестирования

### Общий отчет о прохождении всех тестов

```bash
python -m pytest tests/ -v --html=report.html --self-contained-html
```

### Отчет о покрытии кода тестами

```bash
python -m pytest --cov=core tests/ --cov-report=html --cov-report=term
```

### Отчет о непройденных тестах

```bash
python -m pytest tests/ -v --tb=short -k "not passed"
```

### Отчет о времени выполнения тестов

```bash
python -m pytest tests/ --durations=0
```

## Детализация ключевых модульных тестов

### Тест регистрации и получения компонентов (test_component_registry.py)

- **test_register_component**: Регистрация нового компонента
  - Регистрация компонента с корректным ID и реализацией
  - Попытка регистрации компонента с дублирующим ID (ожидается ошибка)
  - Регистрация компонента с зависимостями
- **test_get_component**: Получение зарегистрированного компонента
  - Получение существующего компонента по ID
  - Попытка получения несуществующего компонента (ожидается None или ошибка)
  - Получение компонента с разрешением зависимостей
- **test_component_lifecyle**: Проверка жизненного цикла компонентов
  - Инициализация компонента при получении
  - Корректное завершение работы компонента при остановке системы
  - Повторная инициализация компонента после перезапуска

### Тест инициализации системы (test_system_initializer.py)

- **test_system_startup**: Запуск системы
  - Корректная загрузка компонентов при старте
  - Разрешение зависимостей между компонентами
  - Проверка порядка инициализации компонентов
- **test_system_shutdown**: Остановка системы
  - Корректное завершение всех компонентов
  - Освобождение ресурсов
  - Сохранение состояния при необходимости
- **test_system_recovery**: Восстановление после сбоев
  - Перезапуск компонента после сбоя
  - Восстановление состояния системы
  - Логирование информации о сбое

### Тест управления окнами (test_window_manager.py)

- **test_find_window**: Поиск окна
  - Поиск окна по заголовку
  - Поиск окна по классу
  - Поиск окна по процессу
  - Поиск несуществующего окна (ожидается пустой результат)
- **test_activate_window**: Активация окна
  - Активация существующего окна
  - Проверка, что окно стало активным
  - Попытка активации несуществующего окна (ожидается ошибка)
- **test_window_info**: Получение информации об окне
  - Получение заголовка окна
  - Получение размеров окна
  - Получение состояния окна (свернуто, развернуто)
- **test_window_operations**: Операции с окном
  - Изменение размера окна
  - Перемещение окна
  - Сворачивание/разворачивание окна
  - Закрытие окна

## Руководство по использованию моков в TDD

### Основные принципы моков

1. **Изолируйте тестируемый компонент** от внешних зависимостей
2. **Имитируйте только необходимые для теста методы** и поведение
3. **Проверяйте не только результаты, но и взаимодействия** с моками
4. **Создавайте моки по уровням** - от полных заглушек до сложных имитаций поведения

### Типы моков для проекта

1. **Dummy** - объекты-заполнители для параметров, которые не используются в тесте
2. **Stub** - объекты с предопределенными ответами на вызовы
3. **Spy** - объекты, отслеживающие вызовы методов и их параметры
4. **Mock** - программируемые объекты с ожиданиями о вызовах
5. **Fake** - упрощенные реализации реальных компонентов

### Примеры использования моков

#### Мок браузера для тестирования ElementFinder

```python
def test_find_element_by_id():
    # Создаем мок-драйвер
    mock_driver = MagicMock()
    mock_element = MagicMock()
    mock_driver.find_element.return_value = mock_element

    # Создаем мок контроллера браузера
    mock_browser_controller = MagicMock()
    mock_browser_controller.driver = mock_driver

    # Создаем тестируемый объект с моком в качестве зависимости
    element_finder = ElementFinder(mock_browser_controller)

    # Вызываем тестируемый метод
    element = element_finder.find_element_by_id("test-id")

    # Проверяем взаимодействие с моком
    mock_driver.find_element.assert_called_once_with(By.ID, "test-id")

    # Проверяем результат
    assert element is mock_element
```

#### Мок контроллера мыши для тестирования UI-взаимодействия

```python
def test_ui_action():
    # Создаем мок контроллера мыши
    mock_mouse = MagicMock()

    # Настраиваем поведение мока
    mock_mouse.click.return_value = True

    # Создаем тестируемый объект
    ui_action = UIAction(mouse_controller=mock_mouse)

    # Вызываем тестируемый метод
    result = ui_action.click_button((100, 200))

    # Проверяем взаимодействие с моком
    mock_mouse.move_to.assert_called_once_with(100, 200)
    mock_mouse.click.assert_called_once()

    # Проверяем результат
    assert result is True
```

### Рекомендации по работе с моками

1. **Используйте патчинг** для замены глобальных объектов:

   ```python
   @patch('module.ClassName')
   def test_function(mock_class):
       mock_class.return_value.method.return_value = 'test'
       result = function_to_test()
       assert result == 'test'
   ```

2. **Создавайте фабрики моков** для часто используемых зависимостей:

   ```python
   def create_browser_mock():
       mock_browser = MagicMock()
       mock_browser.driver.find_element.return_value = MagicMock()
       return mock_browser
   ```

3. **Используйте контекстные менеджеры** для временного патчинга:

   ```python
   def test_function():
       with patch('module.function') as mock_function:
           mock_function.return_value = 'test'
           result = function_to_test()
           assert result == 'test'
   ```

4. **Отдавайте предпочтение моку методов**, а не объектов целиком:

   ```python
   # Предпочтительно
   real_object.method = MagicMock(return_value='test')

   # Менее предпочтительно
   mock_object = MagicMock()
   mock_object.method.return_value = 'test'
   ```

5. **Создавайте автомоки для сложных объектов**:
   ```python
   class BrowserAutoMock:
       def __init__(self):
           self.driver = MagicMock()
           self.driver.find_element.return_value = MagicMock()
           self.driver.find_elements.return_value = [MagicMock(), MagicMock()]
           self.driver.execute_script.return_value = None
   ```
