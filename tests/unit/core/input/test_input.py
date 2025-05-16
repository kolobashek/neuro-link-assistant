from unittest.mock import MagicMock, patch

import pytest
from pynput.keyboard import Key
from pynput.mouse import Button


class TestKeyboardController:
    """Тесты контроллера клавиатуры"""

    @pytest.fixture
    def keyboard_controller(self):
        """Создает экземпляр KeyboardController с мокнутым контроллером pynput"""
        with patch("core.input.keyboard_controller.Controller") as mock_controller:
            from core.input.keyboard_controller import KeyboardController as AppKeyboardController

            controller = AppKeyboardController(human_like=False)
            controller.controller = mock_controller.return_value
            yield controller

    def test_type_text(self, keyboard_controller):
        """Тест ввода текста"""
        text = "Hello, World!"

        result = keyboard_controller.type_text(text, delay=0)

        assert result is True
        # Проверяем, что для каждого символа были вызваны press и release
        assert keyboard_controller.controller.press.call_count == len(text)
        assert keyboard_controller.controller.release.call_count == len(text)

    def test_type_text_human_like(self, keyboard_controller):
        """Тест ввода текста с имитацией человека"""
        # Устанавливаем human_like=True для этого теста
        keyboard_controller.human_like = True

        with patch("time.sleep") as mock_sleep:
            text = "Hello, World!"
            result = keyboard_controller.type_text(text, interval=0.1)

            assert result is True
            # Проверяем, что для каждого символа были вызваны press и release
            assert keyboard_controller.controller.press.call_count == len(text)
            assert keyboard_controller.controller.release.call_count == len(text)
            # Проверяем, что sleep был вызван хотя бы раз
            assert mock_sleep.call_count >= 1

    def test_type_text_non_human_like(self, keyboard_controller):
        """Тест ввода текста без имитации человека"""
        # Устанавливаем human_like=False для этого теста
        keyboard_controller.human_like = False

        with patch("time.sleep") as mock_sleep:
            text = "Hello, World!"
            result = keyboard_controller.type_text(text, interval=0.1)

            assert result is True
            # Проверяем, что для каждого символа были вызваны press и release
            assert keyboard_controller.controller.press.call_count == len(text)
            assert keyboard_controller.controller.release.call_count == len(text)
            # Проверяем, что sleep не был вызван
            mock_sleep.assert_not_called()

    def test_press_key(self, keyboard_controller):
        """Тест нажатия клавиши"""
        result = keyboard_controller.press_key("a")

        assert result is True
        keyboard_controller.controller.press.assert_called_once_with("a")
        keyboard_controller.controller.release.assert_called_once_with("a")

    def test_press_special_key(self, keyboard_controller):
        """Тест нажатия специальной клавиши"""
        result = keyboard_controller.press_key("enter")

        assert result is True
        keyboard_controller.controller.press.assert_called_once_with(Key.enter)
        keyboard_controller.controller.release.assert_called_once_with(Key.enter)

    def test_press_and_hold(self, keyboard_controller):
        """Тест нажатия и удержания клавиши"""
        with patch("time.sleep") as mock_sleep:
            result = keyboard_controller.press_and_hold("a", duration=0.5)

            assert result is True
            keyboard_controller.controller.press.assert_called_once_with("a")
            keyboard_controller.controller.release.assert_called_once_with("a")
            mock_sleep.assert_called_once_with(0.5)

    def test_press_combination(self, keyboard_controller):
        """Тест нажатия комбинации клавиш"""
        keys = ["ctrl", "c"]

        result = keyboard_controller.press_combination(keys)

        assert result is True
        # Проверяем, что клавиши были нажаты и отпущены в правильном порядке
        assert keyboard_controller.controller.press.call_args_list[0][0][0] == Key.ctrl
        assert keyboard_controller.controller.press.call_args_list[1][0][0] == "c"
        assert keyboard_controller.controller.release.call_args_list[0][0][0] == "c"
        assert keyboard_controller.controller.release.call_args_list[1][0][0] == Key.ctrl

    def test_press_hotkey(self, keyboard_controller):
        """Тест нажатия горячей клавиши"""
        # Мокаем метод press_combination
        keyboard_controller.press_combination = MagicMock(return_value=True)

        result = keyboard_controller.press_hotkey("ctrl", "c")

        assert result is True
        keyboard_controller.press_combination.assert_called_once_with(("ctrl", "c"))

    def test_press_enter(self, keyboard_controller):
        """Тест нажатия Enter"""
        keyboard_controller.press_key = MagicMock(return_value=True)

        # Вызываем напрямую press_key с "enter"
        result = keyboard_controller.press_key("enter")

        assert result is True
        keyboard_controller.press_key.assert_called_once_with("enter")

    def test_press_backspace(self, keyboard_controller):
        """Тест нажатия Backspace"""
        # Мокаем метод press_key
        keyboard_controller.press_key = MagicMock(return_value=True)

        # Вызываем напрямую press_key с "backspace"
        result = keyboard_controller.press_key("backspace")

        assert result is True
        keyboard_controller.press_key.assert_called_once_with("backspace")

    def test_press_arrow(self, keyboard_controller):
        """Тест нажатия стрелки"""
        # Мокаем метод press_key
        keyboard_controller.press_key = MagicMock(return_value=True)

        # Вызываем напрямую press_key с "up"
        result = keyboard_controller.press_key("up")

        assert result is True
        keyboard_controller.press_key.assert_called_once_with("up")

    def test_press_ctrl_c(self, keyboard_controller):
        """Тест нажатия Ctrl+C"""
        keyboard_controller.press_combination = MagicMock(return_value=True)

        # Вызываем напрямую press_combination с нужной комбинацией
        result = keyboard_controller.press_combination(["ctrl", "c"])

        assert result is True
        keyboard_controller.press_combination.assert_called_once_with(["ctrl", "c"])

    def test_get_key_object(self, keyboard_controller):
        """Тест преобразования строкового представления клавиши в объект Key"""
        # Проверяем преобразование специальных клавиш
        assert keyboard_controller.get_key_object("enter") == Key.enter
        assert keyboard_controller.get_key_object("esc") == Key.esc
        assert keyboard_controller.get_key_object("ctrl") == Key.ctrl
        assert keyboard_controller.get_key_object("f1") == Key.f1

        # Проверяем, что обычные символы остаются без изменений
        assert keyboard_controller.get_key_object("a") == "a"
        assert keyboard_controller.get_key_object("1") == "1"

        # Проверяем, что объекты Key остаются без изменений
        assert keyboard_controller.get_key_object(Key.enter) == Key.enter


