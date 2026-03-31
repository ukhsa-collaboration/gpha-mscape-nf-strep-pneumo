#!/usr/bin/env nextflow

process DOWNLOAD_S3_FILES {
    /*
       This process takes a sample ID as input and queries onyx to find
       relevant fields relating to files required in s3. These files are
       then downloaded to the given output directory.

        Inputs:
            - climb_id: Climb ID for a given sample
            - output_dir: Directory to write results to

        Outputs:
            - exit_code: Exit status for the program.
            - result_file: Path to the onyx analysis json file.
    */
    container 'ghcr.io/ukhsa-collaboration/gpha-mscape-onyx-analysis-helper:0.3.1'
    cpus 2
    memory '2GB'
    tag "${climb_id}"
    publishDir "$params.outdir/logs/", mode: "copy", pattern: "*_log.txt"

    input:
    val climb_id
    path out_dir
    val server

    output:
    tuple val("${climb_id}"), path("${climb_id}_PlusPF.kraken_assignments.tsv"), path("${climb_id}_PlusPF.kraken_report.txt"), path("${climb_id}.human_filtered.fastq.gz"), emit: s3_results
    path "${climb_id}_s3_download_log.txt", emit: logs

    script:
    """
    download_s3_files_for_analysis.py -i $climb_id -s $server -o .
    """
    }
