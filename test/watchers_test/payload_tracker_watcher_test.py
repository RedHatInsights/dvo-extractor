"""Module containing unit tests for the `ConsumerWatcher` class."""

from unittest.mock import MagicMock, patch

import pytest
from freezegun import freeze_time

from controller.watchers.payload_tracker_watcher import PayloadTrackerWatcher

from ..utils import mock_consumer_record


_INVALID_SERVERS = [
    None,
    [],
    {},
    100,
    100.5,
    "kafka_instance",
]

_INVALID_TOPICS = [
    None,
    [],
    {},
    "",
]


def _prepare_kafka_mock(producer_init_mock):
    """Create a producer mock from its mocked initialization."""
    producer_mock = MagicMock()
    producer_init_mock.return_value = producer_mock
    return producer_mock


@pytest.mark.parametrize("bootstrap_value", _INVALID_SERVERS)
@pytest.mark.parametrize("topic_value", _INVALID_TOPICS)
def test_payload_tracker_watcher_invalid_initialize_invalid_servers(bootstrap_value, topic_value):
    """Test passing invalid data types or values to the `PayloadTrackerWatcher` initializer."""
    with pytest.raises((TypeError, PermissionError, OverflowError, KeyError)):
        _ = PayloadTrackerWatcher(bootstrap_value, topic_value)


@freeze_time("2020-05-07T14:00:00")
def test_payload_tracker_watcher_publish_status():
    """Test publish_status method sends the expected value to Kafka."""
    mocked_values = {
        "request_id": "some request id"
    }
    mocked_input_message = mock_consumer_record(mocked_values)

    with patch("controller.watchers.payload_tracker_watcher.KafkaProducer") as producer_init_mock:
        producer_mock = _prepare_kafka_mock(producer_init_mock)
        sut = PayloadTrackerWatcher(["bootstrap_server"], "valid_topic")
        sut.on_recv(mocked_input_message)
        producer_mock.send.assert_called_with(
            "valid_topic",
            b'{"service": "ccx-data-pipeline", "request_id": "some request id", '
            b'"status": "received", "date": "2020-05-07T14:00:00"}')
