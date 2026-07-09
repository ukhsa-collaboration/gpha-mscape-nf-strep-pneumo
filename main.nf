#!/usr/bin/env nextflow

include { LONGREAD_TYPING } from './workflows/longread_typing'

workflow {

    // Handle either samplesheet or climb id
    if (params.samplesheet && params.sampleid) {
        exit(1, "Please specify one of --sampleid or --samplesheet. Not both.")
    }
    else if(params.samplesheet) {
        log.info "Samplesheet input: ${params.samplesheet}"
        ch_samplesheet = channel.fromPath(params.samplesheet)
    }
    else if (params.sampleid) {
        log.info "Sample ID input: ${params.sampleid}"
        ch_sample = Channel.of(tuple(params.sampleid))
        ch_samplesheet = GENERATE_SAMPLESHEET(ch_sample).out.samplesheet
    }
    else {
        exit(1, "Please specify either --climbid or --samplesheet")
    }

    def ch_sample_inputs = ch_samplesheet
        .splitCsv(header: true, quote: '"')
        .map { row -> tuple([id: row.climb_id], row) }
        .view()
        .multiMap { meta, row ->
            reads: [meta, file(row.fastq_1)]
            kraken_output: params.extract_reads ? [meta, file(row.kraken_output)] : []
            kraken_report: params.extract_reads ? [meta, file(row.kraken_report)] : []
            context: params.context ? "\"${row.context}\"" : null
    }
    ch_sample_inputs.reads.view()
    ch_sample_inputs.context.view()



    def ch_vaccine_serotypes = Channel.value(
        file("${projectDir}/assets/predicted_serotype_vaccine_status.yaml")
    )
    LONGREAD_TYPING(
        ch_sample_inputs.kraken_output,
        ch_sample_inputs.kraken_report,
        ch_sample_inputs.reads,
        ch_sample_inputs.context,
        params.extract_reads,
        params.taxid,
        ch_vaccine_serotypes,
        params.server,
        params.bucket
    )

}
