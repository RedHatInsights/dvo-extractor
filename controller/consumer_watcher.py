"""Module including instrumentation to expose retrieved stats to Prometheus."""

import logging

from insights_messaging.watchers import ConsumerWatcher
from prometheus_client import Counter, start_http_server


log = logging.getLogger(__name__)


class ConsumerWatcher(ConsumerWatcher):
    """A Watcher that stores different Prometheus `Counter`s."""

    def __init__(self, prometheus_port=8000):
        """Create the needed Counter objects and start serving Prometheus stats."""
        super().__init__()
        self._recv_counter = Counter(
            "ccx_consumer_received_counter",
            "Counter of received Kafka messages")
        self._downloaded_counter = Counter(
            "ccx_downloaded_counter",
            "Counter of downloaded items")
        self._processed_counter = Counter(
            "ccx_engine_processed_counter",
            "Counter of files processed by the OCP Engine")
        self._published_counter = Counter(
            "ccx_published_counter",
            "Counter of reports succesfully published")
        self._failures_counter = Counter(
            "ccx_failures_counter",
            "Counter of failures during the pipeline")
        self._not_handling_counter = Counter(
            "ccx_not_handled_counter",
            "Counter of received elements that are not handled by the pipeline")
        start_http_server(prometheus_port)
        log.info(f"ConsumerWatcher created and listening in {prometheus_port}")

    def on_recv(self, input_msg):
        """On received event handler."""
        self._recv_counter.inc()

    def on_download(self, path):
        """On downloaded event handler."""
        self._downloaded_counter.inc()

    def on_process(self, input_msg, result):
        """On processed event handler."""
        self._processed_counter.inc()

    def on_consumer_success(self, input_msg, broker, results):
        """On consumer success event handler."""
        self._published_counter.inc()

    def on_consumer_failure(self, input_msg, ex):
        """On consumer failure event handler."""
        self._failures_counter.inc()

    def on_not_handled(self, input_msg):
        """On not handled messages success event handler."""
        self._not_handling_counter.inc()
