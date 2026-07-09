#!/usr/bin/env nextflow

process CREATE_PNEUMOKITY_ONYX_JSON {
    /*
       This process creates a json file used to populate an onyx analysis table.

        Inputs:
            - meta: Sample metadata
            - csv: Paths to pneumokity result csv files
            - vaccine_serotypes: Path to yaml containing vaccine status information
            - server: Server working on - one of mscape or synthscape
            - context: str of orange box version

        Outputs:
            - pneumokity_summary - tuple of sample metadata and serotyping results file in onyx analysis table format
            - logs: Path to log file for the process

    */
    container 'ghcr.io/ukhsa-collaboration/gpha-mscape-onyx-analysis-helper:0.6.1'
    cpus 2
    memory '2GB'
    tag "${meta.id}"
    publishDir "${params.outdir}/${meta.id}/onyx", mode: params.publish_dir_mode

    input:
    tuple val(meta), val(pneumokity_status), path(csv), path(csv), path(csv)
    path vaccine_serotypes
    val server
    val context

    output:
    tuple val(meta), path("${meta.id}.serotyping.analysis_fields.json"), emit: pneumokity_summary
    path "${meta.id}.serotyping.analysis_fields.log.txt", emit: logs

    script:
    """
    create_pneumokity_analysis_table.py \\
    --store-onyx \\
    -i ${meta.id} \\
    -s $server \\
    -u $context \\
    -o . \\
    -p "${workflow.manifest.name}, ${workflow.manifest.version}, ${workflow.manifest.homePage}" \\
    -vt $vaccine_serotypes \\
    -r $pneumokity_status \\
    """
    }
