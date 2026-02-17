#!/usr/bin/env nextflow

include { RUN_KRACTOR } from '../modules/kractor'
include { RUN_PNEUMOKITY } from '../modules/pneumokity'

workflow LONGREAD_KMER_SEROTYPING {
    take:
    ch_kraken_output  // channel: [ val(meta), path(kraken_stdout) ]
    ch_kraken_report  // channel: [ val(meta), path(kraken_report) ]
    ch_reads          // channel: [ val(meta), path(reads) ]
    val_extract_reads // bool: whether to extract reads using kractor
    val_taxid         // taxid reads will be extracted for

    main:
    if (val_extract_reads) {
        ch_kractor_input = ch_kraken_output
            .join(ch_kraken_report)
            .join(ch_reads)
            .map { meta, kraken_output, kraken_report, reads ->
                tuple(meta, kraken_output, kraken_report, reads)
            }
        RUN_KRACTOR(val_taxid, ch_kractor_input)
        RUN_PNEUMOKITY(RUN_KRACTOR.out.kractor_results)

    }
    else {
        RUN_PNEUMOKITY(ch_reads)
    }

    emit:
    pneumokity_files = RUN_PNEUMOKITY.out.pneumokity_results // channel: [ path(csv), path(csv), path(csv)]

}
