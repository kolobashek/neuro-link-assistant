from unittest.mock import MagicMock

import pytest


@pytest.fixture
def mock_driver():
    return MagicMock()


@pytest.fixture
def js_event_handler(mock_driver):
    # Пример класса для работы с JS-событиями
    class JSEventHandler:
        def __init__(self, driver):
            self.driver = driver

        def trigger_event(self, element, event_name):
            js = (
                f"var evt = new Event('{event_name}', {{bubbles:true}});"
                " arguments[0].dispatchEvent(evt);"
            )
            return self.driver.execute_script(js, element)

        def trigger_click(self, element):
            js = "arguments[0].click();"
            return self.driver.execute_script(js, element)

        def set_value_via_js(self, element, value):
            js = "arguments[0].value = arguments[1];"
            return self.driver.execute_script(js, element, value)

        def get_inner_text_via_js(self, element):
            js = "return arguments[0].innerText;"
            return self.driver.execute_script(js, element)

    return JSEventHandler(mock_driver)


def test_trigger_custom_event(js_event_handler, mock_driver):
    element = MagicMock()
    js_event_handler.trigger_event(element, "focus")
    mock_driver.execute_script.assert_called_once()
    args, kwargs = mock_driver.execute_script.call_args
    assert "dispatchEvent" in args[0]
    assert element in args


def test_trigger_click(js_event_handler, mock_driver):
    element = MagicMock()
    js_event_handler.trigger_click(element)
    mock_driver.execute_script.assert_called_once_with("arguments[0].click();", element)


def test_set_value_via_js(js_event_handler, mock_driver):
    element = MagicMock()
    js_event_handler.set_value_via_js(element, "hello")
    mock_driver.execute_script.assert_called_once_with(
        "arguments[0].value = arguments[1];", element, "hello"
    )


def test_get_inner_text_via_js(js_event_handler, mock_driver):
    element = MagicMock()
    mock_driver.execute_script.return_value = "текст"
    result = js_event_handler.get_inner_text_via_js(element)
    mock_driver.execute_script.assert_called_once_with("return arguments[0].innerText;", element)
    assert result == "текст"


def test_trigger_event_js_error(js_event_handler, mock_driver):
    element = MagicMock()
    mock_driver.execute_script.side_effect = Exception("JS error")
    with pytest.raises(Exception) as excinfo:
        js_event_handler.trigger_event(element, "focus")
    assert "JS error" in str(excinfo.value)
