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
import sys

from insights_messaging.appbuilder import AppBuilder
import pkg_resources

from ccx_data_pipeline.logging import setup_watchtower


def parse_args():
    """Parse the command line options and arguments."""
    parser = argparse.ArgumentParser()
    parser.add_argument("config", nargs="?", help="Application Configuration.")
    parser.add_argument("--version", help="Show version", action="store_true")
    return parser.parse_args()


def print_version(use_stdout=False):
    """Log version information."""
    if use_stdout:
        show_func = print

    else:
        show_func = logging.info

    show_func(
        "Python interpreter version: {}.{}.{}".format(
            sys.version_info.major, sys.version_info.minor, sys.version_info.micro
        )
    )
    show_func(
        "ccx-data-pipeline version: {}".format(
            pkg_resources.get_distribution("ccx-data-pipeline").version
        )
    )


def ccx_data_pipeline():
    """Handle for ccx-data-pipeline command."""
    args = parse_args()

    if args.version:
        print_version(use_stdout=True)
        sys.exit(0)

    with open(args.config) as file_:
        app_builder = AppBuilder(file_.read())
        logging_config = app_builder.service["logging"]
        consumer = app_builder.build_app()
        setup_watchtower(logging_config)
        print_version()
        consumer.run()
        sys.exit(0)
