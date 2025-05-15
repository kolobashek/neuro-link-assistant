import unittest
from unittest.mock import patch

import numpy as np

from core.vision.element_localization import ElementLocalization


class TestElementLocalization(unittest.TestCase):
    """Тесты для модуля локализации элементов на экране"""

    def setUp(self):
        """Настройка перед каждым тестом"""
        self.element_localization = ElementLocalization()

    @patch("core.vision.screen_capture.ScreenCapture.capture_screen")
    @patch("core.vision.element_recognition.ElementRecognition.find_template")
    def test_locate_element_by_template(self, mock_find_template, mock_capture_screen):
        """Тест локализации элемента по шаблону"""
        # Создаем тестовые изображения
        screen = np.zeros((1080, 1920, 3), dtype=np.uint8)
        template = np.zeros((100, 100, 3), dtype=np.uint8)

        # Настраиваем моки
        mock_capture_screen.return_value = screen
        mock_find_template.return_value = (500, 300, 100, 100, 0.95)

        # Локализуем элемент
        result = self.element_localization.locate_element_by_template(template)

        # Проверяем результат и прерываем тест, если он None
        if result is None:
            self.fail("Результат поиска шаблона не должен быть None")
            return

        # Только если result не None, продолжаем проверки
        self.assertIsNotNone(result)
        self.assertEqual(result[0], 500)  # x
        self.assertEqual(result[1], 300)  # y
        self.assertEqual(result[2], 100)  # width
        self.assertEqual(result[3], 100)  # height
        self.assertAlmostEqual(result[4], 0.95)  # confidence

        # Проверяем вызовы функций
        mock_capture_screen.assert_called_once()
        mock_find_template.assert_called_once_with(screen, template, threshold=0.8)

    @patch("core.vision.screen_capture.ScreenCapture.capture_screen")
    @patch("core.vision.element_recognition.ElementRecognition.find_template")
    def test_locate_element_by_template_not_found(self, mock_find_template, mock_capture_screen):
        """Тест локализации элемента, который не найден на экране"""
        # Создаем тестовые изображения
        screen = np.zeros((1080, 1920, 3), dtype=np.uint8)
        template = np.zeros((100, 100, 3), dtype=np.uint8)

        # Настраиваем моки для имитации отсутствия элемента
        mock_capture_screen.return_value = screen
        mock_find_template.return_value = None

        # Локализуем элемент
        result = self.element_localization.locate_element_by_template(template)

        # Проверяем результат
        self.assertIsNone(result)

        # Проверяем вызовы функций
        mock_capture_screen.assert_called_once()
        mock_find_template.assert_called_once_with(screen, template, threshold=0.8)

    @patch("core.vision.screen_capture.ScreenCapture.capture_region")
    @patch("core.vision.element_recognition.ElementRecognition.find_template")
    def test_locate_element_in_region(self, mock_find_template, mock_capture_region):
        """Тест локализации элемента в заданной области экрана"""
        # Создаем тестовые изображения
        region_img = np.zeros((400, 600, 3), dtype=np.uint8)
        template = np.zeros((100, 100, 3), dtype=np.uint8)

        # Настраиваем моки
        mock_capture_region.return_value = region_img
        mock_find_template.return_value = (200, 150, 100, 100, 0.95)

        # Определяем область поиска
        region = (100, 200, 600, 400)  # x, y, width, height

        # Локализуем элемент в области
        result = self.element_localization.locate_element_in_region(template, region)

        # Проверяем результат и прерываем тест, если он None
        if result is None:
            self.fail("Результат поиска шаблона не должен быть None")
            return

        # Только если result не None, продолжаем проверки
        self.assertIsNotNone(result)
        # Координаты должны быть относительно всего экрана, а не только области
        self.assertEqual(result[0], 100 + 200)  # x_region + x_element
        self.assertEqual(result[1], 200 + 150)  # y_region + y_element
        self.assertEqual(result[2], 100)  # width
        self.assertEqual(result[3], 100)  # height
        self.assertAlmostEqual(result[4], 0.95)  # confidence

        # Проверяем вызовы функций
        mock_capture_region.assert_called_once_with(region)
        mock_find_template.assert_called_once_with(region_img, template, threshold=0.8)


if __name__ == "__main__":
    unittest.main()
