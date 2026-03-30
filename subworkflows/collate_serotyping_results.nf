#!/usr/bin/env nextflow

include { CREATE_PNEUMOKITY_ONYX_JSON } from '../modules/create_pneumokity_onyx_json'
include { ONYX_WRITE } from '../modules/onyx_write'
include { S3_UPLOAD } from '../modules/s3_upload'
include { ONYX_UPDATE } from '../modules/onyx_update'
include { ONYX_PUBLISH } from '../modules/onyx_publish'


workflow COLLATE_SEROTYPING_RESULTS {
    take:
    ch_pneumokity_complete // channel [val(meta), path(txt)]
    ch_pneumokity_files  // channel: [val(meta), path(csv), path(csv), path(csv)]
    ch_vaccine_serotypes // channel: [path(yaml)]
    server // val: name of server running pipeline on
    bucket // val: name of bucket to upload results to

    main:
    ch_pneumokity_complete
        .branch { meta, pneumokity_complete ->
            pass: pneumokity_complete.text.contains("True")
            fail: pneumokity_complete.text.contains("False")
    }
    .set { pneumokity_status }

    ch_pneumokity_complete
        .map { meta, pneumokity_complete -> tuple(meta, pneumokity_complete.text) }
        .set { ch_pneumokity_complete }

    CREATE_PNEUMOKITY_ONYX_JSON(ch_pneumokity_complete, ch_pneumokity_files.ifEmpty([[],[],[]]), ch_vaccine_serotypes, server)
    ONYX_WRITE(CREATE_PNEUMOKITY_ONYX_JSON.out.pneumokity_summary, server)
    if (pneumokity_status.pass) {
        S3_UPLOAD(ch_pneumokity_files, server, bucket, ONYX_WRITE.out.analysis_id)
        ONYX_UPDATE(server, ONYX_WRITE.out.analysis_id, S3_UPLOAD.out.s3_locations)
    }
    ch_publish = channel.of()
        .concat(ONYX_WRITE.out.analysis_id, ONYX_UPDATE.out.analysis_id.ifEmpty([[], []]))
        .collect()
        .map { meta_write, id_write, meta_update, id_update ->
            tuple(meta_write, id_write)
         }
    ONYX_PUBLISH(server, ch_publish)

    emit:
    pneumokity_summary = CREATE_PNEUMOKITY_ONYX_JSON.out.pneumokity_summary // channel: [val(meta), path(pneumokity_json)]
    pneumokity_analysis_id = ONYX_PUBLISH.out.analysis_id

}
