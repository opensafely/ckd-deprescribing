#############################################################################################
# Test data for dataset_definition_inex_second_pass.py
#
# Test study window 2022-03-01 to 2026-02-28
# Test eGFR thresholds (stage upper limits): 60, 45, 30, 15
# Everyone born 1952-01-01, so aged 69 in 2021 and 70 in 2022
#
# Note: patient IDs must appear in dataset_inex_first_pass_processed.arrow
#
# opensafely exec ehrql:v1 assure analysis/dataset_definition/test_dataset_definition_inex_second_pass.py
#############################################################################################

from datetime import date
from dataset_definition_inex_second_pass import dataset

test_data = {

    2: {    # female, creatinine 160 twice (eGFR 27.8), 122 days apart -> below 60/45/30, not 15

        "patients": {
            "date_of_birth": date(1952, 1, 1),
            "sex": "female",
        },

        "clinical_events": [
            {
                "date": date(2022, 4, 1),
                "snomedct_code": "1000731000000107",    # creatinine
                "numeric_value": 160,
            },
            {
                "date": date(2022, 8, 1),
                "snomedct_code": "1000731000000107",
                "numeric_value": 160,
            },
        ],

        "expected_in_population": True,
        "expected_columns": {
            "inex_ckd_bin_two_egfr_below_60": True,
            "inex_ckd_bin_two_egfr_below_45": True,
            "inex_ckd_bin_two_egfr_below_30": True,
            "inex_ckd_bin_two_egfr_below_15": False,
        },
    },

    4: {    # female, creatinine 150 twice (eGFR 30.1) -> just above 30 so not below 30

        "patients": {
            "date_of_birth": date(1952, 1, 1),
            "sex": "female",
        },

        "clinical_events": [
            {
                "date": date(2022, 4, 1),
                "snomedct_code": "1000731000000107",
                "numeric_value": 150,
            },
            {
                "date": date(2022, 8, 1),
                "snomedct_code": "1000731000000107",
                "numeric_value": 150,
            },
        ],

        "expected_in_population": True,
        "expected_columns": {
            "inex_ckd_bin_two_egfr_below_60": True,
            "inex_ckd_bin_two_egfr_below_45": True,
            "inex_ckd_bin_two_egfr_below_30": False,
            "inex_ckd_bin_two_egfr_below_15": False,
        },
    },

    5: {    # male, creatinine 400 twice (eGFR 12.2) but only 89 days apart -> all False

        "patients": {
            "date_of_birth": date(1952, 1, 1),
            "sex": "male",
        },

        "clinical_events": [
            {
                "date": date(2022, 4, 1),
                "snomedct_code": "1000731000000107",
                "numeric_value": 400,
            },
            {
                "date": date(2022, 6, 29),
                "snomedct_code": "1000731000000107",
                "numeric_value": 400,
            },
        ],

        "expected_in_population": True,
        "expected_columns": {
            "inex_ckd_bin_two_egfr_below_60": False,
            "inex_ckd_bin_two_egfr_below_45": False,
            "inex_ckd_bin_two_egfr_below_30": False,
            "inex_ckd_bin_two_egfr_below_15": False,
        },
    },

    6: {    # male, creatinine 400 twice (eGFR 12.2) exactly 90 days apart -> all True

        "patients": {
            "date_of_birth": date(1952, 1, 1),
            "sex": "male",
        },

        "clinical_events": [
            {
                "date": date(2022, 4, 1),
                "snomedct_code": "1000731000000107",
                "numeric_value": 400,
            },
            {
                "date": date(2022, 6, 30),
                "snomedct_code": "1000731000000107",
                "numeric_value": 400,
            },
        ],

        "expected_in_population": True,
        "expected_columns": {
            "inex_ckd_bin_two_egfr_below_60": True,
            "inex_ckd_bin_two_egfr_below_45": True,
            "inex_ckd_bin_two_egfr_below_30": True,
            "inex_ckd_bin_two_egfr_below_15": True,
        },
    },

    9: {    # male, creatinine 400 BEFORE window_start (eGFR 12.3) and in window (eGFR 12.2) -> all True

        "patients": {
            "date_of_birth": date(1952, 1, 1),
            "sex": "male",
        },

        "clinical_events": [
            {
                "date": date(2021, 1, 1),
                "snomedct_code": "1000731000000107",
                "numeric_value": 400,
            },
            {
                "date": date(2022, 4, 1),
                "snomedct_code": "1000731000000107",
                "numeric_value": 400,
            },
        ],

        "expected_in_population": True,
        "expected_columns": {
            "inex_ckd_bin_two_egfr_below_60": True,
            "inex_ckd_bin_two_egfr_below_45": True,
            "inex_ckd_bin_two_egfr_below_30": True,
            "inex_ckd_bin_two_egfr_below_15": True,
        },
    },

    11: {   # male, creatinine 3500 (out of range) 90 days before a 250 (eGFR 21.6),
            # second 250 is AFTER window end -> all False

        "patients": {
            "date_of_birth": date(1952, 1, 1),
            "sex": "male",
        },

        "clinical_events": [
            {
                "date": date(2022, 1, 1),
                "snomedct_code": "1000731000000107",
                "numeric_value": 3500,
            },
            {
                "date": date(2022, 4, 1),
                "snomedct_code": "1000731000000107",
                "numeric_value": 250,
            },
            {
                "date": date(2026, 3, 1),
                "snomedct_code": "1000731000000107",
                "numeric_value": 250,
            },
        ],

        "expected_in_population": True,
        "expected_columns": {
            "inex_ckd_bin_two_egfr_below_60": False,
            "inex_ckd_bin_two_egfr_below_45": False,
            "inex_ckd_bin_two_egfr_below_30": False,
            "inex_ckd_bin_two_egfr_below_15": False,
        },
    },

    14: {   # female, creatinine 110 (eGFR 43.8) then 160 (eGFR 27.8) -> below 60/45 only

        "patients": {
            "date_of_birth": date(1952, 1, 1),
            "sex": "female",
        },

        "clinical_events": [
            {
                "date": date(2022, 4, 1),
                "snomedct_code": "1000731000000107",
                "numeric_value": 110,
            },
            {
                "date": date(2022, 8, 1),
                "snomedct_code": "1000731000000107",
                "numeric_value": 160,
            },
        ],

        "expected_in_population": True,
        "expected_columns": {
            "inex_ckd_bin_two_egfr_below_60": True,
            "inex_ckd_bin_two_egfr_below_45": True,
            "inex_ckd_bin_two_egfr_below_30": False,
            "inex_ckd_bin_two_egfr_below_15": False,
        },
    },

}
