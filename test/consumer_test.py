"""Module containing unit tests for the `Consumer` class."""

from unittest.mock import patch

import pytest

from kafka import KafkaConsumer

from controller.consumer import Consumer
from controller.data_pipeline_error import DataPipelineError

from .utils import mock_consumer_record


@pytest.fixture(autouse=True)
def mock_consumer(monkeypatch):
    """Mock KafkaConsumer."""
    monkeypatch.setattr(KafkaConsumer, "__init__", lambda *args, **kargs: None)


_REGEX_BAD_SCHEMA = r'^Unable to extract URL from input message: '
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
    deserialized = Consumer.deserialize(Consumer(None, None, None), value)
    assert isinstance(deserialized, DataPipelineError)
    assert str(deserialized).startswith('Unexpected input message type: ')


_ERR_UNABLE_TO_DECODE = 'Unable to decode received message: '
_ERR_JSON_SCHEMA = 'Invalid input message JSON schema: '
_ERR_BASE64 = 'Base64 encoded identity could not be parsed: '

_INVALID_MESSAGES = [
    ('', _ERR_UNABLE_TO_DECODE),
    ('{}', _ERR_JSON_SCHEMA),
    ('{"noturl":"https://s3.com/hash"}', _ERR_JSON_SCHEMA),
    ('{"url":"value"', _ERR_UNABLE_TO_DECODE),
    ('"url":"value"}', _ERR_UNABLE_TO_DECODE),
    ('"url":"value"', _ERR_UNABLE_TO_DECODE),
    ('"{\"url\":\"value\"}"', _ERR_UNABLE_TO_DECODE),
    # incorrect content of b64_identity (org_id missing)
    ('{"url": "https://s3.com/hash", "b64_identity": "eyJpZGVudGl0eSI6IHsiaW50ZXJuYWwiOiB7Im1pc3'\
        'Npbmdfb3JnX2lkIjogIjEyMzgzMDMyIn19fQ==", "timestamp": "2020-01-23T16:15:59.478901889Z"}',
     _ERR_JSON_SCHEMA),
    # incorrect format of base64 encoding
    ('{"url": "https://s3.com/hash", "b64_identity": "eyJpZGVudGl0eSI6IHsiaW50ZXJuYWwiOiB7Im9yZ1'\
        '9pZCI6ICIxMjM4MzAzMiJ9f", "timestamp": "2020-01-23T16:15:59.478901889Z"}', _ERR_BASE64),
    # org_id not string
    ('{"url": "https://s3.com/hash", "b64_identity": "eyJpZGVudGl0eSI6IHsKICAgICJhY2NvdW50X251bW'\
        'JlciI6ICI2MjEyMzc3IiwKICAgICJhdXRoX3R5cGUiOiAiYmFzaWMtYXV0aCIsCiAgICAiaW50ZXJuYWwiOiB7C'\
        'iAgICAgICAgImF1dGhfdGltZSI6IDE0MDAsCiAgICAgICAgIm9yZ19pZCI6IDEyMzgzMDMyCiAgICB9LAogICAg'\
        'InR5cGUiOiAiVXNlciIsCiAgICAidXNlciI6IHsKICAgICAgICAiZW1haWwiOiAiam5lZWRsZStxYUByZWRoYXQ'\
        'uY29tIiwKICAgICAgICAiZmlyc3RfbmFtZSI6ICJJbnNpZ2h0cyIsCiAgICAgICAgImlzX2FjdGl2ZSI6IHRydW'\
        'UsCiAgICAgICAgImlzX2ludGVybmFsIjogZmFsc2UsCiAgICAgICAgImlzX29yZ19hZG1pbiI6IHRydWUsCiAgI'\
        'CAgICAgImxhc3RfbmFtZSI6ICJRRSIsCiAgICAgICAgImxvY2FsZSI6ICJlbl9VUyIsCiAgICAgICAgInVzZXJu'\
        'YW1lIjogImluc2lnaHRzLXFlIgogICAgfQp9Cn0=", "timestamp": "2020-01-23T16:15:59.478901889Z"}',
     _ERR_JSON_SCHEMA)
]


@pytest.mark.parametrize("msg", _INVALID_MESSAGES)
def test_deserialize_invalid_format_str(msg):
    """Test that passing a malformed message to `deserialize` raises an exception."""
    deserialized = Consumer.deserialize(Consumer(None, None, None), msg[0])
    assert isinstance(deserialized, DataPipelineError)
    assert str(deserialized).startswith(msg[1])


