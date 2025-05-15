  # Общая структура проекта neuro-assistant

  Проект для взаимодействия с операционной системой и внешними интерфейсами. Ниже описана общая структура проекта.

  ## Основные компоненты

  1. **Разделение на платформо-зависимые и платформо-независимые API**
   - Общие компоненты и интерфейсы: `core/common/`
   - Платформо-зависимые компоненты: `core/platform/windows/`

  2. **Основные контроллеры**
   - Контроллер файловой системы
   - Контроллер клавиатуры и мыши
   - Контроллер работы внешних служб (приложений и окон)
   - Контроллер работы системных процессов
   - Контроллер работы системных ошибок

  3. **Модули для работы с системой**
   - `core/filesystem/__init__.py` - Операции файловой системы
   - `core/input/__init__.py` - Операции клавиатуры и мыши
   - `core/process/__init__.py` - Операции системных процессов
   - `core/window/__init__.py` - Операции системных окон

  ## Общая структура интерфейса

  ## Примеры использования всех модулей

  ### Работа с файловой системой


  from core.filesystem import get_file_system

  # Получение контроллера файловой системы
  fs = get_file_system()

  # Использование системы
  if fs.file_exists('path/to/file.txt'):
      content = fs.read_file('path/to/file.txt')
      print(content)

  from core.input import get_input_controller

  # Получение контроллера ввода
  input_ctrl = get_input_controller()

  # Действия клавиатуры
  input_ctrl.keyboard.type_text('Hello, World!')
  input_ctrl.keyboard.hotkey('ctrl', 'a')

  # Действия мыши
  input_ctrl.mouse.move_to(100, 100)
  input_ctrl.mouse.click()

  from core.process import get_process_manager

  # Получение менеджера процессов
  proc_mgr = get_process_manager()

  # Запуск процесса
  pid = proc_mgr.start_process('notepad.exe')

  # Проверка состояния процесса
  if proc_mgr.is_process_running('notepad.exe'):
      print('Notepad запущен')

  # Завершение процесса
  proc_mgr.kill_process(pid)

  from core.window import get_window_manager

  # Получение менеджера окон
  win_mgr = get_window_manager()

  # Получение окна по заголовку
  notepad_window = win_mgr.get_window_by_title('Блокнот')

  if notepad_window:
      # Активация окна
      win_mgr.activate_window(notepad_window)

      # Максимизация окна
      win_mgr.maximize_window(notepad_window)

      # Закрытие окна
      win_mgr.close_window(notepad_window)

  from core.common.error_handler import handle_error, handle_llm_error

  # Общая обработка ошибок
  try:
      # какой-то код
      pass
  except Exception as e:
      handle_error("Произошла ошибка", e, module='my_module')

  # Обработка ошибок LLM
  try:
      # работа с нейросетью
      pass
  except Exception as e:
      handle_llm_error("Ошибка при работе с LLM", e, model="gpt-4", prompt="текст запроса")

                        # Было
  from core.windows.file_system import FileSystem
  fs = FileSystem()

  # Стало
  from core.filesystem import get_file_system
  fs = get_file_system()

                     # Было
  from core.input.keyboard_controller import KeyboardController
  from core.input.mouse_controller import MouseController
  kb = KeyboardController()
  mouse = MouseController()

  # Стало
  from core.input import get_input_controller
  input_ctrl = get_input_controller()
  # Далее используются input_ctrl.keyboard и input_ctrl.mouse
