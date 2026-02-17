#!/usr/bin/env nextflow

include { LONGREAD_KMER_SEROTYPING } from '../subworkflows/longread_kmer_serotyping'

workflow LONGREAD_TYPING {
    take:
    ch_kraken_output
    ch_kraken_report
    ch_reads
    extract_reads
    taxid

    main:
    LONGREAD_KMER_SEROTYPING(
        ch_kraken_output,
        ch_kraken_report,
        ch_reads,
        extract_reads,
        taxid
    )

    emit:
    pneumokity_files = LONGREAD_KMER_SEROTYPING.out.pneumokity_files
}
