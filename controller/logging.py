# Copyright 2020 Red Hat Inc.
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

"""Submodule to configure logging stuff that cannot be afford from configuration file."""

import logging
import os

from boto3.session import Session
from watchtower import CloudWatchLogHandler


def setup_watchtower():
    """Setups the CloudWatch handler if the proper configuration is provided."""
    aws_config_vars = ("CW_AWS_ACCESS_KEY_ID",
                       "CW_AWS_SECRET_ACCESS_KEY",
                       "AWS_REGION_NAME",
                       "CW_LOG_GROUP",
                       "CW_STREAM_NAME")

    if any(key not in os.environ for key in aws_config_vars):
        return

    session = Session(
        aws_access_key_id=os.environ["CW_AWS_ACCESS_KEY_ID"],
        aws_secret_access_key=os.environ["CW_AWS_SECRET_ACCESS_KEY"],
        region_name=os.environ["AWS_REGION_NAME"])
    root_logger = logging.getLogger()
    handler = CloudWatchLogHandler(
        boto3_session=session,
        log_group=os.environ["CW_LOG_GROUP"],
        stream_name=os.environ["CW_STREAM_NAME"])
    root_logger.addHandler(handler)
