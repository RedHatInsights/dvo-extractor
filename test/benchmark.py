"""
Benchmarking.

This is intended to be run directly, not using pytest.
"""

import logging
import kafka
import datetime
import os
import random
import string

from app_common_python import LoadedConfig, isClowderEnabled

logging.getLogger().setLevel(logging.INFO)


def test_benchmark_not_ccx_headers(config):
    """Benchmark the time it takes to send `messages_no` messages with a not-ccx header."""
    start_time = datetime.datetime.now()
    producer = kafka.KafkaProducer(bootstrap_servers=config["kafka_url"])

    for i in range(config["messages_no"]):
        producer.send(
            topic=config["ingress_topic"],
            value=bytes(get_message_value(config["message_len"]), "ascii"),
            headers=[("not-ccx", bytes("test", "utf-8"))],
        )

    end_time = datetime.datetime.now()

    duration = end_time - start_time

    logging.log(logging.INFO, f"test_benchmark_not_ccx_headers duration: {duration}")


def get_message_value(size):
    """Generate a random message with size `size`."""
    return "".join(random.choices(string.ascii_uppercase + string.digits, k=size))


if __name__ == "__main__":
    logging.log(logging.INFO, "starting benchmark tests")

    config = {
        "ingress_topic": os.getenv("KAFKA_INGRESS_TOPIC"),
        "kafka_url": os.getenv("KAFKA_BOOTSTRAP_URL"),
        "messages_no": int(os.getenv("MESSAGES_NO")),
        "message_len": int(os.getenv("MESSAGE_SIZE")),
    }

    if isClowderEnabled():
        clowder_broker_config = LoadedConfig.kafka.brokers[0]
        config["kafka_url"] = f"{clowder_broker_config.hostname}:{clowder_broker_config.port}"

    test_benchmark_not_ccx_headers(config)
