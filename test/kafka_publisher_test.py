"""Module for testing the controller.kafka_publisher module."""

import os
import unittest
from unittest.mock import MagicMock, patch

from kafka.consumer.fetcher import ConsumerRecord

from controller.kafka_publisher import KafkaPublisher


def _mock_consumer_record(value):
    """Construct a value-only `ConsumerRecord`."""
    return ConsumerRecord(None, None, None, None, None, None, value, None, None, None, None, None)


class KafkaPublisherTest(unittest.TestCase):
    """Test cases for testing the class KafkaPublisher."""

    def test_init(self):
        """
        Test KafkaPublisher initializer.

        The test mocks the KafkaProducer from kafka module in order
        to avoid real usage of the library
        """
        producer_kwargs = {
            "bootstrap_servers": ['kafka_server1'],
            "outgoing_topic": "a topic name",
            "client_id": "ccx-data-pipeline"
        }

        with patch('controller.kafka_publisher.KafkaProducer') as kafka_producer_mock:
            sut = KafkaPublisher(**producer_kwargs)

            kafka_producer_mock.assert_called_with(
                bootstrap_servers=['kafka_server1'],
                client_id="ccx-data-pipeline")
            self.assertEqual(sut.topic, "a topic name")

    def test_init_environment_vars(self):
        """Test KafkaPublisher initializer with env vars and no topic."""
        producer_kwargs = {
            "bootstrap_server_env": "MY_TEST_SERVER",
            "outgoing_topic_env": "MY_TOPIC",
            "client_id": "ccx-data-pipeline"
        }

        os.environ["MY_TEST_SERVER"] = "kafka_server1"
        os.environ["MY_TOPIC"] = "a topic name"

        with patch('controller.kafka_publisher.KafkaProducer') as kafka_producer_mock:
            sut = KafkaPublisher(**producer_kwargs)
            kafka_producer_mock.assert_called_with(
                bootstrap_servers=["kafka_server1"],
                client_id="ccx-data-pipeline")
            self.assertEqual(sut.topic, "a topic name")

    def test_init_both(self):
        """Test KafkaPublisher initializer with both env vars and values."""
        producer_kwargs = {
            "bootstrap_servers": ["another_kafkaserver"],
            "bootstrap_server_env": "MY_TEST_SERVER",
            "outgoing_topic": "another_topic",
            "outgoing_topic_env": "MY_TOPIC",
            "client_id": "ccx-data-pipeline"
        }

        os.environ["MY_TEST_SERVER"] = "kafka_server1"
        os.environ["MY_TOPIC"] = "a topic name"

        with patch('controller.kafka_publisher.KafkaProducer') as kafka_producer_mock:
            sut = KafkaPublisher(**producer_kwargs)
            kafka_producer_mock.assert_called_with(
                bootstrap_servers=["kafka_server1"],
                client_id="ccx-data-pipeline")
            self.assertEqual(sut.topic, "a topic name")

    def test_init_no_topic(self):
        """Test KafkaPublisher initializer without outgoing topic."""
        producer_kwargs = {
            "bootstrap_servers": ['kafka_server1'],
            "client_id": "ccx-data-pipeline"
        }

        with self.assertRaises(KeyError):
            _ = KafkaPublisher(**producer_kwargs)

    # pylint: disable=no-self-use
    def test_publish(self):
        """
        Test Producer.publish method.

        The kafka.KafkaProducer class is mocked in order to avoid the usage
        of the real library
        """
        producer_kwargs = {
            "bootstrap_servers": ['kafka_server1'],
            "client_id": "ccx-data-pipeline"
        }

        topic_name = "KAFKATOPIC"
        values = {
            "ClusterName": "the cluster name",
            "identity": {"identity": {"internal": {"org_id": "5000"}}},
            "timestamp": "2020-01-23T16:15:59.478901889Z"
        }
        input_msg = _mock_consumer_record(values)
        message_to_publish = '{"key1": "value1"}'
        expected_message = (
            b'{"OrgID": 5000, "ClusterName": "the cluster name", '
            b'"Report": {"key1": "value1"}, "LastChecked": "2020-01-23T16:15:59.478901889Z"}\n')

        with patch('controller.kafka_publisher.KafkaProducer') as kafka_producer_init_mock:
            producer_mock = MagicMock()
            kafka_producer_init_mock.return_value = producer_mock

            sut = KafkaPublisher(
                outgoing_topic=topic_name, **producer_kwargs
            )

            sut.publish(input_msg, message_to_publish)
            producer_mock.send.assert_called_with(topic_name, expected_message)
