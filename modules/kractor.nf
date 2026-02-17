#!/usr/bin/env nextflow

process RUN_KRACTOR {
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
    container 'quay.io/biocontainers/kractor:4.0.0--h4349ce8_0'
    cpus 2
    memory '2GB'
    tag "${meta.id}"
    publishDir "${params.outdir}/${meta.id}", mode: params.publish_dir_mode

    input:
    val taxid
    tuple val(meta), path(kraken_stdout), path(kraken_report), path(fastq)

    output:
    tuple val(meta), path("${meta.id}.taxon_extracted.human_filtered.fastq.gz"), emit: kractor_results
    path("${meta.id}.kractor.summary.txt"), emit: kractor_summary

    script:
    """
    kractor -i $fastq -k $kraken_stdout -r $kraken_report -t $taxid \\
    --children  -o ${meta.id}.taxon_extracted.human_filtered.fastq.gz \\
    --summary > ${meta.id}.kractor.summary.txt
    """

   }
