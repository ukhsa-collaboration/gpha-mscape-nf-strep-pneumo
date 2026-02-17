#!/usr/bin/env nextflow

include { ADD_PNEUMOKITY_RESULTS_ONYX } from '../modules/add_results_onyx'

workflow COLLATE_SEROTYPING_RESULTS {
    take:
    ch_pneumokity_files  // channel: [val(meta), path(csv), path(csv), path(csv)]
    ch_vaccine_serotypes // channel: [path(yaml)]
    server // val: name of server running pipeline on

    main:
    if (ch_pneumokity_files) {
        ADD_PNEUMOKITY_RESULTS_ONYX(ch_pneumokity_files, ch_vaccine_serotypes, server)
    }

    emit:
    pneumokity_analysis_id = ADD_PNEUMOKITY_RESULTS_ONYX.out.analysis_id // channel: [val(meta), val(analysis_id)]
    pneumokity_summary = ADD_PNEUMOKITY_RESULTS_ONYX.out.pneumokity_summary

}
