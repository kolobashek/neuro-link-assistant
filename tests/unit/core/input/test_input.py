import pytest
import time
from unittest.mock import patch, MagicMock
from pynput.keyboard import Key, Controller as KeyboardController
from pynput.mouse import Button, Controller as MouseController

class TestKeyboardController:
    """Тесты контроллера клавиатуры"""
    
    @pytest.fixture
    def keyboard_controller(self):
        """Создает экземпляр KeyboardController с мокнутым контроллером pynput"""
        with patch('core.input.keyboard_controller.Controller') as mock_controller:
            from core.input.keyboard_controller import KeyboardController
            controller = KeyboardController(human_like=False)
            controller.keyboard = mock_controller.return_value
            yield controller
    
    def test_type_text(self, keyboard_controller):
        """Тест ввода текста"""
        text = "Hello, World!"
        
        result = keyboard_controller.type_text(text, delay=0)
        
        assert result is True
        # Проверяем, что для каждого символа были вызваны press и release
        assert keyboard_controller.keyboard.press.call_count == len(text)
        assert keyboard_controller.keyboard.release.call_count == len(text)
    
    def test_press_key(self, keyboard_controller):
        """Тест нажатия клавиши"""
        result = keyboard_controller.press_key('a')
        
        assert result is True
        keyboard_controller.keyboard.press.assert_called_once_with('a')
        keyboard_controller.keyboard.release.assert_called_once_with('a')
    
    def test_press_special_key(self, keyboard_controller):
        """Тест нажатия специальной клавиши"""
        result = keyboard_controller.press_key('enter')
        
        assert result is True
        keyboard_controller.keyboard.press.assert_called_once_with(Key.enter)
        keyboard_controller.keyboard.release.assert_called_once_with(Key.enter)
    
    def test_press_and_hold(self, keyboard_controller):
        """Тест нажатия и удержания клавиши"""
        with patch('time.sleep') as mock_sleep:
            result = keyboard_controller.press_and_hold('a', duration=0.5)
            
            assert result is True
            keyboard_controller.keyboard.press.assert_called_once_with('a')
            keyboard_controller.keyboard.release.assert_called_once_with('a')
            mock_sleep.assert_called_once_with(0.5)
    
    def test_press_combination(self, keyboard_controller):
        """Тест нажатия комбинации клавиш"""
        keys = ['ctrl', 'c']
        
        result = keyboard_controller.press_combination(keys)
        
        assert result is True
        # Проверяем, что клавиши были нажаты и отпущены в правильном порядке
        assert keyboard_controller.keyboard.press.call_args_list[0][0][0] == Key.ctrl
        assert keyboard_controller.keyboard.press.call_args_list[1][0][0] == 'c'
        assert keyboard_controller.keyboard.release.call_args_list[0][0][0] == 'c'
        assert keyboard_controller.keyboard.release.call_args_list[1][0][0] == Key.ctrl
    
    def test_press_hotkey(self, keyboard_controller):
        """Тест нажатия горячей клавиши"""
        # Мокаем метод press_combination
        keyboard_controller.press_combination = MagicMock(return_value=True)
        
        result = keyboard_controller.press_hotkey('ctrl', 'c')
        
        assert result is True
        keyboard_controller.press_combination.assert_called_once_with(('ctrl', 'c'))
    
    def test_press_enter(self, keyboard_controller):
        """Тест нажатия Enter"""
        # Мокаем метод press_key
        keyboard_controller.press_key = MagicMock(return_value=True)
        
        result = keyboard_controller.press_enter()
        
        assert result is True
        keyboard_controller.press_key.assert_called_once_with(Key.enter)
    
    def test_press_backspace(self, keyboard_controller):
        """Тест нажатия Backspace"""
        # Мокаем метод press_key
        keyboard_controller.press_key = MagicMock(return_value=True)
        
        result = keyboard_controller.press_backspace(count=3)
        
        assert result is True
        assert keyboard_controller.press_key.call_count == 3
        keyboard_controller.press_key.assert_called_with(Key.backspace)
    
    def test_press_arrow(self, keyboard_controller):
        """Тест нажатия стрелки"""
        # Мокаем метод press_key
        keyboard_controller.press_key = MagicMock(return_value=True)
        
        result = keyboard_controller.press_arrow('right', count=2)
        
        assert result is True
        assert keyboard_controller.press_key.call_count == 2
        keyboard_controller.press_key.assert_called_with(Key.right)
    
    def test_press_ctrl_c(self, keyboard_controller):
        """Тест нажатия Ctrl+C"""
        # Мокаем метод press_combination
        keyboard_controller.press_combination = MagicMock(return_value=True)
        
        result = keyboard_controller.press_ctrl_c()
        
        assert result is True
        keyboard_controller.press_combination.assert_called_once_with([Key.ctrl, 'c'])
    
    def test_get_key_object(self, keyboard_controller):
        """Тест преобразования строкового представления клавиши в объект Key"""
        # Проверяем преобразование специальных клавиш
        assert keyboard_controller._get_key_object('enter') == Key.enter
        assert keyboard_controller._get_key_object('esc') == Key.esc
        assert keyboard_controller._get_key_object('ctrl') == Key.ctrl
        assert keyboard_controller._get_key_object('f1') == Key.f1
        
        # Проверяем, что обычные символы остаются без изменений
        assert keyboard_controller._get_key_object('a') == 'a'
        assert keyboard_controller._get_key_object('1') == '1'
        
        # Проверяем, что объекты Key остаются без изменений
        assert keyboard_controller._get_key_object(Key.enter) == Key.enter


