import logging
import json
from kafka import KafkaProducer
from insights_messaging.publishers import Publisher

log = logging.getLogger(__name__)


class Publisher(Publisher):
    def __init__(self, **kwargs):
        self.topic = kwargs.pop('outgoing_topic')
        self.producer = KafkaProducer(**kwargs)

    def publish(self, input_msg, response):
        try:
            # Flush kafkacat buffer.
            # Response is already a string, no need to JSON dump.
            message = response + "\n"
            log.debug(f"Sending response to the {self.topic} topic.")
            # Convert message string into a byte array.
            self.producer.send(self.topic, message.encode('utf-8'))
            log.debug("Message has been sent successfully.")
        except KeyboardInterrupt:
            self.producer.close()
