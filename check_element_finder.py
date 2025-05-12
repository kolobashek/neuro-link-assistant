print("Проверка импорта ElementFinder")
from core.web.element_finder import ElementFinder
finder = ElementFinder(None)
print("Методы класса:", [m for m in dir(finder) if not m.startswith("_")])
print("Есть ли find_elements_by_tag:", hasattr(finder, "find_elements_by_tag"))
