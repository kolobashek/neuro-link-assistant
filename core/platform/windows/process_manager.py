  # Windows-специфичный менеджер управления процессами
import os
import subprocess
import psutil
import time
from core.common.error_handler import handle_error

class WindowsProcessManager:
      """Управление процессами в Windows"""

      def start_process(self, command, shell=True, cwd=None, env=None):
          """
          Запускает процесс

          Args:
              command (str): Команда для запуска
              shell (bool): Использовать ли оболочку
              cwd (str, optional): Рабочая директория
              env (dict, optional): Переменные окружения

          Returns:
              int: ID процесса или None в случае ошибки
          """
          try:
              process = subprocess.Popen(
                  command,
                  shell=shell,
                  cwd=cwd,
                  env=env
              )
              return process.pid
          except Exception as e:
              handle_error(f"Ошибка при запуске процесса '{command}': {e}", e, module='process')
              return None

      def kill_process(self, pid):
          """
          Завершает процесс по ID

          Args:
              pid (int): ID процесса

          Returns:
              bool: True, если процесс успешно завершен
          """
          try:
              if psutil.pid_exists(pid):
                  process = psutil.Process(pid)
                  process.terminate()

                  # Ждем завершения процесса
                  gone, still_alive = psutil.wait_procs([process], timeout=3)
                  if still_alive:
                      # Если процесс не завершился, убиваем его
                      process.kill()
                  return True
              else:
                  handle_error(f"Процесс с ID {pid} не найден", module='process', log_level='warning')
                  return False
          except Exception as e:
              handle_error(f"Ошибка при завершении процесса {pid}: {e}", e, module='process')
              return False

      def is_process_running(self, name):
          """
          Проверяет, запущен ли процесс с указанным именем

          Args:
              name (str): Имя процесса

          Returns:
              bool: True, если процесс запущен
          """
          try:
              for proc in psutil.process_iter(['pid', 'name']):
                  if name.lower() in proc.info['name'].lower():
                      return True
              return False
          except Exception as e:
              handle_error(f"Ошибка при проверке процесса {name}: {e}", e, module='process')
              return False

      def get_process_by_name(self, name):
          """
          Получает список процессов с указанным именем

          Args:
              name (str): Имя процесса

          Returns:
              list: Список найденных процессов
          """
          try:
              matching_processes = []
              for proc in psutil.process_iter(['pid', 'name']):
                  if name.lower() in proc.info['name'].lower():
                      matching_processes.append(proc)
              return matching_processes
          except Exception as e:
              handle_error(f"Ошибка при получении процесса {name}: {e}", e, module='process')
              return []

      def get_all_processes(self):
          """
          Получает список всех запущенных процессов

          Returns:
              list: Список текущих процессов
          """
          try:
              return list(psutil.process_iter(['pid', 'name', 'username']))
          except Exception as e:
              handle_error(f"Ошибка при получении списка процессов: {e}", e, module='process')
              return []
