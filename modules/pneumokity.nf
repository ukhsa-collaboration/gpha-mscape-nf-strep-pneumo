#!/usr/bin/env nextflow

process RUN_PNEUMOKITY {
    /*
       This process takes a sample ID as input and queries onyx to find
       relevant fields relating to files required in s3. These files are
       then downloaded to the given output directory.

        Inputs:
            - filtered_fastq: Path to fastq file filtered for Streptococcus reads
        Outputs:
            - results_folder: Folder containing pneumokity results
    */
    container 'docker.io/nanozoo/pneumokity:1.0--ec3a71f'
    cpus 2
    memory '2GB'
    tag "${meta.id}"
    publishDir "${params.outdir}/${meta.id}", mode: params.publish_dir_mode
    errorStrategy 'ignore'

    input:
    tuple val(meta), path(filtered_fastq)

    output:
    tuple val(meta), path("pneumo_capsular_typing/${meta.id}_alldata.csv"), path("pneumo_capsular_typing/${meta.id}_quality_system_data.csv"), path("pneumo_capsular_typing/${meta.id}_result_data.csv"), emit: pneumokity_results

    script:
    """
    pneumokity.py mix -f $filtered_fastq $filtered_fastq -o .
    """

   }
