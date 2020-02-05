"""Module including instrumentation to expose retrieved stats to Prometheus."""

import logging

from insights_messaging.watchers import ConsumerWatcher
from prometheus_client import Counter, start_http_server, REGISTRY


log = logging.getLogger(__name__)


class ConsumerWatcher(ConsumerWatcher):
    """A Watcher that stores different Prometheus `Counter`s."""

    def __init__(self, prometheus_port=8000):
        """Create the needed Counter objects and start serving Prometheus stats."""
        super().__init__()
        self._recv_total = Counter(
            "ccx_consumer_received_total",
            "Counter of received Kafka messages")
        self._downloaded_total = Counter(
            "ccx_downloaded_total",
            "Counter of downloaded items")
        self._processed_total = Counter(
            "ccx_engine_processed_total",
            "Counter of files processed by the OCP Engine")
        self._published_total = Counter(
            "ccx_published_total",
            "Counter of reports succesfully published")
        self._failures_total = Counter(
            "ccx_failures_total",
            "Counter of failures during the pipeline")
        self._not_handling_total = Counter(
            "ccx_not_handled_total",
            "Counter of received elements that are not handled by the pipeline")
        start_http_server(prometheus_port)
        log.info(f"ConsumerWatcher created and listening in {prometheus_port}")

    def on_recv(self, input_msg):
        """On received event handler."""
        self._recv_total.inc()

    def on_download(self, path):
        """On downloaded event handler."""
        self._downloaded_total.inc()

    def on_process(self, input_msg, result):
        """On processed event handler."""
        self._processed_total.inc()

    def on_consumer_success(self, input_msg, broker, results):
        """On consumer success event handler."""
        self._published_total.inc()

    def on_consumer_failure(self, input_msg, ex):
        """On consumer failure event handler."""
        self._failures_total.inc()

    def on_not_handled(self, input_msg):
        """On not handled messages success event handler."""
        self._not_handling_total.inc()

    def __del__(self):
        """Destructor for handling counters unregistering."""
        REGISTRY.unregister(self._recv_total)
        REGISTRY.unregister(self._downloaded_total)
        REGISTRY.unregister(self._processed_total)
        REGISTRY.unregister(self._published_total)
        REGISTRY.unregister(self._failures_total)
        REGISTRY.unregister(self._not_handling_total)
