import unittest
from unittest.mock import patch, MagicMock
import numpy as np
import cv2
from core.vision.element_recognition import ElementRecognition

class TestElementRecognition(unittest.TestCase):
    """Тесты для модуля распознавания элементов интерфейса"""
    
    def setUp(self):
        """Настройка перед каждым тестом"""
        self.element_recognition = ElementRecognition()
    
    @patch('cv2.matchTemplate')
    @patch('cv2.minMaxLoc')
    def test_find_template(self, mock_min_max_loc, mock_match_template):
        """Тест поиска шаблона на изображении"""
        # Создаем тестовые изображения
        screen = np.zeros((1080, 1920, 3), dtype=np.uint8)
        template = np.zeros((100, 100, 3), dtype=np.uint8)
        
        # Настраиваем моки
        mock_match_template.return_value = np.zeros((980, 1820), dtype=np.float32)
        mock_min_max_loc.return_value = (0, 0.95, (0, 0), (500, 300))
        
        # Ищем шаблон
        result = self.element_recognition.find_template(screen, template, threshold=0.8)
        
        # Проверяем результат
        self.assertIsNotNone(result)
        self.assertEqual(result[0], 500)  # x
        self.assertEqual(result[1], 300)  # y
        self.assertEqual(result[2], 100)  # width
        self.assertEqual(result[3], 100)  # height
        self.assertAlmostEqual(result[4], 0.95)  # confidence
        
        # Проверяем вызовы функций
        mock_match_template.assert_called_once()
        mock_min_max_loc.assert_called_once()
    
    @patch('cv2.matchTemplate')
    @patch('cv2.minMaxLoc')
    def test_find_template_not_found(self, mock_min_max_loc, mock_match_template):
        """Тест поиска шаблона, который не найден на изображении"""
        # Создаем тестовые изображения
        screen = np.zeros((1080, 1920, 3), dtype=np.uint8)
        template = np.zeros((100, 100, 3), dtype=np.uint8)
        
        # Настраиваем моки для имитации низкой уверенности
        mock_match_template.return_value = np.zeros((980, 1820), dtype=np.float32)
        mock_min_max_loc.return_value = (0, 0.7, (0, 0), (500, 300))
        
        # Ищем шаблон с порогом 0.8
        result = self.element_recognition.find_template(screen, template, threshold=0.8)
        
        # Проверяем результат
        self.assertIsNone(result)
        
        # Проверяем вызовы функций
        mock_match_template.assert_called_once()
        mock_min_max_loc.assert_called_once()
    
    def test_get_element_center(self):
        """Тест получения центра элемента"""
        # Координаты элемента (x, y, width, height)
        element = (100, 200, 300, 400)
        
        # Получаем центр элемента
        center_x, center_y = self.element_recognition.get_element_center(element)
        
        # Проверяем результат
        self.assertEqual(center_x, 250)  # 100 + 300/2
        self.assertEqual(center_y, 400)  # 200 + 400/2
    
    @patch('cv2.rectangle')
    def test_highlight_element(self, mock_rectangle):
        """Тест выделения элемента на изображении"""
        # Создаем тестовое изображение
        image = np.zeros((1080, 1920, 3), dtype=np.uint8)
        
        # Координаты элемента (x, y, width, height)
        element = (100, 200, 300, 400)
        
        # Выделяем элемент
        result = self.element_recognition.highlight_element(image.copy(), element)
        
        # Проверяем результат
        self.assertIsNotNone(result)
        
        # Проверяем вызов функции rectangle
        mock_rectangle.assert_called_once()
        args, kwargs = mock_rectangle.call_args
        self.assertEqual(args[1], (100, 200))  # Верхний левый угол
        self.assertEqual(args[2], (100+300, 200+400))  # Нижний правый угол

if __name__ == '__main__':
    unittest.main()