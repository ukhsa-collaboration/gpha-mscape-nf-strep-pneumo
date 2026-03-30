# gpha-mscape-nf-strep-pneumo

This repository contains a nextflow pipeline and associated scripts for
the characterisation of Streptococcus pneumoniae in metagenomic samples.

## Installation

To clone this repo:  
`git clone git@github.com:ukhsa-collaboration/gpha-mscape-nf-strep-pneumo.git`

No further installation is required for use on Bryn as the nextflow pipeline
is containerised and will pull in relevant containers as required when the
pipeline is run.

## Usage

Example command:
```bash
nextflow run main.nf \
--samplesheet /path/to/samplesheet.csv \
--taxid 1313 \
--extract_reads True \
--outdir /path/to/outdir \
--server server-name \
--bucket "name-of-s3-bucket"
```

## Parameters

| Parameter     |   Description |
|---------------|---------------|
| samplesheet   | Path to csv file containing sample information. Requires following columns: climb_id, fastq_1, fastq_2, kraken_output, kraken_report. |
| taxid         | NCBI taxon ID to extract reads for |
| extract_reads | Boolean specifying if taxon reads should be extracted from fastq before running pneumokity |
| outdir        | Path to output directory |
| server        | Name of server working on |
| bucket        | Name of s3 bucket to upload result files to |

## Pipeline overview

The pipeline consists of the following steps:
1. (Optional) Extracts reads for taxon of interest from a sample e.g. all
   reads classified as Streptoccocus or below (taxid: 1301), or all reads
   classified as Streptococcus pneumoniae (taxid: 1313).
2. Run pneumokity on reads (extracted by taxon or all reads in the sample).
   Pneumokity is a kmer-based serotyping tool from Streptoccocus pneumoniae.
3. Collate pneumokity results into the format required for onyx. This includes
   adding the vaccine status of the identified serotype if pneumokity ran
   successfully.
4. Creation of an onyx analysis table and adding any results files produced
   by pneumokity to s3 storage.
5. Publishing of the onyx analysis table.

### Current pipeline structure
Long read typing workflow:
```
longread_typing
|-- longread_kmer_serotyping
    |-- run_kractor (optional)
    |-- run_pneumokity

|-- collate_serotyping_results
    |-- create_pneumokity_onyx_json
    |-- onyx_write
    |-- s3_upload (pneumokity success only)
    |-- onyx_update (pneumokity success only)
    |-- onyx_publish
```
### Future additions

The following elements may be added in future versions of the pipeline:
- Streptococcus pneumoniae speciation - integration of the code used to confirm
  if samples containing Streptococcus reads contain Streptococcus pneumoniae as
  a workflow to run before longread_typing.
- PneumoCAT2 typing - addition of an extra mapping-based typing method in
  longread_typing for extra verification and added resolution for difficult to
  resolve serotypes.
