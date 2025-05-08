import unittest
from unittest.mock import patch, MagicMock, Mock
import winreg
from core.windows.registry_manager import RegistryManager

class TestRegistryManager(unittest.TestCase):
    """Тесты для менеджера реестра Windows"""
    
    def setUp(self):
        """Настройка перед каждым тестом"""
        self.registry_manager = RegistryManager()
    
    @patch('winreg.OpenKey')
    @patch('winreg.QueryValueEx')
    @patch('winreg.CloseKey')  # Добавляем патч для CloseKey
    def test_read_value(self, mock_close_key, mock_query_value, mock_open_key):
        """Тест чтения значения из реестра"""
        # Настраиваем моки
        mock_key = Mock()
        mock_open_key.return_value = mock_key
        mock_query_value.return_value = ("test_value", winreg.REG_SZ)
        
        # Читаем значение из реестра
        value = self.registry_manager.read_value(
            winreg.HKEY_CURRENT_USER,
            "Software\\Test",
            "TestValue"
        )
        
        # Проверяем результат
        self.assertEqual(value, "test_value")
        mock_open_key.assert_called_once_with(winreg.HKEY_CURRENT_USER, "Software\\Test", 0, winreg.KEY_READ)
        mock_query_value.assert_called_once_with(mock_key, "TestValue")
        mock_close_key.assert_called_once_with(mock_key)
    
    @patch('winreg.OpenKey')
    @patch('winreg.QueryValueEx')
    def test_read_value_not_found(self, mock_query_value, mock_open_key):
        """Тест чтения несуществующего значения из реестра"""
        # Настраиваем моки для имитации отсутствия значения
        mock_key = Mock()
        mock_open_key.return_value = mock_key
        mock_query_value.side_effect = FileNotFoundError()
        
        # Патчим CloseKey, чтобы избежать ошибки
        with patch('winreg.CloseKey'):
            # Читаем несуществующее значение из реестра
            value = self.registry_manager.read_value(
                winreg.HKEY_CURRENT_USER,
                "Software\\Test",
                "NonExistentValue"
            )
        
        # Проверяем результат
        self.assertIsNone(value)
    
    @patch('winreg.OpenKey')
    def test_read_value_key_not_found(self, mock_open_key):
        """Тест чтения значения из несуществующего ключа реестра"""
        # Настраиваем мок для имитации отсутствия ключа
        mock_open_key.side_effect = FileNotFoundError()
        
        # Читаем значение из несуществующего ключа реестра
        value = self.registry_manager.read_value(
            winreg.HKEY_CURRENT_USER,
            "Software\\NonExistentKey",
            "TestValue"
        )
        
        # Проверяем результат
        self.assertIsNone(value)
    
    @patch('winreg.CreateKey')
    @patch('winreg.SetValueEx')
    @patch('winreg.CloseKey')  # Добавляем патч для CloseKey
    def test_write_value(self, mock_close_key, mock_set_value, mock_create_key):
        """Тест записи значения в реестр"""
        # Настраиваем моки
        mock_key = Mock()
        mock_create_key.return_value = mock_key
        
        # Записываем значение в реестр
        result = self.registry_manager.write_value(
            winreg.HKEY_CURRENT_USER,
            "Software\\Test",
            "TestValue",
            "new_value",
            winreg.REG_SZ
        )
        
        # Проверяем результат
        self.assertTrue(result)
        mock_create_key.assert_called_once_with(winreg.HKEY_CURRENT_USER, "Software\\Test")
        mock_set_value.assert_called_once_with(mock_key, "TestValue", 0, winreg.REG_SZ, "new_value")
        mock_close_key.assert_called_once_with(mock_key)
    
    @patch('winreg.CreateKey')
    @patch('winreg.SetValueEx')
    def test_write_value_error(self, mock_set_value, mock_create_key):
        """Тест обработки ошибки при записи значения в реестр"""
        # Настраиваем моки для имитации ошибки
        mock_create_key.side_effect = Exception("Test error")
        
        # Записываем значение в реестр с ошибкой
        result = self.registry_manager.write_value(
            winreg.HKEY_CURRENT_USER,
            "Software\\Test",
            "TestValue",
            "new_value",
            winreg.REG_SZ
        )
        
        # Проверяем результат
        self.assertFalse(result)
    
    @patch('winreg.OpenKey')
    @patch('winreg.DeleteValue')
    @patch('winreg.CloseKey')  # Добавляем патч для CloseKey
    def test_delete_value(self, mock_close_key, mock_delete_value, mock_open_key):
        """Тест удаления значения из реестра"""
        # Настраиваем моки
        mock_key = Mock()
        mock_open_key.return_value = mock_key
        
        # Удаляем значение из реестра
        result = self.registry_manager.delete_value(
            winreg.HKEY_CURRENT_USER,
            "Software\\Test",
            "TestValue"
        )
        
        # Проверяем результат
        self.assertTrue(result)
        mock_open_key.assert_called_once_with(winreg.HKEY_CURRENT_USER, "Software\\Test", 0, winreg.KEY_WRITE)
        mock_delete_value.assert_called_once_with(mock_key, "TestValue")
        mock_close_key.assert_called_once_with(mock_key)
    
    @patch('winreg.OpenKey')
    @patch('winreg.DeleteValue')
    def test_delete_value_not_found(self, mock_delete_value, mock_open_key):
        """Тест удаления несуществующего значения из реестра"""
        # Настраиваем моки для имитации отсутствия значения
        mock_key = Mock()
        mock_open_key.return_value = mock_key
        mock_delete_value.side_effect = FileNotFoundError()
        
        # Патчим CloseKey, чтобы избежать ошибки
        with patch('winreg.CloseKey'):
            # Удаляем несуществующее значение из реестра
            result = self.registry_manager.delete_value(
                winreg.HKEY_CURRENT_USER,
                "Software\\Test",
                "NonExistentValue"
            )
        
        # Проверяем результат
        self.assertFalse(result)
    
    @patch('winreg.OpenKey')
    @patch('winreg.EnumValue')
    @patch('winreg.CloseKey')  # Добавляем патч для CloseKey
    def test_list_values(self, mock_close_key, mock_enum_value, mock_open_key):
        """Тест получения списка значений из реестра"""
        # Настраиваем моки
        mock_key = Mock()
        mock_open_key.return_value = mock_key
        
        # Настраиваем мок для EnumValue, чтобы он возвращал разные значения при последовательных вызовах
        mock_enum_value.side_effect = [
            ("Value1", "data1", winreg.REG_SZ),
            ("Value2", "data2", winreg.REG_SZ),
            ("Value3", 123, winreg.REG_DWORD),
            WindowsError()  # Вызываем исключение для завершения цикла
        ]
        
        # Получаем список значений из реестра
        values = self.registry_manager.list_values(
            winreg.HKEY_CURRENT_USER,
            "Software\\Test"
        )
        
        # Проверяем результат
        self.assertEqual(len(values), 3)
        self.assertEqual(values[0]["name"], "Value1")
        self.assertEqual(values[0]["data"], "data1")
        self.assertEqual(values[0]["type"], winreg.REG_SZ)
        self.assertEqual(values[1]["name"], "Value2")
        self.assertEqual(values[1]["data"], "data2")
        self.assertEqual(values[1]["type"], winreg.REG_SZ)
        self.assertEqual(values[2]["name"], "Value3")
        self.assertEqual(values[2]["data"], 123)
        self.assertEqual(values[2]["type"], winreg.REG_DWORD)
        mock_close_key.assert_called_once_with(mock_key)
    
    @patch('winreg.OpenKey')
    def test_list_values_key_not_found(self, mock_open_key):
        """Тест получения списка значений из несуществующего ключа реестра"""
        # Настраиваем мок для имитации отсутствия ключа
        mock_open_key.side_effect = FileNotFoundError()
        
        # Получаем список значений из несуществующего ключа реестра
        values = self.registry_manager.list_values(
            winreg.HKEY_CURRENT_USER,
            "Software\\NonExistentKey"
        )
        
        # Проверяем результат
        self.assertEqual(values, [])
    
    @patch('winreg.OpenKey')
    @patch('winreg.EnumKey')
    @patch('winreg.CloseKey')  # Добавляем патч для CloseKey
    def test_list_keys(self, mock_close_key, mock_enum_key, mock_open_key):
        """Тест получения списка подключей из реестра"""
        # Настраиваем моки
        mock_key = Mock()
        mock_open_key.return_value = mock_key
        
        # Настраиваем мок для EnumKey, чтобы он возвращал разные значения при последовательных вызовах
        mock_enum_key.side_effect = [
            "Subkey1",
            "Subkey2",
            "Subkey3",
            WindowsError()  # Вызываем исключение для завершения цикла
        ]
        
        # Получаем список подключей из реестра
        keys = self.registry_manager.list_keys(
            winreg.HKEY_CURRENT_USER,
            "Software\\Test"
        )
        
        # Проверяем результат
        self.assertEqual(len(keys), 3)
        self.assertEqual(keys[0], "Subkey1")
        self.assertEqual(keys[1], "Subkey2")
        self.assertEqual(keys[2], "Subkey3")
        mock_close_key.assert_called_once_with(mock_key)
    
    @patch('winreg.OpenKey')
    def test_list_keys_key_not_found(self, mock_open_key):
        """Тест получения списка подключей из несуществующего ключа реестра"""
        # Настраиваем мок для имитации отсутствия ключа
        mock_open_key.side_effect = FileNotFoundError()
        
        # Получаем список подключей из несуществующего ключа реестра
        keys = self.registry_manager.list_keys(
            winreg.HKEY_CURRENT_USER,
            "Software\\NonExistentKey"
        )
        
        # Проверяем результат
        self.assertEqual(keys, [])
    
    @patch('winreg.CreateKey')
    @patch('winreg.CloseKey')  # Добавляем патч для CloseKey
    def test_create_key(self, mock_close_key, mock_create_key):
        """Тест создания ключа реестра"""
        # Настраиваем моки
        mock_key = Mock()
        mock_create_key.return_value = mock_key
        
        # Создаем ключ реестра
        result = self.registry_manager.create_key(
            winreg.HKEY_CURRENT_USER,
            "Software\\Test\\NewKey"
        )
        
        # Проверяем результат
        self.assertTrue(result)
        mock_create_key.assert_called_once_with(winreg.HKEY_CURRENT_USER, "Software\\Test\\NewKey")
        mock_close_key.assert_called_once_with(mock_key)
    
    @patch('winreg.CreateKey')
    def test_create_key_error(self, mock_create_key):
        """Тест обработки ошибки при создании ключа реестра"""
        # Настраиваем мок для имитации ошибки
        mock_create_key.side_effect = Exception("Test error")
        
        # Создаем ключ реестра с ошибкой
        result = self.registry_manager.create_key(
            winreg.HKEY_CURRENT_USER,
            "Software\\Test\\NewKey"
        )
        
        # Проверяем результат
        self.assertFalse(result)
    
    @patch('winreg.OpenKey')
    @patch('winreg.DeleteKey')
    @patch('winreg.CloseKey')  # Добавляем патч для CloseKey
    def test_delete_key(self, mock_close_key, mock_delete_key, mock_open_key):
        """Тест удаления ключа реестра"""
        # Настраиваем моки
        mock_key = Mock()
        mock_open_key.return_value = mock_key
        
        # Удаляем ключ реестра
        result = self.registry_manager.delete_key(
            winreg.HKEY_CURRENT_USER,
            "Software\\Test\\KeyToDelete"
        )
        
        # Проверяем результат
        self.assertTrue(result)
        # Проверяем, что OpenKey был вызван с правильными параметрами
        # Для удаления ключа нам нужно открыть родительский ключ
        mock_open_key.assert_called_once_with(winreg.HKEY_CURRENT_USER, "Software\\Test", 0, winreg.KEY_WRITE)
        # Проверяем, что DeleteKey был вызван с правильными параметрами
        mock_delete_key.assert_called_once_with(mock_key, "KeyToDelete")
        mock_close_key.assert_called_once_with(mock_key)
    
    @patch('winreg.OpenKey')
    def test_delete_key_not_found(self, mock_open_key):
        """Тест удаления несуществующего ключа реестра"""
        # Настраиваем мок для имитации отсутствия ключа
        mock_open_key.side_effect = FileNotFoundError()
        
        # Удаляем несуществующий ключ реестра
        result = self.registry_manager.delete_key(
            winreg.HKEY_CURRENT_USER,
            "Software\\Test\\NonExistentKey"
        )
        
        # Проверяем результат
        self.assertFalse(result)