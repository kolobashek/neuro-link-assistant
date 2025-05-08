import numpy as np
import cv2
import pytesseract
from core.vision.screen_capture import ScreenCapture
from core.common.error_handler import handle_error

class ElementRecognition:
    """
    Класс для распознавания элементов интерфейса.
    """
    
    def __init__(self, screen_capture=None):
        """
        Инициализация распознавателя элементов.
        
        Args:
            screen_capture (ScreenCapture, optional): Экземпляр класса для захвата экрана
        """
        self.screen_capture = screen_capture or ScreenCapture()
        
        # Настройка Tesseract OCR
        try:
            # Путь к исполняемому файлу Tesseract (если не в PATH)
            # pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
            pass
        except Exception as e:
            handle_error(f"Ошибка при настройке Tesseract OCR: {e}", e, module='vision')
    
    def find_template(self, screenshot, template, threshold=0.8):
        """
        Ищет шаблон на изображении
        
        Args:
            screenshot (numpy.ndarray или str): Изображение, на котором ищем
            template (numpy.ndarray или str): Шаблон или путь к файлу шаблона
            threshold (float): Порог уверенности (0-1)
        
        Returns:
            tuple: Координаты найденного шаблона (x, y, width, height, confidence) или None
        """
        try:
            # Если screenshot - это путь к файлу, загружаем его
            if isinstance(screenshot, str):
                screenshot_img = cv2.imread(screenshot)
                if screenshot_img is None:
                    handle_error(f"Не удалось загрузить изображение из файла: {screenshot}", module='vision')
                    return None
            else:
                # Иначе используем переданный numpy массив
                screenshot_img = screenshot
            
            # Если template - это путь к файлу, загружаем его
            if isinstance(template, str):
                template_img = cv2.imread(template)
                if template_img is None:
                    handle_error(f"Не удалось загрузить шаблон из файла: {template}", module='vision')
                    return None
            else:
                # Иначе используем переданный numpy массив
                template_img = template
            
            # Получаем размеры шаблона
            h, w = template_img.shape[:2]
            
            # Ищем шаблон на изображении
            result = cv2.matchTemplate(screenshot_img, template_img, cv2.TM_CCOEFF_NORMED)
            
            # Находим позицию с максимальным значением
            min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)
            
            # Если максимальное значение больше порога, считаем, что шаблон найден
            if max_val >= threshold:
                x, y = max_loc
                return (x, y, w, h, max_val)
            
            return None
        except Exception as e:
            handle_error(f"Ошибка при поиске шаблона: {e}", e, module='vision')
            return None
    
    def find_all_templates(self, screenshot, template, threshold=0.8, max_results=10):
        """
        Ищет все вхождения шаблона на скриншоте.
        
        Args:
            screenshot (numpy.ndarray): Скриншот, на котором ищем
            template (numpy.ndarray): Шаблон, который ищем
            threshold (float, optional): Порог уверенности (0-1)
            max_results (int, optional): Максимальное количество результатов
            
        Returns:
            list: Список координат найденных элементов [(x, y, width, height, confidence), ...]
        """
        try:
            # Проверяем, что скриншот и шаблон не пустые
            if screenshot is None or template is None:
                return []
            
            # Получаем размеры шаблона
            h, w = template.shape[:2]
            
            # Ищем шаблон на скриншоте
            result = cv2.matchTemplate(screenshot, template, cv2.TM_CCOEFF_NORMED)
            
            # Находим все позиции, где значение выше порога
            locations = np.where(result >= threshold)
            
            # Формируем список координат
            matches = []
            for pt in zip(*locations[::-1]):  # Переворачиваем, т.к. numpy возвращает (y, x)
                x, y = pt
                confidence = result[y, x]
                matches.append((x, y, w, h, confidence))
            
            # Сортируем по уверенности (от большей к меньшей)
            matches.sort(key=lambda x: x[4], reverse=True)
            
            # Ограничиваем количество результатов
            return matches[:max_results]
        except Exception as e:
            handle_error(f"Ошибка при поиске всех шаблонов: {e}", e, module='vision')
            return []
    
    def find_text(self, screenshot, lang='eng'):
        """
        Распознает текст на скриншоте.
        
        Args:
            screenshot (numpy.ndarray): Скриншот, на котором ищем текст
            lang (str, optional): Язык текста
            
        Returns:
            str: Распознанный текст
        """
        try:
            # Проверяем, что скриншот не пустой
            if screenshot is None:
                return ""
            
            # Конвертируем в grayscale
            gray = cv2.cvtColor(screenshot, cv2.COLOR_BGR2GRAY)
            
            # Распознаем текст
            text = pytesseract.image_to_string(gray, lang=lang)
            
            return text
        except Exception as e:
            handle_error(f"Ошибка при распознавании текста: {e}", e, module='vision')
            return ""
    
    def find_color(self, screenshot, color, tolerance=10):
        """
        Ищет заданный цвет на скриншоте.
        
        Args:
            screenshot (numpy.ndarray): Скриншот, на котором ищем
            color (tuple): Цвет в формате BGR (B, G, R)
            tolerance (int, optional): Допустимое отклонение
            
        Returns:
            list: Список координат найденных пикселей [(x, y), ...]
        """
        try:
            # Проверяем, что скриншот не пустой
            if screenshot is None:
                return []
            
            # Создаем маску для заданного цвета с учетом допуска
            lower = np.array([max(0, c - tolerance) for c in color])
            upper = np.array([min(255, c + tolerance) for c in color])
            mask = cv2.inRange(screenshot, lower, upper)
            
            # Находим координаты пикселей, соответствующих маске
            coordinates = np.column_stack(np.where(mask.T > 0))
            
            # Преобразуем в список кортежей (x, y)
            return [(x, y) for x, y in coordinates]
        except Exception as e:
            handle_error(f"Ошибка при поиске цвета: {e}", e, module='vision')
            return []
    
    def get_element_center(self, element):
        """
        Получает координаты центра элемента.
        
        Args:
            element (tuple): Координаты элемента (x, y, width, height)
            
        Returns:
            tuple: Координаты центра элемента (x, y)
        """
        try:
            x, y, w, h = element[:4]
            center_x = x + w // 2
            center_y = y + h // 2
            return (center_x, center_y)
        except Exception as e:
            handle_error(f"Ошибка при получении центра элемента: {e}", e, module='vision')
            return (0, 0)
    
    def highlight_element(self, screenshot, element, color=(0, 255, 0), thickness=2):
        """
        Выделяет элемент на скриншоте.
        
        Args:
            screenshot (numpy.ndarray): Скриншот
            element (tuple): Координаты элемента (x, y, width, height)
            color (tuple, optional): Цвет рамки (B, G, R)
            thickness (int, optional): Толщина рамки
            
        Returns:
            numpy.ndarray: Скриншот с выделенным элементом
        """
        try:
            # Проверяем, что скриншот не пустой
            if screenshot is None:
                return None
            
            # Создаем копию скриншота
            result = screenshot.copy()
            
            # Получаем координаты элемента
            x, y, w, h = element[:4]
            
            # Рисуем прямоугольник
            cv2.rectangle(result, (x, y), (x + w, y + h), color, thickness)
            
            return result
        except Exception as e:
            handle_error(f"Ошибка при выделении элемента: {e}", e, module='vision')
            return screenshot