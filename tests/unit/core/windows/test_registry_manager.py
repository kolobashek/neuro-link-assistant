import pytest
import winreg
from unittest.mock import patch, MagicMock

class TestRegistryManager:
    """Тесты класса управления реестром Windows"""
    
    @pytest.fixture
    def registry_manager(self):
        """Создает экземпляр RegistryManager"""
        from core.windows.registry_manager import RegistryManager
        return RegistryManager()
    
    @patch('winreg.OpenKey')
    @patch('winreg.QueryValueEx')
    def test_read_value(self, mock_query_value, mock_open_key, registry_manager):
        """Тест чтения значения из реестра"""
        # Настраиваем моки
        mock_key = MagicMock()
        mock_open_key.return_value = mock_key
        mock_query_value.return_value = ("test_value", winreg.REG_SZ)
        
        # Читаем значение из реестра
        value = registry_manager.read_value(
            winreg.HKEY_CURRENT_USER,
            "Software\\Test",
            "TestValue"
        )
        
        # Проверяем результат
        assert value == "test_value"
        mock_open_key.assert_called_once_with(winreg.HKEY_CURRENT_USER, "Software\\Test", 0, winreg.KEY_READ)
        mock_query_value.assert_called_once_with(mock_key, "TestValue")
    
    @patch('winreg.OpenKey')
    @patch('winreg.QueryValueEx')
    def test_read_value_not_found(self, mock_query_value, mock_open_key, registry_manager):
        """Тест чтения несуществующего значения из реестра"""
        # Настраиваем моки для имитации отсутствия значения
        mock_open_key.return_value = MagicMock()
        mock_query_value.side_effect = FileNotFoundError()
        
        # Читаем значение из реестра
        value = registry_manager.read_value(
            winreg.HKEY_CURRENT_USER,
            "Software\\Test",
            "NonExistentValue"
        )
        
        # Проверяем результат
        assert value is None
    
    @patch('winreg.OpenKey')
    def test_read_value_key_not_found(self, mock_open_key, registry_manager):
        """Тест чтения значения из несуществующего ключа реестра"""
        # Настраиваем моки для имитации отсутствия ключа
        mock_open_key.side_effect = FileNotFoundError()
        
        # Читаем значение из реестра
        value = registry_manager.read_value(
            winreg.HKEY_CURRENT_USER,
            "Software\\NonExistentKey",
            "TestValue"
        )
        
        # Проверяем результат
        assert value is None
    
    @patch('winreg.CreateKey')
    @patch('winreg.SetValueEx')
    def test_write_value(self, mock_set_value, mock_create_key, registry_manager):
        """Тест записи значения в реестр"""
        # Настраиваем моки
        mock_key = MagicMock()
        mock_create_key.return_value = mock_key
        
        # Записываем значение в реестр
        result = registry_manager.write_value(
            winreg.HKEY_CURRENT_USER,
            "Software\\Test",
            "TestValue",
            "new_value",
            winreg.REG_SZ
        )
        
        # Проверяем результат
        assert result is True
        mock_create_key.assert_called_once_with(winreg.HKEY_CURRENT_USER, "Software\\Test")
        mock_set_value.assert_called_once_with(mock_key, "TestValue", 0, winreg.REG_SZ, "new_value")
    
    @patch('winreg.CreateKey')
    @patch('winreg.SetValueEx')
    def test_write_value_error(self, mock_set_value, mock_create_key, registry_manager):
        """Тест записи значения в реестр с ошибкой"""
        # Настраиваем моки для имитации ошибки
        mock_create_key.return_value = MagicMock()
        mock_set_value.side_effect = PermissionError()
        
        # Записываем значение в реестр
        result = registry_manager.write_value(
            winreg.HKEY_CURRENT_USER,
            "Software\\Test",
            "TestValue",
            "new_value",
            winreg.REG_SZ
        )
        
        # Проверяем результат
        assert result is False
    
    @patch('winreg.OpenKey')
    @patch('winreg.DeleteValue')
    def test_delete_value(self, mock_delete_value, mock_open_key, registry_manager):
        """Тест удаления значения из реестра"""
        # Настраиваем моки
        mock_key = MagicMock()
        mock_open_key.return_value = mock_key
        
        # Удаляем значение из реестра
        result = registry_manager.delete_value(
            winreg.HKEY_CURRENT_USER,
            "Software\\Test",
            "TestValue"
        )
        
        # Проверяем результат
        assert result is True
        mock_open_key.assert_called_once_with(winreg.HKEY_CURRENT_USER, "Software\\Test", 0, winreg.KEY_WRITE)
        mock_delete_value.assert_called_once_with(mock_key, "TestValue")
    
    @patch('winreg.OpenKey')
    @patch('winreg.DeleteValue')
    def test_delete_value_not_found(self, mock_delete_value, mock_open_key, registry_manager):
        """Тест удаления несуществующего значения из реестра"""
        # Настраиваем моки для имитации отсутствия значения
        mock_open_key.return_value = MagicMock()
        mock_delete_value.side_effect = FileNotFoundError()
        
        # Удаляем значение из реестра
        result = registry_manager.delete_value(
            winreg.HKEY_CURRENT_USER,
            "Software\\Test",
            "NonExistentValue"
        )
        
        # Проверяем результат
        assert result is False
    
    @patch('winreg.OpenKey')
    @patch('winreg.EnumValue')
    def test_list_values(self, mock_enum_value, mock_open_key, registry_manager):
        """Тест получения списка значений из реестра"""
        # Настраиваем моки
        mock_key = MagicMock()
        mock_open_key.return_value = mock_key
        
        # Настраиваем мок для EnumValue, чтобы он возвращал разные значения при последовательных вызовах
        mock_enum_value.side_effect = [
            ("Value1", "data1", winreg.REG_SZ),
            ("Value2", "data2", winreg.REG_SZ),
            ("Value3", 123, winreg.REG_DWORD),
            WindowsError()  # Вызываем исключение для завершения цикла
        ]
        
        # Получаем список значений из реестра
        values = registry_manager.list_values(
            winreg.HKEY_CURRENT_USER,
            "Software\\Test"
        )
        
        # Проверяем результат
        assert len(values) == 3
        assert values[0] == {"name": "Value1", "data": "data1", "type": winreg.REG_SZ}
        assert values[1] == {"name": "Value2", "data": "data2", "type": winreg.REG_SZ}
        assert values[2] == {"name": "Value3", "data": 123, "type": winreg.REG_DWORD}
    
    @patch('winreg.OpenKey')
    def test_list_values_key_not_found(self, mock_open_key, registry_manager):
        """Тест получения списка значений из несуществующего ключа реестра"""
        # Настраиваем моки для имитации отсутствия ключа
        mock_open_key.side_effect = FileNotFoundError()
        
        # Получаем список значений из реестра
        values = registry_manager.list_values(
            winreg.HKEY_CURRENT_USER,
            "Software\\NonExistentKey"
        )
        
        # Проверяем результат
        assert values == []
    
    @patch('winreg.OpenKey')
    @patch('winreg.EnumKey')
    def test_list_keys(self, mock_enum_key, mock_open_key, registry_manager):
        """Тест получения списка подключей из реестра"""
        # Настраиваем моки
        mock_key = MagicMock()
        mock_open_key.return_value = mock_key
        
        # Настраиваем мок для EnumKey, чтобы он возвращал разные значения при последовательных вызовах
        mock_enum_key.side_effect = [
            "Subkey1",
            "Subkey2",
            "Subkey3",
            WindowsError()  # Вызываем исключение для завершения цикла
        ]
        
        # Получаем список подключей из реестра
        keys = registry_manager.list_keys(
            winreg.HKEY_CURRENT_USER,
            "Software\\Test"
        )
        
        # Проверяем результат
        assert len(keys) == 3
        assert "Subkey1" in keys
        assert "Subkey2" in keys
        assert "Subkey3" in keys
    
    @patch('winreg.OpenKey')
    def test_list_keys_key_not_found(self, mock_open_key, registry_manager):
        """Тест получения списка подключей из несуществующего ключа реестра"""
        # Настраиваем моки для имитации отсутствия ключа
        mock_open_key.side_effect = FileNotFoundError()
        
        # Получаем список подключей из реестра
        keys = registry_manager.list_keys(
            winreg.HKEY_CURRENT_USER,
            "Software\\NonExistentKey"
        )
        
        # Проверяем результат
        assert keys == []
    
    @patch('winreg.CreateKey')
    def test_create_key(self, mock_create_key, registry_manager):
        """Тест создания ключа реестра"""
        # Настраиваем моки
        mock_key = MagicMock()
        mock_create_key.return_value = mock_key
        
        # Создаем ключ реестра
        result = registry_manager.create_key(
            winreg.HKEY_CURRENT_USER,
            "Software\\Test\\NewKey"
        )
        
        # Проверяем результат
        assert result is True
        mock_create_key.assert_called_once_with(winreg.HKEY_CURRENT_USER, "Software\\Test\\NewKey")
    
    @patch('winreg.CreateKey')
    def test_create_key_error(self, mock_create_key, registry_manager):
        """Тест создания ключа реестра с ошибкой"""
        # Настраиваем моки для имитации ошибки
        mock_create_key.side_effect = PermissionError()
        
        # Создаем ключ реестра
        result = registry_manager.create_key(
            winreg.HKEY_CURRENT_USER,
            "Software\\Test\\NewKey"
        )
        
        # Проверяем результат
        assert result is False
    
    @patch('winreg.OpenKey')
    @patch('winreg.DeleteKey')
    def test_delete_key(self, mock_delete_key, mock_open_key, registry_manager):
        """Тест удаления ключа реестра"""
        # Настраиваем моки
        mock_key = MagicMock()
        mock_open_key.return_value = mock_key
        
        # Удаляем ключ реестра
        result = registry_manager.delete_key(
            winreg.HKEY_CURRENT_USER,
            "Software\\Test\\KeyToDelete"
        )
        
        # Проверяем результат
        assert result is True
        mock_open_key.assert_called_once_with(winreg.HKEY_CURRENT_USER, "Software\\Test", 0, winreg.KEY_WRITE)
        mock_delete_key.assert_called_once_with(mock_key, "KeyToDelete")
    
    @patch('winreg.OpenKey')
    @patch('winreg.DeleteKey')
    def test_delete_key_not_found(self, mock_delete_key, mock_open_key, registry_manager):
        """Тест удаления несуществующего ключа реестра"""
        # Настраиваем моки для имитации отсутствия ключа
        mock_open_key.return_value = MagicMock()
        mock_delete_key.side_effect = FileNotFoundError()
        
        # Удаляем ключ реестра
        result = registry_manager.delete_key(
            winreg.HKEY_CURRENT_USER,
            "Software\\Test\\NonExistentKey"
        )
        
        # Проверяем результат
        assert result is False