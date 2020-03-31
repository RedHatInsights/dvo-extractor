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
import os
import sys

import boto3
from insights_messaging.appbuilder import AppBuilder


def parse_args():
    """Parse the command line options and arguments."""
    parser = argparse.ArgumentParser()
    parser.add_argument("config", help="Application Configuration.")
    return parser.parse_args()


def ccx_data_pipeline():
    """Handle for ccx-data-pipeline command."""
    args = parse_args()

    aws_config_vars = ('CW_AWS_ACCESS_KEY_ID', 'CW_AWS_SECRET_ACCESS_KEY', 'AWS_REGION_NAME')
    if all(key in os.environ for key in aws_config_vars):
        boto3.setup_default_session(
            aws_access_key_id=os.environ.get('CW_AWS_ACCESS_KEY_ID'),
            aws_secret_access_key=os.environ.get('CW_AWS_SECRET_ACCESS_KEY'),
            region_name=os.environ.get('AWS_REGION_NAME'))

    with open(args.config) as file_:
        AppBuilder(file_.read()).build_app().run()
        sys.exit(0)
