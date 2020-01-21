import os

from contextlib import contextmanager
from tempfile import NamedTemporaryFile

from minio import Minio
from minio.error import ResponseError

from controller.data_pipeline_error import DataPipelineError

import logging


log = logging.getLogger(__name__)


class MinioDownloader:
    """
    Downloader for Minio S3 storage
    """
    def __init__(self, endpoint=None, access_key=None, secret_key=None,
                 access_key_env=None, secret_key_env=None, secure=True):

        if access_key_env is not None and secret_key_env is not None:
            # Use environment vars
            access_key = os.environ.get(access_key_env, access_key)
            secret_key = os.environ.get(secret_key_env, secret_key)

        self.minioClient = Minio(endpoint,
            access_key=access_key,
            secret_key=secret_key,
            secure=secure)

    @contextmanager
    def get(self, src):
        """
        Get a file from Minio S3 server for an specified path and store it
        into a temporary file
        """

        # Make sure the file URL has the correct format
        # Format: <bucket name>/<file name>
        if src is None or src.count("/") != 1:
            raise DataPipelineError(f"Invalid URL format: {src}")

        bucket, obj = src.split("/")

        try:
            data = self.minioClient.get_object(bucket, obj)
            with NamedTemporaryFile() as file_data:
                for d in data.stream(32*1024):
                    file_data.write(d)
                file_data.flush()
                yield file_data.name

        except ResponseError as err:
            log.error(f"Error getting the file {src}: {err}")
