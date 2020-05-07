"""Module with utilities for the tests."""

import time

from kafka.consumer.fetcher import ConsumerRecord


def mock_consumer_record(value):
    """Construct a value-only `ConsumerRecord`."""
    return ConsumerRecord(None, None, None, int((time.time() * 1000) - 60),
                          None, None, value, None, None, None, None, None)
