"""Module containing unit tests for the `ConsumerWatcher` class."""

from unittest.mock import patch

import pytest

from ccx_data_pipeline.watchers.stats_watcher import StatsWatcher


_INVALID_PORTS = [
    None,
    '8000',
    8000.0,
    80,
    70000
]


@pytest.mark.parametrize("value", _INVALID_PORTS)
def test_stats_watcher_initialize_invalid_port(value):
    """Test passing invalid data types or values to the `StatsWatcher` initializer fails."""
    with pytest.raises((TypeError, PermissionError, OverflowError)):
        _ = StatsWatcher(value)


_VALID_PORTS = [
    dict(),
    {"prometheus_port": 9500}
]


@pytest.mark.parametrize("value", _VALID_PORTS)
@patch('ccx_data_pipeline.watchers.stats_watcher.start_http_server')
def test_stats_watcher_initialize(start_http_server_mock, value):
    """Test valid values in the initialize `StatsWatcher`."""
    StatsWatcher(**value)
    port = value.get("prometheus_port", 8000)  # 8000 is the default value
    start_http_server_mock.assert_called_with(port)
