"""Module containing the implementation of the `DataPipelineError` exception class."""


class DataPipelineError(Exception):
    """
    Represents a data pipeline exception.

    This should make it easier to differentiate between
    exceptions caused by internal and external code.
    """

    def format(self, input_msg):
        """Format the error by adding information about input Kafka message."""
        return (f"Status: Error; "
                f"Topic: {input_msg.topic}; "
                f"Partition: {input_msg.partition}; "
                f"Offset: {input_msg.offset}; "
                f"Cause: {self}")
