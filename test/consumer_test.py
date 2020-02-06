"""Module containing unit tests for the `Consumer` class."""

from unittest.mock import patch

import pytest

from kafka.consumer.fetcher import ConsumerRecord

from controller.consumer import Consumer
from controller.data_pipeline_error import DataPipelineError

_REGEX_BAD_SCHEMA = r'^Unable to extract URL from input message: '


def _mock_consumer_record(value):
    """Construct a value-only `ConsumerRecord`."""
    return ConsumerRecord(None, None, None, None, None, None, value, None, None, None, None, None)


_INVALID_TYPE_VALUES = [
    None,
    42,
    3.14,
    True,
    [],
    {}
]


@pytest.mark.parametrize("value", _INVALID_TYPE_VALUES)
def test_deserialize_invalid_type(value):
    """Test that passing invalid data type to `deserialize` raises an exception."""
    assert Consumer.deserialize(None, value) is None


_INVALID_MESSAGES = [
    '',
    '{}',
    '{"noturl":"https://s3.com/hash"}'
    '{"url":"value"',
    '"url":"value"}',
    '"url":"value"',
    '"{\"url\":\"value\"}"'
]


@pytest.mark.parametrize("msg", _INVALID_MESSAGES)
def test_deserialize_invalid_format_str(msg):
    """Test that passing a malformed message to `deserialize` raises an exception."""
    assert Consumer.deserialize(None, msg) is None


@pytest.mark.parametrize("msg", _INVALID_MESSAGES)
def test_deserialize_invalid_format_bytes(msg):
    """Test that passing a malformed message to `deserialize` raises an exception."""
    assert Consumer.deserialize(None, msg.encode("utf-8")) is None


@pytest.mark.parametrize("msg", _INVALID_MESSAGES)
def test_deserialize_invalid_format_bytearray(msg):
    """Test that passing a malformed message to `deserialize` raises an exception."""
    assert Consumer.deserialize(None, bytearray(msg.encode("utf-8"))) is None


_VALID_MESSAGES = [
    ('{"url": ""}', {"url": ""}),

    ('{"url": "https://s3.com/hash", "unused-property": null}',
     {"url": "https://s3.com/hash", "unused-property": None}),

    ('{"account":12345678, "url":"any/url"}', {"account": 12345678, "url": "any/url"})
]


@pytest.mark.parametrize("msg,value", _VALID_MESSAGES)
def test_deserialize_valid_str(msg, value):
    """Test that proper string JSON input messages are correctly deserialized."""
    assert Consumer.deserialize(None, msg) == value


@pytest.mark.parametrize("msg,value", _VALID_MESSAGES)
def test_deserialize_valid_bytes(msg, value):
    """Test that proper bytes JSON input messages are correctly deserialized."""
    assert Consumer.deserialize(None, msg.encode("utf-8")) == value


@pytest.mark.parametrize("msg,value", _VALID_MESSAGES)
def test_deserialize_valid_bytearray(msg, value):
    """Test that proper bytearray JSON input messages are correctly deserialized."""
    assert Consumer.deserialize(None, bytearray(msg.encode("utf-8"))) == value


# This would have been a valid input, but it's supposed to be a `dict`, not `str`.
_DICT_STR = '{"url": "bucket/file"}'

_INVALID_RECORD_VALUES = [
    '',
    _DICT_STR,
    _DICT_STR.encode("utf-8"),
    bytearray(_DICT_STR.encode("utf-8")),
    [],
    {},
    {"noturl": "bucket/file"}
]


@pytest.mark.parametrize("value", _INVALID_RECORD_VALUES)
@patch('insights_messaging.consumers.kafka.KafkaConsumer.__init__', lambda *args, **kwargs: None)
def test_handles_invalid(value):
    """Test that `Consumer` refuses to handle malformed input messages."""
    consumer = Consumer(None, None, None)
    assert not consumer.handles(_mock_consumer_record(value))


_VALID_RECORD_VALUES = [
    {"url": ""},
    {"url": "bucket/file"},
    {"url": "https://a-valid-domain.com/precious_url"}
]


@pytest.mark.parametrize("value", _VALID_RECORD_VALUES)
def test_handles_valid(value):
    """Test that `Consumer` accepts handling of correctly formatted input messages."""
    assert Consumer.handles(None, _mock_consumer_record(value))


@pytest.mark.parametrize("value", _INVALID_RECORD_VALUES)
def test_get_url_invalid(value):
    """Test that `Consumer.get_url` raises the appropriate exception."""
    with pytest.raises(DataPipelineError, match=_REGEX_BAD_SCHEMA):
        Consumer.get_url(None, value)


@pytest.mark.parametrize("value", _VALID_RECORD_VALUES)
def test_get_url_valid(value):
    """Test that `Consumer.get_url` returns the expected value."""
    assert Consumer.get_url(None, _mock_consumer_record(value)) == value['url']


_VALID_TOPICS = [
    "topic",
    "funny-topic"
]

_VALID_GROUPS = [
    "group",
    "good-boys"
]

_VALID_SERVERS = [
    "server",
    "great.server.net"
]


def _mock_kafka_init(self, publisher, downloader, engine, incoming_topic,
                     group_id, bootstrap_servers, retry_backoff_ms=1000):
    self.INCOMING_TOPIC = incoming_topic
    self.GROUP_ID = group_id
    self.BOOSTRAP_SERVERS = bootstrap_servers


@pytest.mark.parametrize("topic", _VALID_TOPICS)
@pytest.mark.parametrize("group", _VALID_GROUPS)
@pytest.mark.parametrize("server", _VALID_SERVERS)
@patch('insights_messaging.consumers.kafka.Kafka.__init__', _mock_kafka_init)
def test_consumer_init(topic, group, server):
    """Test of our Consumer constructor, with direct (not loaded from env) config."""
    cons = Consumer(None, None, None, group, "GROUP_ENV",
                    topic, "TOPIC_ENV", [server], "SERVER_ENV")

    assert cons.INCOMING_TOPIC == topic
    assert cons.GROUP_ID == group
    assert cons.BOOSTRAP_SERVERS == [server]
