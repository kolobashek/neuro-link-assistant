import cv2
import numpy as np
import pyautogui
from .screen_capture import ScreenCapture

class ElementRecognition:
    """
    Класс для распознавания элементов интерфейса на экране.
    """
    
    def __init__(self):
        """Инициализация класса распознавания элементов."""
        self.screen_capture = ScreenCapture()
    
    def find_template(self, template, screenshot=None, threshold=0.8, region=None):
        """
        Находит шаблон на скриншоте.
        
        Args:
            template (str or numpy.ndarray): Путь к файлу шаблона или изображение шаблона
            screenshot (numpy.ndarray, optional): Скриншот для поиска
            threshold (float, optional): Порог соответствия (0-1)
            region (tuple, optional): Область поиска (left, top, width, height)
            
        Returns:
            tuple: (x, y, width, height) найденного элемента или None
        """
        try:
            # Загружаем шаблон, если передан путь к файлу
            if isinstance(template, str):
                template_img = cv2.imread(template)
            else:
                template_img = template
            
            # Если скриншот не передан, делаем новый
            if screenshot is None:
                screenshot = self.screen_capture.capture_screen(region)
            
            # Получаем размеры шаблона
            h, w = template_img.shape[:2]
            
            # Выполняем шаблонное сопоставление
            result = cv2.matchTemplate(screenshot, template_img, cv2.TM_CCOEFF_NORMED)
            
            # Находим позиции, где соответствие превышает порог
            locations = np.where(result >= threshold)
            
            # Если найдены соответствия
            if len(locations[0]) > 0:
                # Берем первое (наилучшее) соответствие
                min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)
                top_left = max_loc
                
                # Если был указан регион, корректируем координаты
                if region:
                    top_left = (top_left[0] + region[0], top_left[1] + region[1])
                
                return (top_left[0], top_left[1], w, h)
            
            return None
        except Exception as e:
            print(f"Error finding template: {e}")
            return None
    
    def find_all_templates(self, template, screenshot=None, threshold=0.8, region=None):
        """
        Находит все вхождения шаблона на скриншоте.
        
        Args:
            template (str or numpy.ndarray): Путь к файлу шаблона или изображение шаблона
            screenshot (numpy.ndarray, optional): Скриншот для поиска
            threshold (float, optional): Порог соответствия (0-1)
            region (tuple, optional): Область поиска (left, top, width, height)
            
        Returns:
            list: Список кортежей (x, y, width, height) найденных элементов
        """
        try:
            # Загружаем шаблон, если передан путь к файлу
            if isinstance(template, str):
                template_img = cv2.imread(template)
            else:
                template_img = template
            
            # Если скриншот не передан, делаем новый
            if screenshot is None:
                screenshot = self.screen_capture.capture_screen(region)
            
            # Получаем размеры шаблона
            h, w = template_img.shape[:2]
            
            # Выполняем шаблонное сопоставление
            result = cv2.matchTemplate(screenshot, template_img, cv2.TM_CCOEFF_NORMED)
            
            # Находим позиции, где соответствие превышает порог
            locations = np.where(result >= threshold)
            
            # Преобразуем в список координат
            points = list(zip(*locations[::-1]))
            
            # Группируем близкие точки
            rect_list = []
            for point in points:
                # Если был указан регион, корректируем координаты
                if region:
                    point = (point[0] + region[0], point[1] + region[1])
                
                # Проверяем, не перекрывается ли с уже найденными
                overlap = False
                for rect in rect_list:
                    if (abs(rect[0] - point[0]) < w // 2 and 
                        abs(rect[1] - point[1]) < h // 2):
                        overlap = True
                        break
                
                if not overlap:
                    rect_list.append((point[0], point[1], w, h))
            
            return rect_list
        except Exception as e:
            print(f"Error finding all templates: {e}")
            return []
    
    def find_text(self, text, screenshot=None, region=None):
        """
        Находит текст на скриншоте с помощью OCR.
        
        Args:
            text (str): Текст для поиска
            screenshot (numpy.ndarray, optional): Скриншот для поиска
            region (tuple, optional): Область поиска (left, top, width, height)
            
        Returns:
            list: Список кортежей (x, y, width, height) найденных текстовых блоков
        """
        try:
            # Для этой функции требуется pytesseract
            import pytesseract
            pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
            
            # Если скриншот не передан, делаем новый
            if screenshot is None:
                screenshot = self.screen_capture.capture_screen(region)
            
            # Конвертируем в grayscale для лучшего распознавания
            gray = cv2.cvtColor(screenshot, cv2.COLOR_BGR2GRAY)
            
            # Применяем пороговую фильтрацию для улучшения контраста
            _, thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
            
            # Распознаем текст
            data = pytesseract.image_to_data(thresh, output_type=pytesseract.Output.DICT)
            
            # Ищем вхождения искомого текста
            results = []
            for i in range(len(data['text'])):
                if text.lower() in data['text'][i].lower():
                    x = data['left'][i]
                    y = data['top'][i]
                    w = data['width'][i]
                    h = data['height'][i]
                    
                    # Если был указан регион, корректируем координаты
                    if region:
                        x += region[0]
                        y += region[1]
                    
                    results.append((x, y, w, h))
            
            return results
        except ImportError:
            print("pytesseract is not installed. Please install it using: pip install pytesseract")
            return []
        except Exception as e:
            print(f"Error finding text: {e}")
            return []
    
    def find_color(self, color, screenshot=None, threshold=10, region=None):
        """
        Находит области указанного цвета на скриншоте.
        
        Args:
            color (tuple): Цвет в формате BGR (B, G, R)
            screenshot (numpy.ndarray, optional): Скриншот для поиска
            threshold (int, optional): Допустимое отклонение цвета
            region (tuple, optional): Область поиска (left, top, width, height)
            
        Returns:
            list: Список кортежей (x, y, width, height) найденных областей
        """
        try:
            # Если скриншот не передан, делаем новый
            if screenshot is None:
                screenshot = self.screen_capture.capture_screen(region)
            
            # Создаем нижнюю и верхнюю границы цвета
            lower_bound = np.array([max(0, c - threshold) for c in color], dtype=np.uint8)
            upper_bound = np.array([min(255, c + threshold) for c in color], dtype=np.uint8)
            
            # Создаем маску для выделения областей указанного цвета
            mask = cv2.inRange(screenshot, lower_bound, upper_bound)
            
            # Находим контуры областей
            contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            
            # Преобразуем контуры в прямоугольники
            rects = []
            for contour in contours:
                x, y, w, h = cv2.boundingRect(contour)
                
                # Если был указан регион, корректируем координаты
                if region:
                    x += region[0]
                    y += region[1]
                
                rects.append((x, y, w, h))
            
            return rects
        except Exception as e:
            print(f"Error finding color: {e}")
            return []
    
    def get_element_center(self, rect):
        """
        Получает координаты центра элемента.
        
        Args:
            rect (tuple): Прямоугольник элемента (x, y, width, height)
            
        Returns:
            tuple: (x, y) координаты центра
        """
        if rect is None:
            return None
        
        x, y, w, h = rect
        return (x + w // 2, y + h // 2)
    
    def highlight_element(self, screenshot, rect, color=(0, 255, 0), thickness=2):
        """
        Выделяет элемент на скриншоте.
        
        Args:
            screenshot (numpy.ndarray): Скриншот
            rect (tuple): Прямоугольник элемента (x, y, width, height)
            color (tuple, optional): Цвет рамки в формате BGR
            thickness (int, optional): Толщина рамки
            
        Returns:
            numpy.ndarray: Скриншот с выделенным элементом
        """
        if rect is None or screenshot is None:
            return screenshot
        
        result = screenshot.copy()
        x, y, w, h = rect
        cv2.rectangle(result, (x, y), (x + w, y + h), color, thickness)
        
        return result