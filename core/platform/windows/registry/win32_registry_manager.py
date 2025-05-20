# -*- coding: utf-8 -*-
"""
Реализация менеджера реестра для Windows.
"""
import winreg
from typing import Any, Dict, List

from core.common.error_handler import handle_error
from core.common.registry.base import AbstractRegistryManager


class Win32RegistryManager(AbstractRegistryManager):
    """
    Менеджер реестра Windows.
    Предоставляет функции для работы с реестром Windows.
    """

    # Константы для корневых ключей реестра
    HKEY_CLASSES_ROOT = winreg.HKEY_CLASSES_ROOT
    HKEY_CURRENT_USER = winreg.HKEY_CURRENT_USER
    HKEY_LOCAL_MACHINE = winreg.HKEY_LOCAL_MACHINE
    HKEY_USERS = winreg.HKEY_USERS
    HKEY_CURRENT_CONFIG = winreg.HKEY_CURRENT_CONFIG

    def read_value(self, root_key: Any, key_path: str, value_name: str) -> Any:
        """
        Читает значение из реестра.

        Args:
            root_key (Any): Корневой ключ (HKEY_*)
            key_path (str): Путь к ключу
            value_name (str): Имя значения

        Returns:
            Any: Значение из реестра или None, если значение не найдено
        """
        try:
            key = winreg.OpenKey(root_key, key_path, 0, winreg.KEY_READ)
            value, _ = winreg.QueryValueEx(key, value_name)
            winreg.CloseKey(key)
            return value
        except FileNotFoundError:
            # Ключ или значение не найдены
            return None
        except Exception as e:
            handle_error(
                f"Error reading registry value {key_path}\\{value_name}: {e}", e, module="registry"
            )
            return None

    def write_value(
        self, root_key: Any, key_path: str, value_name: str, value: Any, value_type=winreg.REG_SZ
    ) -> bool:
        """
        Записывает значение в реестр.

        Args:
            root_key (Any): Корневой ключ (HKEY_*)
            key_path (str): Путь к ключу
            value_name (str): Имя значения
            value (Any): Значение для записи
            value_type (int, optional): Тип значения (REG_*)

        Returns:
            bool: True в случае успешной записи
        """
        try:
            key = winreg.CreateKey(root_key, key_path)
            winreg.SetValueEx(key, value_name, 0, value_type, value)
            winreg.CloseKey(key)
            return True
        except Exception as e:
            handle_error(
                f"Error writing registry value {key_path}\\{value_name}: {e}", e, module="registry"
            )
            return False

    def delete_value(self, root_key: Any, key_path: str, value_name: str) -> bool:
        """
        Удаляет значение из реестра.

        Args:
            root_key (Any): Корневой ключ (HKEY_*)
            key_path (str): Путь к ключу
            value_name (str): Имя значения

        Returns:
            bool: True в случае успешного удаления
        """
        try:
            key = winreg.OpenKey(root_key, key_path, 0, winreg.KEY_WRITE)
            winreg.DeleteValue(key, value_name)
            winreg.CloseKey(key)
            return True
        except FileNotFoundError:
            # Ключ или значение не найдены
            return False
        except Exception as e:
            handle_error(
                f"Error deleting registry value {key_path}\\{value_name}: {e}", e, module="registry"
            )
            return False

    def list_values(self, root_key: Any, key_path: str) -> List[Dict[str, Any]]:
        """
        Получает список всех значений в ключе реестра.

        Args:
            root_key (Any): Корневой ключ (HKEY_*)
            key_path (str): Путь к ключу

        Returns:
            List[Dict[str, Any]]: Список словарей с информацией о значениях
        """
        try:
            key = winreg.OpenKey(root_key, key_path, 0, winreg.KEY_READ)
            values = []

            i = 0
            while True:
                try:
                    name, data, type_id = winreg.EnumValue(key, i)
                    values.append({"name": name, "data": data, "type": type_id})
                    i += 1
                except WindowsError:
                    # Достигнут конец списка значений
                    break

            winreg.CloseKey(key)
            return values
        except FileNotFoundError:
            # Ключ не найден
            return []
        except Exception as e:
            handle_error(f"Error listing registry values in {key_path}: {e}", e, module="registry")
            return []

    def list_keys(self, root_key: Any, key_path: str) -> List[str]:
        """
        Получает список всех подключей в ключе реестра.

        Args:
            root_key (Any): Корневой ключ (HKEY_*)
            key_path (str): Путь к ключу

        Returns:
            List[str]: Список имен подключей
        """
        try:
            key = winreg.OpenKey(root_key, key_path, 0, winreg.KEY_READ)
            keys = []

            i = 0
            while True:
                try:
                    subkey = winreg.EnumKey(key, i)
                    keys.append(subkey)
                    i += 1
                except WindowsError:
                    # Достигнут конец списка подключей
                    break

            winreg.CloseKey(key)
            return keys
        except FileNotFoundError:
            # Ключ не найден
            return []
        except Exception as e:
            handle_error(f"Error listing registry subkeys in {key_path}: {e}", e, module="registry")
            return []

    def create_key(self, root_key: Any, key_path: str) -> bool:
        """
        Создает ключ реестра.

        Args:
            root_key (Any): Корневой ключ (HKEY_*)
            key_path (str): Путь к ключу

        Returns:
            bool: True в случае успешного создания
        """
        try:
            key = winreg.CreateKey(root_key, key_path)
            winreg.CloseKey(key)
            return True
        except Exception as e:
            handle_error(f"Error creating registry key {key_path}: {e}", e, module="registry")
            return False

    def delete_key(self, root_key: Any, key_path: str) -> bool:
        """
        Удаляет ключ реестра.

        Args:
            root_key (Any): Корневой ключ (HKEY_*)
            key_path (str): Путь к ключу

        Returns:
            bool: True в случае успешного удаления
        """
        try:
            # Разделяем путь на родительский ключ и имя удаляемого ключа
            parent_path, key_name = key_path.rsplit("\\", 1) if "\\" in key_path else ("", key_path)

            # Открываем родительский ключ
            parent_key = winreg.OpenKey(root_key, parent_path, 0, winreg.KEY_WRITE)

            # Удаляем ключ
            winreg.DeleteKey(parent_key, key_name)

            winreg.CloseKey(parent_key)
            return True
        except FileNotFoundError:
            # Ключ не найден
            return False
        except Exception as e:
            handle_error(f"Error deleting registry key {key_path}: {e}", e, module="registry")
            return False

    def key_exists(self, root_key: Any, key_path: str) -> bool:
        """
        Проверяет существование ключа реестра.

        Args:
            root_key (Any): Корневой ключ (HKEY_*)
            key_path (str): Путь к ключу

        Returns:
            bool: True, если ключ существует
        """
        try:
            key = winreg.OpenKey(root_key, key_path, 0, winreg.KEY_READ)
            winreg.CloseKey(key)
            return True
        except FileNotFoundError:
            return False
        except Exception as e:
            handle_error(
                f"Error checking registry key existence {key_path}: {e}", e, module="registry"
            )
            return False

    def value_exists(self, root_key: Any, key_path: str, value_name: str) -> bool:
        """
        Проверяет существование значения в реестре.

        Args:
            root_key (Any): Корневой ключ (HKEY_*)
            key_path (str): Путь к ключу
            value_name (str): Имя значения

        Returns:
            bool: True, если значение существует
        """
        try:
            key = winreg.OpenKey(root_key, key_path, 0, winreg.KEY_READ)
            value, _ = winreg.QueryValueEx(key, value_name)
            winreg.CloseKey(key)
            return True
        except FileNotFoundError:
            return False
        except Exception as e:
            handle_error(
                f"Error checking registry value existence {key_path}\\{value_name}: {e}",
                e,
                module="registry",
            )
            return False

    def get_value_type(self, root_key: Any, key_path: str, value_name: str) -> int:
        """
        Получает тип значения в реестре.

        Args:
            root_key (Any): Корневой ключ (HKEY_*)
            key_path (str): Путь к ключу
            value_name (str): Имя значения

        Returns:
            int: Тип значения (REG_*) или -1 в случае ошибки
        """
        try:
            key = winreg.OpenKey(root_key, key_path, 0, winreg.KEY_READ)
            _, value_type = winreg.QueryValueEx(key, value_name)
            winreg.CloseKey(key)
            return value_type
        except FileNotFoundError:
            return -1
        except Exception as e:
            handle_error(
                f"Error getting registry value type {key_path}\\{value_name}: {e}",
                e,
                module="registry",
            )
            return -1

    def export_key(self, root_key: Any, key_path: str, file_path: str) -> bool:
        """
        Экспортирует ключ реестра в файл .reg.

        Args:
            root_key (Any): Корневой ключ (HKEY_*)
            key_path (str): Путь к ключу
            file_path (str): Путь к файлу .reg

        Returns:
            bool: True в случае успешного экспорта
        """
        try:
            # Определяем имя корневого ключа для файла .reg
            root_key_names = {
                winreg.HKEY_CLASSES_ROOT: "HKEY_CLASSES_ROOT",
                winreg.HKEY_CURRENT_USER: "HKEY_CURRENT_USER",
                winreg.HKEY_LOCAL_MACHINE: "HKEY_LOCAL_MACHINE",
                winreg.HKEY_USERS: "HKEY_USERS",
                winreg.HKEY_CURRENT_CONFIG: "HKEY_CURRENT_CONFIG",
            }

            if root_key not in root_key_names:
                handle_error("Unknown root key for registry export", module="registry")
                return False

            root_key_name = root_key_names[root_key]

            # Создаем процесс для экспорта через regedit
            import subprocess

            cmd = f'regedit /e "{file_path}" "{root_key_name}\\{key_path}"'
            subprocess.run(cmd, shell=True, check=True)

            return True
        except Exception as e:
            handle_error(
                f"Error exporting registry key {key_path} to {file_path}: {e}", e, module="registry"
            )
            return False

    def import_reg_file(self, file_path: str) -> bool:
        """
        Импортирует файл .reg в реестр.

        Args:
            file_path (str): Путь к файлу .reg

        Returns:
            bool: True в случае успешного импорта
        """
        try:
            import subprocess

            cmd = f'regedit /s "{file_path}"'
            subprocess.run(cmd, shell=True, check=True)
            return True
        except Exception as e:
            handle_error(f"Error importing registry file {file_path}: {e}", e, module="registry")
            return False
