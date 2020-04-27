# Copyright 2019, 2020 Red Hat Inc.
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

"""Module that implements a custom Kafka publisher."""

import logging

import json
from kafka import KafkaProducer
from insights_messaging.publishers import Publisher

from controller.data_pipeline_error import DataPipelineError

LOG = logging.getLogger(__name__)


class KafkaPublisher(Publisher):
    """
    KafkaPublisher based on the base Kafka publisher.

    The results of the data analysis are received as a JSON (string)
    and turned into a byte array using UTF-8 encoding.
    The bytes are then sent to the output Kafka topic.

    Custom error handling for the whole pipeline is implemented here.
    """

    def __init__(self, outgoing_topic, bootstrap_servers, **kwargs):
        """Construct a new `KafkaPublisher` given `kwargs` from the config YAML."""
        self.topic = outgoing_topic
        self.bootstrap_servers = bootstrap_servers

        if self.topic is None:
            raise KeyError('outgoing_topic')

        self.producer = KafkaProducer(bootstrap_servers=self.bootstrap_servers, **kwargs)
        LOG.info("Producing to topic '%s' on brokers %s",
                 self.topic, self.bootstrap_servers)

    def publish(self, input_msg, response):
        """
        Publish an EOL-terminated JSON message to the output Kafka topic.

        The response is assumed to be a string representing a valid JSON object.
        A newline character will be appended to it, it will be converted into
        a byte array using UTF-8 encoding and the result of that will be sent
        to the producer to produce a message in the output Kafka topic.
        """
        try:
            # Flush kafkacat buffer.
            # Response is already a string, no need to JSON dump.
            org_id = input_msg.value["identity"]["identity"]["internal"]["org_id"]
            msg_timestamp = input_msg.value["timestamp"]
            output_msg = {
                "OrgID": int(org_id),
                "ClusterName": input_msg.value["ClusterName"],
                "Report": json.loads(response),
                "LastChecked": msg_timestamp
            }

            message = json.dumps(output_msg) + "\n"

            LOG.debug("Sending response to the %s topic.", self.topic)
            # Convert message string into a byte array.
            self.producer.send(self.topic, message.encode('utf-8'))
            LOG.debug("Message has been sent successfully.")
            LOG.debug("Message context: OrgId=%s, ClusterName=\"%s\", LastChecked=\"%s\"",
                      output_msg["OrgID"], output_msg["ClusterName"], output_msg["LastChecked"])

            LOG.info("Status: Success; "
                     "Topic: %s; "
                     "Partition: %s; "
                     "Offset: %s; "
                     "LastChecked: %s",
                     input_msg.topic, input_msg.partition, input_msg.offset, msg_timestamp)

        except UnicodeEncodeError:
            raise DataPipelineError(f"Error encoding the response to publish: {message}")

        except ValueError:
            raise DataPipelineError(f"Error extracting the OrgID: {org_id}")

    def error(self, input_msg, ex):
        """Handle pipeline errors by logging them."""
        # The super call is probably unnecessary because the default behavior
        # is to do nothing, but let's call it in case it ever does anything.
        super().error(input_msg, ex)

        if not isinstance(ex, DataPipelineError):
            ex = DataPipelineError(ex)

        LOG.error(ex.format(input_msg))
