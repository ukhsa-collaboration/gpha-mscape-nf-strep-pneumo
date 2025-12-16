#!/usr/bin/env nextflow

include { DOWNLOAD_S3_FILES } from './modules/s3_download'
include { RUN_KRACTOR } from './modules/kractor'
include { RUN_PNEUMOKITY } from './modules/pneumokity'


workflow {
    DOWNLOAD_S3_FILES(params.climbid, params.outdir, params.server)
    RUN_KRACTOR(params.climbid, params.taxid, DOWNLOAD_S3_FILES.out.s3_results)
    RUN_PNEUMOKITY(params.climbid, RUN_KRACTOR.out.kractor_results)
}
