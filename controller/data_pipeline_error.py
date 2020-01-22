"""Module containing the implementation of the `DataPipelineError` exception class."""


class DataPipelineError(Exception):
    """
    Represents a data pipeline exception.

    This should make it easier to differentiate between
    exceptions caused by internal and external code.
    """
