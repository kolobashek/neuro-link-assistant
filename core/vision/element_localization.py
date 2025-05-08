import numpy as np
import cv2
from core.vision.screen_capture import ScreenCapture
from core.vision.element_recognition import ElementRecognition
from core.common.error_handler import handle_error

class ElementLocalization:
    """Класс для локализации элементов на экране"""
    
    def __init__(self):
        """Инициализация"""
        self.screen_capture = ScreenCapture()
        self.element_recognition = ElementRecognition()
    
    def locate_element_by_template(self, template, threshold=0.8):
        """
        Локализует элемент на экране по шаблону
        
        Args:
            template (numpy.ndarray): Шаблон элемента
            threshold (float): Порог уверенности (0-1)
        
        Returns:
            tuple: Координаты найденного элемента (x, y, width, height, confidence) или None
        """
        try:
            # Захватываем экран
            screen = self.screen_capture.capture_screen()
            
            # Ищем шаблон на экране
            return self.element_recognition.find_template(screen, template, threshold=threshold)
        except Exception as e:
            handle_error(f"Ошибка при локализации элемента: {e}", e, module='vision')
            return None
    
    def locate_element_in_region(self, template, region, threshold=0.8):
        """
        Локализует элемент в указанной области экрана
        
        Args:
            template (numpy.ndarray): Шаблон элемента
            region (tuple): Координаты области (x, y, width, height)
            threshold (float): Порог уверенности (0-1)
        
        Returns:
            tuple: Координаты найденного элемента (x, y, width, height, confidence) или None
        """
        try:
            # Захватываем область экрана
            region_img = self.screen_capture.capture_region(region)
            
            # Ищем шаблон в области
            result = self.element_recognition.find_template(region_img, template, threshold=threshold)
            
            # Если элемент найден, корректируем координаты относительно всего экрана
            if result:
                x, y, w, h, conf = result
                return (region[0] + x, region[1] + y, w, h, conf)
            
            return None
        except Exception as e:
            handle_error(f"Ошибка при локализации элемента в области: {e}", e, module='vision')
            return None