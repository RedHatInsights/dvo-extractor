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

import os
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
    def __init__(self, publisher, downloader, engine,
                 group_id=None, group_id_env=None,
                 incoming_topic=None, incoming_topic_env=None,
                 bootstrap_servers=None, bootstrap_server_env=None, retry_backoff_ms=1000):
        """Construct a new external data pipeline Kafka consumer."""
        if group_id_env is not None:
            env_group = os.environ.get(group_id_env, None)
            if env_group is None:
                LOG.warning("Ignoring unset group id environment variable "
                            "'%s', falling back to '%s'", group_id_env, group_id)
            else:
                group_id = env_group

        if incoming_topic_env is not None:
            env_topic = os.environ.get(incoming_topic_env, None)
            if env_topic is None:
                LOG.warning("Ignoring unset incoming topic environment variable "
                            "'%s', falling back to '%s'", incoming_topic_env, incoming_topic)
            else:
                incoming_topic = env_topic

        if bootstrap_server_env is not None:
            env_server = os.environ.get(bootstrap_server_env, None)
            if env_server is None:
                LOG.warning("Ignoring unset bootstrap server environment variable "
                            "'%s', falling back to %s", bootstrap_server_env, bootstrap_servers)
            else:
                bootstrap_servers = [env_server]

        LOG.info("Consuming topic '%s' from brokers %s as group '%s'",
                 incoming_topic, bootstrap_servers, group_id)

        super().__init__(publisher, downloader, engine, incoming_topic,
                         group_id, bootstrap_servers, retry_backoff_ms=retry_backoff_ms)

    def deserialize(self, bytes_):
        """
        Deserialize JSON message received from Kafka.

        Returns:
            dict: Deserialized input message if successful.
            DataPipelineError: Exception containing error message if anything failed.

            The exception is returns instead of being thrown in order to prevent
            breaking the message handling / polling loop in `Consumer.run`.
        """
        if isinstance(bytes_, (str, bytes, bytearray)):
            try:
                msg = json.loads(bytes_)
                jsonschema.validate(instance=msg, schema=INPUT_MESSAGE_SCHEMA)
                LOG.debug("JSON schema validated")

                b64_identity = msg["b64_identity"]

                if isinstance(b64_identity, str):
                    b64_identity = b64_identity.encode()

                decoded_identity = json.loads(base64.b64decode(b64_identity))
                jsonschema.validate(instance=decoded_identity, schema=IDENTITY_SCHEMA)
                LOG.debug("Identity schema validated")

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

    def handles(self, input_msg):
        """Check format of the input message and decide if it can be handled by this consumer."""
        if not isinstance(input_msg, ConsumerRecord):
            LOG.debug("Unexpected input message type (expected 'ConsumerRecord', got %s)",
                      input_msg.__class__.__name__)
            self.fire('on_not_handled', input_msg)
            return False

        if isinstance(input_msg.value, DataPipelineError):
            LOG.error(input_msg.value.format(input_msg))
            return False

        if not isinstance(input_msg.timestamp, int):
            LOG.error("Unexpected Kafka record timestamp type (expected 'int', got '%s')",
                      input_msg.timestamp.__class__.__name__)
            return False

        # HACK: Skip old record to reduce time required to catch up.
        MAX_RECORD_AGE = 2 * 60 * 60  # 2 hours (in seconds)
        # Kafka record timestamp is int64 in milliseconds.
        if (input_msg.timestamp / 1000) < (time.time() - MAX_RECORD_AGE):
            LOG.debug("Skipping old message (topic: '%s', partition: %d, offset: %d, timestamp: %d)",
                      input_msg.topic, input_msg.partition, input_msg.offset, input_msg.timestamp)
            return False

        # ---- Redundant checks. Already checked by JSON schema in `deserialize`. ----
        if not isinstance(input_msg.value, dict):
            LOG.debug("Unexpected input message value type (expected 'dict', got '%s')",
                      input_msg.value.__class__.__name__)
            self.fire('on_not_handled', input_msg)
            return False

        if "url" not in input_msg.value:
            LOG.debug("Input message is missing a 'url' field: %s", input_msg.value)
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
            LOG.debug("Extracted URL from input message: %s", url)
            return url

        # This should never happen, but let's check it just to be absolutely sure.
        # The `handles` method should prevent this from
        # being called if the input message format is wrong.
        except Exception as ex:
            raise DataPipelineError(f"Unable to extract URL from input message: {ex}")
