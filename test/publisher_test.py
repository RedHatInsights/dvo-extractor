"""Module for testing the controller.publisher module."""

import os
import unittest
from unittest.mock import MagicMock, patch

from controller.publisher import Publisher


class PublisherTest(unittest.TestCase):
    """Test cases for testing the class Publisher."""

    def test_init(self):
        """
        Test Publisher initializer.

        The test mocks the KafkaProducer from kafka module in order
        to avoid real usage of the library
        """
        producer_kwargs = {
            "bootstrap_servers": ['kafka_server1'],
            "outgoing_topic": "a topic name",
            "client_id": "ccx-data-pipeline"
        }

        with patch('controller.publisher.KafkaProducer') as kafka_producer_mock:
            sut = Publisher(**producer_kwargs)

            kafka_producer_mock.assert_called_with(
                bootstrap_servers=['kafka_server1'],
                client_id="ccx-data-pipeline")
            self.assertEqual(sut.topic, "a topic name")

    def test_init_environment_vars(self):
        """Test Publisher initializer with env vars and no topic."""
        producer_kwargs = {
            "bootstrap_server_env": "MY_TEST_SERVER",
            "outgoing_topic_env": "MY_TOPIC",
            "client_id": "ccx-data-pipeline"
        }

        os.environ["MY_TEST_SERVER"] = "kafka_server1"
        os.environ["MY_TOPIC"] = "a topic name"

        with patch('controller.publisher.KafkaProducer') as kafka_producer_mock:
            sut = Publisher(**producer_kwargs)
            kafka_producer_mock.assert_called_with(
                bootstrap_servers=["kafka_server1"],
                client_id="ccx-data-pipeline")
            self.assertEqual(sut.topic, "a topic name")

    def test_init_both(self):
        """Test Publisher initializer with both env vars and values."""
        producer_kwargs = {
            "bootstrap_servers": ["another_kafkaserver"],
            "bootstrap_server_env": "MY_TEST_SERVER",
            "outgoing_topic": "another_topic",
            "outgoing_topic_env": "MY_TOPIC",
            "client_id": "ccx-data-pipeline"
        }

        os.environ["MY_TEST_SERVER"] = "kafka_server1"
        os.environ["MY_TOPIC"] = "a topic name"

        with patch('controller.publisher.KafkaProducer') as kafka_producer_mock:
            sut = Publisher(**producer_kwargs)
            kafka_producer_mock.assert_called_with(
                bootstrap_servers=["kafka_server1"],
                client_id="ccx-data-pipeline")
            self.assertEqual(sut.topic, "a topic name")

    def test_init_no_topic(self):
        """Test Publisher initializer without outgoing topic."""
        producer_kwargs = {
            "bootstrap_servers": ['kafka_server1'],
            "client_id": "ccx-data-pipeline"
        }

        with self.assertRaises(KeyError):
            _ = Publisher(**producer_kwargs)

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
        message_to_publish = '{"key1": "value1"}'
        expected_message = b'{"key1": "value1"}\n'

        with patch('controller.publisher.KafkaProducer') as kafka_producer_init_mock:
            producer_mock = MagicMock()
            kafka_producer_init_mock.return_value = producer_mock

            sut = Publisher(
                outgoing_topic=topic_name, **producer_kwargs
            )

            sut.publish(None, message_to_publish)
            producer_mock.send.assert_called_with(topic_name, expected_message)
