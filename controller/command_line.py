"""Command line entry point functions and tooling."""

import argparse
import prometheus_client
from insights_messaging.appbuilder import AppBuilder


def parse_args():
    """Parse the arguments passed to the `main` entry point."""
    p = argparse.ArgumentParser()
    p.add_argument("config", help="Application Configuration.")
    return p.parse_args()


def main():
    """Entry point function handling the command `ccx-data-pipeline`."""
    args = parse_args()

    prometheus_client.start_http_server(8000)
    with open(args.config) as f:
        AppBuilder(f.read()).build_app().run()