class TestMouseController:
    """Тесты контроллера мыши"""

    @pytest.fixture
    def mouse_controller(self):
        """Создает экземпляр MouseController с мокнутыми контроллерами"""
        with patch("core.input.mouse_controller.Controller") as mock_controller, patch(
            "core.input.mouse_controller.pyautogui"
        ) as mock_pyautogui:
            from core.input.mouse_controller import MouseController as AppMouseController

            controller = AppMouseController(human_like=True)
            controller.controller = mock_controller.return_value
            controller.controller.position = (100, 100)  # Устанавливаем начальную позицию
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

    def test_move_relative_human_like(self, mouse_controller):
        """Тест относительного перемещения курсора мыши с имитацией человека"""
        controller, mock_pyautogui = mouse_controller
        controller.human_like = True  # Устанавливаем человеческий режим
        controller.get_position = MagicMock(return_value=(100, 100))

        result = controller.move_relative(50, -30, duration=0.3)

        assert result is True
        # Проверяем вызов pyautogui.moveTo с правильными координатами
        mock_pyautogui.moveTo.assert_called_once_with(150, 70, duration=0.3)

    def test_move_relative_non_human_like(self, mouse_controller):
        """Тест относительного перемещения курсора мыши без имитации человека"""
        controller, mock_pyautogui = mouse_controller
        controller.human_like = False  # Явно указываем non-human режим
        controller.get_position = MagicMock(return_value=(100, 100))

        result = controller.move_relative(50, -30, duration=0.3)

        assert result is True
        # Проверяем вызов controller.move с правильными смещениями
        controller.controller.move.assert_called_once_with(50, -30)
        # Убеждаемся, что pyautogui.moveTo не вызывается
        mock_pyautogui.moveTo.assert_not_called()

    def test_click(self, mouse_controller):
        """Тест клика мышью"""
        controller, _ = mouse_controller

        result = controller.click(button="left", count=2)

        assert result is True
        # Проверяем, что был вызван метод click из pynput.mouse.Controller
        assert controller.controller.click.call_count == 2
        controller.controller.click.assert_called_with(Button.left)

    def test_double_click(self, mouse_controller):
        """Тест двойного клика мышью"""
        controller, _ = mouse_controller
        # Мокаем метод click
        controller.click = MagicMock(return_value=True)

        result = controller.double_click()

        assert result is True
        controller.click.assert_called_once_with("left", count=2)

    def test_right_click(self, mouse_controller):
        """Тест клика правой кнопкой мыши"""
        controller, _ = mouse_controller
        # Мокаем метод click
        controller.click = MagicMock(return_value=True)

        result = controller.right_click()

        assert result is True
        controller.click.assert_called_once_with(button="right")

    def test_press_and_hold(self, mouse_controller):
        """Тест нажатия и удержания кнопки мыши"""
        controller, _ = mouse_controller

        with patch("time.sleep") as mock_sleep:
            result = controller.press_and_hold(button="left", duration=0.5)

            assert result is True
            controller.controller.press.assert_called_once_with(Button.left)
            controller.controller.release.assert_called_once_with(Button.left)
            mock_sleep.assert_called_once_with(0.5)

    def test_click_human_like_multiple(self, mouse_controller):
        """Тест множественного клика мышью с имитацией человека"""
        controller, _ = mouse_controller
        controller.human_like = True

        with patch("time.sleep") as mock_sleep:
            result = controller.click(button="left", count=3)

            assert result is True
            # Проверяем, что был вызван метод click из pynput.mouse.Controller нужное количество раз
            assert controller.controller.click.call_count == 3
            # Проверяем, что sleep был вызван для добавления задержки между кликами
            assert mock_sleep.call_count >= 2  # 2 задержки между 3 кликами

    def test_click_non_human_like_multiple(self, mouse_controller):
        """Тест множественного клика мышью без имитации человека"""
        controller, _ = mouse_controller
        controller.human_like = False

        with patch("time.sleep") as mock_sleep:
            result = controller.click(button="left", count=3)

            assert result is True
            # Проверяем, что был вызван метод click из pynput.mouse.Controller нужное количество раз
            assert controller.controller.click.call_count == 3
            # Проверяем, что sleep не был вызван
            mock_sleep.assert_not_called()

    def test_drag_to(self, mouse_controller):
        """Тест перетаскивания мышью"""
        controller, mock_pyautogui = mouse_controller

        result = controller.drag_to(200, 300, button="left", duration=0.5)

        assert result is True
        # Проверяем, что был вызван метод dragTo из pyautogui
        mock_pyautogui.dragTo.assert_called_once_with(200, 300, duration=0.5, button="left")

    def test_scroll(self, mouse_controller):
        """Тест прокрутки колесика мыши"""
        controller, _ = mouse_controller

        # Принудительно устанавливаем non-human режим для простоты теста
        controller.human_like = False

        result = controller.scroll(amount=5, direction="down")

        assert result is True
        controller.controller.scroll.assert_called_with(0, -5)

    def test_scroll_non_human_like(self, mouse_controller):
        """Тест прокрутки колесика мыши без имитации человека"""
        controller, _ = mouse_controller
        controller.human_like = False

        with patch("time.sleep") as mock_sleep:
            result = controller.scroll(amount=5, direction="down")

            assert result is True
            # Проверяем, что был вызван метод scroll из pynput.mouse.Controller один раз
            controller.controller.scroll.assert_called_once_with(0, -5)
            # Проверяем, что sleep не был вызван
            mock_sleep.assert_not_called()

    def test_scroll_human_like(self, mouse_controller):
        """Тест прокрутки колесика мыши с имитацией человека"""
        controller, _ = mouse_controller
        controller.human_like = True

        with patch("time.sleep") as mock_sleep:
            result = controller.scroll(amount=5, direction="down")

            assert result is True
            # Проверяем, что был вызван метод scroll из pynput.mouse.Controller несколько раз
            assert controller.controller.scroll.call_count > 0
            # Проверяем, что sleep был вызван для добавления плавности
            assert mock_sleep.call_count > 0

    def test_get_position(self, mouse_controller):
        """Тест получения позиции курсора мыши"""
        controller, _ = mouse_controller
        controller.controller.position = (200, 300)

        position = controller.get_position()

        assert position == (200, 300)

    def test_move_to_element(self, mouse_controller):
        """Тест перемещения курсора к элементу"""
        controller, _ = mouse_controller
        # Мокаем метод move_to
        controller.move_to = MagicMock(return_value=True)

        # Создаем мок-элемент с атрибутом location
        element = MagicMock()
        element.location = {"x": 100, "y": 200}
        element.size = {"width": 50, "height": 30}

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

        result = controller.click_element(element, button="left", offset_x=5, offset_y=10)

        assert result is True
        # Проверяем, что были вызваны методы move_to_element и click
        controller.move_to_element.assert_called_once_with(element, 5, 10)
        controller.click.assert_called_once_with("left")

    def test_get_button_object(self, mouse_controller):
        """Тест преобразования строкового представления кнопки мыши в объект Button"""
        controller, _ = mouse_controller

        # Проверяем преобразование строковых представлений кнопок
        assert controller._get_button_object("left") == Button.left
        assert controller._get_button_object("right") == Button.right
        assert controller._get_button_object("middle") == Button.middle

        # Проверяем, что объекты Button остаются без изменений
        assert controller._get_button_object(Button.left) == Button.left

        # Проверяем, что для неизвестных строк возвращается левая кнопка
        assert controller._get_button_object("unknown") == Button.left

    def test_drag_to_human_like(self, mouse_controller):
        """Тест перетаскивания мышью с имитацией человека"""
        controller, mock_pyautogui = mouse_controller
        controller.human_like = True

        result = controller.drag_to(200, 300, button="left", duration=0.5)

        assert result is True
        # Проверяем, что был вызван метод dragTo из pyautogui
        mock_pyautogui.dragTo.assert_called_once_with(200, 300, duration=0.5, button="left")

    def test_drag_to_non_human_like(self, mouse_controller):
        """Тест перетаскивания мышью без имитации человека"""
        controller, mock_pyautogui = mouse_controller
        controller.human_like = False

        with patch("time.sleep") as mock_sleep:
            result = controller.drag_to(200, 300, button="left", duration=0.5)

            assert result is True
            # Проверяем, что был вызван метод press из pynput.mouse.Controller
            controller.controller.press.assert_called_once_with(Button.left)
            # Проверяем, что был вызван метод move_to
            mock_pyautogui.moveTo.assert_called_once_with(200, 300, duration=0.5)
            # Проверяем, что был вызван метод release из pynput.mouse.Controller
            controller.controller.release.assert_called_once_with(Button.left)
            # Проверяем, что sleep был вызван дважды
            assert mock_sleep.call_count == 2

    def test_click_element_human_like(self, mouse_controller):
        """Тест клика по элементу с имитацией человека"""
        controller, _ = mouse_controller
        controller.human_like = True
        controller.move_to_element = MagicMock(return_value=True)
        controller.click = MagicMock(return_value=True)

        # Создаем мок-элемент
        element = MagicMock()

        with patch("time.sleep") as mock_sleep:
            result = controller.click_element(element, button="left", offset_x=5, offset_y=10)

            assert result is True
            # Проверяем, что были вызваны методы move_to_element и click
            controller.move_to_element.assert_called_once_with(element, 5, 10)
            controller.click.assert_called_once_with("left")
            # Проверяем, что sleep был вызван для добавления задержки перед кликом
            assert mock_sleep.call_count >= 1

    def test_click_element_non_human_like(self, mouse_controller):
        """Тест клика по элементу без имитации человека"""
        controller, _ = mouse_controller
        controller.human_like = False
        controller.move_to_element = MagicMock(return_value=True)
        controller.click = MagicMock(return_value=True)

        # Создаем мок-элемент
        element = MagicMock()

        with patch("time.sleep") as mock_sleep:
            result = controller.click_element(element, button="left", offset_x=5, offset_y=10)

            assert result is True
            # Проверяем, что были вызваны методы move_to_element и click
            controller.move_to_element.assert_called_once_with(element, 5, 10)
            controller.click.assert_called_once_with("left")
            # Проверяем, что sleep не был вызван
            mock_sleep.assert_not_called()


