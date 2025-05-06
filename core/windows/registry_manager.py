import winreg

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
    
    # Константы для типов данных реестра
    REG_SZ = winreg.REG_SZ
    REG_BINARY = winreg.REG_BINARY
    REG_DWORD = winreg.REG_DWORD
    REG_QWORD = winreg.REG_QWORD
    REG_MULTI_SZ = winreg.REG_MULTI_SZ
    REG_EXPAND_SZ = winreg.REG_EXPAND_SZ
    
    def read_value(self, root_key, key_path, value_name):
        """
        Читает значение из реестра.
        
        Args:
            root_key (int): Корневой ключ реестра
            key_path (str): Путь к ключу
            value_name (str): Имя значения
            
        Returns:
            tuple: (значение, тип) или (None, None) в случае ошибки
        """
        try:
            key = winreg.OpenKey(root_key, key_path, 0, winreg.KEY_READ)
            value, value_type = winreg.QueryValueEx(key, value_name)
            winreg.CloseKey(key)
            return value, value_type
        except Exception as e:
            print(f"Error reading registry value: {e}")
            return None, None
    
    def write_value(self, root_key, key_path, value_name, value, value_type=None):
        """
        Записывает значение в реестр.
        
        Args:
            root_key (int): Корневой ключ реестра
            key_path (str): Путь к ключу
            value_name (str): Имя значения
            value: Значение для записи
            value_type (int, optional): Тип значения
            
        Returns:
            bool: True в случае успешной записи
        """
        try:
            # Если тип не указан, определяем его автоматически
            if value_type is None:
                if isinstance(value, str):
                    value_type = winreg.REG_SZ
                elif isinstance(value, int):
                    value_type = winreg.REG_DWORD
                elif isinstance(value, bytes):
                    value_type = winreg.REG_BINARY
                else:
                    value_type = winreg.REG_SZ
                    value = str(value)
            
            # Создаем ключ, если он не существует
            try:
                key = winreg.OpenKey(root_key, key_path, 0, winreg.KEY_WRITE)
            except:
                key = winreg.CreateKey(root_key, key_path)
            
            winreg.SetValueEx(key, value_name, 0, value_type, value)
            winreg.CloseKey(key)
            return True
        except Exception as e:
            print(f"Error writing registry value: {e}")
            return False
    
    def delete_value(self, root_key, key_path, value_name):
        """
        Удаляет значение из реестра.
        
        Args:
            root_key (int): Корневой ключ реестра
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
        except Exception as e:
            print(f"Error deleting registry value: {e}")
            return False
    
    def create_key(self, root_key, key_path):
        """
        Создает ключ реестра.
        
        Args:
            root_key (int): Корневой ключ реестра
            key_path (str): Путь к ключу
            
        Returns:
            bool: True в случае успешного создания
        """
        try:
            key = winreg.CreateKey(root_key, key_path)
            winreg.CloseKey(key)
            return True
        except Exception as e:
            print(f"Error creating registry key: {e}")
            return False
    
    def delete_key(self, root_key, key_path):
        """
        Удаляет ключ реестра.
        
        Args:
            root_key (int): Корневой ключ реестра
            key_path (str): Путь к ключу
            
        Returns:
            bool: True в случае успешного удаления
        """
        try:
            # Проверяем, есть ли подключи
            try:
                key = winreg.OpenKey(root_key, key_path, 0, winreg.KEY_READ)
                subkey_count = winreg.QueryInfoKey(key)[0]
                winreg.CloseKey(key)
                
                # Если есть подключи, удаляем их рекурсивно
                if subkey_count > 0:
                    key = winreg.OpenKey(root_key, key_path, 0, winreg.KEY_READ)
                    for i in range(subkey_count):
                        # Получаем имя подключа (всегда берем индекс 0, так как после удаления индексы смещаются)
                        subkey_name = winreg.EnumKey(key, 0)
                        # Рекурсивно удаляем подключ
                        self.delete_key(root_key, f"{key_path}\\{subkey_name}")
                    winreg.CloseKey(key)
            except WindowsError:
                pass
            
            # Удаляем сам ключ
            winreg.DeleteKey(root_key, key_path)
            return True
        except Exception as e:
            print(f"Error deleting registry key: {e}")
            return False
    
    def list_values(self, root_key, key_path):
        """
        Получает список значений ключа реестра.
        
        Args:
            root_key (int): Корневой ключ реестра
            key_path (str): Путь к ключу
            
        Returns:
            list: Список кортежей (имя, значение, тип)
        """
        try:
            key = winreg.OpenKey(root_key, key_path, 0, winreg.KEY_READ)
            values = []
            
            i = 0
            while True:
                try:
                    name, value, value_type = winreg.EnumValue(key, i)
                    values.append((name, value, value_type))
                    i += 1
                except WindowsError:
                    break
            
            winreg.CloseKey(key)
            return values
        except Exception as e:
            print(f"Error listing registry values: {e}")
            return []
    
    def list_keys(self, root_key, key_path):
        """
        Получает список подключей ключа реестра.
        
        Args:
            root_key (int): Корневой ключ реестра
            key_path (str): Путь к ключу
            
        Returns:
            list: Список имен подключей
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
                    break
            
            winreg.CloseKey(key)
            return keys
        except Exception as e:
            print(f"Error listing registry keys: {e}")
            return []