import os
import unittest
from unittest.mock import MagicMock, patch

import numpy as np


class TestScreenCapture(unittest.TestCase):
    def setUp(self):
        """Подготовка перед каждым тестом"""
        from core.vision.screen_capture import ScreenCapture

        self.screen_capture = ScreenCapture()

        # Создаем директорию для тестовых скриншотов
        self.test_dir = "test_screenshots"
        if not os.path.exists(self.test_dir):
            os.makedirs(self.test_dir)

    def tearDown(self):
        """Очистка после каждого теста"""
        # Удаляем тестовые скриншоты
        import shutil

        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)

    @patch("core.vision.screen_capture.pyautogui.screenshot")
    def test_capture_screen(self, mock_screenshot):
        """Тест захвата всего экрана"""
        # Создаем мок-объект для скриншота
        mock_img = MagicMock()
        mock_img.size = (1920, 1080)
        # Преобразуем в numpy массив для имитации изображения
        mock_array = np.zeros((1080, 1920, 3), dtype=np.uint8)
        # Исправляем лямбда-функцию, чтобы она принимала любые аргументы
        mock_img.__array__ = lambda *args, **kwargs: mock_array
        mock_screenshot.return_value = mock_img

        # Захватываем экран
        screenshot = self.screen_capture.capture_screen()

        # Проверяем результат
        self.assertIsNotNone(screenshot, "Скриншот не должен быть None")
        # Проверяем размеры только если скриншот не None
        if screenshot is not None:
            self.assertEqual(screenshot.shape[0], 1080)  # Высота
            self.assertEqual(screenshot.shape[1], 1920)  # Ширина
            self.assertEqual(screenshot.shape[2], 3)  # Каналы (RGB)

        # Проверяем, что pyautogui.screenshot был вызван
        mock_screenshot.assert_called_once()

    @patch("core.vision.screen_capture.pyautogui.screenshot")
    def test_capture_region(self, mock_screenshot):
        """Тест захвата области экрана"""
        # Создаем мок-объект для скриншота
        mock_img = MagicMock()
        mock_img.size = (500, 300)
        # Преобразуем в numpy массив для имитации изображения
        mock_array = np.zeros((300, 500, 3), dtype=np.uint8)
        # Исправляем лямбда-функцию, чтобы она принимала любые аргументы
        mock_img.__array__ = lambda *args, **kwargs: mock_array
        mock_screenshot.return_value = mock_img

        # Захватываем область экрана
        region = (100, 100, 500, 300)  # x, y, width, height

        # Вызываем метод capture_region
        screenshot = self.screen_capture.capture_region(region)

        # Проверяем результат
        self.assertIsNotNone(screenshot, "Скриншот не должен быть None")
        # Проверяем размеры только если скриншот не None
        if screenshot is not None:
            self.assertEqual(screenshot.shape[0], 300)  # Высота
            self.assertEqual(screenshot.shape[1], 500)  # Ширина
            self.assertEqual(screenshot.shape[2], 3)  # Каналы (RGB)

        # Проверяем, что pyautogui.screenshot был вызван с правильными параметрами
        mock_screenshot.assert_called_once_with(region=region)

    @patch("core.vision.screen_capture.pyautogui.screenshot")
    @patch("cv2.imwrite")
    def test_save_screenshot(self, mock_imwrite, mock_screenshot):
        """Тест сохранения скриншота в файл"""
        # Создаем мок-объект для скриншота
        mock_img = MagicMock()
        mock_img.size = (1920, 1080)
        # Преобразуем в numpy массив для имитации изображения
        mock_array = np.zeros((1080, 1920, 3), dtype=np.uint8)
        # Исправляем лямбда-функцию, чтобы она принимала любые аргументы
        mock_img.__array__ = lambda *args, **kwargs: mock_array
        mock_screenshot.return_value = mock_img

        # Настраиваем мок для imwrite
        mock_imwrite.return_value = True

        # Сохраняем скриншот
        filename = "test_screenshot.png"
        result = self.screen_capture.save_screenshot(filename)

        # Проверяем результат
        self.assertTrue(result)
        mock_screenshot.assert_called_once()
        mock_imwrite.assert_called_once()

    @patch("core.vision.screen_capture.pyautogui.size")
    def test_get_screen_size(self, mock_size):
        """Тест получения размеров экрана"""
        # Настраиваем мок для size
        mock_size.return_value = (1920, 1080)

        # Получаем размеры экрана
        width, height = self.screen_capture.get_screen_size()

        # Проверяем результат
        self.assertEqual(width, 1920)
        self.assertEqual(height, 1080)
        mock_size.assert_called_once()

    @patch("core.vision.screen_capture.pyautogui.screenshot")
    def test_capture_screen_error(self, mock_screenshot):
        """Тест обработки ошибки при захвате экрана"""
        # Настраиваем мок для имитации ошибки
        mock_screenshot.side_effect = Exception("Test error")

        # Захватываем экран с ошибкой
        screenshot = self.screen_capture.capture_screen()

        # Проверяем результат
        self.assertIsNone(screenshot)
        mock_screenshot.assert_called_once()
