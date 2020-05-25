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


def print_version():
    """Log version information."""
    logger = logging.getLogger(__name__)
    logger.info(
        "Python interpreter version: %d.%d.%d",
        sys.version_info.major,
        sys.version_info.minor,
        sys.version_info.micro,
    )
    logger.info(
        "ccx-data-pipeline version: %s", pkg_resources.get_distribution("ccx-data-pipeline").version
    )


def ccx_data_pipeline():
    """Handle for ccx-data-pipeline command."""
    args = parse_args()

    if args.version:
        logging.basicConfig(format="%(message)s", level=logging.INFO)
        print_version()
        sys.exit(0)

    with open(args.config) as file_:
        app_builder = AppBuilder(file_.read())
        logging_config = app_builder.service["logging"]
        logging.config.dictConfig(logging_config)
        print_version()
        consumer = app_builder.build_app()
        setup_watchtower(logging_config)
        consumer.run()
        sys.exit(0)
