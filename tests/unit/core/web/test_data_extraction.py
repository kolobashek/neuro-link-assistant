import pytest
from unittest.mock import MagicMock

@pytest.fixture
def element_finder():
    mock_driver = MagicMock()
    mock_browser_controller = MagicMock()
    mock_browser_controller.driver = mock_driver
    from core.web.element_finder import ElementFinder
    return ElementFinder(mock_browser_controller)

def test_extract_text_from_element(element_finder):
    mock_element = MagicMock()
    mock_element.text = "Привет, мир!"
    text = element_finder.get_element_text(mock_element)
    assert text == "Привет, мир!"

def test_extract_attribute_from_element(element_finder):
    mock_element = MagicMock()
    mock_element.get_attribute.return_value = "https://example.com"
    value = element_finder.get_element_attribute(mock_element, "href")
    mock_element.get_attribute.assert_called_once_with("href")
    assert value == "https://example.com"

def test_extract_multiple_elements_text(element_finder):
    mock_elements = [MagicMock(text="A"), MagicMock(text="B"), MagicMock(text="C")]
    # Допустим, у тебя есть метод для получения текста всех элементов
    texts = [element_finder.get_element_text(e) for e in mock_elements]
    assert texts == ["A", "B", "C"]

def test_extract_table_data(element_finder):
    # Пример: извлечь все ячейки таблицы (упрощённо)
    mock_row1 = MagicMock()
    mock_row1.text = "row1"
    mock_row2 = MagicMock()
    mock_row2.text = "row2"
    table_elements = [mock_row1, mock_row2]
    texts = [element_finder.get_element_text(e) for e in table_elements]
    assert texts == ["row1", "row2"]
