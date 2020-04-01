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
import sys

from insights_messaging.appbuilder import AppBuilder

from controller.logging import setup_watchtower


def parse_args():
    """Parse the command line options and arguments."""
    parser = argparse.ArgumentParser()
    parser.add_argument("config", help="Application Configuration.")
    return parser.parse_args()


def ccx_data_pipeline():
    """Handle for ccx-data-pipeline command."""
    args = parse_args()

    with open(args.config) as file_:
        consumer = AppBuilder(file_.read()).build_app()
        setup_watchtower()
        consumer.run()
        sys.exit(0)
