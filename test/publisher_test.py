import unittest
from unittest.mock import MagicMock, patch

from controller.publisher import Publisher


class PublisherTest(unittest.TestCase):
    def test_init(self):
        producer_kwargs = {
            "bootstrap_servers": ['kafka_server1'],
            "client_id": "ccx-data-pipeline"
        }

        with patch('controller.publisher.KafkaProducer') as kafka_producer_mock:
            sut = Publisher(
                outgoing_topic="a topic name", **producer_kwargs
            )

            kafka_producer_mock.assert_called_with(**producer_kwargs)
            self.assertEqual(sut.topic, "a topic name")

    def test_init_no_topic(self):
        producer_kwargs = {
            "bootstrap_servers": ['kafka_server1'],
            "client_id": "ccx-data-pipeline"
        }

        with self.assertRaises(KeyError):
            sut = Publisher(**producer_kwargs)

    def test_publish(self):
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
