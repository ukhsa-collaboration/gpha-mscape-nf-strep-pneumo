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

    input:
    tuple val(meta), path(filtered_fastq)

    output:
    tuple val(meta), path("pneumokity_complete.txt"), optional: true, emit: pneumokity_complete
    tuple path("pneumo_capsular_typing/${meta.id}_alldata.csv"), path("pneumo_capsular_typing/${meta.id}_quality_system_data.csv"), path("pneumo_capsular_typing/${meta.id}_result_data.csv"), optional: true, emit: pneumokity_files

    script:
    """
    set +e
    pneumokity.py mix -f $filtered_fastq $filtered_fastq -o . &> pneumokity_stdout.txt
    exit_status=\$?
    if [ \$exit_status == 0 ] ; then
        result="True"
        echo \$result > pneumokity_complete.txt
        exit \$exit_status
    elif grep "ERROR: No Mash data - empty file" pneumokity_stdout.txt ; then
        result="False"
        echo \$result > pneumokity_complete.txt
        exit_status=0
        exit \$exit_status
    else
        exit \$exit_status
    fi
    """

   }
