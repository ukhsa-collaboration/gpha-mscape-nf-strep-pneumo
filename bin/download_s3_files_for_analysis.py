#!/usr/bin/env python3

"""Simple script to get s3 keys for required files for Strep pnuemo
analysis and download them.
"""

import argparse
import logging
import os
import sys
import pandas as pd
from pathlib import Path
from onyx import OnyxConfig, OnyxClient, OnyxEnv, OnyxField
from onyx_analysis_helper import onyx_analysis_helper_functions as oa
from onyx_analysis_helper import s3_functions as s3f

# Set up onyx config
CONFIG = OnyxConfig(
    domain=os.environ[OnyxEnv.DOMAIN],
    token=os.environ[OnyxEnv.TOKEN],
)

# Args and logging
def get_args():
    """Get command line arguments"""
    parser = argparse.ArgumentParser(
        prog="s3 file finder",
        description="""Simple script to query onyx for taxon reports and
        fastqs in s3 and then download to location specified.
        """,
    )
    parser.add_argument("--input", "-i", type=str, required=True, help="Sample ID")
    parser.add_argument(
        "--output", "-o", type=str, required=True, help="Folder to save downloaded files to"
    )
    parser.add_argument(
        "--server",
        "-s",
        type=str,
        required=True,
        choices=["mscape", "synthscape"],
        help="Specify server code is being run on",
    )

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


# Functions for retrieving info from onyx and downloading samples from s3
@oa.call_to_onyx
def retrieve_sample_information(climb_id: str, project: str):
    "Retrieves sample information from onyx and returns as dataframe"
    with OnyxClient(CONFIG) as client:
        sample_data = pd.DataFrame(client.query(
            project = project,
            query=(
                OnyxField(climb_id=climb_id)
            ),
            include=("climb_id", "taxon_reports", "human_filtered_reads_1")
        ))

    exitcode = 0

    return sample_data, exitcode


def get_s3_paths(sample_data: pd.DataFrame):
    "Takes information from Onyx to generate s3 keys and buckets for downloading objects from s3"
    # Make dict
    s3_dict = {}

    # Get climb id from df
    climb_id = sample_data['climb_id'].values[0]

    # Extract bucket names from s3 address in df
    s3_dict['taxon_bucket'] = sample_data['taxon_reports'].values[0].split("s3://")[1].split("/")[0]
    s3_dict['reads_bucket'] = sample_data['human_filtered_reads_1'].values[0].split("s3://")[1].split("/")[0]

    # Get basename for fastq file
    input_fastq_file = Path(sample_data['human_filtered_reads_1'].values[0]).name

    # s3 keys without bucket names
    s3_dict['kraken_stdout'] = f"{climb_id}/{climb_id}_PlusPF.kraken_assignments.tsv"
    s3_dict['kraken_report'] = f"{climb_id}/{climb_id}_PlusPF.kraken_report.txt"
    s3_dict['input_fastq'] = f"{climb_id}/{input_fastq_file}"

    return s3_dict


def download_files_from_s3(s3_dict: dict, outdir: os.path):
    "Download files from s3, return file paths in dict"
    local_dict = {}
    exitcodes = {0}

    s3_client = s3f.set_up_s3_client()
    local_dict['kraken_stdout'], exitcode = s3f.download_file_from_s3(s3_client, s3_dict['taxon_bucket'], s3_dict['kraken_stdout'], outdir)
    exitcodes.add(exitcode)
    local_dict['kraken_report'], exitcode = s3f.download_file_from_s3(s3_client, s3_dict['taxon_bucket'], s3_dict['kraken_report'], outdir)
    exitcodes.add(exitcode)
    local_dict['input_fastq'], exitcode = s3f.download_file_from_s3(s3_client, s3_dict['reads_bucket'], s3_dict['input_fastq'], outdir)
    exitcodes.add(exitcode)

    if exitcodes == {0}:
        exitcode = 0
    else:
        exitcode = 1

    return local_dict, exitcode


# Main script
def main():
    "Main function to retrieve s3 keys from onyx and download files from s3"

    args = get_args()
    exitcode = 0

    # Set up log file
    log_file = Path(args.output) / f"{args.input}_s3_download_log.txt"
    set_up_logger(log_file)

    # Extract info from onyx
    sample_df, exitcode = retrieve_sample_information(args.input, args.server)
    if exitcode == 1:
        logging.error("Unsuccessful connection to onyx, see logs for details")
        return exitcode

    # Get onyx info into format needed for boto3
    s3_dict = get_s3_paths(sample_df)

    # Download files from s3
    local_dict, exitcode = download_files_from_s3(s3_dict, args.output)
    if exitcode == 1:
        logging.error("At least one s3 download failed, see logs for details")
        return exitcode

    return exitcode

if __name__ == "__main__":
    sys.exit(main())
