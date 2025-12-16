#!/usr/bin/env nextflow

include { DOWNLOAD_S3_FILES } from './modules/s3_download'


workflow {
    DOWNLOAD_S3_FILES(params.climbid, params.outdir, params.server)
}
