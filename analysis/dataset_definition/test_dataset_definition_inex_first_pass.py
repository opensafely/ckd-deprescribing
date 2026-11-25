#############################################################################################
# Test data for dataset_definition_inex_first_pass.py
#
# Test study window 2022-03-01 to 2026-02-28
# Test cut-offs: female > 67.2, male > 85.1 umol/L; uACR > 3 mg/mmol
#
# opensafely exec ehrql:v1 assure analysis/dataset_definition/test_dataset_definition_inex_first_pass.py
#############################################################################################

from datetime import date
from dataset_definition_inex_first_pass import dataset

test_data = {

    1: {    # female: first high creatinine BEFORE window, second in window -> True
            # uACR 3.5 then 5, >= 90 days apart -> True

        "patients": {
            "date_of_birth": date(1950, 1, 1),
            "sex": "female",
        },

        "practice_registrations": [
            {
                "start_date": date(2015, 1, 1),
                "end_date": None,
            }
        ],

        "clinical_events": [
            {
                "date": date(2011, 12, 1),
                "snomedct_code": "1000731000000107",    # creatinine
                "numeric_value": 70,
            },
            {
                "date": date(2022, 4, 1),
                "snomedct_code": "1000731000000107",
                "numeric_value": 72,
            },
            {
                "date": date(2022, 4, 1),
                "snomedct_code": "1023491000000104",    # uACR
                "numeric_value": 3.5,
            },
            {
                "date": date(2022, 9, 1),
                "snomedct_code": "1023491000000104",
                "numeric_value": 5,
            },
        ],

        "ons_deaths": [],

        "expected_in_population": True,
        "expected_columns": {
            "inex_qa_bin_dob_known": True,
            "inex_qa_bin_dob_before_dod": True,
            "inex_qa_bin_dob_not_future": True,
            "inex_qa_bin_dod_not_future": True,
            "inex_dem_bin_sex": True,
            "inex_dem_bin_age_possible": True,
            "inex_dem_bin_alive_study_window_start": True,
            "inex_ckd_bin_two_scr_above_cutoff": True,
            "inex_ckd_bin_two_uacr_raised": True,
        },
    },

    2: {    # female: creatinine 60 and 65 (below 67.2) -> False
            # uACR exactly 3 twice -> False ("<3" stored as 3, so cut-off is > 3)

        "patients": {
            "date_of_birth": date(1950, 1, 1),
            "sex": "female",
        },

        "practice_registrations": [
            {
                "start_date": date(2015, 1, 1),
                "end_date": None,
            }
        ],

        "clinical_events": [
            {
                "date": date(2022, 4, 1),
                "snomedct_code": "1000731000000107",
                "numeric_value": 60,
            },
            {
                "date": date(2022, 9, 1),
                "snomedct_code": "1000731000000107",
                "numeric_value": 65,
            },
            {
                "date": date(2022, 4, 1),
                "snomedct_code": "1023491000000104",
                "numeric_value": 3,
            },
            {
                "date": date(2022, 9, 1),
                "snomedct_code": "1023491000000104",
                "numeric_value": 3,
            },
        ],
        
        "ons_deaths": [],

        "expected_in_population": True,
        "expected_columns": {
            "inex_qa_bin_dob_known": True,
            "inex_qa_bin_dob_before_dod": True,
            "inex_qa_bin_dob_not_future": True,
            "inex_qa_bin_dod_not_future": True,
            "inex_dem_bin_sex": True,
            "inex_dem_bin_age_possible": True,
            "inex_dem_bin_alive_study_window_start": True,
            "inex_ckd_bin_two_scr_above_cutoff": False,
            "inex_ckd_bin_two_uacr_raised": False,
        },
    },

    3: {    # male: creatinine 80 and 84 (above female but below male cut-off 85.1) -> False

        "patients": {
            "date_of_birth": date(1950, 1, 1),
            "sex": "male",
        },

        "practice_registrations": [
            {
                "start_date": date(2015, 1, 1),
                "end_date": None,
            }
        ],

        "clinical_events": [
            {
                "date": date(2022, 4, 1),
                "snomedct_code": "1000731000000107",
                "numeric_value": 80,
            },
            {
                "date": date(2022, 9, 1),
                "snomedct_code": "1000731000000107",
                "numeric_value": 84,
            },
        ],

        "ons_deaths": [],

        "expected_in_population": True,
        "expected_columns": {
            "inex_qa_bin_dob_known": True,
            "inex_qa_bin_dob_before_dod": True,
            "inex_qa_bin_dob_not_future": True,
            "inex_qa_bin_dod_not_future": True,
            "inex_dem_bin_sex": True,
            "inex_dem_bin_age_possible": True,
            "inex_dem_bin_alive_study_window_start": True,
            "inex_ckd_bin_two_scr_above_cutoff": False,
            "inex_ckd_bin_two_uacr_raised": False,
        },
    },

    4: {    # female: two high creatinines only 60 days apart -> False

        "patients": {
            "date_of_birth": date(1950, 1, 1),
            "sex": "female",
        },

        "practice_registrations": [
            {
                "start_date": date(2015, 1, 1),
                "end_date": None,
            }
        ],

        "clinical_events": [
            {
                "date": date(2022, 4, 1),
                "snomedct_code": "1000731000000107",
                "numeric_value": 100,
            },
            {
                "date": date(2022, 5, 31),
                "snomedct_code": "1000731000000107",
                "numeric_value": 100,
            },
        ],

        "ons_deaths": [],

        "expected_in_population": True,
        "expected_columns": {
            "inex_qa_bin_dob_known": True,
            "inex_qa_bin_dob_before_dod": True,
            "inex_qa_bin_dob_not_future": True,
            "inex_qa_bin_dod_not_future": True,
            "inex_dem_bin_sex": True,
            "inex_dem_bin_age_possible": True,
            "inex_dem_bin_alive_study_window_start": True,
            "inex_ckd_bin_two_scr_above_cutoff": False,
            "inex_ckd_bin_two_uacr_raised": False,
        },
    },


    5: {    # deregistered before the window starts -> not in population

        "patients": {
            "date_of_birth": date(1950, 1, 1),
            "sex": "female",
        },

        "practice_registrations": [
            {
                "start_date": date(2015, 1, 1),
                "end_date": date(2021, 12, 31),
            }
        ],

        "clinical_events": [],

        "ons_deaths": [],


        "expected_in_population": False,
    },

    6: {    # born 2010: aged 16 at window end -> age_possible False
            # missing sex

        "patients": {
            "date_of_birth": date(2010, 1, 1),
        },

        "practice_registrations": [
            {
                "start_date": date(2015, 1, 1),
                "end_date": None,
            }
        ],

        "clinical_events": [],

        "ons_deaths": [],


        "expected_in_population": True,
        "expected_columns": {
            "inex_qa_bin_dob_known": True,
            "inex_qa_bin_dob_before_dod": True,
            "inex_qa_bin_dob_not_future": True,
            "inex_qa_bin_dod_not_future": True,
            "inex_dem_bin_sex": None,
            "inex_dem_bin_age_possible": False,
            "inex_dem_bin_alive_study_window_start": True,
            "inex_ckd_bin_two_scr_above_cutoff": False,
            "inex_ckd_bin_two_uacr_raised": False,
        },
    },

    7: {    # died before window start (registration still open into window) -> alive False

        "patients": {
            "date_of_birth": date(1950, 1, 1),
            "sex": "female",
            "date_of_death": date(2022, 1, 1),
        },

        "clinical_events": {},

        "ons_deaths": {
            "date": date(2022, 1, 1),
        },

        "practice_registrations": [
            {
                "start_date": date(2015, 1, 1),
                "end_date": date(2023, 1, 1),
            }
        ],

        "expected_in_population": True,
        "expected_columns": {
            "inex_qa_bin_dob_known": True,
            "inex_qa_bin_dob_before_dod": True,
            "inex_qa_bin_dob_not_future": True,
            "inex_qa_bin_dod_not_future": True,
            "inex_dem_bin_sex": True,
            "inex_dem_bin_age_possible": True,
            "inex_dem_bin_alive_study_window_start": False,
            "inex_ckd_bin_two_scr_above_cutoff": False,
            "inex_ckd_bin_two_uacr_raised": False,
        },
    }
}