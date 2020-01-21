"""Consumer implementation based on base Kafka class."""

import json
import logging
from insights_messaging.consumers.kafka import Kafka

log = logging.getLogger(__name__)


class Consumer(Kafka):
    """
    Consumer implementation based on base Kafka class.

    This consumer retrieves a message at a time from a configure source (which is Kafka),
    extracts an URL from it, downloads an archive using the configured downloader, and
    then passes the file to an internal engine for further processing.
    """

    def __init__(self,
                 publisher,
                 downloader,
                 engine,
                 incoming_topic,
                 group_id,
                 bootstrap_servers,
                 retry_backoff_ms=1000,
                 uploader={}):
        """Construct an instance of Consumer class."""
        super().__init__(publisher, downloader, engine, incoming_topic, group_id,
                         bootstrap_servers, retry_backoff_ms)

    def deserialize(self, bytes_):
        """Deserialize JSON message received from kafka."""
        try:
            return json.loads(bytes_)

        except json.JSONDecodeError:
            log.error(f"Unable to decode received message: {bytes_}")

    def handles(self, input_msg):
        """
        Handle all messages received from Kafka.

        Depending on the message format created in deserialize,
        we should take decissions about handling or not every input
        message.
        """
        return input_msg.value is not None

    def get_url(self, input_msg):
        """
        Retrieve URL to storage (S3/Minio) from Kafka message.

        Same as previous 2 methods, when we receive and figure out the
        message format, we can modify this method
        """
        url = input_msg.value.get('url', '')
        log.debug(url)
        return url
