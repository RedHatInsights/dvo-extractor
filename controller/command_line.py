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

"""command_line submodule includes the handlers for CLI commands."""

import argparse
import logging
import os

from insights_messaging.appbuilder import AppBuilder
from boto3.session import Session
from watchtower import CloudWatchLogHandler


def parse_args():
    """Parse the command line options and arguments."""
    p = argparse.ArgumentParser()
    p.add_argument("config", help="Application Configuration.")
    return p.parse_args()


def ccx_data_pipeline():
    """Handler for ccx-data-pipeline command."""
    args = parse_args()

    aws_session = Session(
        aws_access_key_id=os.environ.get('CWS_AWS_ACCESS_KEY_ID'),
        aws_secret_access_key=os.environ.get('CWS_AWS_SECRET_ACCESS_KEY'),
        region_name=os.environ.get('AWS_REGION_NAME'))
    cloudwatch_handler = CloudWatchLogHandler(
        boto3_session=aws_session,
        log_group=os.environ.get('CWS_LOG_GROUP'),
        stream_name=os.environ.get('CWS_STREAM_NAME'))
    root_logger = logging.getLogger()
    root_logger.addHandler(cloudwatch_handler)

    with open(args.config) as f:
        AppBuilder(f.read()).build_app().run()