@pytest.mark.parametrize("msg", _INVALID_MESSAGES)
def test_deserialize_invalid_format_bytes(msg):
    """Test that passing a malformed message to `deserialize` raises an exception."""
    deserialized = Consumer.deserialize(Consumer(None, None, None), msg[0].encode("utf-8"))
    assert isinstance(deserialized, DataPipelineError)
    assert str(deserialized).startswith(msg[1])


@pytest.mark.parametrize("msg", _INVALID_MESSAGES)
def test_deserialize_invalid_format_bytearray(msg):
    """Test that passing a malformed message to `deserialize` raises an exception."""
    deserialized = Consumer.deserialize(
        Consumer(None, None, None), bytearray(msg[0].encode("utf-8")))
    assert isinstance(deserialized, DataPipelineError)
    assert str(deserialized).startswith(msg[1])


_VALID_MESSAGES = [
    ('{"url": "",'
     '"b64_identity": "eyJpZGVudGl0eSI6IHsiaW50ZXJuYWwiOiB7Im9yZ19pZCI6ICIxMjM4MzAzMiJ9fX0=",'
     '"timestamp": "2020-01-23T16:15:59.478901889Z"}',
     {
         "url": "",
         "identity": {"identity": {"internal": {"org_id": "12383032"}}},
         "timestamp": "2020-01-23T16:15:59.478901889Z",
         "ClusterName": None
     }),

    ('{"url": "https://s3.com/hash", "unused-property": null, '
     '"b64_identity": "eyJpZGVudGl0eSI6IHsiaW50ZXJuYWwiOiB7Im9yZ19pZCI6ICIxMjM4MzAzMiJ9fX0=",'
     '"timestamp": "2020-01-23T16:15:59.478901889Z"}',
     {
         "url": "https://s3.com/hash",
         "unused-property": None,
         "identity": {"identity": {"internal": {"org_id": "12383032"}}},
         "timestamp": "2020-01-23T16:15:59.478901889Z",
         "ClusterName": None
     }),

    ('{"account":12345678, "url":"any/url", '
     '"b64_identity": "eyJpZGVudGl0eSI6IHsiaW50ZXJuYWwiOiB7Im9yZ19pZCI6ICIxMjM4MzAzMiJ9fX0=",'
     '"timestamp": "2020-01-23T16:15:59.478901889Z"}',
     {
         "account": 12345678,
         "url": "any/url",
         "identity": {"identity": {"internal": {"org_id": "12383032"}}},
         "timestamp": "2020-01-23T16:15:59.478901889Z",
         "ClusterName": None
     }),

    ('{"account":12345678, "url":"any/url", '
     '"b64_identity": "eyJpZGVudGl0eSI6IHsKICAgICJhY2NvdW50X251bWJlciI6ICI2MjEyMzc3IiwKICAgICJhdX'
     'RoX3R5cGUiOiAiYmFzaWMtYXV0aCIsCiAgICAiaW50ZXJuYWwiOiB7CiAgICAgICAgImF1dGhfdGltZSI6IDE0MDAsC'
     'iAgICAgICAgIm9yZ19pZCI6ICIxMjM4MzAzMiIKICAgIH0sCiAgICAidHlwZSI6ICJVc2VyIiwKICAgICJ1c2VyIjog'
     'ewogICAgICAgICJlbWFpbCI6ICJqbmVlZGxlK3FhQHJlZGhhdC5jb20iLAogICAgICAgICJmaXJzdF9uYW1lIjogIkl'
     'uc2lnaHRzIiwKICAgICAgICAiaXNfYWN0aXZlIjogdHJ1ZSwKICAgICAgICAiaXNfaW50ZXJuYWwiOiBmYWxzZSwKIC'
     'AgICAgICAiaXNfb3JnX2FkbWluIjogdHJ1ZSwKICAgICAgICAibGFzdF9uYW1lIjogIlFFIiwKICAgICAgICAibG9jY'
     'WxlIjogImVuX1VTIiwKICAgICAgICAidXNlcm5hbWUiOiAiaW5zaWdodHMtcWUiCiAgICB9Cn0KfQ==",'
     '"timestamp": "2020-01-23T16:15:59.478901889Z"}',
     {
         "account": 12345678,
         "url": "any/url",
         "identity": {"identity": {
             "account_number": "6212377",
             "auth_type": "basic-auth",
             "internal": {
                 "auth_time": 1400,
                 "org_id": "12383032"
             },
             "type": "User",
             "user": {
                 "email": "jneedle+qa@redhat.com",
                 "first_name": "Insights",
                 "is_active": True,
                 "is_internal": False,
                 "is_org_admin": True,
                 "last_name": "QE",
                 "locale": "en_US",
                 "username": "insights-qe"
             }
         }},
         "timestamp": "2020-01-23T16:15:59.478901889Z",
         "ClusterName": None
     }),

    ('{"account":12345678, "url":"any/url", '
     '"b64_identity": "eyJpZGVudGl0eSI6IHsiYWNjb3VudF9udW1iZXIiOiAiNjIxMjM3NyIsICJhdXRoX3R5cGUiOiA'
     'iYmFzaWMtYXV0aCIsICJpbnRlcm5hbCI6IHsiYXV0aF90aW1lIjogMC41NiwgIm9yZ19pZCI6ICIxMjM4MzAzMiJ9LCA'
     'idHlwZSI6ICJVc2VyIiwgInVzZXIiOiB7ImVtYWlsIjogImpuZWVkbGUrcWFAcmVkaGF0LmNvbSIsICJmaXJzdF9uYW1'
     'lIjogIkluc2lnaHRzIiwgImlzX2FjdGl2ZSI6IHRydWUsICJpc19pbnRlcm5hbCI6IGZhbHNlLCAiaXNfb3JnX2FkbWl'
     'uIjogdHJ1ZSwgImxhc3RfbmFtZSI6ICJRRSIsICJsb2NhbGUiOiAiZW5fVVMiLCAidXNlcm5hbWUiOiAiaW5zaWdodHM'
     'tcWUifX19",'
     '"timestamp": "2020-01-23T16:15:59.478901889Z"}',
     {
         "account": 12345678,
         "url": "any/url",
         "identity": {"identity": {
             "account_number": "6212377",
             "auth_type": "basic-auth",
             "internal": {
                 "auth_time": 0.56,
                 "org_id": "12383032"
             },
             "type": "User",
             "user": {
                 "email": "jneedle+qa@redhat.com",
                 "first_name": "Insights",
                 "is_active": True,
                 "is_internal": False,
                 "is_org_admin": True,
                 "last_name": "QE",
                 "locale": "en_US",
                 "username": "insights-qe"
             }
         }},
         "timestamp": "2020-01-23T16:15:59.478901889Z",
         "ClusterName": None
     }),
    ('{"account":"5869752","category":"periodic",'
     '"metadata":{"reporter":"","stale_timestamp":"0001-01-01T00:00:00Z"},'
     '"request_id":"1cafddc658c942be8660ea0341fe8027","principal":"10918904",'
     '"service":"openshift","size":15099,'
     '"url":"https://insights-upload-perma.s3.amazonaws.com/1cafddc658c942be8660ea0341fe8027?'
     'X-Amz-Algorithm=AWS4-HMAC-SHA256\u0026X-Amz-Credential=AKIAJW4PUHKGSOIEEI7A%2F20200313%2F'
     'us-east-1%2Fs3%2Faws4_request\u0026X-Amz-Date=20200313T083008Z\u0026X-Amz-Expires=86400'
     '\u0026X-Amz-SignedHeaders=host\u0026'
     'X-Amz-Signature=0db0ae5569ef7bf5e1eb59d64d8b420c323f43fa0154a6bfb81b8873b1d0e836",'
     '"b64_identity":"eyJlbnRpdGxlbWVudHMiOnt9LCJpZGVudGl0eSI6eyJpbnRlcm5hbCI6eyJhdXRoX3RpbWUiOjAu'
     'Mjk5OTk5OTUyMzE2MjgsIm9yZ19pZCI6IjEwOTE4OTA0In0sImFjY291bnRfbnVtYmVyIjoiNTg2OTc1MiIsImF1dGhf'
     'dHlwZSI6InVoYy1hdXRoIiwic3lzdGVtIjp7ImNsdXN0ZXJfaWQiOiIxODJjMTVkZi02MDE0LTQyZjgtYmRkMC02OGMy'
     'YzViMGI4MWUifSwidHlwZSI6IlN5c3RlbSJ9fQ==",'
     '"timestamp":"2020-03-13T08:30:08.968858699Z"}',
     {
         "account": "5869752",
         "category": "periodic",
         "metadata": {
             "reporter": "",
             "stale_timestamp": "0001-01-01T00:00:00Z",
         },
         "request_id": "1cafddc658c942be8660ea0341fe8027",
         "principal": "10918904",
         "service": "openshift",
         "size": 15099,
         "url": (
             "https://insights-upload-perma.s3.amazonaws.com/1cafddc658c942be8660ea0341fe8027?"
             "X-Amz-Algorithm=AWS4-HMAC-SHA256\u0026X-Amz-Credential=AKIAJW4PUHKGSOIEEI7A%2F"
             "20200313%2Fus-east-1%2Fs3%2Faws4_request\u0026X-Amz-Date=20200313T083008Z\u0026"
             "X-Amz-Expires=86400\u0026X-Amz-SignedHeaders=host\u0026"
             "X-Amz-Signature=0db0ae5569ef7bf5e1eb59d64d8b420c323f43fa0154a6bfb81b8873b1d0e836"),
         "identity": {
             "entitlements": {},
             "identity": {
                 "internal": {
                     "auth_time": 0.29999995231628,
                     "org_id": "10918904"
                 },
                 "account_number": '5869752',
                 "auth_type": "uhc-auth",
                 "system": {
                     "cluster_id": "182c15df-6014-42f8-bdd0-68c2c5b0b81e"
                 },
                 "type": "System"
             },
         },
         "timestamp": "2020-03-13T08:30:08.968858699Z",
         "ClusterName": "182c15df-6014-42f8-bdd0-68c2c5b0b81e"
     })
]


