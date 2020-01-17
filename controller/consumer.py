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
        # self.dest_bucket = uploader.pop('bucket')

    def deserialize(self, bytes_):
        """
        Deserialize JSON message received from kafka
        """
        return json.loads(bytes_)

    def handles(self, input_msg):
        """
        Depending on the message format created in deserialize,
        we should take decissions about handling or not every input
        message
        """
        return True

    def get_url(self, input_msg):
        """
        Same sa previous 2 methods, when we receive and figure out the
        message format, we can modify this method
        """
        filename = input_msg.key.decode('utf-8')
        log.debug(filename)
        return filename

    def process(self, input_msg):
        try:
            print(input_msg)
        except Exception as ex:
            self.publisher.error(input_msg, ex)
            self.fire("on_consumer_failure", input_msg, ex)
            raise
        finally:
            self.fire("on_consumer_complete", input_msg)


