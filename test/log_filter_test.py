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

"""Module containing unit tests for the `LogFilter` class."""

from logging import LogRecord
import pytest

from ccx_data_pipeline.log_filter import LogFilter

_MODULES = ["publisher", "consumer"]

_LEVELS = ["ERROR", "DEBUG"]

_LINE_NUMBERS = [1, 42]

_MESSAGES = ["Everything is working correctly", "Something we wrong"]


@pytest.mark.parametrize("module", _MODULES)
@pytest.mark.parametrize("level", _LEVELS)
@pytest.mark.parametrize("lineno", _LINE_NUMBERS)
@pytest.mark.parametrize("msg", _MESSAGES)
def test_log_filter(module, level, lineno, msg):
    """Test that all messages get through the log filter."""
    record = LogRecord(
        f"ccx_data_pipeline.{module}", level, f"{module}.py", lineno, msg, tuple(), Exception(),
    )
    assert LogFilter.filter(None, record) is True
