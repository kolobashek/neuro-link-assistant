import cv2
import numpy as np
import pyautogui

from core.common.error_handler import handle_error


class ScreenCapture:
    """
    Класс для захвата и обработки скриншотов экрана.
    """

    def capture_screen(self, region=None):
        """
        Захватывает весь экран или указанную область

        Args:
            region (tuple, optional): Координаты области (x, y, width, height)

        Returns:
            numpy.ndarray: Изображение экрана или None в случае ошибки
        """
        try:
            if region:
                return self.capture_region(region)

            # Захватываем экран
            screenshot = pyautogui.screenshot()

            # Преобразуем в numpy массив
            # Для тестов, обрабатываем случай, когда screenshot - это MagicMock

            if hasattr(screenshot, "__array__") and callable(getattr(screenshot, "__array__")):
                try:

                    img = np.asarray(
                        screenshot
                    )  # Используем np.asarray вместо прямого вызова __array__
                except TypeError:

                    # Если возникает ошибка, используем стандартный способ
                    img = np.array(screenshot)
            else:
                img = np.array(screenshot)

            return img
        except Exception as e:
            handle_error(f"Ошибка при захвате экрана: {e}", e, module="vision")
            return None

    def capture_region(self, region):
        """
        Захватывает указанную область экрана

        Args:
            region (tuple): Координаты области (x, y, width, height)

        Returns:
            numpy.ndarray: Изображение области экрана или None в случае ошибки
        """
        try:
            # Захватываем указанную область экрана
            screenshot = pyautogui.screenshot(region=region)

            # Преобразуем в numpy массив
            img = np.array(screenshot)

            return img
        except Exception as e:
            handle_error(f"Ошибка при захвате области экрана: {e}", e, module="vision")
            return None

    def save_screenshot(self, filename, region=None):
        """
        Сохраняет скриншот в файл

        Args:
            filename (str): Путь к файлу для сохранения
            region (tuple, optional): Координаты области (x, y, width, height)

        Returns:
            bool: True, если скриншот успешно сохранен
        """
        try:
            # Захватываем экран или область
            if region:
                img = self.capture_region(region)
            else:
                img = self.capture_screen()

            if img is None:
                return False

            # Сохраняем изображение
            cv2.imwrite(filename, img)

            return True
        except Exception as e:
            handle_error(f"Ошибка при сохранении скриншота: {e}", e, module="vision")
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
            handle_error(f"Ошибка при получении размера экрана: {e}", e, module="vision")
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

            # Вычисляем MSE (Mean Squared Error) и преобразуем в показатель сходства
            mse = np.mean((gray1.astype(float) - gray2.astype(float)) ** 2)
            if mse == 0:
                score = 1.0
            else:
                # Преобразуем MSE в показатель сходства (1 - идентичные изображения)
                max_mse = 255.0**2
                score = 1.0 - (mse / max_mse)

            return score
        except Exception as e:
            handle_error(f"Ошибка при сравнении изображений: {e}", e, module="vision")
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
            handle_error(f"Ошибка при обнаружении изменений: {e}", e, module="vision")
            return (img1, 0.0)
