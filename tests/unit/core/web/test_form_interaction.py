import pytest
from unittest.mock import MagicMock, patch
from selenium.webdriver.common.by import By

@pytest.fixture
def element_finder():
    # Мокаем browser_controller с .driver
    mock_driver = MagicMock()
    mock_browser_controller = MagicMock()
    mock_browser_controller.driver = mock_driver
    from core.web.element_finder import ElementFinder
    return ElementFinder(mock_browser_controller)

def test_send_keys_to_input(element_finder):
    mock_element = MagicMock()
    # Проверяем, что send_keys возвращает True при успешном вводе
    result = element_finder.send_keys(mock_element, "тестовый текст")
    mock_element.clear.assert_called_once()
    mock_element.send_keys.assert_called_once_with("тестовый текст")
    assert result is True

def test_send_keys_to_input_none(element_finder):
    # Если элемент None, метод должен вернуть False
    result = element_finder.send_keys(None, "текст")
    assert result is False

def test_click_element_success(element_finder):
    mock_element = MagicMock()
    result = element_finder.click_element(mock_element)
    mock_element.click.assert_called_once()
    assert result is True

def test_click_element_none(element_finder):
    result = element_finder.click_element(None)
    assert result is False

def test_get_element_text_success(element_finder):
    mock_element = MagicMock()
    mock_element.text = "Текст элемента"
    text = element_finder.get_element_text(mock_element)
    assert text == "Текст элемента"

def test_get_element_text_none(element_finder):
    text = element_finder.get_element_text(None)
    assert text is None

def test_get_element_attribute_success(element_finder):
    mock_element = MagicMock()
    mock_element.get_attribute.return_value = "значение"
    value = element_finder.get_element_attribute(mock_element, "data-test")
    mock_element.get_attribute.assert_called_once_with("data-test")
    assert value == "значение"

def test_get_element_attribute_none(element_finder):
    value = element_finder.get_element_attribute(None, "data-test")
    assert value is None

def test_find_element_by_name(element_finder):
    # Проверяем, что find_element_by_name вызывает find_element с правильными аргументами
    with patch.object(element_finder, 'find_element', return_value="mocked") as mock_find:
        result = element_finder.find_element_by_name("username")
        mock_find.assert_called_once_with('name', "username", 10)
        assert result == "mocked"

def test_is_element_present_true(element_finder):
    # Мокаем driver.find_element чтобы не выбрасывал исключение
    element_finder.browser.driver.find_element.return_value = MagicMock()
    result = element_finder.is_element_present('id', "test-id")
    assert result is True

def test_is_element_present_false(element_finder):
    from selenium.common.exceptions import NoSuchElementException
    element_finder.browser.driver.find_element.side_effect = NoSuchElementException("not found")
    result = element_finder.is_element_present('id', "test-id")
    assert result is False