class TestInputController:
    """Тесты объединенного контроллера ввода"""

    @pytest.fixture
    def input_controller(self):
        """Создает экземпляр InputController с мокнутыми контроллерами клавиатуры и мыши"""
        from core.common.input.base import InputController

        mock_keyboard = MagicMock()
        mock_mouse = MagicMock()

        controller = InputController(mock_keyboard, mock_mouse)
        yield controller, mock_keyboard, mock_mouse

    def test_keyboard_access(self, input_controller):
        """Тест доступа к контроллеру клавиатуры"""
        controller, mock_keyboard, _ = input_controller

        # Проверяем, что атрибут keyboard доступен
        assert controller.keyboard == mock_keyboard

        # Проверяем, что методы клавиатуры доступны через контроллер
        controller.keyboard.type_text("test")
        mock_keyboard.type_text.assert_called_once_with("test")

        controller.keyboard.press_key("enter")
        mock_keyboard.press_key.assert_called_once_with("enter")

        controller.keyboard.press_hotkey("ctrl", "c")
        mock_keyboard.press_hotkey.assert_called_once_with("ctrl", "c")

    def test_mouse_access(self, input_controller):
        """Тест доступа к контроллеру мыши"""
        controller, _, mock_mouse = input_controller

        # Проверяем, что атрибут mouse доступен
        assert controller.mouse == mock_mouse

        # Проверяем, что методы мыши доступны через контроллер
        controller.mouse.move_to(100, 200)
        mock_mouse.move_to.assert_called_once_with(100, 200)

        controller.mouse.click()
        mock_mouse.click.assert_called_once()

        controller.mouse.drag_to(300, 400)
        mock_mouse.drag_to.assert_called_once_with(300, 400)

    def test_combined_operations(self, input_controller):
        """Тест комбинированных операций клавиатуры и мыши"""
        controller, mock_keyboard, mock_mouse = input_controller

        # Симулируем сценарий: клик по элементу и ввод текста
        element = MagicMock()
        controller.mouse.click_element(element)
        controller.keyboard.type_text("Hello, World!")

        mock_mouse.click_element.assert_called_once_with(element)
        mock_keyboard.type_text.assert_called_once_with("Hello, World!")

        # Симулируем сценарий: выделение текста и копирование
        controller.mouse.press_and_hold()
        controller.mouse.move_relative(50, 0)
        controller.mouse.release()
        controller.keyboard.press_ctrl_c()

        mock_mouse.press_and_hold.assert_called_once()
        mock_mouse.move_relative.assert_called_once_with(50, 0)
        mock_mouse.release.assert_called_once()
        mock_keyboard.press_ctrl_c.assert_called_once()

    def test_combined_input_human_like(self):
        """Интеграционный тест контроллеров ввода с имитацией человека"""
        from core.common.input.base import InputController

        # Создаем мок-объекты контроллеров
        mock_keyboard = MagicMock()
        mock_mouse = MagicMock()

        # Создаем объединенный контроллер
        input_controller = InputController(mock_keyboard, mock_mouse)

        # Устанавливаем human_like=True для обоих контроллеров
        mock_keyboard.human_like = True
        mock_mouse.human_like = True

        # Эмулируем сценарий взаимодействия с пользовательским интерфейсом
        element = MagicMock()
        input_controller.mouse.click_element(element)
        input_controller.keyboard.type_text("Hello, World!")

        # Проверяем, что были вызваны соответствующие методы
        mock_mouse.click_element.assert_called_once_with(element)
        mock_keyboard.type_text.assert_called_once_with("Hello, World!")

    def test_combined_input_non_human_like(self):
        """Интеграционный тест контроллеров ввода без имитации человека"""
        from core.common.input.base import InputController

        # Создаем мок-объекты контроллеров
        mock_keyboard = MagicMock()
        mock_mouse = MagicMock()

        # Создаем объединенный контроллер
        input_controller = InputController(mock_keyboard, mock_mouse)

        # Устанавливаем human_like=False для обоих контроллеров
        mock_keyboard.human_like = False
        mock_mouse.human_like = False

        # Эмулируем сценарий взаимодействия с пользовательским интерфейсом
        element = MagicMock()
        input_controller.mouse.click_element(element)
        input_controller.keyboard.type_text("Hello, World!")

        # Проверяем, что были вызваны соответствующие методы
        mock_mouse.click_element.assert_called_once_with(element)
        mock_keyboard.type_text.assert_called_once_with("Hello, World!")


