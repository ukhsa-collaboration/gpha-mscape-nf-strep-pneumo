#!/usr/bin/env nextflow

include { LONGREAD_KMER_SEROTYPING } from '../subworkflows/longread_kmer_serotyping'
include { COLLATE_SEROTYPING_RESULTS } from '../subworkflows/collate_serotyping_results'

workflow LONGREAD_TYPING {
    take:
    ch_kraken_output
    ch_kraken_report
    ch_reads
    context
    extract_reads
    taxid
    ch_vaccine_serotypes
    server
    bucket

    main:
    LONGREAD_KMER_SEROTYPING(
        ch_kraken_output,
        ch_kraken_report,
        ch_reads,
        extract_reads,
        taxid
    )
    ch_pneumokity = LONGREAD_KMER_SEROTYPING.out.pneumokity_complete
        .join(LONGREAD_KMER_SEROTYPING.out.pneumokity_files)
    COLLATE_SEROTYPING_RESULTS(
        ch_pneumokity,
        ch_vaccine_serotypes,
        server,
        bucket,
        context
    )

    emit:
    pneumokity_files = LONGREAD_KMER_SEROTYPING.out.pneumokity_files
    pneumokity_summary = COLLATE_SEROTYPING_RESULTS.out.pneumokity_summary
}
