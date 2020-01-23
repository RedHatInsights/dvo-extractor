"""Module containing unit tests for the `Consumer` class."""

import pytest

from controller.consumer import Consumer
from controller.data_pipeline_error import DataPipelineError

from kafka.consumer.fetcher import ConsumerRecord

_REGEX_BAD_TYPE = r'^Unexpected input message type: '
_REGEX_BAD_JSON = r'^Unable to decode received message \(.*\):'


def _mock_consumer_record(value):
    """Construct a value-only `ConsumerRecord`."""
    return ConsumerRecord(None, None, None, None, None, None, value, None, None, None, None, None)


def _to_bytearray(string):
    """Convert a string into a UTF-8 encoded byte array."""
    return bytearray(string.encode("utf-8"))


def test_deserialize_invalid_type():
    """Test that passing invalid data type to `deserialize` raises an exception."""
    with pytest.raises(DataPipelineError, match=_REGEX_BAD_TYPE):
        Consumer.deserialize(None, None)

    with pytest.raises(DataPipelineError, match=_REGEX_BAD_TYPE):
        Consumer.deserialize(None, '')

    with pytest.raises(DataPipelineError, match=_REGEX_BAD_TYPE):
        Consumer.deserialize(None, bytes())


def test_deserialize_invalid_format():
    """Test that passing a malformed message to `deserialize` raises an exception."""
    with pytest.raises(DataPipelineError, match=_REGEX_BAD_JSON):
        Consumer.deserialize(None, _to_bytearray(''))

    with pytest.raises(DataPipelineError, match=_REGEX_BAD_JSON):
        Consumer.deserialize(None, _to_bytearray('"'))

    with pytest.raises(DataPipelineError, match=_REGEX_BAD_JSON):
        Consumer.deserialize(None, _to_bytearray('{"key":"value"'))

    with pytest.raises(DataPipelineError, match=_REGEX_BAD_JSON):
        Consumer.deserialize(None, _to_bytearray('"key":"value"}'))

    with pytest.raises(DataPipelineError, match=_REGEX_BAD_JSON):
        Consumer.deserialize(None, _to_bytearray('"key":"value"'))


def test_deserialize_valid():
    """Test that proper JSON input messages are correctly deserialized."""
    assert Consumer.deserialize(None, _to_bytearray('""')) == ""
    assert Consumer.deserialize(None, _to_bytearray('[]')) == []
    assert Consumer.deserialize(None, _to_bytearray('{}')) == dict()
    assert Consumer.deserialize(None, _to_bytearray('{"key":"value"}')) == {"key": "value"}


def test_handles_invalid():
    """Test that `Consumer` refuses to handle malformed input messages."""
    assert not Consumer.handles(None, _mock_consumer_record(None))

    dict_str = '{"url": "bucket/file"}'
    assert not Consumer.handles(None, _mock_consumer_record(''))
    assert not Consumer.handles(None, _mock_consumer_record(dict_str))
    assert not Consumer.handles(None, _mock_consumer_record(dict_str.encode("utf-8")))
    assert not Consumer.handles(None, _mock_consumer_record(_to_bytearray(dict_str)))

    assert not Consumer.handles(None, _mock_consumer_record(dict()))
    assert not Consumer.handles(None, _mock_consumer_record({"noturl": "bucket/file"}))


def test_handles_valid():
    """Test that `Consumer` accepts handling of correctly formatted input messages."""
    assert Consumer.handles(None, _mock_consumer_record({"url": ""}))
    assert Consumer.handles(None, _mock_consumer_record({"url": "bucket/file"}))
