"""Module containing unit tests for the `HTTPDownloader` class."""

from unittest.mock import MagicMock, patch

import pytest

from controller.http_downloader import HTTPDownloader
from controller.data_pipeline_error import DataPipelineError


_REGEX_BAD_URL_FORMAT = r'^Invalid URL format: .*'
_INVALID_TYPE_URLS = [
    42,
    2.71,
    True,
    list(),
    dict()
]


@pytest.mark.parametrize("url", _INVALID_TYPE_URLS)
def test_get_invalid_type(url):
    """Test that passing invalid data type to `get` raises an exception."""
    with pytest.raises(TypeError):
        with HTTPDownloader.get(None, url):
            pass


_INVALID_URLS = [
    None,
    "",
    "ftp://server",
    "bucket/file"
]


@pytest.mark.parametrize("url", _INVALID_URLS)
def test_get_invalid_url(url):
    """Test that passing invalid URL to `get` raises an exception."""
    with pytest.raises(DataPipelineError, match=_REGEX_BAD_URL_FORMAT):
        with HTTPDownloader.get(None, url):
            pass


_VALID_URL = "https://zzzzzzzzzzzzzzzzzzzzzzzz.s3.amazonaws.com/aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa"\
    "?X-Amz-Algorithm=AWS4-HMAC-SHA256&X-Amz-Credential="\
    "ZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZ&X-Amz-Date=19700101T000000Z"\
    "&X-Amz-Expires=86400&X-Amz-SignedHeaders=host&X-Amz-Signature="\
    "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa"


@patch('requests.get')
def test_get_valid_url(get_mock):
    """Test that passing a valid URL the `get` method tries to download it."""
    response_mock = MagicMock()
    get_mock.return_value = response_mock
    response_mock.content = b"file content"

    with HTTPDownloader.get(None, _VALID_URL) as filename:
        with open(filename, 'rb') as f:
            file_content = f.read()
            assert file_content == response_mock.content
