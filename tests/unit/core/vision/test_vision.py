import pytest
import os
import cv2
import numpy as np
import time
from unittest.mock import patch, MagicMock

class TestScreenCapture:
    """Тесты захвата скриншотов"""
    
    def setup_method(self):
        """Подготовка перед каждым тестом"""
        from core.vision.screen_capture import ScreenCapture
        self.screen_capture = ScreenCapture()
        
        # Создаем директорию для тестовых скриншотов
        self.test_dir = "test_screenshots"
        if not os.path.exists(self.test_dir):
            os.makedirs(self.test_dir)
    
    def teardown_method(self):
        """Очистка после каждого теста"""
        # Удаляем тестовые скриншоты
        import shutil
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)
    
    def test_capture_screen(self):
        """Тест захвата скриншота"""
        screenshot = self.screen_capture.capture_screen()
        
        assert screenshot is not None
        assert isinstance(screenshot, np.ndarray)
        assert screenshot.shape[2] == 3  # Проверяем, что изображение цветное (BGR)
    
    def test_capture_region(self):
        """Тест захвата области экрана"""
        # Захватываем область 100x100 пикселей в левом верхнем углу
        region = (0, 0, 100, 100)
        screenshot = self.screen_capture.capture_screen(region)
        
        assert screenshot is not None
        assert isinstance(screenshot, np.ndarray)
        assert screenshot.shape[0] == 100  # Высота
        assert screenshot.shape[1] == 100  # Ширина
    
    def test_save_screenshot(self):
        """Тест сохранения скриншота"""
        screenshot_path = os.path.join(self.test_dir, "test_screenshot.png")
        
        result = self.screen_capture.save_screenshot(screenshot_path)
        
        assert result is True
        assert os.path.exists(screenshot_path)
    
    def test_get_screen_size(self):
        """Тест получения размера экрана"""
        size = self.screen_capture.get_screen_size()
        
        assert size is not None
        assert len(size) == 2
        assert size[0] > 0  # Ширина
        assert size[1] > 0  # Высота


class TestElementRecognition:
    """Тесты распознавания элементов интерфейса"""
    
    def setup_method(self):
        """Подготовка перед каждым тестом"""
        from core.vision.element_recognition import ElementRecognition
        self.element_recognition = ElementRecognition()
        
        # Создаем директорию для тестовых изображений
        self.test_dir = "test_images"
        if not os.path.exists(self.test_dir):
            os.makedirs(self.test_dir)
        
        # Создаем тестовое изображение с простой фигурой
        self.test_image_path = os.path.join(self.test_dir, "test_image.png")
        self.create_test_image()
        
        # Создаем шаблон для поиска
        self.template_path = os.path.join(self.test_dir, "template.png")
        self.create_template()
    
    def teardown_method(self):
        """Очистка после каждого теста"""
        # Удаляем тестовые изображения
        import shutil
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)
    
    def create_test_image(self):
        """Создает тестовое изображение с простой фигурой"""
        # Создаем пустое изображение
        img = np.zeros((300, 500, 3), dtype=np.uint8)
        
        # Рисуем прямоугольник
        cv2.rectangle(img, (100, 100), (200, 200), (0, 0, 255), -1)
        
        # Рисуем круг
        cv2.circle(img, (350, 150), 50, (0, 255, 0), -1)
        
        # Сохраняем изображение
        cv2.imwrite(self.test_image_path, img)
    
    def create_template(self):
        """Создает шаблон для поиска"""
        # Создаем шаблон (часть тестового изображения с прямоугольником)
        img = np.zeros((300, 500, 3), dtype=np.uint8)
        cv2.rectangle(img, (100, 100), (200, 200), (0, 0, 255), -1)
        
        # Вырезаем область с прямоугольником
        template = img[90:210, 90:210]
        
        # Сохраняем шаблон
        cv2.imwrite(self.template_path, template)
    
    def test_find_template(self):
        """Тест поиска шаблона на изображении"""
        # Создаем тестовые изображения вместо загрузки из файла
        screen = np.zeros((200, 200, 3), dtype=np.uint8)
        template = np.zeros((50, 50, 3), dtype=np.uint8)
        
        # Добавляем патч для имитации успешного поиска
        with patch('cv2.matchTemplate') as mock_match_template:
            with patch('cv2.minMaxLoc') as mock_min_max_loc:
                # Настраиваем моки
                mock_match_template.return_value = np.zeros((150, 150), dtype=np.float32)
                mock_min_max_loc.return_value = (0, 0.95, (0, 0), (100, 100))
                
                # Ищем шаблон
                result = self.element_recognition.find_template(screen, template, threshold=0.8)
                
                # Проверяем результат
                assert result is not None
                assert result[0] == 100  # x
                assert result[1] == 100  # y
                assert result[2] == 50   # width
                assert result[3] == 50   # height
                assert result[4] == 0.95 # confidence
    
    def test_get_element_center(self):
        """Тест получения центра элемента"""
        rect = (100, 100, 100, 100)
        
        center = self.element_recognition.get_element_center(rect)
        
        assert center is not None
        assert center == (150, 150)
    
    def test_highlight_element(self):
        """Тест выделения элемента на изображении"""
        # Загружаем тестовое изображение
        img = cv2.imread(self.test_image_path)
        
        # Определяем прямоугольник для выделения
        rect = (100, 100, 100, 100)
        
        # Выделяем элемент
        result = self.element_recognition.highlight_element(img, rect)
        
        assert result is not None
        assert isinstance(result, np.ndarray)
        
        # Проверяем, что размеры изображения не изменились
        assert result.shape == img.shape