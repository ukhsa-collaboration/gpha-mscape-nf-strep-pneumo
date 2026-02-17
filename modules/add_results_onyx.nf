#!/usr/bin/env nextflow

process ADD_PNEUMOKITY_RESULTS_ONYX {
    /*
       This process adds pneumokity results to an onyx analysis table.

        Inputs:
            - meta: Sample metadata
            - csv: Paths to pneumokity result csv files
            - server: Server working on - one of mscape or synthscape

        Outputs:
            - meta: Sample metadata
            - analysis_id: Onyx analysis ID
            - exit_code: Exit status for the program.
            - result_file: Path to the onyx analysis json file.

    */
    container 'ghcr.io/ukhsa-collaboration/gpha-mscape-sample-qc:0.1.0'
    cpus 2
    memory '2GB'
    tag "${meta.id}"
    publishDir "${params.outdir}/${meta.id}/onyx", mode: params.publish_dir_mode

    input:
    tuple val(meta), path(csv), path(csv), path(csv)
    path vaccine_serotypes
    val server

    output:
    tuple val(meta), path("${meta.id}.analysis_id.txt"), emit: analysis_id
    path "${meta.id}_strep_serotyping_analysis_fields.json", emit: pneumokity_summary
    path "${meta.id}_strep_pneumo_analysis_table_log.txt", emit: logs

    script:
    """
    create_pneumokity_analysis_table.py \\
    -i ${meta.id} \\
    -s $server \\
    -o . \\
    -p "${workflow.manifest.name}, ${workflow.manifest.version}, ${workflow.manifest.homePage}" \\
    -vt $vaccine_serotypes \\
    --store-onyx > ${meta.id}.analysis_id.txt
    """
    }
