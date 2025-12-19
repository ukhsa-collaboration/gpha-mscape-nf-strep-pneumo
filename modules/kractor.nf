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
    container 'quay.io/biocontainers/kractor:3.1.0--h4349ce8_0'
    cpus 2
    memory '2GB'
    tag "${climb_id}"
    publishDir "$params.outdir/filtered_fastqs", mode: 'copy'

    input:
    val taxid
    tuple val(climb_id), path(kraken_stdout), path(kraken_report), path(fastq)

    output:
    tuple val("${climb_id}"), path("${climb_id}.taxon_extracted.human_filtered.fastq.gz"), emit: kractor_results

    script:
    """
    kractor -i $fastq -k $kraken_stdout -r $kraken_report -t $taxid --children  -o ${climb_id}.taxon_extracted.human_filtered.fastq.gz
    """

   }
