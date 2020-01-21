import json
import logging
from insights_messaging.consumers.kafka import Kafka

log = logging.getLogger(__name__)

class Consumer(Kafka):
    def __init__(self,
                 publisher,
                 downloader,
                 engine,
                 incoming_topic,
                 group_id,
                 bootstrap_servers,
                 retry_backoff_ms=1000,
                 uploader={}):
        super().__init__(publisher, downloader, engine, incoming_topic, group_id,
                         bootstrap_servers, retry_backoff_ms)

    def deserialize(self, bytes_):
        """
        Deserialize JSON message received from kafka
        """

        try:
            return json.loads(bytes_)

        except json.JSONDecodeError:
            log.error(f"Unable to decode received message: {bytes_}")

    def handles(self, input_msg):
        """
        Depending on the message format created in deserialize,
        we should take decissions about handling or not every input
        message
        """
        return input_msg.value is not None

    def get_url(self, input_msg):
        """
        Same sa previous 2 methods, when we receive and figure out the
        message format, we can modify this method
        """
        url = input_msg.value.get('url', '')
        log.debug(url)
        return url
