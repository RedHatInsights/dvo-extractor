# Copyright 2020 Red Hat Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Consumer implementation based on base Kafka class."""

import json
import logging
import base64
import binascii
import time

import jsonschema
from kafka.consumer.fetcher import ConsumerRecord
from insights_messaging.consumers.kafka import Kafka

from controller.data_pipeline_error import DataPipelineError
from controller.schemas import INPUT_MESSAGE_SCHEMA, IDENTITY_SCHEMA

LOG = logging.getLogger(__name__)


class Consumer(Kafka):
    """
    Consumer implementation based on base Kafka class.

    This consumer retrieves a message at a time from a configure source (which is Kafka),
    extracts an URL from it, downloads an archive using the configured downloader, and
    then passes the file to an internal engine for further processing.
    """

    # pylint: disable=too-many-arguments
    def __init__(self, publisher, downloader, engine, group_id=None,
                 incoming_topic=None, bootstrap_servers=None, max_record_age=7200,
                 retry_backoff_ms=1000, **kwargs):
        """Construct a new external data pipeline Kafka consumer."""
        if isinstance(bootstrap_servers, str):
            bootstrap_servers = bootstrap_servers.split(',')

        LOG.info("Consuming topic '%s' from brokers %s as group '%s'",
                 incoming_topic, bootstrap_servers, group_id)

        super().__init__(publisher, downloader, engine, incoming_topic,
                         group_id, bootstrap_servers, retry_backoff_ms=retry_backoff_ms, **kwargs)
        self.max_record_age = max_record_age
        self.log_pattern = f"topic: {incoming_topic}, group_id: {group_id}"

    def deserialize(self, bytes_):
        """
        Deserialize JSON message received from Kafka.

        Returns:
            dict: Deserialized input message if successful.
            DataPipelineError: Exception containing error message if anything failed.

            The exception is returns instead of being thrown in order to prevent
            breaking the message handling / polling loop in `Consumer.run`.
        """
        LOG.debug("Deserializing incoming bytes (%s)", self.log_pattern)

        if isinstance(bytes_, (str, bytes, bytearray)):
            try:
                msg = json.loads(bytes_)
                jsonschema.validate(instance=msg, schema=INPUT_MESSAGE_SCHEMA)
                LOG.debug("JSON schema validated (%s)", self.log_pattern)
                b64_identity = msg["b64_identity"]

                if isinstance(b64_identity, str):
                    b64_identity = b64_identity.encode()

                decoded_identity = json.loads(base64.b64decode(b64_identity))
                jsonschema.validate(instance=decoded_identity, schema=IDENTITY_SCHEMA)
                LOG.debug("Identity schema validated (%s)", self.log_pattern)

                msg["ClusterName"] = decoded_identity.get(
                    "identity", {}).get("system", {}).get("cluster_id", None)

                msg["identity"] = decoded_identity
                del msg["b64_identity"]
                return msg

            except json.JSONDecodeError as ex:
                return DataPipelineError(f"Unable to decode received message: {ex}")

            except jsonschema.ValidationError as ex:
                return DataPipelineError(f"Invalid input message JSON schema: {ex}")

            except binascii.Error as ex:
                return DataPipelineError(f"Base64 encoded identity could not be parsed: {ex}")

        else:
            return DataPipelineError(f"Unexpected input message type: {bytes_.__class__.__name__}")

    def _handles_timestamp_check(self, input_msg):
        if not isinstance(input_msg.timestamp, int):
            LOG.error("Unexpected Kafka record timestamp type (expected 'int', got '%s')(%s)",
                      input_msg.timestamp.__class__.__name__,
                      Consumer.get_stringfied_record(input_msg))
            return False

        # Kafka record timestamp is int64 in milliseconds.
        if (input_msg.timestamp / 1000) < (time.time() - self.max_record_age):
            LOG.debug("Skipping old message (%s)", Consumer.get_stringfied_record(input_msg))
            return False

        return True

    def handles(self, input_msg):
        """Check format of the input message and decide if it can be handled by this consumer."""
        if not isinstance(input_msg, ConsumerRecord):
            LOG.debug("Unexpected input message type (expected 'ConsumerRecord', got %s)(%s)",
                      input_msg.__class__.__name__, Consumer.get_stringfied_record(input_msg))
            self.fire('on_not_handled', input_msg)
            return False

        if isinstance(input_msg.value, DataPipelineError):
            LOG.error("%s (topic: '%s', partition: %d, offset: %d, timestamp: %d)",
                      input_msg.value.format(input_msg), input_msg.topic, input_msg.partition,
                      input_msg.offset, input_msg.timestamp)
            return False

        if not self._handles_timestamp_check(input_msg):
            return False

        # ---- Redundant checks. Already checked by JSON schema in `deserialize`. ----
        # These checks are actually triggered by some of the unit tests for this method.
        if not isinstance(input_msg.value, dict):
            LOG.debug("Unexpected input message value type (expected 'dict', got '%s') (%s)",
                      input_msg.value.__class__.__name__, Consumer.get_stringfied_record(input_msg))
            self.fire('on_not_handled', input_msg)
            return False

        if "url" not in input_msg.value:
            LOG.debug("Input message is missing a 'url' field: %s "
                      "(%s)", input_msg.value, Consumer.get_stringfied_record(input_msg))
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
            LOG.debug("Extracted URL from input message: %s (%s)",
                      url, Consumer.get_stringfied_record(input_msg))
            return url

        # This should never happen, but let's check it just to be absolutely sure.
        # The `handles` method should prevent this from
        # being called if the input message format is wrong.
        except Exception as ex:
            raise DataPipelineError(f"Unable to extract URL from input message: {ex}")

    @staticmethod
    def get_stringfied_record(input_record):
        """Retrieve a string with information about the received record ready to log."""
        return (f"topic: '{input_record.topic}', partition: {input_record.partition}, "
                f"offset: {input_record.offset}, timestamp: {input_record.timestamp}")
