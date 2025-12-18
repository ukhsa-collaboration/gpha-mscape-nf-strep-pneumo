#!/usr/bin/env nextflow

include { DOWNLOAD_S3_FILES } from './modules/s3_download'
include { RUN_KRACTOR } from './modules/kractor'
include { RUN_PNEUMOKITY } from './modules/pneumokity'

Channel
    .fromPath(params.samplesheet)
    .splitCsv(header: true)
    .map { row ->
        def climb_id = row.climb_id
        return climb_id
    }
    .set { ch_samplesheet }

workflow {
    DOWNLOAD_S3_FILES(ch_samplesheet, params.outdir, params.server)
    RUN_KRACTOR(params.taxid, DOWNLOAD_S3_FILES.out.s3_results)
    RUN_PNEUMOKITY(RUN_KRACTOR.out.kractor_results)
}
