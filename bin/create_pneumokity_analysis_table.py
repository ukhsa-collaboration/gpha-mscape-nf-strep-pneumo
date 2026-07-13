#!/usr/bin/env python3

"""Script and associated functions to take strep pneumo serotyping
results and create an onyx analysis table format json file.
"""

# Imports
import argparse
import logging
import os
import sys
from ast import literal_eval
from pathlib import Path

import pandas as pd
import yaml
from onyx import OnyxConfig, OnyxEnv
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
        prog="Create pneumokity analysis table",
        description="""Simple script to generate onyx analysis fields from pneumokity results
        """,
    )
    parser.add_argument("--climbid", "-i", type=str, required=True, help="Sample ID")
    parser.add_argument(
        "--output",
        "-o",
        type=str,
        required=True,
        help="Folder to save downloaded files to",
    )
    parser.add_argument(
        "--vaccine-serotypes",
        "-vt",
        type=str,
        required=True,
        help="Path to yaml containing vaccine serotype information",
    )
    parser.add_argument(
        "--server",
        "-s",
        type=str,
        required=True,
        choices=["mscape", "synthscape"],
        help="Specify server code is being run on",
    )
    parser.add_argument(
        "--pipeline_info",
        "-p",
        type=str,
        required=True,
        help="Comma separated str in format: 'pipeline name, version, homepage'",
    )
    parser.add_argument(
        "--pneumokity_result",
        "-r",
        type=str,
        required=True,
        help="Argument stating whether pneumokity ran successfully",
    )
    parser.add_argument(
        "--context",
        "-c",
        dest="orange_box_version",
        type=str,
        required=False,
        help="Orange box version used to determine if should run.",
    )
    # Add group options to specify onyx behaviour
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument(
        "--store-onyx",
        required=False,
        action="store_true",
        help="Use this option to store results as an onyx analysis object for later upload",
    )
    group.add_argument(
        "--test-onyx",
        required=False,
        action="store_true",
        help="Use this option to do a test upload and check for errors before attempting an upload to onyx",
    )
    group.add_argument(
        "--prod-onyx",
        required=False,
        action="store_true",
        help="Use this option to upload results to onyx",
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


# Functions to extract info from pneumokity results
def get_pneumokity_quality_info(quality_file: Path) -> dict:
    """Parses the quality system data file produced by pneumokity to extract
    version numbers and databases used to run pneumokity.
    Arguments:
        quality_file -- Path to file containing quality system information
    Returns:
        quality_dict -- Dictionary of quality system information
    """
    with Path(quality_file).open("r") as file:
        quality_info = pd.read_csv(file, converters={"fastq_files": literal_eval}).loc[
            0
        ]

    # Pull out relevant fields to make dict
    quality_dict = {
        "workflow": quality_info["workflow"],
        "fastq_files_analysed": quality_info["fastq_files"],
        "kmer_min_percent": str(quality_info["minpercent"]),
        "database": quality_info["database"],
    }

    return quality_dict


def get_pneumokity_results(result_file: Path, all_data_file: Path) -> dict:
    """Parses the result_data file from pneumokity to extract key results.
    Arguments:
        result_file -- Path to file containing pneumokity headline results
        all_data_file -- Path to file containing all pneumokity results
    Returns:
        Dictionary of pneumokity results
    """
    with Path(result_file).open("r") as file:
        result_summary = pd.read_csv(
            file,
            dtype=str,
            converters={
                "top_hits": literal_eval,
                "stage2_hits": literal_eval,
                "stage2_result": literal_eval,
            },
        ).loc[0]

    with Path(all_data_file).open("r") as file:
        top_hit_data = pd.read_csv(file, dtype=str).loc[0]

    # Extract out main results
    result_dict = {
        "predicted_serotype": result_summary["predicted_serotype"],
        "rag_status": result_summary["rag_status"],
        "stage1_result": result_summary["stage1_result"],
        "stage2_result": result_summary["stage2_result"],
        "stage2_hits": result_summary["stage2_hits"],
        "top_hit_info": {
            "serotype": top_hit_data["Serotype"],
            "top_hit_identity": top_hit_data["identity"],
            "top_hit_shared_hashes": top_hit_data["shared-hashes"],
            "top_hit_percent": top_hit_data["percent"],
            "top_hit_median_multiplicity": top_hit_data["median-multiplicity"],
        },
        "top_5_hits": result_summary["top_hits"],
    }

    return result_dict


def get_analysis_status(result_dict: dict):
    """Check if pneumokity returned a serotype or failed
    Arguments:
        result_dict -- Dict containing pneumokity results
    Returns:
        result_dict -- Updated result dict with analysis status of pneumokity added
    """
    fails = [
        "Below 70% hit",
        "Below 20% hit",
        "Median multiplicity low",
    ]

    result_dict["analysis_status"] = next(
        ("Fail" for fail in fails if fail in result_dict["predicted_serotype"]), "Pass"
    )

    return result_dict


def get_vaccine_status(result_dict: dict, vaccine_status_file: Path) -> dict:
    """ "Takes predicted serotype and checks if it is a vaccine preventable
    serotype. Returns overall vaccine status (vaccine preventable or
    non-vaccine preventable) and dict of serotype presence in different
    vaccines.
    Arguments:
        result_dict -- Dictionary containing key pneumokity results
        vaccine_file -- File containing information on the serotypes
                        included in different vaccines
    Returns:
        vaccine_status_dict -- Updated result dict containing vaccine status information
    """
    with Path(vaccine_status_file).open("r") as file:
        vaccine_dict = yaml.safe_load(file)

    serotype = result_dict["predicted_serotype"]

    # Handle pneumokity fails:
    if result_dict["analysis_status"] == "Fail":
        result_dict["vaccine_status"] = "No result"
        result_dict["vaccine_coverage"] = {
            "PCV13": "No result",
            "PCV15": "No result",
            "PCV20": "No result",
            "PPV23": "No result",
        }

    # Handle incomplete serotype outcomes
    elif serotype in vaccine_dict["predicted_serotype_incomplete"].keys():
        result_dict["vaccine_status"] = vaccine_dict["predicted_serotype_incomplete"][
            serotype
        ]["result"]
        result_dict["vaccine_coverage"] = {
            "PCV13": vaccine_dict["predicted_serotype_incomplete"][serotype]["PCV13"],
            "PCV15": vaccine_dict["predicted_serotype_incomplete"][serotype]["PCV15"],
            "PCV20": vaccine_dict["predicted_serotype_incomplete"][serotype]["PCV20"],
            "PPV23": vaccine_dict["predicted_serotype_incomplete"][serotype]["PPV23"],
        }

    # Handle other serotypes
    else:
        result_dict["vaccine_coverage"] = {}
        # Get serotype status for individual vaccines:
        for vaccine in vaccine_dict["vaccine_serotypes"]:
            status_set = set()
            if serotype in vaccine_dict["vaccine_serotypes"][vaccine]:
                result_dict["vaccine_coverage"][f"{vaccine}"] = "Included"
                status_set.add("VT")
            else:
                result_dict["vaccine_coverage"][f"{vaccine}"] = "Not included"
                status_set.add("Non-VT")
        # Get overall vaccine status:
        if status_set == {"VT"} or status_set == {"VT", "Non-VT"}:
            result_dict["vaccine_status"] = "Vaccine serotype"
        elif status_set == {"Non-VT"}:
            result_dict["vaccine_status"] = "Non-vaccine serotype"

    return result_dict


# TODO: Placeholder function
def get_ipd_status(predicted_serotype: dict, ipd_dict: dict) -> dict:
    """Takes predicted serotype and checks if it is serotype associated
    with IPD. Returns overall vaccine status (vaccine preventable or
    non-vaccine preventable) and dict of serotype presence in different
    vaccines.
    Arguments:
        predicted_serotype -- Serotype of sample
        ipd_dict -- Dictionary containing information on IPD status of
                    serotypes
    Returns:
        result_dict -- Updated result_dict containing vaccine information
    """
    ipd_dict = {}

    return ipd_dict


def make_pipeline_dict(pipeline_str) -> dict:
    """Create dict of pipeline info from input pipeline info string.
    Arguments:
        pipeline_str -- Comma separated string of pipeline info in format
                        'pipeline_name,pipeline_version,pipeline_homepage'
    Returns:
        pipeline_dict -- Dictionary containing pipeline information
    """

    pipeline_list = pipeline_str.split(",")
    pipeline_dict = {
        "name": pipeline_list[0],
        "version": pipeline_list[1],
        "homePage": pipeline_list[2],
    }

    return pipeline_dict


def create_analysis_fields(
    record_id: str,
    pneumokity_settings: dict,
    pneumokity_results: dict,
    server: str,
    pipeline_info: dict,
    orange_box_version: str,
) -> tuple[oa.OnyxAnalysis, int]:
    """Set up fields dictionary used to populate analysis table containing
    Streptococcus pneumoniae serotyping results.
    Arguments:
        record_id -- Climb ID for sample
        pneumokity_settings -- Dictionary containing settings and versions used to run pneumokity
        headline_result -- Short description of main result- - from pnuemokity predicted serotype
        pneumokity_results -- Dictionary containing pneumokity results
        server -- Server code is running on, one of "mscape" or "synthscape"
        orange_box_version -- orange box version.
    Returns:
        onyx_analysis -- Class containing required fields for input to onyx
                         analysis table
        exitcode -- Exit code for checks - will be 0 if all checks passed, 1 if any checks failed
    """
    onyx_analysis = oa.OnyxAnalysis()
    onyx_analysis.add_analysis_details(
        analysis_name="ukhsa-streptococcus-pneumoniae-serotyping",
        analysis_description="This is an analysis to serotype strep pneumo in metagenomic samples",
    )
    onyx_analysis.pipeline_name = pipeline_info["name"]
    onyx_analysis.pipeline_version = pipeline_info["version"]
    onyx_analysis.pipeline_url = pipeline_info["homePage"]
    onyx_analysis.outputs = "No s3 outputs"  # ty:ignore[invalid-assignment]
    # Add pneumokity settings and onyx analysis hash
    methods_fail = onyx_analysis.add_methods(
        methods_dict={
            "pneumokity_settings": pneumokity_settings,
        }
    )

    _, onyx_versions, query_exitcode = oa.get_data_and_versions_from_onyx(
        sample_id=record_id, server=server, fields=["climb_id"]
    )

    if query_exitcode == 0:
        # Add onyx versions and orange box version
        methods_versions_fail = onyx_analysis.add_versions_to_methods(
            tool_versions={"orange_box_version": orange_box_version},
            onyx_versions=onyx_versions,  # onyx versions hash automatically generated
        )
    else:
        methods_versions_fail = False

    headline_result = pneumokity_results["predicted_serotype"]
    results_fail = onyx_analysis.add_results(
        top_result=headline_result, results_dict=pneumokity_results
    )
    onyx_analysis.add_server_records(sample_id=record_id, server_name=server)
    required_field_fail, attribute_fail = onyx_analysis.check_analysis_object(
        publish_analysis=False
    )

    if any(
        [
            methods_fail,
            methods_versions_fail,
            results_fail,
            required_field_fail,
            attribute_fail,
        ]
    ):  # noqa SIM108
        exitcode = 1
    else:
        exitcode = 0

    return onyx_analysis, exitcode


# Main script
def main():
    "Main function to process pneumokity results ready for submission to onyx"
    args = get_args()
    exitcode = 0

    # Set up log file
    log_file = Path(args.output) / f"{args.climbid}.serotyping.analysis_fields.log.txt"
    set_up_logger(log_file)

    orange_box_version = (
        args.orange_box_version if args.orange_box_version else "unknown"
    )

    if args.pneumokity_result == "True":
        # Paths to pneumokity files
        quality_file = Path(args.output) / f"{args.climbid}_quality_system_data.csv"
        result_file = Path(args.output) / f"{args.climbid}_result_data.csv"
        data_file = Path(args.output) / f"{args.climbid}_alldata.csv"

        # Get information from pneumokity result files
        quality_dict = get_pneumokity_quality_info(quality_file)
        result_dict = get_pneumokity_results(result_file, data_file)

        # Check if analysis failed or result was obtained
        result_dict = get_analysis_status(result_dict)
        result_dict = get_vaccine_status(result_dict, args.vaccine_serotypes)
    else:
        quality_dict = {"quality_info": "No Mash data - empty file"}
        result_dict = {"predicted_serotype": "No Mash data - empty file"}
    # Convert pipeline info to dict
    pipeline_dict = make_pipeline_dict(args.pipeline_info)

    # Create onyx analysis dict
    onyx_analysis, exitcode = create_analysis_fields(
        record_id=args.climbid,
        pneumokity_settings=quality_dict,
        pneumokity_results=result_dict,
        server=args.server,
        pipeline_info=pipeline_dict,
        orange_box_version=orange_box_version,
    )

    # Exit if analysis object not made correctly
    if exitcode == 1:
        logging.error(
            "Invalid attribute in analysis fields submitted, check logs for details"
        )
        return exitcode

    # Store analysis table info in json file
    if args.store_onyx:
        onyx_json_file = (
            Path(args.output) / f"{args.climbid}.serotyping.analysis_fields.json"
        )
        result_file = onyx_analysis.write_analysis_to_json(result_file=onyx_json_file)
        logging.info("Onyx analysis fields written to file %s", result_file)
        exitcode = 0
        return exitcode

    # Test push data to onyx
    if args.test_onyx:
        result, exitcode = onyx_analysis.write_analysis_to_onyx(
            server=args.server, dryrun=True, publish_analysis=False
        )

    # Push analysis table to onyx
    if args.prod_onyx:
        result, exitcode = onyx_analysis.write_analysis_to_onyx(
            server=args.server, dryrun=False, publish_analysis=False
        )

    return exitcode


if __name__ == "__main__":
    sys.exit(main())