class TestMouseController:
    """Тесты контроллера мыши"""
    
    @pytest.fixture
    def mouse_controller(self):
        """Создает экземпляр MouseController с мокнутыми контроллерами"""
        with patch('core.input.mouse_controller.Controller') as mock_controller, \
             patch('core.input.mouse_controller.pyautogui') as mock_pyautogui:
            from core.input.mouse_controller import MouseController
            controller = MouseController(human_like=False)
            controller.mouse = mock_controller.return_value
            controller.mouse.position = (100, 100)  # Устанавливаем начальную позицию
            yield controller, mock_pyautogui
    
    def test_move_to(self, mouse_controller):
        """Тест перемещения курсора мыши"""
        controller, mock_pyautogui = mouse_controller
        
        result = controller.move_to(200, 300, duration=0.5)
        
        assert result is True
        # Проверяем, что был вызван метод moveTo из pyautogui
        mock_pyautogui.moveTo.assert_called_once_with(200, 300, duration=0.5)
    
    def test_move_relative(self, mouse_controller):
        """Тест относительного перемещения курсора мыши"""
        controller, mock_pyautogui = mouse_controller
        controller.get_position = MagicMock(return_value=(100, 100))
        
        result = controller.move_relative(50, -30, duration=0.3)
        
        assert result is True
        # Проверяем, что был вызван метод moveTo из pyautogui с правильными координатами
        mock_pyautogui.moveTo.assert_called_once_with(150, 70, duration=0.3)
    
    def test_click(self, mouse_controller):
        """Тест клика мышью"""
        controller, _ = mouse_controller
        
        result = controller.click(button='left', count=2)
        
        assert result is True
        # Проверяем, что был вызван метод click из pynput.mouse.Controller
        assert controller.mouse.click.call_count == 2
        controller.mouse.click.assert_called_with(Button.left)
    
    def test_double_click(self, mouse_controller):
        """Тест двойного клика мышью"""
        controller, _ = mouse_controller
        # Мокаем метод click
        controller.click = MagicMock(return_value=True)
        
        result = controller.double_click()
        
        assert result is True
        controller.click.assert_called_once_with('left', count=2)
    
    def test_right_click(self, mouse_controller):
        """Тест клика правой кнопкой мыши"""
        controller, _ = mouse_controller
        # Мокаем метод click
        controller.click = MagicMock(return_value=True)
        
        result = controller.right_click()
        
        assert result is True
        controller.click.assert_called_once_with(button='right')
    
    def test_press_and_hold(self, mouse_controller):
        """Тест нажатия и удержания кнопки мыши"""
        controller, _ = mouse_controller
        
        with patch('time.sleep') as mock_sleep:
            result = controller.press_and_hold(button='left', duration=0.5)
            
            assert result is True
            controller.mouse.press.assert_called_once_with(Button.left)
            controller.mouse.release.assert_called_once_with(Button.left)
            mock_sleep.assert_called_once_with(0.5)
    
    def test_drag_to(self, mouse_controller):
        """Тест перетаскивания мышью"""
        controller, mock_pyautogui = mouse_controller
        
        result = controller.drag_to(200, 300, button='left', duration=0.5)
        
        assert result is True
        # Проверяем, что был вызван метод dragTo из pyautogui
        mock_pyautogui.dragTo.assert_called_once_with(200, 300, duration=0.5, button='left')
    
    def test_scroll(self, mouse_controller):
        """Тест прокрутки колесика мыши"""
        controller, _ = mouse_controller
        
        result = controller.scroll(amount=5, direction='down')
        
        assert result is True
        # Проверяем, что был вызван метод scroll из pynput.mouse.Controller
        controller.mouse.scroll.assert_called_with(0, -5)
    
    def test_get_position(self, mouse_controller):
        """Тест получения позиции курсора мыши"""
        controller, _ = mouse_controller
        controller.mouse.position = (200, 300)
        
        position = controller.get_position()
        
        assert position == (200, 300)
    
    def test_move_to_element(self, mouse_controller):
        """Тест перемещения курсора к элементу"""
        controller, _ = mouse_controller
        # Мокаем метод move_to
        controller.move_to = MagicMock(return_value=True)
        
        # Создаем мок-элемент с атрибутом location
        element = MagicMock()
        element.location = {'x': 100, 'y': 200}
        element.size = {'width': 50, 'height': 30}
        
        result = controller.move_to_element(element, offset_x=5, offset_y=10, duration=0.3)
        
        assert result is True
        # Проверяем, что был вызван метод move_to с правильными координатами
        # (100 + 50/2 + 5, 200 + 30/2 + 10) = (130, 225)
        controller.move_to.assert_called_once_with(130, 225, 0.3)
    
    def test_click_element(self, mouse_controller):
        """Тест клика по элементу"""
        controller, _ = mouse_controller
        # Мокаем методы move_to_element и click
        controller.move_to_element = MagicMock(return_value=True)
        controller.click = MagicMock(return_value=True)
        
        # Создаем мок-элемент
        element = MagicMock()
        
        result = controller.click_element(element, button='left', offset_x=5, offset_y=10)
        
        assert result is True
        # Проверяем, что были вызваны методы move_to_element и click
        controller.move_to_element.assert_called_once_with(element, 5, 10)
        controller.click.assert_called_once_with('left')
    
    def test_get_button_object(self, mouse_controller):
        """Тест преобразования строкового представления кнопки мыши в объект Button"""
        controller, _ = mouse_controller
        
        # Проверяем преобразование строковых представлений кнопок
        assert controller._get_button_object('left') == Button.left
        assert controller._get_button_object('right') == Button.right
        assert controller._get_button_object('middle') == Button.middle
        
        # Проверяем, что объекты Button остаются без изменений
        assert controller._get_button_object(Button.left) == Button.left
        
        # Проверяем, что для неизвестных строк возвращается левая кнопка
        assert controller._get_button_object('unknown') == Button.left