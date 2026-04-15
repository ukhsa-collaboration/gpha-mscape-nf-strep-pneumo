#!/usr/bin/env python3

"""
Unit tests for functions in the create_pneumokity_analysis_table.py
script in bin/.
"""
import datetime
import json
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
def vaccine_file():
    file = "assets/predicted_serotype_vaccine_status.yaml"
    return file

@pytest.fixture
def expected_pipeline_info():
    pipeline_dict = {
        "name": "gpha-mscape-nf-strep-pneumo",
        "version": "v0.1.0",
        "homePage": "https://github.com/ukhsa-collaboration/gpha-mscape-nf-strep-pneumo"
    }

    return pipeline_dict

@pytest.fixture
def expected_quality_dict():
    quality_dict = {
        "workflow": "PneumoKITy V1.0",
        "fastq_files_analysed": ['C-123456789.taxon_extracted.human_filtered.fastq.gz', 
                                 'C-123456789.taxon_extracted.human_filtered.fastq.gz'],
        "kmer_min_percent": "90",
        "database": "/PneumoKITy/ctvdb",
    }

    return quality_dict

@pytest.fixture
def expected_headline_result():
    result = "Predicted serotype: 1; rag_status: GREEN"

    return result

@pytest.fixture
def expected_result_dict():
    result_dict = {
        "predicted_serotype": "1",
        "rag_status": "GREEN",
        "stage1_result": "1",
        "stage2_result": '{}',
        "top_hit_info": {
            "serotype": "01",
            "top_hit_identity": "0.981234567",
            "top_hit_percent": "96.1234567",
            "top_hit_shared_hashes": "961/1000",
            "top_hit_median_multiplicity": "50",
        },
        "top_5_hits": "{'01': 96.1, '02': 80.3, '19A-II': 79.3, '12A': 30.2, '11A/11D': 27.6}",
    }

    return result_dict

@pytest.fixture
def expected_result_dict_with_analysis_status():
    result_dict = {
        "predicted_serotype": "1",
        "rag_status": "GREEN",
        "analysis_status": "Pass",
        "stage1_result": "1",
        "stage2_result": '{}',
        "top_hit_info": {
            "serotype": "01",
            "top_hit_identity": "0.981234567",
            "top_hit_percent": "96.1234567",
            "top_hit_shared_hashes": "961/1000",
            "top_hit_median_multiplicity": "50",
        },
        "top_5_hits": "{'01': 96.1, '02': 80.3, '19A-II': 79.3, '12A': 30.2, '11A/11D': 27.6}",
    }

    return result_dict

@pytest.fixture
def expected_result_dict_with_vaccine_status():
    result_dict = {
        "predicted_serotype": "1",
        "rag_status": "GREEN",
        "analysis_status": "Pass",
        "stage1_result": "1",
        "stage2_result": '{}',
        "top_hit_info": {
            "serotype": "01",
            "top_hit_identity": "0.981234567",
            "top_hit_percent": "96.1234567",
            "top_hit_shared_hashes": "961/1000",
            "top_hit_median_multiplicity": "50",
        },
        "vaccine_status": "Vaccine serotype",
        "vaccine_coverage": {
            "PCV7": "Not included",
            "PCV13": "Included",
            "PCV15": "Included",
            "PCV20": "Included",
            "PPV23": "Included"
        },
        "top_5_hits": "{'01': 96.1, '02': 80.3, '19A-II': 79.3, '12A': 30.2, '11A/11D': 27.6}",
    }

    return result_dict


@pytest.fixture
def expected_fields_dict(expected_quality_dict, expected_result_dict_with_vaccine_status):
    fields_dict = {
        "name": "ukhsa-streptococcus-pneumoniae-serotyping",
        "description": "This is an analysis to serotype strep pneumo in metagenomic samples",
        "analysis_date": datetime.datetime.now().date().isoformat(),
        "pipeline_name": "gpha-mscape-nf-strep-pneumo",
        "pipeline_url": "https://github.com/ukhsa-collaboration/gpha-mscape-nf-strep-pneumo",
        "pipeline_version": "v0.1.0",
        "methods": json.dumps(expected_quality_dict),
        "result": "1",
        "result_metrics": json.dumps(expected_result_dict_with_vaccine_status),
        "synthscape_records": ["C-123456789"],
        "identifiers": [],
    }

    return fields_dict

# Incomplete serotype
@pytest.fixture
def expected_result_dict_incomplete_serotype():
    result_dict = {
        "predicted_serotype": "12F_12A_12B_44_46",
        "analysis_status": "Pass",
        "rag_status": "RED",
        "stage1_result": "",
        "stage2_result": '{}',
        "top_hit_info": {
            "serotype": "12F_12A_12B_44_46",
            "top_hit_identity": "0.975366",
            "top_hit_percent": "97.5366",
            "top_hit_shared_hashes": "975/1000",
            "top_hit_median_multiplicity": "10",
        },
        "top_5_hits": "{'01': 96.1, '02': 80.3, '19A-II': 79.3, '12A': 30.2, '11A/11D': 27.6}",
    }

    return result_dict

