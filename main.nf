#!/usr/bin/env nextflow

include { DOWNLOAD_S3_FILES } from './modules/s3_download'
include { RUN_KRACTOR } from './modules/kractor'


workflow {
    DOWNLOAD_S3_FILES(params.climbid, params.outdir, params.server)
    RUN_KRACTOR(params.climbid, params.taxid, DOWNLOAD_S3_FILES.out.s3_results)
}
