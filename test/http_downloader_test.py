# Copyright 2020 Red Hat, Inc
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Module containing unit tests for the `HTTPDownloader` class."""

from unittest.mock import MagicMock, patch

import pytest

from ccx_data_pipeline.http_downloader import HTTPDownloader
from ccx_data_pipeline.data_pipeline_error import DataPipelineError


_REGEX_BAD_URL_FORMAT = r"^Invalid URL format: .*"
_INVALID_TYPE_URLS = [42, 2.71, True, list(), dict()]


@pytest.mark.parametrize("url", _INVALID_TYPE_URLS)
def test_get_invalid_type(url):
    """Test that passing invalid data type to `get` raises an exception."""
    with pytest.raises(TypeError):
        sut = HTTPDownloader()
        with sut.get(url):
            pass


_INVALID_URLS = [None, "", "ftp://server", "bucket/file"]


@pytest.mark.parametrize("url", _INVALID_URLS)
def test_get_invalid_url(url):
    """Test that passing invalid URL to `get` raises an exception."""
    with pytest.raises(DataPipelineError, match=_REGEX_BAD_URL_FORMAT):
        sut = HTTPDownloader()
        with sut.get(url):
            pass


_VALID_URLS = [
    "https://zzzzzzzzzzzzzzzzzzzzzzzz.s3.amazonaws.com/aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa"
    "?X-Amz-Algorithm=AWS4-HMAC-SHA256&X-Amz-Credential="
    "ZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZ&X-Amz-Date=19700101T000000Z"
    "&X-Amz-Expires=86400&X-Amz-SignedHeaders=host&X-Amz-Signature="
    "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa",
    "https://insights-dev-upload-perm.s3.amazonaws.com/upload-service-1-48nb7/gPRz2EdWpr-000144"
    "?X-Amz-Algorithm=AWS4-HMAC-SHA256&X-Amz-Credential=AKIAJW4PUHKGSOIEEI7A%2F20200311%2F"
    "us-east-1%2Fs3%2Faws4_request&X-Amz-Date=20200311T080728Z&X-Amz-Expires=86400&"
    "X-Amz-SignedHeaders=host&"
    "X-Amz-Signature=d345738105796fd81e3e643cf9cf86067956c0cd0783b3a69cd0268566f108a4 ",
    "http://minio:9000/insights-upload-perma/hpe-dl380pgen8-02-vm-9.hpe2.lab.eng.bos.redhat.com/"
    "Z0ThU1Jyxc-000004?X-Amz-Algorithm=AWS4-HMAC-SHA256&"
    "X-Amz-Credential=BQA2GEXO711FVBVXDWKM%2F20200520%2Fus-east-1%2Fs3%2Faws4_request&"
    "X-Amz-Date=20200520T140918Z&X-Amz-Expires=86400&X-Amz-SignedHeaders=host&"
    "X-Amz-Signature=39f482f7650c6c65ed7e182d512a8fc3420b9a0d34292814be713258cbc24f04",
]


@patch("requests.get")
@pytest.mark.parametrize("url", _VALID_URLS)
def test_get_valid_url(get_mock, url):
    """Test that passing a valid URL the `get` method tries to download it."""
    response_mock = MagicMock()
    get_mock.return_value = response_mock
    response_mock.content = b"file content"
    sut = HTTPDownloader()

    with sut.get(url) as filename:
        with open(filename, "rb") as file_desc:
            file_content = file_desc.read()
            assert file_content == response_mock.content