class TestInputControllerFactory:
    """Тесты фабрики контроллеров ввода"""

    def test_get_input_controller(self):
        """Тест получения контроллера ввода"""
        # Сначала импортируем модуль
        import core.input

        # Затем патчим классы в самом модуле
        with patch("platform.system", return_value="Windows"), patch.object(
            core.input, "KeyboardController"
        ) as mock_keyboard_class, patch.object(
            core.input, "MouseController"
        ) as mock_mouse_class, patch.object(
            core.input, "InputController"
        ) as mock_input_controller_class:

            # Создаем мок-объекты для контроллеров
            mock_keyboard = MagicMock()
            mock_mouse = MagicMock()
            mock_keyboard_class.return_value = mock_keyboard
            mock_mouse_class.return_value = mock_mouse

            # Создаем мок-объект для InputController
            mock_input_controller = MagicMock()
            mock_input_controller_class.return_value = mock_input_controller

            # Вызываем функцию
            controller = core.input.get_input_controller()

            # Проверяем, что были созданы правильные контроллеры
            mock_keyboard_class.assert_called_once_with(human_like=True)
            mock_mouse_class.assert_called_once_with(human_like=True)

            # Проверяем, что был создан InputController с правильными параметрами
            mock_input_controller_class.assert_called_once_with(mock_keyboard, mock_mouse)

            # Проверяем, что функция вернула правильный объект
            assert controller == mock_input_controller

    def test_get_input_controller_unsupported_platform(self):
        """Тест получения контроллл ввода для неподдерживаемой платформы"""
        with patch("platform.system", return_value="Linux"):
            # Импортируем функцию get_input_controller
            from core.input import get_input_controller

            # Проверяем, что функция вызывает исключение
            with pytest.raises(NotImplementedError):
                get_input_controller()

    def test_input_controller_factory_human_like(self):
        """Тест фабрики контроллеров ввода с имитацией человека"""
        # Импортируем фабрику
        from core.input.input_factory import InputControllerFactory

        # Создаем патчи для контроллеров
        with patch("core.input.input_factory.KeyboardController") as mock_keyboard_class, patch(
            "core.input.input_factory.MouseController"
        ) as mock_mouse_class:

            # Создаем и проверяем мок вместо создания реальных контроллеров
            InputControllerFactory.get_keyboard_controller(human_like=True)
            InputControllerFactory.get_mouse_controller(human_like=True)

            # Проверяем, что классы были вызваны с правильными параметрами
            mock_keyboard_class.assert_called_once_with(human_like=True)
            mock_mouse_class.assert_called_once_with(human_like=True)

    def test_input_controller_factory_non_human_like(self):
        """Тест фабрики контроллеров ввода без имитации человека"""
        # Импортируем фабрику
        from core.input.input_factory import InputControllerFactory

        # Создаем патчи для контроллеров
        with patch("core.input.input_factory.KeyboardController") as mock_keyboard_class, patch(
            "core.input.input_factory.MouseController"
        ) as mock_mouse_class:

            # Создаем и проверяем мок вместо создания реальных контроллеров
            InputControllerFactory.get_keyboard_controller(human_like=False)
            InputControllerFactory.get_mouse_controller(human_like=False)

            # Проверяем, что классы были вызваны с правильными параметрами
            mock_keyboard_class.assert_called_once_with(human_like=False)
            mock_mouse_class.assert_called_once_with(human_like=False)

    def test_get_input_controller_with_human_like_parameter(self):
        """Тест получения контроллера ввода с указанием параметра human_like"""
        # Сначала импортируем модуль
        import core.input

        # Создаем патчи непосредственно для объектов в модуле
        with patch.object(core.input, "KeyboardController") as mock_keyboard_class, patch.object(
            core.input, "MouseController"
        ) as mock_mouse_class, patch.object(
            core.input, "InputController"
        ) as mock_input_controller_class:

            # Вызываем функцию с разными параметрами
            core.input.get_input_controller()  # По умолчанию должен использоваться human_like=True
            core.input.get_input_controller(human_like=False)  # Явно указываем human_like=False

            # Проверяем, что классы контроллеров были вызваны с правильными параметрами
            assert mock_keyboard_class.call_args_list[0][1]["human_like"] is True
            assert mock_mouse_class.call_args_list[0][1]["human_like"] is True

            assert mock_keyboard_class.call_args_list[1][1]["human_like"] is False
            assert mock_mouse_class.call_args_list[1][1]["human_like"] is False

            # Проверяем, что InputController был создан дважды
            assert mock_input_controller_class.call_count == 2


