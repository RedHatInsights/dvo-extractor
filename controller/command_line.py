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

import boto3
from insights_messaging.appbuilder import AppBuilder


def parse_args():
    """Parse the command line options and arguments."""
    p = argparse.ArgumentParser()
    p.add_argument("config", help="Application Configuration.")
    return p.parse_args()


def ccx_data_pipeline():
    """Handler for ccx-data-pipeline command."""
    args = parse_args()

    if ('CW_AWS_ACCESS_KEY_ID' in os.environ and
            'CW_AWS_SECRET_ACCESS_KEY' in os.environ and
            'AWS_REGION_NAME' in os.environ):
        boto3.setup_default_session(
            aws_access_key_id=os.environ.get('CW_AWS_ACCESS_KEY_ID'),
            aws_secret_access_key=os.environ.get('CW_AWS_SECRET_ACCESS_KEY'),
            region_name=os.environ.get('AWS_REGION_NAME'))

    with open(args.config) as f:
        AppBuilder(f.read()).build_app().run()
        exit(0)
