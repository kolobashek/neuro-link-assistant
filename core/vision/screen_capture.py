import numpy as np
import pyautogui
import cv2
from PIL import Image
import io

class ScreenCapture:
    """
    Класс для захвата и обработки скриншотов экрана.
    """
    
    def capture_screen(self, region=None):
        """
        Захватывает скриншот всего экрана или указанной области.
        
        Args:
            region (tuple, optional): Область экрана (left, top, width, height)
            
        Returns:
            numpy.ndarray: Изображение в формате OpenCV (BGR)
        """
        try:
            # Захватываем скриншот с помощью pyautogui
            screenshot = pyautogui.screenshot(region=region)
            
            # Конвертируем в формат OpenCV (BGR)
            img = np.array(screenshot)
            img = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)
            
            return img
        except Exception as e:
            print(f"Error capturing screen: {e}")
            return None
    
    def save_screenshot(self, path, img=None, region=None):
        """
        Сохраняет скриншот в файл.
        
        Args:
            path (str): Путь для сохранения файла
            img (numpy.ndarray, optional): Изображение для сохранения
            region (tuple, optional): Область экрана (left, top, width, height)
            
        Returns:
            bool: True в случае успешного сохранения
        """
        try:
            # Если изображение не передано, захватываем новый скриншот
            if img is None:
                img = self.capture_screen(region)
            
            # Сохраняем изображение
            cv2.imwrite(path, img)
            
            return True
        except Exception as e:
            print(f"Error saving screenshot: {e}")
            return False
    
    def get_screen_size(self):
        """
        Получает размер экрана.
        
        Returns:
            tuple: (width, height) экрана
        """
        try:
            width, height = pyautogui.size()
            return (width, height)
        except Exception as e:
            print(f"Error getting screen size: {e}")
            return (0, 0)
    
    def compare_images(self, img1, img2, threshold=0.95):
        """
        Сравнивает два изображения.
        
        Args:
            img1 (numpy.ndarray): Первое изображение
            img2 (numpy.ndarray): Второе изображение
            threshold (float, optional): Порог схожести (0-1)
            
        Returns:
            float: Степень схожести (0-1)
        """
        try:
            # Проверяем, что изображения имеют одинаковый размер
            if img1.shape != img2.shape:
                # Изменяем размер второго изображения до размера первого
                img2 = cv2.resize(img2, (img1.shape[1], img1.shape[0]))
            
            # Конвертируем в grayscale для сравнения
            gray1 = cv2.cvtColor(img1, cv2.COLOR_BGR2GRAY)
            gray2 = cv2.cvtColor(img2, cv2.COLOR_BGR2GRAY)
            
            # Вычисляем SSIM (Structural Similarity Index)
            score, _ = cv2.compareSSIM(gray1, gray2)
            
            return score
        except Exception as e:
            print(f"Error comparing images: {e}")
            return 0.0
    
    def detect_changes(self, img1, img2, threshold=30):
        """
        Обнаруживает изменения между двумя изображениями.
        
        Args:
            img1 (numpy.ndarray): Первое изображение
            img2 (numpy.ndarray): Второе изображение
            threshold (int, optional): Порог изменений (0-255)
            
        Returns:
            tuple: (изображение с выделенными изменениями, процент изменений)
        """
        try:
            # Проверяем, что изображения имеют одинаковый размер
            if img1.shape != img2.shape:
                # Изменяем размер второго изображения до размера первого
                img2 = cv2.resize(img2, (img1.shape[1], img1.shape[0]))
            
            # Конвертируем в grayscale
            gray1 = cv2.cvtColor(img1, cv2.COLOR_BGR2GRAY)
            gray2 = cv2.cvtColor(img2, cv2.COLOR_BGR2GRAY)
            
            # Вычисляем абсолютную разницу
            diff = cv2.absdiff(gray1, gray2)
            
            # Применяем пороговую фильтрацию
            _, thresh = cv2.threshold(diff, threshold, 255, cv2.THRESH_BINARY)
            
            # Находим контуры изменений
            contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            
            # Создаем копию первого изображения для отображения изменений
            result = img1.copy()
            
            # Рисуем контуры изменений
            cv2.drawContours(result, contours, -1, (0, 0, 255), 2)
            
            # Вычисляем процент изменений
            change_percent = (np.count_nonzero(thresh) / thresh.size) * 100
            
            return (result, change_percent)
        except Exception as e:
            print(f"Error detecting changes: {e}")
            return (img1, 0.0)