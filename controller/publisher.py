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
            message = json.dumps(response)
            log.debug(f"Sending response to the {self.topic} topic.")
            log.debug(f"Response: {message}")
            self.producer.send(self.topic, message.encode('utf-8'))
        except KeyboardInterrupt:
            self.producer.close()
