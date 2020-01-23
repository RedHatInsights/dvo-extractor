"""Consumer implementation based on base Kafka class."""

import json
import logging
from kafka.consumer.fetcher import ConsumerRecord
from insights_messaging.consumers.kafka import Kafka

from controller.data_pipeline_error import DataPipelineError

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
        """Deserialize JSON message received from Kafka."""
        if isinstance(bytes_, bytearray):
            try:
                return json.loads(bytes_)
            except json.JSONDecodeError as ex:
                raise DataPipelineError(f"Unable to decode received message ({ex}): {bytes_}")
        else:
            raise DataPipelineError(f"Unexpected input message type: {bytes_.__class__.__name__}")

    def handles(self, input_msg):
        """Check format of the input message and decide if it can be handled by this consumer."""
        if not isinstance(input_msg, ConsumerRecord):
            log.debug("Unexpected input message type " +
                      f"(expected 'ConsumerRecord', got {input_msg.__class__.__name__})")
            return False

        if not isinstance(input_msg.value, dict):
            log.debug("Unexpected input message value type " +
                      f"(expected 'dict', got '{input_msg.value.__class__.__name__}')")
            return False

        if "url" not in input_msg.value:
            log.debug(f"Input message is missing a 'url' field: {input_msg.value}")
            return False

        return True

    def get_url(self, input_msg):
        """
        Retrieve URL to storage (S3/Minio) from Kafka message.

        Same as previous 2 methods, when we receive and figure out the
        message format, we can modify this method
        """
        try:
            url = input_msg.value["url"]
            log.debug(f"Extracted URL from input message: {url}")
            return url

        # This should never happen, but let's check it just to be absolutely sure.
        # The `handles` method should prevent this from
        # being called if the input message format is wrong.
        except Exception as ex:
            raise DataPipelineError(f"Unable to extract URL from input message: {ex}")
