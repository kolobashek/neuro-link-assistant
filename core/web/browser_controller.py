import os

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.edge.options import Options as EdgeOptions
from selenium.webdriver.edge.service import Service as EdgeService
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from selenium.webdriver.firefox.service import Service as FirefoxService
from webdriver_manager.chrome import ChromeDriverManager
from webdriver_manager.firefox import GeckoDriverManager
from webdriver_manager.microsoft import EdgeChromiumDriverManager


class BrowserController:
    """
    Класс для управления веб-браузером.
    """

    def __init__(self, browser_type="chrome", headless=False):
        """
        Инициализация контроллера браузера.

        Args:
            browser_type (str, optional): Тип браузера ('chrome', 'firefox', 'edge')
            headless (bool, optional): Запускать браузер в фоновом режиме
        """
        self.browser_type = browser_type.lower()
        self.headless = headless
        self.driver = None

    def initialize(self):
        """
        Инициализирует браузер.

        Returns:
            bool: True в случае успешной инициализации
        """
        try:
            if self.browser_type == "chrome":
                options = Options()
                if self.headless:
                    options.add_argument("--headless")

                # Добавляем полезные опции
                options.add_argument("--start-maximized")
                options.add_argument("--disable-notifications")
                options.add_argument("--disable-popup-blocking")
                options.add_argument("--disable-infobars")

                # Инициализируем драйвер Chrome
                self.driver = webdriver.Chrome(
                    service=ChromeService(ChromeDriverManager().install()), options=options
                )

            elif self.browser_type == "firefox":

                options = FirefoxOptions()
                if self.headless:
                    options.add_argument("--headless")

                # Инициализируем драйвер Firefox
                self.driver = webdriver.Firefox(
                    service=FirefoxService(GeckoDriverManager().install()), options=options
                )

            elif self.browser_type == "edge":

                options = EdgeOptions()
                if self.headless:
                    options.add_argument("--headless")

                # Инициализируем драйвер Edge
                self.driver = webdriver.Edge(
                    service=EdgeService(EdgeChromiumDriverManager().install()), options=options
                )

            else:
                print(f"Unsupported browser type: {self.browser_type}")
                return False

            # Устанавливаем таймаут ожидания
            self.driver.implicitly_wait(10)

            return True

        except Exception as e:
            print(f"Error initializing browser: {e}")
            return False

    def navigate(self, url):
        """
        Переходит по указанному URL.

        Args:
            url (str): URL для перехода

        Returns:
            bool: True в случае успешного перехода
        """
        try:
            if self.driver is None:
                if not self.initialize():
                    return False

            # Дополнительная проверка, что драйвер был успешно инициализирован
            if self.driver is None:
                print("Browser driver is still None after initialization")
                return False

            self.driver.get(url)
            return True
        except Exception as e:
            print(f"Error navigating to URL: {e}")
            return False

    def get_current_url(self):
        """
        Получает текущий URL.

        Returns:
            str: Текущий URL или None в случае ошибки
        """
        try:
            if self.driver is None:
                return None

            return self.driver.current_url
        except Exception as e:
            print(f"Error getting current URL: {e}")
            return None

    def get_page_title(self):
        """
        Получает заголовок текущей страницы.

        Returns:
            str: Заголовок страницы или None в случае ошибки
        """
        try:
            if self.driver is None:
                return None

            return self.driver.title
        except Exception as e:
            print(f"Error getting page title: {e}")
            return None

    def refresh_page(self):
        """
        Обновляет текущую страницу.

        Returns:
            bool: True в случае успешного обновления
        """
        try:
            if self.driver is None:
                return False

            self.driver.refresh()
            return True
        except Exception as e:
            print(f"Error refreshing page: {e}")
            return False

    def go_back(self):
        """
        Переходит на предыдущую страницу.

        Returns:
            bool: True в случае успешного перехода
        """
        try:
            if self.driver is None:
                return False

            self.driver.back()
            return True
        except Exception as e:
            print(f"Error going back: {e}")
            return False

    def go_forward(self):
        """
        Переходит на следующую страницу.

        Returns:
            bool: True в случае успешного перехода
        """
        try:
            if self.driver is None:
                return False

            self.driver.forward()
            return True
        except Exception as e:
            print(f"Error going forward: {e}")
            return False

    def execute_script(self, script, *args):
        """
        Выполняет JavaScript на странице.

        Args:
            script (str): JavaScript-код для выполнения
            *args: Аргументы для скрипта

        Returns:
            any: Результат выполнения скрипта или None в случае ошибки
        """
        try:
            if self.driver is None:
                return None

            return self.driver.execute_script(script, *args)
        except Exception as e:
            print(f"Error executing script: {e}")
            return None

    def take_screenshot(self, path):
        """
        Делает скриншот текущей страницы.

        Args:
            path (str): Путь для сохранения скриншота

        Returns:
            bool: True в случае успешного сохранения
        """
        try:
            if self.driver is None:
                return False

            # Создаем директорию, если она не существует
            os.makedirs(os.path.dirname(path), exist_ok=True)

            self.driver.save_screenshot(path)
            return True
        except Exception as e:
            print(f"Error taking screenshot: {e}")
            return False

    def close(self):
        """
        Закрывает текущую вкладку браузера.

        Returns:
            bool: True в случае успешного закрытия
        """
        try:
            if self.driver is None:
                return True

            self.driver.close()
            return True
        except Exception as e:
            print(f"Error closing browser tab: {e}")
            return False

    def quit(self):
        """
        Закрывает браузер полностью.

        Returns:
            bool: True в случае успешного закрытия
        """
        try:
            if self.driver is None:
                return True

            self.driver.quit()
            self.driver = None
            return True
        except Exception as e:
            print(f"Error quitting browser: {e}")
            self.driver = None
            return False

    def __del__(self):
        """Деструктор для закрытия браузера при уничтожении объекта."""
        self.quit()
