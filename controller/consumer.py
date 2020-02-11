"""Consumer implementation based on base Kafka class."""

import os
import json
import logging
import base64

import jsonschema
from kafka.consumer.fetcher import ConsumerRecord
from insights_messaging.consumers.kafka import Kafka

from controller.data_pipeline_error import DataPipelineError
from controller.schemas import INPUT_MESSAGE_SCHEMA

log = logging.getLogger(__name__)


class Consumer(Kafka):
    """
    Consumer implementation based on base Kafka class.

    This consumer retrieves a message at a time from a configure source (which is Kafka),
    extracts an URL from it, downloads an archive using the configured downloader, and
    then passes the file to an internal engine for further processing.
    """

    def __init__(self, publisher, downloader, engine,
                 group_id=None, group_id_env=None,
                 incoming_topic=None, incoming_topic_env=None,
                 bootstrap_servers=None, bootstrap_server_env=None, retry_backoff_ms=1000):
        """Construct a new external data pipeline Kafka consumer."""
        if group_id_env is not None:
            env_group = os.environ.get(group_id_env, None)
            if env_group is None:
                log.warning(f"Ignoring unset group id environment variable "
                            f"'{group_id_env}', falling back to '{group_id}'")
            else:
                group_id = env_group

        if incoming_topic_env is not None:
            env_topic = os.environ.get(incoming_topic_env, None)
            if env_topic is None:
                log.warning(f"Ignoring unset incoming topic environment variable "
                            f"'{incoming_topic_env}', falling back to '{incoming_topic}'")
            else:
                incoming_topic = env_topic

        if bootstrap_server_env is not None:
            env_server = os.environ.get(bootstrap_server_env, None)
            if env_server is None:
                log.warning(f"Ignoring unset bootstrap server environment variable "
                            f"'{bootstrap_server_env}', falling back to {bootstrap_servers}")
            else:
                bootstrap_servers = [env_server]

        log.info(f"Consuming topic '{incoming_topic}' from brokers {bootstrap_servers}"
                 f" as group '{group_id}'")

        super().__init__(publisher, downloader, engine, incoming_topic,
                         group_id, bootstrap_servers, retry_backoff_ms=retry_backoff_ms)

    def deserialize(self, bytes_):
        """Deserialize JSON message received from Kafka."""
        if isinstance(bytes_, (str, bytes, bytearray)):
            try:
                msg = json.loads(bytes_)
                jsonschema.validate(instance=msg, schema=INPUT_MESSAGE_SCHEMA)
                log.debug("JSON schema validated")

                b64_identity = msg["b64_identity"]

                if isinstance(b64_identity, str):
                    b64_identity = b64_identity.encode()

                msg["identity"] = json.loads(base64.b64decode(b64_identity))
                del msg["b64_identity"]
                return msg

            except json.JSONDecodeError as ex:
                log.error(f"Unable to decode received message ({ex}): {bytes_}")
                return None

            except jsonschema.ValidationError as ex:
                log.error(f"Invalid input message JSON schema: {ex}")
                return None

        else:
            log.error(f"Unexpected input message type: {bytes_.__class__.__name__}")
            return None

    def handles(self, input_msg):
        """Check format of the input message and decide if it can be handled by this consumer."""
        if not isinstance(input_msg, ConsumerRecord):
            log.debug("Unexpected input message type "
                      f"(expected 'ConsumerRecord', got {input_msg.__class__.__name__})")
            self.fire('on_not_handled', input_msg)
            return False

        # ---- Redundant checks. Already checked by JSON schema in `deserialize`. ----
        if not isinstance(input_msg.value, dict):
            log.debug("Unexpected input message value type "
                      f"(expected 'dict', got '{input_msg.value.__class__.__name__}')")
            self.fire('on_not_handled', input_msg)
            return False

        if "url" not in input_msg.value:
            log.debug(f"Input message is missing a 'url' field: {input_msg.value}")
            self.fire('on_not_handled', input_msg)
            return False
        # ----------------------------------------------------------------------------

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