@pytest.fixture
def expected_result_dict_incomplete_serotype_vaccine_status():
    result_dict = {
        "predicted_serotype": "12F_12A_12B_44_46",
        "analysis_status": "Pass",
        "rag_status": "RED",
        "stage1_result": "",
        "stage2_result": '{}',
        "top_hit_info": {
            "serotype": "12F_12A_12B_44_46",
            "top_hit_identity": "0.975366",
            "top_hit_percent": "97.5366",
            "top_hit_shared_hashes": "975/1000",
            "top_hit_median_multiplicity": "10",
        },
        "vaccine_status": "Cannot split vaccine type from non-vaccine type serotypes",
        "vaccine_coverage": {
            "PCV7": "Not included",
            "PCV13": "Not included",
            "PCV15": "Not included",
            "PCV20": "Inconclusive",
            "PPV23": "Inconclusive"
        },
        "top_5_hits": "{'01': 96.1, '02': 80.3, '19A-II': 79.3, '12A': 30.2, '11A/11D': 27.6}",
    }

    return result_dict

# Fail test fixtures
@pytest.fixture
def expected_result_dict_fail():
    result_dict = {
        "predicted_serotype": "Below 20% hit",
        "rag_status": "RED",
        "stage1_result": "",
        "stage2_result": {},
        "top_hit_info": {
            "serotype": "12",
            "top_hit_identity": "0.234366",
            "top_hit_percent": "23.4366",
            "top_hit_shared_hashes": "234/1000",
            "top_hit_median_multiplicity": "10",
        },
        "top_5_hits": "{'01': 96.1, '02': 80.3, '19A-II': 79.3, '12A': 30.2, '11A/11D': 27.6}",
    }

    return result_dict

@pytest.fixture
def expected_result_dict_with_analysis_status_fail():
    result_dict = {
        "predicted_serotype": "Below 20% hit",
        "analysis_status": "Fail",
        "rag_status": "RED",
        "stage1_result": "",
        "stage2_result": {},
        "top_hit_info": {
            "serotype": "12",
            "top_hit_identity": "0.234366",
            "top_hit_percent": "23.4366",
            "top_hit_shared_hashes": "234/1000",
            "top_hit_median_multiplicity": "10",
        },
        "top_5_hits": "{'01': 96.1, '02': 80.3, '19A-II': 79.3, '12A': 30.2, '11A/11D': 27.6}",
    }

    return result_dict

@pytest.fixture
def expected_result_dict_with_vaccine_status_fail():
    result_dict = {
        "predicted_serotype": "Below 20% hit",
        "analysis_status": "Fail",
        "rag_status": "RED",
        "stage1_result": "",
        "stage2_result": {},
        "top_hit_info": {
            "serotype": "12",
            "top_hit_identity": "0.234366",
            "top_hit_percent": "23.4366",
            "top_hit_shared_hashes": "234/1000",
            "top_hit_median_multiplicity": "10",
        },
        "vaccine_status": "No result",
        "vaccine_coverage": {
            "PCV7": "No result",
            "PCV13": "No result",
            "PCV15": "No result",
            "PCV20": "No result",
            "PPV23": "No result"
        },
        "top_5_hits": "{'01': 96.1, '02': 80.3, '19A-II': 79.3, '12A': 30.2, '11A/11D': 27.6}",
    }

    return result_dict

# Tests
def test_get_pneumokity_quality_info(quality_file, expected_quality_dict):

    quality_dict = pat.get_pneumokity_quality_info(quality_file)

    print(quality_dict)
    print(expected_quality_dict)

    assert quality_dict == expected_quality_dict

def test_get_pneumokity_result_info(result_file, data_file, expected_result_dict):

    result_dict = pat.get_pneumokity_results(result_file, data_file)

    print(result_dict)

    assert result_dict == expected_result_dict

@pytest.mark.parametrize(
    "result_dict,expected_output",
    [
        ("expected_result_dict", "expected_result_dict_with_analysis_status"),
        ("expected_result_dict_fail", "expected_result_dict_with_analysis_status_fail"),
    ],
)
def test_get_analysis_status(result_dict, expected_output, request):
    result_dict = request.getfixturevalue(result_dict)
    expected_output = request.getfixturevalue(expected_output)

    updated_result_dict = pat.get_analysis_status(result_dict)

    print(updated_result_dict)

    assert updated_result_dict == expected_output

@pytest.mark.parametrize(
    "result_dict,vaccine_info_file,expected_output",
    [
        ("expected_result_dict_with_analysis_status", "vaccine_file", "expected_result_dict_with_vaccine_status"),
        ("expected_result_dict_incomplete_serotype", "vaccine_file", "expected_result_dict_incomplete_serotype_vaccine_status"),
        ("expected_result_dict_with_analysis_status_fail", "vaccine_file", "expected_result_dict_with_vaccine_status_fail")
    ],
)
def test_get_vaccine_status(result_dict, vaccine_info_file, expected_output, request):
    result_dict = request.getfixturevalue(result_dict)
    vaccine_file = request.getfixturevalue(vaccine_info_file)
    expected_output = request.getfixturevalue(expected_output)

    vaccine_dict = pat.get_vaccine_status(result_dict, vaccine_file)

    print(vaccine_dict)

    assert vaccine_dict == expected_output


def test_create_analysis_fields(expected_quality_dict, expected_result_dict_with_vaccine_status, expected_fields_dict, expected_pipeline_info):

    analysis_fields, exitcode = pat.create_analysis_fields("C-123456789", expected_quality_dict, expected_result_dict_with_vaccine_status, "synthscape", expected_pipeline_info)

    print(analysis_fields.__dict__)

    assert analysis_fields.__dict__ == expected_fields_dict
    assert exitcode == 0
