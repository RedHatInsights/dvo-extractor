"""Module containing the LogFilter class used for log filtering."""

import logging


class LogFilter(logging.Filter):
    """Class that implements the `filter` function for log filtering."""

    def filter(self, record):
        """Determine whether a message should be logged or not."""
        return True
