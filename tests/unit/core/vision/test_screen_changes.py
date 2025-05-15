import unittest
from unittest.mock import patch

import numpy as np

from core.vision.screen_changes import ScreenChanges


class TestScreenChanges(unittest.TestCase):
    """Тесты для модуля обработки изменений на экране"""

    def setUp(self):
        """Настройка перед каждым тестом"""
        self.screen_changes = ScreenChanges()

    @patch("core.vision.screen_capture.ScreenCapture.capture_screen")
    @patch("core.vision.image_comparison.ImageComparison.compare_images")
    def test_detect_changes(self, mock_compare_images, mock_capture_screen):
        """Тест обнаружения изменений на экране"""
        # Создаем тестовые изображения
        img1 = np.zeros((100, 100, 3), dtype=np.uint8)
        img2 = np.ones((100, 100, 3), dtype=np.uint8) * 255

        # Настраиваем моки
        mock_capture_screen.side_effect = [img1, img2]
        mock_compare_images.return_value = 0.3  # Низкое сходство = большие изменения

        # Обнаруживаем изменения
        changes_detected = self.screen_changes.detect_changes(threshold=0.8)

        # Проверяем результат
        self.assertTrue(changes_detected)

        # Проверяем вызовы функций
        self.assertEqual(mock_capture_screen.call_count, 2)
        mock_compare_images.assert_called_once_with(img1, img2)

    @patch("core.vision.screen_capture.ScreenCapture.capture_screen")
    @patch("core.vision.image_comparison.ImageComparison.compare_images")
    def test_detect_no_changes(self, mock_compare_images, mock_capture_screen):
        """Тест обнаружения отсутствия изменений на экране"""
        # Создаем тестовые изображения
        img1 = np.zeros((100, 100, 3), dtype=np.uint8)
        img2 = np.zeros((100, 100, 3), dtype=np.uint8)

        # Настраиваем моки
        mock_capture_screen.side_effect = [img1, img2]
        mock_compare_images.return_value = 0.9  # Высокое сходство = мало изменений

        # Обнаруживаем изменения
        changes_detected = self.screen_changes.detect_changes(threshold=0.8)

        # Проверяем результат
        self.assertFalse(changes_detected)

        # Проверяем вызовы функций
        self.assertEqual(mock_capture_screen.call_count, 2)
        mock_compare_images.assert_called_once_with(img1, img2)

    @patch("core.vision.screen_capture.ScreenCapture.capture_region")
    @patch("core.vision.image_comparison.ImageComparison.compare_images")
    def test_detect_changes_in_region(self, mock_compare_images, mock_capture_region):
        """Тест обнаружения изменений в заданной области экрана"""
        # Создаем тестовые изображения
        img1 = np.zeros((100, 100, 3), dtype=np.uint8)
        img2 = np.ones((100, 100, 3), dtype=np.uint8) * 255

        # Настраиваем моки
        mock_capture_region.side_effect = [img1, img2]
        mock_compare_images.return_value = 0.3  # Низкое сходство = большие изменения

        # Определяем область
        region = (100, 200, 300, 400)  # x, y, width, height

        # Обнаруживаем изменения в области
        changes_detected = self.screen_changes.detect_changes_in_region(region, threshold=0.8)

        # Проверяем результат
        self.assertTrue(changes_detected)

        # Проверяем вызовы функций
        self.assertEqual(mock_capture_region.call_count, 2)
        self.assertEqual(mock_capture_region.call_args_list[0][0][0], region)
        self.assertEqual(mock_capture_region.call_args_list[1][0][0], region)
        mock_compare_images.assert_called_once_with(img1, img2)

    @patch("core.vision.screen_capture.ScreenCapture.capture_screen")
    @patch("core.vision.image_comparison.ImageComparison.compare_images")
    @patch("time.sleep")
    def test_wait_for_changes(self, mock_sleep, mock_compare_images, mock_capture_screen):
        """Тест ожидания изменений на экране"""
        # Создаем тестовые изображения
        img1 = np.zeros((100, 100, 3), dtype=np.uint8)
        img2 = np.ones((100, 100, 3), dtype=np.uint8) * 255

        # Настраиваем моки
        mock_capture_screen.side_effect = [img1, img1, img2]
        mock_compare_images.side_effect = [0.9, 0.3]  # Сначала нет изменений, потом есть

        # Ожидаем изменений
        changes_detected = self.screen_changes.wait_for_changes(timeout=5, threshold=0.8)

        # Проверяем результат
        self.assertTrue(changes_detected)

        # Проверяем вызовы функций
        self.assertEqual(mock_capture_screen.call_count, 3)
        self.assertEqual(mock_compare_images.call_count, 2)
        mock_sleep.assert_called_with(0.5)  # Проверяем, что была задержка между проверками


if __name__ == "__main__":
    unittest.main()