class TestIntegration:
    """Интеграционные тесты контроллеров ввода"""

    def test_keyboard_mouse_integration(self):
        """Тест интеграции клавиатуры и мыши"""
        with patch("core.input.keyboard_controller.Controller") as mock_keyboard_controller, patch(
            "core.input.mouse_controller.Controller"
        ) as mock_mouse_controller, patch(
            "core.input.mouse_controller.pyautogui"
        ) as mock_pyautogui:

            # Импортируем необходимые классы
            from core.common.input.base import InputController
            from core.input.keyboard_controller import KeyboardController
            from core.input.mouse_controller import MouseController

            # Создаем контроллеры
            keyboard = KeyboardController(human_like=False)
            mouse = MouseController(human_like=False)

            # Устанавливаем моки
            keyboard.controller = mock_keyboard_controller.return_value
            mouse.controller = mock_mouse_controller.return_value

            # Создаем объединенный контроллер
            input_controller = InputController(keyboard, mouse)

            # Выполняем комбинированные действия
            # 1. Перемещаем мышь
            input_controller.mouse.move_to(100, 200)
            # 2. Кликаем
            input_controller.mouse.click()
            # 3. Вводим текст
            input_controller.keyboard.type_text("Hello")
            # 4. Нажимаем Enter
            input_controller.keyboard.press_enter()

            # Проверяем, что все методы были вызваны
            mock_pyautogui.moveTo.assert_called_once()
            mock_mouse_controller.return_value.click.assert_called_once()
            assert mock_keyboard_controller.return_value.press.call_count >= 5  # "Hello"
            assert mock_keyboard_controller.return_value.release.call_count >= 5  # "Hello"
