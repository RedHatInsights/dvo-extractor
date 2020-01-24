"""Module that defines a Downloader object to get HTTP urls."""

import os
import logging
import re
from contextlib import contextmanager
from tempfile import NamedTemporaryFile

import requests

from controller.data_pipeline_error import DataPipelineError


log = logging.getLogger(__name__)


class HTTPDownloader:
    """Downloader for HTTP uris."""

    HTTP_RE = r"https?://(.+)"

    @contextmanager
    def get(self, src):
        """Download a file from HTTP server and store it in a temporary file."""
        if src is None or not re.match(HTTPDownloader.HTTP_RE, src):
            raise DataPipelineError(f"Invalid URL format: {src}")

        try:
            request = requests.get(src)
            data = request.content
            with NamedTemporaryFile() as file_data:
                file_data.write(data)
                file_data.flush()
                yield file_data.name

        except requests.exceptions.ConnectionError as err:
            log.error(f"Error getting the file {src}: {err}")
            raise err
