import winreg
from core.common.error_handler import handle_error

class RegistryManager:
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
    
    def read_value(self, hkey, key_path, value_name):
        """
        Читает значение из реестра.
        
        Args:
            hkey (int): Корневой ключ (HKEY_*)
            key_path (str): Путь к ключу
            value_name (str): Имя значения
            
        Returns:
            any: Значение из реестра или None, если значение не найдено
        """
        try:
            key = winreg.OpenKey(hkey, key_path, 0, winreg.KEY_READ)
            value, _ = winreg.QueryValueEx(key, value_name)
            winreg.CloseKey(key)
            return value
        except FileNotFoundError:
            # Ключ или значение не найдены
            return None
        except Exception as e:
            handle_error(f"Error reading registry value {key_path}\\{value_name}: {e}", e, module='registry')
            return None
    
    def write_value(self, hkey, key_path, value_name, value, value_type=winreg.REG_SZ):
        """
        Записывает значение в реестр.
        
        Args:
            hkey (int): Корневой ключ (HKEY_*)
            key_path (str): Путь к ключу
            value_name (str): Имя значения
            value (any): Значение для записи
            value_type (int, optional): Тип значения (REG_*)
            
        Returns:
            bool: True в случае успешной записи
        """
        try:
            key = winreg.CreateKey(hkey, key_path)
            winreg.SetValueEx(key, value_name, 0, value_type, value)
            winreg.CloseKey(key)
            return True
        except Exception as e:
            handle_error(f"Error writing registry value {key_path}\\{value_name}: {e}", e, module='registry')
            return False
    
    def delete_value(self, hkey, key_path, value_name):
        """
        Удаляет значение из реестра.
        
        Args:
            hkey (int): Корневой ключ (HKEY_*)
            key_path (str): Путь к ключу
            value_name (str): Имя значения
            
        Returns:
            bool: True в случае успешного удаления
        """
        try:
            key = winreg.OpenKey(hkey, key_path, 0, winreg.KEY_WRITE)
            winreg.DeleteValue(key, value_name)
            winreg.CloseKey(key)
            return True
        except FileNotFoundError:
            # Ключ или значение не найдены
            return False
        except Exception as e:
            handle_error(f"Error deleting registry value {key_path}\\{value_name}: {e}", e, module='registry')
            return False
    
    def list_values(self, hkey, key_path):
        """
        Получает список всех значений в ключе реестра.
        
        Args:
            hkey (int): Корневой ключ (HKEY_*)
            key_path (str): Путь к ключу
            
        Returns:
            list: Список словарей с информацией о значениях
        """
        try:
            key = winreg.OpenKey(hkey, key_path, 0, winreg.KEY_READ)
            values = []
            
            i = 0
            while True:
                try:
                    name, data, type_id = winreg.EnumValue(key, i)
                    values.append({
                        "name": name,
                        "data": data,
                        "type": type_id
                    })
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
            handle_error(f"Error listing registry values in {key_path}: {e}", e, module='registry')
            return []
    
    def list_keys(self, hkey, key_path):
        """
        Получает список всех подключей в ключе реестра.
        
        Args:
            hkey (int): Корневой ключ (HKEY_*)
            key_path (str): Путь к ключу
            
        Returns:
            list: Список имен подключей
        """
        try:
            key = winreg.OpenKey(hkey, key_path, 0, winreg.KEY_READ)
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
            handle_error(f"Error listing registry subkeys in {key_path}: {e}", e, module='registry')
            return []
    
    def create_key(self, hkey, key_path):
        """
        Создает ключ реестра.
        
        Args:
            hkey (int): Корневой ключ (HKEY_*)
            key_path (str): Путь к ключу
            
        Returns:
            bool: True в случае успешного создания
        """
        try:
            key = winreg.CreateKey(hkey, key_path)
            winreg.CloseKey(key)
            return True
        except Exception as e:
            handle_error(f"Error creating registry key {key_path}: {e}", e, module='registry')
            return False
    
    def delete_key(self, hkey, key_path):
        """
        Удаляет ключ реестра.
        
        Args:
            hkey (int): Корневой ключ (HKEY_*)
            key_path (str): Путь к ключу
            
        Returns:
            bool: True в случае успешного удаления
        """
        try:
            # Разделяем путь на родительский ключ и имя удаляемого ключа
            parent_path, key_name = key_path.rsplit('\\', 1) if '\\' in key_path else ('', key_path)
            
            # Открываем родительский ключ
            parent_key = winreg.OpenKey(hkey, parent_path, 0, winreg.KEY_WRITE)
            
            # Удаляем ключ
            winreg.DeleteKey(parent_key, key_name)
            
            winreg.CloseKey(parent_key)
            return True
        except FileNotFoundError:
            # Ключ не найден
            return False
        except Exception as e:
            handle_error(f"Error deleting registry key {key_path}: {e}", e, module='registry')
            return False
    
    def key_exists(self, hkey, key_path):
        """
        Проверяет существование ключа реестра.
        
        Args:
            hkey (int): Корневой ключ (HKEY_*)
            key_path (str): Путь к ключу
            
        Returns:
            bool: True, если ключ существует
        """
        try:
            key = winreg.OpenKey(hkey, key_path, 0, winreg.KEY_READ)
            winreg.CloseKey(key)
            return True
        except FileNotFoundError:
            return False
        except Exception as e:
            handle_error(f"Error checking registry key {key_path}: {e}", e, module='registry')
            return False
    
    def value_exists(self, hkey, key_path, value_name):
        """
        Проверяет существование значения в реестре.
        
        Args:
            hkey (int): Корневой ключ (HKEY_*)
            key_path (str): Путь к ключу
            value_name (str): Имя значения
            
        Returns:
            bool: True, если значение существует
        """
        try:
            key = winreg.OpenKey(hkey, key_path, 0, winreg.KEY_READ)
            try:
                winreg.QueryValueEx(key, value_name)
                exists = True
            except FileNotFoundError:
                exists = False
            winreg.CloseKey(key)
            return exists
        except FileNotFoundError:
            return False
        except Exception as e:
            handle_error(f"Error checking registry value {key_path}\\{value_name}: {e}", e, module='registry')
            return False