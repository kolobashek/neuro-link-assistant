import time

from core.common.error_handler import handle_error
from core.vision.image_comparison import ImageComparison
from core.vision.screen_capture import ScreenCapture


class ScreenChanges:
    """Класс для обработки изменений на экране"""

    def __init__(self):
        """Инициализация"""
        self.screen_capture = ScreenCapture()
        self.image_comparison = ImageComparison()

    def detect_changes(self, delay=0.5, threshold=0.95):
        """
        Обнаруживает изменения на экране

        Args:
            delay (float): Задержка между снимками в секундах
            threshold (float): Порог сходства (0-1), ниже которого считается, что есть изменения

        Returns:
            bool: True, если обнаружены изменения, иначе False
        """
        try:
            # Захватываем первый снимок экрана
            img1 = self.screen_capture.capture_screen()

            # Ждем указанное время
            time.sleep(delay)

            # Захватываем второй снимок экрана
            img2 = self.screen_capture.capture_screen()

            # Сравниваем изображения
            similarity = self.image_comparison.compare_images(img1, img2)

            # Если сходство ниже порога, значит есть изменения
            return similarity < threshold
        except Exception as e:
            handle_error(f"Ошибка при обнаружении изменений: {e}", e, module="vision")
            return False

    def detect_changes_in_region(self, region, delay=0.5, threshold=0.95):
        """
        Обнаруживает изменения в указанной области экрана

        Args:
            region (tuple): Координаты области (x, y, width, height)
            delay (float): Задержка между снимками в секундах
            threshold (float): Порог сходства (0-1), ниже которого считается, что есть изменения

        Returns:
            bool: True, если обнаружены изменения, иначе False
        """
        try:
            # Захватываем первый снимок области
            img1 = self.screen_capture.capture_region(region)

            # Ждем указанное время
            time.sleep(delay)

            # Захватываем второй снимок области
            img2 = self.screen_capture.capture_region(region)

            # Сравниваем изображения
            similarity = self.image_comparison.compare_images(img1, img2)

            # Если сходство ниже порога, значит есть изменения
            return similarity < threshold
        except Exception as e:
            handle_error(f"Ошибка при обнаружении изменений в области: {e}", e, module="vision")
            return False

    def wait_for_changes(self, timeout=10, delay=0.5, threshold=0.95):
        """
        Ожидает изменений на экране в течение указанного времени

        Args:
            timeout (float): Максимальное время ожидания в секундах
            delay (float): Задержка между проверками в секундах
            threshold (float): Порог сходства (0-1), ниже которого считается, что есть изменения

        Returns:
            bool: True, если обнаружены изменения, иначе False
        """
        try:
            # Запоминаем время начала
            start_time = time.time()

            # Захватываем первый снимок экрана
            img1 = self.screen_capture.capture_screen()

            # Ждем изменений в течение указанного времени
            while time.time() - start_time < timeout:
                # Ждем указанное время
                time.sleep(delay)

                # Захватываем текущий снимок экрана
                img2 = self.screen_capture.capture_screen()

                # Сравниваем изображения
                similarity = self.image_comparison.compare_images(img1, img2)

                # Если сходство ниже порога, значит есть изменения
                if similarity < threshold:
                    return True

                # Обновляем первый снимок
                img1 = img2

            # Если время вышло, а изменений не обнаружено
            return False
        except Exception as e:
            handle_error(f"Ошибка при ожидании изменений: {e}", e, module="vision")
            return False

    def wait_for_changes_in_region(self, region, timeout=10, delay=0.5, threshold=0.95):
        """
        Ожидает изменений в указанной области экрана в течение указанного времени

        Args:
            region (tuple): Координаты области (x, y, width, height)
            timeout (float): Максимальное время ожидания в секундах
            delay (float): Задержка между проверками в секундах
            threshold (float): Порог сходства (0-1), ниже которого считается, что есть изменения

        Returns:
            bool: True, если обнаружены изменения, иначе False
        """
        try:
            # Запоминаем время начала
            start_time = time.time()

            # Захватываем первый снимок области
            img1 = self.screen_capture.capture_region(region)

            # Ждем изменений в течение указанного времени
            while time.time() - start_time < timeout:
                # Ждем указанное время
                time.sleep(delay)

                # Захватываем текущий снимок области
                img2 = self.screen_capture.capture_region(region)

                # Сравниваем изображения
                similarity = self.image_comparison.compare_images(img1, img2)

                # Если сходство ниже порога, значит есть изменения
                if similarity < threshold:
                    return True

                # Обновляем первый снимок
                img1 = img2

            # Если время вышло, а изменений не обнаружено
            return False
        except Exception as e:
            handle_error(f"Ошибка при ожидании изменений в области: {e}", e, module="vision")
            return False
