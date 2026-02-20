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
                              help="Analysis ID for analysis table")
    s3_subparser.add_argument("--input-json", "-j", type=Path, 
                              help="Path to files to be uploaded to s3")
    # Onyx update
    onyx_update_subparser = subparsers.add_parser("update", parents=[base_subparser],
                                    help = "Update onyx analysis with s3 paths")
    onyx_update_subparser.add_argument("--analysis-id", "-a", type=str, 
                              help="Analysis ID for analysis table")
    onyx_update_subparser.add_argument("--input-files", "-f", type=Path, 
                              help="Path to file of s3 file locations")

    # Onyx publish
    onyx_publish_subparser = subparsers.add_parser("publish", parents=[base_subparser],
                                    help = "Publish onyx analysis")
    onyx_publish_subparser.add_argument("--analysis-id", "-a", type=str, 
                              help="Analysis ID for analysis table")

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
