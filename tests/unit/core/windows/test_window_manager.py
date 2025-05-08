import pytest
from unittest.mock import patch, MagicMock
from core.windows import WindowManager

class TestWindowManager:
    """Тесты менеджера окон Windows"""
    
    @pytest.fixture
    def window_manager(self):
        """Создает экземпляр WindowManager"""
        return WindowManager()
    
    @patch('win32gui.EnumWindows')
    def test_find_window_by_title(self, mock_enum_windows, window_manager):
        """Тест поиска окна по заголовку"""
        # Создаем функцию для имитации обратного вызова EnumWindows
        def fake_enum_windows(callback, extra):
            # Имитируем окна
            callback(1001, None)  # Окно с заголовком "Test Window"
            callback(1002, None)  # Окно с заголовком "Another Window"
            callback(1003, None)  # Окно с заголовком "Not Matching"
        
        # Настраиваем моки
        mock_enum_windows.side_effect = fake_enum_windows
        
        # Настраиваем мок для GetWindowText
        with patch('win32gui.GetWindowText', side_effect=lambda hwnd: {
            1001: "Test Window",
            1002: "Another Test Window",
            1003: "Not Matching"
        }.get(hwnd, "")):
            # Настраиваем мок для IsWindowVisible
            with patch('win32gui.IsWindowVisible', return_value=True):
                # Настраиваем мок для GetClassName
                with patch('win32gui.GetClassName', return_value="TestClass"):
                    # Настраиваем мок для GetWindowRect
                    with patch('win32gui.GetWindowRect', return_value=(0, 0, 100, 100)):
                        # Ищем окно по заголовку
                        window = window_manager.find_window(title="Test Window")
                        
                        # Проверяем результат
                        assert window is not None
                        assert window["hwnd"] == 1001
                        assert window["title"] == "Test Window"
                        assert window["class"] == "TestClass"
                        assert window["rect"] == (0, 0, 100, 100)
    
    @patch('win32gui.EnumWindows')
    def test_find_window_by_class(self, mock_enum_windows, window_manager):
        """Тест поиска окна по имени класса"""
        # Создаем функцию для имитации обратного вызова EnumWindows
        def fake_enum_windows(callback, extra):
            # Имитируем окна
            callback(1001, None)  # Окно с классом "TestClass"
            callback(1002, None)  # Окно с классом "AnotherClass"
        
        # Настраиваем моки
        mock_enum_windows.side_effect = fake_enum_windows
        
        # Настраиваем мок для GetWindowText
        with patch('win32gui.GetWindowText', return_value="Test Window"):
            # Настраиваем мок для IsWindowVisible
            with patch('win32gui.IsWindowVisible', return_value=True):
                # Настраиваем мок для GetClassName
                with patch('win32gui.GetClassName', side_effect=lambda hwnd: {
                    1001: "TestClass",
                    1002: "AnotherClass"
                }.get(hwnd, "")):
                    # Настраиваем мок для GetWindowRect
                    with patch('win32gui.GetWindowRect', return_value=(0, 0, 100, 100)):
                        # Ищем окно по имени класса
                        window = window_manager.find_window(class_name="TestClass")
                        
                        # Проверяем результат
                        assert window is not None
                        assert window["hwnd"] == 1001
                        assert window["title"] == "Test Window"
                        assert window["class"] == "TestClass"
    
    @patch('win32gui.EnumWindows')
    @patch('win32process.GetWindowThreadProcessId')
    @patch('psutil.Process')
    def test_find_window_by_process(self, mock_process, mock_get_process_id, mock_enum_windows, window_manager):
        """Тест поиска окна по имени процесса"""
        # Создаем функцию для имитации обратного вызова EnumWindows
        def fake_enum_windows(callback, extra):
            # Имитируем окна
            callback(1001, None)  # Окно процесса "test_process.exe"
            callback(1002, None)  # Окно процесса "another_process.exe"
        
        # Настраиваем моки
        mock_enum_windows.side_effect = fake_enum_windows
        
        # Настраиваем мок для GetWindowThreadProcessId
        mock_get_process_id.side_effect = lambda hwnd: (0, {
            1001: 2001,
            1002: 2002
        }.get(hwnd, 0))
        
        # Настраиваем мок для Process
        mock_process_obj1 = MagicMock()
        mock_process_obj1.name.return_value = "test_process.exe"
        
        mock_process_obj2 = MagicMock()
        mock_process_obj2.name.return_value = "another_process.exe"
        
        mock_process.side_effect = lambda pid: {
            2001: mock_process_obj1,
            2002: mock_process_obj2
        }.get(pid)
        
        # Настраиваем мок для GetWindowText
        with patch('win32gui.GetWindowText', return_value="Test Window"):
            # Настраиваем мок для IsWindowVisible
            with patch('win32gui.IsWindowVisible', return_value=True):
                # Настраиваем мок для GetClassName
                with patch('win32gui.GetClassName', return_value="TestClass"):
                    # Настраиваем мок для GetWindowRect
                    with patch('win32gui.GetWindowRect', return_value=(0, 0, 100, 100)):
                        # Ищем окно по имени процесса
                        window = window_manager.find_window(process_name="test_process")
                        
                        # Проверяем результат
                        assert window is not None
                        assert window["hwnd"] == 1001
                        assert window["title"] == "Test Window"
                        assert window["class"] == "TestClass"
    
    @patch('win32gui.SetForegroundWindow')
    def test_activate_window(self, mock_set_foreground, window_manager):
        """Тест активации окна"""
        # Создаем информацию об окне
        window_info = {"hwnd": 1001, "title": "Test Window"}
        
        # Настраиваем мок для IsIconic
        with patch('win32gui.IsIconic', return_value=False):
            # Активируем окно
            result = window_manager.activate_window(window_info)
            
            # Проверяем результат
            assert result is True
            
            # Проверяем вызов SetForegroundWindow
            mock_set_foreground.assert_called_once_with(1001)
    
    @patch('win32gui.SetForegroundWindow')
    @patch('win32gui.ShowWindow')
    def test_activate_minimized_window(self, mock_show_window, mock_set_foreground, window_manager):
        """Тест активации свернутого окна"""
        # Создаем информацию об окне
        window_info = {"hwnd": 1001, "title": "Test Window"}
        
        # Настраиваем мок для IsIconic
        with patch('win32gui.IsIconic', return_value=True):
            # Активируем окно
            result = window_manager.activate_window(window_info)
            
            # Проверяем результат
            assert result is True
            
            # Проверяем вызов ShowWindow
            import win32con
            mock_show_window.assert_called_once_with(1001, win32con.SW_RESTORE)
            
            # Проверяем вызов SetForegroundWindow
            mock_set_foreground.assert_called_once_with(1001)
    
    def test_activate_invalid_window(self, window_manager):
        """Тест активации недопустимого окна"""
        # Активируем недопустимое окно
        result = window_manager.activate_window(None)
        
        # Проверяем результат
        assert result is False
        
        # Активируем окно без hwnd
        result = window_manager.activate_window({"title": "Test Window"})
        
        # Проверяем результат
        assert result is False
    
    @patch('win32gui.PostMessage')
    def test_close_window(self, mock_post_message, window_manager):
        """Тест закрытия окна"""
        # Создаем информацию об окне
        window_info = {"hwnd": 1001, "title": "Test Window"}
        
        # Закрываем окно
        result = window_manager.close_window(window_info)
        
        # Проверяем результат
        assert result is True
        
        # Проверяем вызов PostMessage
        import win32con
        mock_post_message.assert_called_once_with(1001, win32con.WM_CLOSE, 0, 0)
    
    def test_close_invalid_window(self, window_manager):
        """Тест закрытия недопустимого окна"""
        # Закрываем недопустимое окно
        result = window_manager.close_window(None)
        
        # Проверяем результат
        assert result is False
        
        # Закрываем окно без hwnd
        result = window_manager.close_window({"title": "Test Window"})
        
        # Проверяем результат
        assert result is False
    
    @patch('win32gui.GetWindowText')
    def test_get_window_text(self, mock_get_window_text, window_manager):
        """Тест получения текста заголовка окна"""
        # Настраиваем мок для GetWindowText
        mock_get_window_text.return_value = "Test Window"
        
        # Создаем информацию об окне
        window_info = {"hwnd": 1001}
        
        # Получаем текст заголовка
        text = window_manager.get_window_text(window_info)
        
        # Проверяем результат
        assert text == "Test Window"
        
        # Проверяем вызов GetWindowText
        mock_get_window_text.assert_called_once_with(1001)
    
    def test_get_window_text_invalid(self, window_manager):
        """Тест получения текста заголовка недопустимого окна"""
        # Получаем текст заголовка недопустимого окна
        text = window_manager.get_window_text(None)
        
        # Проверяем результат
        assert text == ""
        
        # Получаем текст заголовка окна без hwnd
        text = window_manager.get_window_text({"title": "Test Window"})
        
        # Проверяем результат
        assert text == ""
    
    @patch('win32gui.EnumWindows')
    def test_get_all_windows(self, mock_enum_windows, window_manager):
        """Тест получения списка всех окон"""
        # Создаем функцию для имитации обратного вызова EnumWindows
        def fake_enum_windows(callback, extra):
            # Имитируем окна
            callback(1001, None)  # Окно с заголовком "Window 1"
            callback(1002, None)  # Окно с заголовком "Window 2"
            callback(1003, None)  # Окно с пустым заголовком
        
        # Настраиваем моки
        mock_enum_windows.side_effect = fake_enum_windows
        
        # Настраиваем мок для GetWindowText
        with patch('win32gui.GetWindowText', side_effect=lambda hwnd: {
            1001: "Window 1",
            1002: "Window 2",
            1003: ""
        }.get(hwnd, "")):
            # Настраиваем мок для IsWindowVisible
            with patch('win32gui.IsWindowVisible', return_value=True):
                # Настраиваем мок для GetClassName
                with patch('win32gui.GetClassName', return_value="TestClass"):
                    # Настраиваем мок для GetWindowRect
                    with patch('win32gui.GetWindowRect', return_value=(0, 0, 100, 100)):
                        # Получаем список всех окон
                        windows = window_manager.get_all_windows()
                        
                        # Проверяем результат
                        assert len(windows) == 2  # Окно с пустым заголовком должно быть пропущено
                        assert windows[0]["hwnd"] == 1001
                        assert windows[0]["title"] == "Window 1"
                        assert windows[0]["class"] == "TestClass"
                        assert windows[1]["hwnd"] == 1002
                        assert windows[1]["title"] == "Window 2"
                        assert windows[1]["class"] == "TestClass"