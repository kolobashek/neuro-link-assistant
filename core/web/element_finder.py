from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException

class ElementFinder:
    """
    Класс для поиска элементов на веб-странице.
    """

    def __init__(self, browser_controller):
        """
        Инициализация искателя элементов.

        Args:
            browser_controller (BrowserController): Контроллер браузера
        """
        self.browser = browser_controller

    def find_element(self, by, value, timeout=10):
        """
        Находит элемент на странице.

        Args:
            by (str): Метод поиска ('id', 'name', 'xpath', 'css', 'class', 'tag', 'link_text', 'partial_link_text')
            value (str): Значение для поиска
            timeout (int, optional): Таймаут ожидания в секундах

        Returns:
            WebElement: Найденный элемент или None
        """
        try:
            if self.browser.driver is None:
                return None

            # Преобразуем строковый метод поиска в константу By
            by_method = self._get_by_method(by)

            # Ожидаем появления элемента
            element = WebDriverWait(self.browser.driver, timeout).until(
                EC.presence_of_element_located((by_method, value))
            )

            return element
        except TimeoutException:
            print(f"Timeout waiting for element: {by}={value}")
            return None
        except Exception as e:
            print(f"Error finding element: {e}")
            return None

    def find_elements(self, by, value, timeout=10):
        """
        Находит все элементы на странице, соответствующие критериям.

        Args:
            by (str): Метод поиска ('id', 'name', 'xpath', 'css', 'class', 'tag', 'link_text', 'partial_link_text')
            value (str): Значение для поиска
            timeout (int, optional): Таймаут ожидания в секундах

        Returns:
            list: Список найденных элементов или пустой список
        """
        try:
            if self.browser.driver is None:
                return []

            # Преобразуем строковый метод поиска в константу By
            by_method = self._get_by_method(by)

            # Ожидаем появления хотя бы одного элемента
            WebDriverWait(self.browser.driver, timeout).until(
                EC.presence_of_element_located((by_method, value))
            )

            # Получаем все элементы
            elements = self.browser.driver.find_elements(by_method, value)

            return elements
        except TimeoutException:
            print(f"Timeout waiting for elements: {by}={value}")
            return []
        except Exception as e:
            print(f"Error finding elements: {e}")
            return []

    def find_element_by_id(self, id, timeout=10):
        """
        Находит элемент по ID.

        Args:
            id (str): ID элемента
            timeout (int, optional): Таймаут ожидания в секундах

        Returns:
            WebElement: Найденный элемент или None
        """
        return self.find_element('id', id, timeout)

    def find_element_by_name(self, name, timeout=10):
        """
        Находит элемент по имени.

        Args:
            name (str): Имя элемента
            timeout (int, optional): Таймаут ожидания в секундах

        Returns:
            WebElement: Найденный элемент или None
        """
        return self.find_element('name', name, timeout)

    def find_element_by_xpath(self, xpath, timeout=10):
        """
        Находит элемент по XPath.

        Args:
            xpath (str): XPath-выражение
            timeout (int, optional): Таймаут ожидания в секундах

        Returns:
            WebElement: Найденный элемент или None
        """
        return self.find_element('xpath', xpath, timeout)

    def find_element_by_css(self, css, timeout=10):
        """
        Находит элемент по CSS-селектору.

        Args:
            css (str): CSS-селектор
            timeout (int, optional): Таймаут ожидания в секундах

        Returns:
            WebElement: Найденный элемент или None
        """
        return self.find_element('css', css, timeout)

    def find_element_by_class(self, class_name, timeout=10):
        """
        Находит элемент по имени класса.

        Args:
            class_name (str): Имя класса
            timeout (int, optional): Таймаут ожидания в секундах

        Returns:
            WebElement: Найденный элемент или None
        """
        return self.find_element('class', class_name, timeout)

    def find_element_by_tag(self, tag_name, timeout=10):
        """
        Находит элемент по имени тега.

        Args:
            tag_name (str): Имя тега
            timeout (int, optional): Таймаут ожидания в секундах

        Returns:
            WebElement: Найденный элемент или None
        """
        return self.find_element('tag', tag_name, timeout)

    def find_elements_by_tag(self, tag_name, timeout=10):
        """
        Находит все элементы по имени тега.

        Args:
            tag_name (str): Имя тега
            timeout (int, optional): Таймаут ожидания в секундах

        Returns:
            list: Список найденных элементов или пустой список
        """
        return self.find_elements('tag', tag_name, timeout)

    def find_element_by_link_text(self, link_text, timeout=10):
        """
        Находит элемент по тексту ссылки.

        Args:
            link_text (str): Текст ссылки
            timeout (int, optional): Таймаут ожидания в секундах

        Returns:
            WebElement: Найденный элемент или None
        """
        return self.find_element('link_text', link_text, timeout)

    def find_element_by_partial_link_text(self, partial_link_text, timeout=10):
        """
        Находит элемент по частичному тексту ссылки.

        Args:
            partial_link_text (str): Частичный текст ссылки
            timeout (int, optional): Таймаут ожидания в секундах

        Returns:
            WebElement: Найденный элемент или None
        """
        return self.find_element('partial_link_text', partial_link_text, timeout)

    def wait_for_element(self, by, value, timeout=10, condition='presence'):
        """
        Ожидает появления элемента на странице.

        Args:
            by (str): Метод поиска ('id', 'name', 'xpath', 'css', 'class', 'tag', 'link_text', 'partial_link_text')
            value (str): Значение для поиска
            timeout (int, optional): Таймаут ожидания в секундах
            condition (str, optional): Условие ожидания ('presence', 'visibility', 'clickable')

        Returns:
            WebElement: Найденный элемент или None
        """
        try:
            if self.browser.driver is None:
                return None

            # Преобразуем строковый метод поиска в константу By
            by_method = self._get_by_method(by)

            # Выбираем условие ожидания
            if condition == 'visibility':
                wait_condition = EC.visibility_of_element_located((by_method, value))
            elif condition == 'clickable':
                wait_condition = EC.element_to_be_clickable((by_method, value))
            else:  # 'presence' по умолчанию
                wait_condition = EC.presence_of_element_located((by_method, value))

            # Ожидаем выполнения условия
            element = WebDriverWait(self.browser.driver, timeout).until(wait_condition)

            return element
        except TimeoutException:
            print(f"Timeout waiting for element with condition '{condition}': {by}={value}")
            return None
        except Exception as e:
            print(f"Error waiting for element: {e}")
            return None

    def wait_for_text(self, by, value, text, timeout=10):
        """
        Ожидает появления текста в элементе.

        Args:
            by (str): Метод поиска ('id', 'name', 'xpath', 'css', 'class', 'tag', 'link_text', 'partial_link_text')
            value (str): Значение для поиска
            text (str): Ожидаемый текст
            timeout (int, optional): Таймаут ожидания в секундах

        Returns:
            bool: True, если текст появился в элементе
        """
        try:
            if self.browser.driver is None:
                return False

            # Преобразуем строковый метод поиска в константу By
            by_method = self._get_by_method(by)

            # Ожидаем появления текста в элементе
            WebDriverWait(self.browser.driver, timeout).until(
                EC.text_to_be_present_in_element((by_method, value), text)
            )

            return True
        except TimeoutException:
            print(f"Timeout waiting for text '{text}' in element: {by}={value}")
            return False
        except Exception as e:
            print(f"Error waiting for text: {e}")
            return False

    def is_element_present(self, by, value):
        """
        Проверяет наличие элемента на странице.

        Args:
            by (str): Метод поиска ('id', 'name', 'xpath', 'css', 'class', 'tag', 'link_text', 'partial_link_text')
            value (str): Значение для поиска

        Returns:
            bool: True, если элемент присутствует
        """
        try:
            if self.browser.driver is None:
                return False

            # Преобразуем строковый метод поиска в константу By
            by_method = self._get_by_method(by)

            # Проверяем наличие элемента
            self.browser.driver.find_element(by_method, value)
            return True
        except NoSuchElementException:
            return False
        except Exception as e:
            print(f"Error checking element presence: {e}")
            return False

    def get_element_text(self, element):
        """
        Получает текст элемента.

        Args:
            element (WebElement): Элемент

        Returns:
            str: Текст элемента или None в случае ошибки
        """
        try:
            if element is None:
                return None

            return element.text
        except Exception as e:
            print(f"Error getting element text: {e}")
            return None

    def get_element_attribute(self, element, attribute):
        """
        Получает значение атрибута элемента.

        Args:
            element (WebElement): Элемент
            attribute (str): Имя атрибута

        Returns:
            str: Значение атрибута или None в случае ошибки
        """
        try:
            if element is None:
                return None

            return element.get_attribute(attribute)
        except Exception as e:
            print(f"Error getting element attribute: {e}")
            return None

    def click_element(self, element):
        """
        Кликает по элементу.

        Args:
            element (WebElement): Элемент

        Returns:
            bool: True в случае успешного клика
        """
        try:
            if element is None:
                return False

            element.click()
            return True
        except Exception as e:
            print(f"Error clicking element: {e}")
            return False

    def send_keys(self, element, text):
        """
        Вводит текст в элемент.

        Args:
            element (WebElement): Элемент
            text (str): Текст для ввода

        Returns:
            bool: True в случае успешного ввода
        """
        try:
            if element is None:
                return False

            element.clear()
            element.send_keys(text)
            return True
        except Exception as e:
            print(f"Error sending keys to element: {e}")
            return False

    def _get_by_method(self, by):
        """
        Преобразует строковый метод поиска в константу By.

        Args:
            by (str): Метод поиска ('id', 'name', 'xpath', 'css', 'class', 'tag', 'link_text', 'partial_link_text')

        Returns:
            By: Константа By для указанного метода
        """
        by = by.lower()

        if by == 'id':
            return By.ID
        elif by == 'name':
            return By.NAME
        elif by == 'xpath':
            return By.XPATH
        elif by == 'css':
            return By.CSS_SELECTOR
        elif by == 'class':
            return By.CLASS_NAME
        elif by == 'tag':
            return By.TAG_NAME
        elif by == 'link_text':
            return By.LINK_TEXT
        elif by == 'partial_link_text':
            return By.PARTIAL_LINK_TEXT
        else:
            raise ValueError(f"Unsupported locator method: {by}")
