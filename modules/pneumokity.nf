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
    publishDir "$params.outdir", mode: 'copy'

    input:
    val climb_id
    path filtered_fastq

    output:
    tuple path("pneumo_capsular_typing/${climb_id}_alldata.csv"), path("pneumo_capsular_typing/${climb_id}_quality_system_data.csv"), path("pneumo_capsular_typing/${climb_id}_result_data.csv"), emit: pneumokity_results

    script:
    """
    pneumokity.py mix -f $filtered_fastq $filtered_fastq -o .
    """

   }
