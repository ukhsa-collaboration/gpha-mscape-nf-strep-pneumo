#!/usr/bin/env python3

"""
Unit tests for functions in the create_pneumokity_analysis_table.py
script in bin/.
"""
import sys
import pytest  # noqa: F401

sys.path.append('bin/')

import create_pneumokity_analysis_table as pat  # noqa: F401

# Fixtures
@pytest.fixture
def quality_file():
    file = "tests/test_data/C-123456789_quality_system_data.csv"
    return file

@pytest.fixture
def result_file():
    file = "tests/test_data/C-123456789_result_data.csv"
    return file

@pytest.fixture
def data_file():
    file = "tests/test_data/C-123456789_alldata.csv"
    return file

@pytest.fixture
def expected_quality_dict():
    quality_dict = {
        "workflow": "PneumoKITy V1.0",
        "fastq_files_analysed": ['C-123456789.taxon_extracted.human_filtered.fastq.gz', 
                                 'C-123456789.taxon_extracted.human_filtered.fastq.gz'],
        "kmer_min_percent": 90,
        "database": "/PneumoKITy/ctvdb",
    }

    return quality_dict

@pytest.fixture
def expected_headline_result():
    result = "Predicted serotype: 01; rag_status: GREEN"

    return result

@pytest.fixture
def expected_result_dict():
    result_dict = {
        "predicted_serotype": "01",
        "rag_status": "GREEN",
        "stage1_result": "01",
        "stage2_result": {},
        "top_hit_info": {
            "serotype": "01",
            "top_hit_identity": "0.981234567",
            "top_hit_percent": "96.1234567",
            "top_hit_shared_hashes": "961/1000",
            "top_hit_median_multiplicity": "50",
        },
        "top_5_hits": {
            '01': 96.1,
            '02': 80.3,
            '19A-II': 79.3,
            '12A': 30.2,
            '11A/11D': 27.6
        },
    }

    return result_dict

@pytest.fixture
def expected_result_dict_with_vaccine_status():
    result_dict = {
        "predicted_serotype": "01",
        "rag_status": "GREEN",
        "stage1_result": "01",
        "stage2_result": {},
        "top_hit_info": {
            "serotype": "01",
            "top_hit_identity": "0.981234567",
            "top_hit_percent": "96.1234567",
            "top_hit_shared_hashes": "961/1000",
            "top_hit_median_multiplicity": "50",
        },
        "vaccine_status": "Vaccine preventable serotype",
        "vaccine_coverage": {
            "PCV7": "Not included",
            "PCV13": "Included",
            "PCV15": "Included",
            "PCV20": "Included",
            "PPV23": "Included"
        },
        "top_5_hits": {
            '01': 96.1,
            '02': 80.3,
            '19A-II': 79.3,
            '12A': 30.2,
            '11A/11D': 27.6
        },
    }

    return result_dict

@pytest.fixture
def expected_result_dict_with_vaccine_status_and_ipd_status():
    result_df = {
        "predicted_serotype": "01",
        "rag_status": "GREEN",
        "stage1_result": "01",
        "stage2_result": {},
        "top_hit_info": {
            "serotype": "01",
            "top_hit_identity": "0.981234567",
            "top_hit_percent": "96.1234567",
            "top_hit_shared_hashes": "961/1000",
            "top_hit_median_multiplicity": "50",
        },
        "vaccine_status": "Vaccine preventable serotype",
        "vaccine_coverage": {
            "PCV7": "Not included",
            "PCV13": "Included",
            "PCV15": "Included",
            "PCV20": "Included",
            "PPV23": "Included"
        },
        "ipd_status": "Serotype associated with IPD",
        "top_5_hits": {
            '01': 96.1,
            '02': 80.3,
            '19A-II': 79.3,
            '12A': 30.2,
            '11A/11D': 27.6
        },
    }

    return result_df

@pytest.fixture
def expected_fields_dict(expected_config_dict, expected_result_dict):
    fields_dict = {
        "name": "ukhsa-classifier-qc-metrics",
        "description": "This is an analysis to generate QC statistics for individual samples",
        "analysis_date": datetime.datetime.now().date().isoformat(),
        "pipeline_name": "mscape-sample-qc",
        "pipeline_url": "https://github.com/ukhsa-collaboration/mscape-sample-qc",
        "pipeline_version": "0.1.0",
        "methods": json.dumps(expected_config_dict),
        "result": "Warning: Check QC results before use",
        "result_metrics": json.dumps(expected_result_dict),
        "synthscape_records": ["C-123456789"],
        "identifiers": [],
    }

    return fields_dict

# Tests
def test_get_pneumokity_quality_info(quality_file, expected_quality_dict):

    quality_dict = pat.get_pneumokity_quality_info(quality_file)

    print(quality_dict)
    print(expected_quality_dict)

    assert quality_dict == expected_quality_dict

def test_get_pneumokity_result_info(result_file, data_file, expected_result_dict):

    result_dict = pat.get_pneumokity_results(result_file, data_file)

    print(result_dict)
    print(expected_result_dict)

    assert result_dict == expected_result_dict
