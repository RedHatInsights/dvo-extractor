"""Module containing unit tests for the `LogFilter` class."""

from logging import LogRecord
import pytest

from controller.log_filter import LogFilter

_MODULES = [
    "publisher",
    "consumer"
]

_LEVELS = [
    "ERROR"
    "DEBUG"
]

_LINE_NUMBERS = [
    1,
    42
]

_MESSAGES = [
    "Everything is working correctly",
    "Something we wrong"
]


@pytest.mark.parametrize("module", _MODULES)
@pytest.mark.parametrize("level", _LEVELS)
@pytest.mark.parametrize("lineno", _LINE_NUMBERS)
@pytest.mark.parametrize("msg", _MESSAGES)
def test_log_filter(module, level, lineno, msg):
    """Test that all messages get through the log filter."""
    record = LogRecord(f"controller.{module}", level,
                       f"{module}.py", lineno, msg, tuple(), Exception())
    assert LogFilter.filter(None, record) is True