@pytest.mark.parametrize("msg,value", _VALID_MESSAGES)
def test_deserialize_valid_str(msg, value):
    """Test that proper string JSON input messages are correctly deserialized."""
    assert Consumer.deserialize(Consumer(None, None, None), msg) == value


@pytest.mark.parametrize("msg,value", _VALID_MESSAGES)
def test_deserialize_valid_bytes(msg, value):
    """Test that proper bytes JSON input messages are correctly deserialized."""
    assert Consumer.deserialize(Consumer(None, None, None), msg.encode("utf-8")) == value


@pytest.mark.parametrize("msg,value", _VALID_MESSAGES)
def test_deserialize_valid_bytearray(msg, value):
    """Test that proper bytearray JSON input messages are correctly deserialized."""
    assert Consumer.deserialize(Consumer(None, None, None), bytearray(msg.encode("utf-8"))) == value


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
    assert not consumer.handles(mock_consumer_record(value))


_VALID_RECORD_VALUES = [
    {"url": ""},
    {"url": "bucket/file"},
    {"url": "https://a-valid-domain.com/precious_url"}
]


@pytest.mark.parametrize("value", _VALID_RECORD_VALUES)
@patch('insights_messaging.consumers.kafka.Kafka.__init__', lambda *a, **k: None)
def test_handles_valid(value):
    """Test that `Consumer` accepts handling of correctly formatted input messages."""
    sut = Consumer(None, None, None)
    assert sut.handles(mock_consumer_record(value))


@pytest.mark.parametrize("value", _INVALID_RECORD_VALUES)
def test_get_url_invalid(value):
    """Test that `Consumer.get_url` raises the appropriate exception."""
    with pytest.raises(DataPipelineError, match=_REGEX_BAD_SCHEMA):
        Consumer.get_url(None, value)


@pytest.mark.parametrize("value", _VALID_RECORD_VALUES)
def test_get_url_valid(value):
    """Test that `Consumer.get_url` returns the expected value."""
    assert Consumer.get_url(None, mock_consumer_record(value)) == value['url']


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


@pytest.mark.parametrize("topic", _VALID_TOPICS)
@pytest.mark.parametrize("group", _VALID_GROUPS)
@pytest.mark.parametrize("server", _VALID_SERVERS)
def test_consumer_init_direct(topic, group, server):
    """Test of our Consumer constructor, using direct configuration options."""
    with patch('insights_messaging.consumers.kafka.Kafka.__init__') as mock_kafka_init:
        with patch('os.environ', new=dict()):
            Consumer(None, None, None, group, topic, [server])

            mock_kafka_init.assert_called_with(
                None, None, None, topic, group, [server], retry_backoff_ms=1000)
