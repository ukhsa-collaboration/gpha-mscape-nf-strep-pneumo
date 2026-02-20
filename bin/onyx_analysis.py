#!/usr/bin/env python3

"""Script and associated functions to upload analyses to onyx
and add files to s3.
"""

# Imports
import datetime
import json
import logging
import yaml
import os
import sys
import argparse
from pathlib import Path
import pandas as pd
from ast import literal_eval
from onyx import OnyxClient, OnyxConfig, OnyxEnv
from onyx_analysis_helper import onyx_analysis_helper_functions as oa

# Set up onyx config
CONFIG = OnyxConfig(
    domain=os.environ[OnyxEnv.DOMAIN],
    token=os.environ[OnyxEnv.TOKEN],
)

# Functions
# Args and logging
def get_args():
    """Get command line arguments"""
    parser = argparse.ArgumentParser(
        prog="onyx_helper",
        description="""Script with sub-commands to populate onyx analysis
        table and push analysis files to s3.
        """,
    )

    # Set up parsers and sub-parsers
    base_subparser = argparse.ArgumentParser(add_help=False)
    subparsers = parser.add_subparsers(dest = "command", required=True)

    # Add base args shared by all sub-parsers
    base_subparser.add_argument("--climbid", "-i", type=str, required=True, help="Sample ID")
    base_subparser.add_argument(
        "--output", "-o", type=str, required=True, help="Folder to save outputs"
    )
    base_subparser.add_argument(
        "--server",
        "-s",
        type=str,
        required=True,
        choices=["mscape", "synthscape"],
        help="Specify server code is being run on",
    )

    # Add subparsers and specific args for each
    # Onyx write
    onyx_write_subparser = subparsers.add_parser("write", parents=[base_subparser],
                                     help = "Write initial analysis table to onyx")
    onyx_write_subparser.add_argument("--input-json", "-j", type=Path,
                              help="Path to input file with onyx analysis json")

    # s3 push
    s3_subparser = subparsers.add_parser("s3_upload", parents=[base_subparser],
                                    help = "Push analysis files to s3")
    s3_subparser.add_argument("--bucket", "-b", type=Path,
                              help="s3 bucket to push files to")
    s3_subparser.add_argument("--analysis-id", "-a", type=str,
                              help="File containing analysis ID")
    s3_subparser.add_argument("--input-files", "-f", type=str,
                              help="Comma separated list of files to be uploaded to s3")
    # Onyx update
    onyx_update_subparser = subparsers.add_parser("update", parents=[base_subparser],
                                    help = "Update onyx analysis with s3 paths")
    onyx_update_subparser.add_argument("--analysis-id", "-a", type=str,
                              help="File containing analysis ID")
    onyx_update_subparser.add_argument("--input-json", "-j", type=Path,
                              help="Path to file of s3 file locations")

    # Onyx publish
    onyx_publish_subparser = subparsers.add_parser("publish", parents=[base_subparser],
                                    help = "Publish onyx analysis")
    onyx_publish_subparser.add_argument("--analysis-id", "-a", type=str,
                              help="File containing analysis ID")

    return parser.parse_args()


def set_up_logger(stdout_file):
    """Creates logger for component - all logging messages go to stdout
    log file, error messages also go to stderr log. If component runs
    correctly, stderr is empty.
    """
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
    formatter = logging.Formatter("[%(asctime)s] %(levelname)s: %(message)s")

    out_handler = logging.FileHandler(stdout_file, mode="a")
    out_handler.setFormatter(formatter)
    logger.addHandler(out_handler)

    return logger


# Main script
def main():
    "Main function to handle onyx helper commands"
    args = get_args()
    exitcode = 0

    # Set up log file
    log_file = Path(args.output) / f"{args.climbid}.onyx_helper.{args.command}.log.txt"
    set_up_logger(log_file)

    if args.command == "write":
        onyx_analysis = oa.OnyxAnalysis()
        # Read in analysis json
        try:
            onyx_analysis.read_analysis_from_json(args.input_json)
            logging.info("Analysis table successfully read from json: %s", args.input_json)
        except:
            logging.error("Couldn't read analysis from json: %s", args.input_json)
            exitcode = 1
            return exitcode
        # Check correctly formatted
        check_status_list = onyx_analysis.check_analysis_object(publish_analysis=False)
        if any(status for status in check_status_list): # noqa SIM108
            logging.error("Analysis fields read in from json failed checks")
            exitcode = 1
            return exitcode
        # Write to onyx
        analysis_id, exitcode = onyx_analysis.write_analysis_to_onyx(server=args.server,
                                                                     dryrun=True, # Amend to False when ready to run
                                                                     publish_analysis=False)
        if exitcode == 1:
            logging.error("Unsuccessful write to onyx, check logs for details.")
        # Write analysis ID to file
        analysis_id_file = Path(args.output) / f"{args.climbid}.onyx_helper.{args.command}.analysis_id.txt"

        with Path(analysis_id_file).open("w") as file:
            file.write(f"{analysis_id}")

        return exitcode

    elif args.command == "s3_upload":
        pass

    elif args.command == "update":
        pass

    elif args.command == "publish":
        pass

    return exitcode

if __name__ == "__main__":
    sys.exit(main())
