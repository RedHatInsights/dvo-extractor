"""Module containing the implementation of the `DataPipelineError` exception class."""


class DataPipelineError(Exception):
    """
    Represents a data pipeline exception.

    This should make it easier to differentiate between
    exceptions caused by internal and external code.
    """

    def __init__(self, *args, **kwargs):
        """Construct a new data pipeline exception instance."""
        super().__init__(*args, **kwargs)
