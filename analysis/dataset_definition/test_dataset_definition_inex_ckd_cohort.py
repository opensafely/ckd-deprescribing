#############################################################################################
# Test data for dataset_definition_inex_ckd_cohort.py (CKD G4, upper limit eGFR 30)
#
# Test study window 2022-03-01 to 2026-02-28
# Everyone female, born 1952-01-01 (aged 70-74 in window) unless stated
# Creatinine 100 -> eGFR ~49 (HIGH, >= 30); creatinine 200 -> eGFR ~21 (LOW, < 30)
# Everyone registered from 2010-01-01 with no end date unless stated
#
# Note: patient IDs must appear in dataset_inex_second_pass_processed_g4.arrow
#
# opensafely exec ehrql:v1 assure analysis/dataset_definition/test_dataset_definition_inex_ckd_cohort.py -- --ckd_stage g4
#############################################################################################

from datetime import date, timedelta
import json
from dataset_definition_inex_ckd_cohort import dataset

with open("output/ckd_cohort_config.json") as f:
    k_loops = json.load(f)["k_loops"]

CREATININE = "1000731000000107"
HIGH = 100
LOW = 200


def scr(event_date, value):
    return {"date": event_date, "snomedct_code": CREATININE, "numeric_value": value}


def female_1952():
    return {"date_of_birth": date(1952, 1, 1), "sex": "female"}


def registered_2010():
    return [{"start_date": date(2010, 1, 1), "end_date": None}]


# unresolved patient: a low every 90 days, each pair broken by a high in between,
# enough pairs that every one of the k_loops + 1 rounds finds an eGFR3
unresolved_start = date(2022, 3, 1)
unresolved_events = [scr(date(2020, 1, 1), HIGH)]
for i in range(k_loops + 2):
    unresolved_events.append(scr(unresolved_start + timedelta(days=90 * i), LOW))
    if i < k_loops + 1:
        unresolved_events.append(scr(unresolved_start + timedelta(days=90 * i + 45), HIGH))


test_data = {

    # ---------------------------------------------------------------------------------------
    # CKD COHORT LOGIC
    # ---------------------------------------------------------------------------------------

    2: {    # happy path: high, then two lows 122 days apart -> included on second low

        "patients": female_1952(),
        "practice_registrations": registered_2010(),
        "clinical_events": [
            scr(date(2021, 1, 1), HIGH),
            scr(date(2022, 6, 1), LOW),
            scr(date(2022, 10, 1), LOW),
        ],

        "expected_in_population": True,
        "expected_columns": {
            "inex_ckd_date_egfr0": date(2021, 1, 1),
            "inex_ckd_date_egfr1": date(2022, 6, 1),
            "inex_ckd_date_index_date": date(2022, 10, 1),
            "inex_ckd_bin_no_egfr0": False,
            "inex_ckd_bin_no_egfr2": False,
            "inex_ckd_bin_unresolved": False,
            "inex_ckd_num_n_loop_restarts": 0,
            "inex_ckd_bin_same_registration": True,
            "inex_ckd_bin_index_in_window": True,
            "inex_dem_bin_alive": True,
            "inex_dem_bin_age_include": True,
            "inex_dem_num_age": 70,
            "inex_dem_bin_is_registered": True,
            "inex_dem_bin_12m_registered": True,
            "inex_krt_bin_has_primary_care_krt_code": False,
            "inex_krt_bin_has_secondary_care_krt_code": False,
        },
    },

    5: {    # lows exactly 90 days apart -> pair qualifies

        "patients": female_1952(),
        "practice_registrations": registered_2010(),
        "clinical_events": [
            scr(date(2021, 1, 1), HIGH),
            scr(date(2022, 6, 1), LOW),
            scr(date(2022, 8, 30), LOW),
        ],

        "expected_in_population": True,
        "expected_columns": {
            "inex_ckd_date_egfr1": date(2022, 6, 1),
            "inex_ckd_date_index_date": date(2022, 8, 30),
            "inex_ckd_bin_no_egfr2": False,
        },
    },

    6: {    # lows only 89 days apart -> no eGFR2 (cannot confirm CKD)

        "patients": female_1952(),
        "practice_registrations": registered_2010(),
        "clinical_events": [
            scr(date(2021, 1, 1), HIGH),
            scr(date(2022, 6, 1), LOW),
            scr(date(2022, 8, 29), LOW),
        ],

        "expected_in_population": True,
        "expected_columns": {
            "inex_ckd_date_index_date": None,
            "inex_ckd_bin_no_egfr2": True,
            "inex_ckd_bin_unresolved": False,
            "inex_ckd_num_n_loop_restarts": 0,
        },
    },

    14: {   # one restart: high between the first two lows -> pair restarts after the high

        "patients": female_1952(),
        "practice_registrations": registered_2010(),
        "clinical_events": [
            scr(date(2021, 1, 1), HIGH),
            scr(date(2022, 3, 1), LOW),
            scr(date(2022, 4, 1), HIGH),
            scr(date(2022, 5, 1), LOW),
            scr(date(2022, 9, 1), LOW),
        ],

        "expected_in_population": True,
        "expected_columns": {
            "inex_ckd_date_egfr0": date(2022, 4, 1),
            "inex_ckd_date_egfr1": date(2022, 5, 1),
            "inex_ckd_date_index_date": date(2022, 9, 1),
            "inex_ckd_bin_unresolved": False,
            "inex_ckd_num_n_loop_restarts": 1,
        },
    },

    15: {   # Rule A: an extra low < 90 days after eGFR1 does not break the pair

        "patients": female_1952(),
        "practice_registrations": registered_2010(),
        "clinical_events": [
            scr(date(2021, 1, 1), HIGH),
            scr(date(2022, 4, 1), LOW),
            scr(date(2022, 5, 1), LOW),
            scr(date(2022, 8, 1), LOW),
        ],

        "expected_in_population": True,
        "expected_columns": {
            "inex_ckd_date_egfr1": date(2022, 4, 1),
            "inex_ckd_date_index_date": date(2022, 8, 1),
            "inex_ckd_num_n_loop_restarts": 0,
        },
    },

    21: {   # no earlier high -> no eGFR0 (cannot confirm incident)

        "patients": female_1952(),
        "practice_registrations": registered_2010(),
        "clinical_events": [
            scr(date(2022, 4, 1), LOW),
            scr(date(2022, 8, 1), LOW),
        ],

        "expected_in_population": True,
        "expected_columns": {
            "inex_ckd_date_egfr0": None,
            "inex_ckd_date_index_date": date(2022, 8, 1),
            "inex_ckd_bin_no_egfr0": True,
            "inex_ckd_bin_same_registration": False,
        },
    },

    25: {   # restart, then no low >= 90 days after the new eGFR1 -> no eGFR2

        "patients": female_1952(),
        "practice_registrations": registered_2010(),
        "clinical_events": [
            scr(date(2021, 1, 1), HIGH),
            scr(date(2022, 4, 1), LOW),
            scr(date(2022, 5, 1), HIGH),
            scr(date(2022, 8, 1), LOW),
        ],

        "expected_in_population": True,
        "expected_columns": {
            "inex_ckd_date_index_date": None,
            "inex_ckd_bin_no_egfr2": True,
            "inex_ckd_bin_unresolved": False,
            "inex_ckd_num_n_loop_restarts": 1,
        },
    },

    30: {   # every pair broken by a high for more than k_loops rounds -> unresolved

        "patients": female_1952(),
        "practice_registrations": registered_2010(),
        "clinical_events": unresolved_events,

        "expected_in_population": True,
        "expected_columns": {
            "inex_ckd_bin_no_egfr2": False,
            "inex_ckd_bin_unresolved": True,
            "inex_ckd_num_n_loop_restarts": k_loops + 1,
        },
    },

    34: {   # same-day high and low on the eGFR2 date -> lowest wins, no restart

        "patients": female_1952(),
        "practice_registrations": registered_2010(),
        "clinical_events": [
            scr(date(2021, 1, 1), HIGH),
            scr(date(2022, 4, 1), LOW),
            scr(date(2022, 8, 1), LOW),
            scr(date(2022, 8, 1), HIGH),
        ],

        "expected_in_population": True,
        "expected_columns": {
            "inex_ckd_date_index_date": date(2022, 8, 1),
            "inex_ckd_num_n_loop_restarts": 0,
        },
    },

    38: {   # first-ever confirmation before the window (prevalent) -> index not in window

        "patients": female_1952(),
        "practice_registrations": registered_2010(),
        "clinical_events": [
            scr(date(2019, 1, 1), HIGH),
            scr(date(2020, 1, 1), LOW),
            scr(date(2020, 6, 1), LOW),
            scr(date(2022, 6, 1), LOW),
        ],

        "expected_in_population": True,
        "expected_columns": {
            "inex_ckd_date_index_date": date(2020, 6, 1),
            "inex_ckd_bin_index_in_window": False,
        },
    },

    40: {   # second low after window end -> creatinine after window not extracted -> no eGFR2

        "patients": female_1952(),
        "practice_registrations": registered_2010(),
        "clinical_events": [
            scr(date(2024, 1, 1), HIGH),
            scr(date(2025, 12, 1), LOW),
            scr(date(2026, 3, 15), LOW),
        ],

        "expected_in_population": True,
        "expected_columns": {
            "inex_ckd_date_index_date": None,
            "inex_ckd_bin_no_egfr2": True,
        },
    },

    # ---------------------------------------------------------------------------------------
    # REGISTRATION
    # ---------------------------------------------------------------------------------------

    44: {   # registration ended before the index date -> not registered

        "patients": female_1952(),
        "practice_registrations": [
            {"start_date": date(2010, 1, 1), "end_date": date(2022, 5, 1)},
        ],
        "clinical_events": [
            scr(date(2021, 1, 1), HIGH),
            scr(date(2022, 3, 1), LOW),
            scr(date(2022, 7, 1), LOW),
        ],

        "expected_in_population": True,
        "expected_columns": {
            "inex_ckd_date_index_date": date(2022, 7, 1),
            "inex_dem_bin_is_registered": False,
            "inex_dem_bin_12m_registered": False,
            "inex_ckd_bin_same_registration": False,
        },
    },

    54: {   # registered < 12 months before index; eGFR0 is transferred history from before registration

        "patients": female_1952(),
        "practice_registrations": [
            {"start_date": date(2022, 1, 1), "end_date": None},
        ],
        "clinical_events": [
            scr(date(2021, 6, 1), HIGH),
            scr(date(2022, 3, 1), LOW),
            scr(date(2022, 7, 1), LOW),
        ],

        "expected_in_population": True,
        "expected_columns": {
            "inex_ckd_date_egfr0": date(2021, 6, 1),
            "inex_ckd_bin_no_egfr0": False,
            "inex_dem_bin_is_registered": True,
            "inex_dem_bin_12m_registered": False,
            "inex_ckd_bin_same_registration": False,
        },
    },

    55: {   # deregisters ON the index date -> not registered (strict end date)

        "patients": female_1952(),
        "practice_registrations": [
            {"start_date": date(2010, 1, 1), "end_date": date(2022, 7, 1)},
        ],
        "clinical_events": [
            scr(date(2021, 1, 1), HIGH),
            scr(date(2022, 3, 1), LOW),
            scr(date(2022, 7, 1), LOW),
        ],

        "expected_in_population": True,
        "expected_columns": {
            "inex_ckd_date_index_date": date(2022, 7, 1),
            "inex_dem_bin_is_registered": False,
            "inex_dem_bin_12m_registered": False,
        },
    },

    58: {   # moved practice between eGFR0 and the index date (no gap) -> 12m ok, not same registration

        "patients": female_1952(),
        "practice_registrations": [
            {"start_date": date(2010, 1, 1), "end_date": date(2020, 12, 31)},
            {"start_date": date(2021, 1, 1), "end_date": None},
        ],
        "clinical_events": [
            scr(date(2020, 6, 1), HIGH),
            scr(date(2022, 4, 1), LOW),
            scr(date(2022, 8, 1), LOW),
        ],

        "expected_in_population": True,
        "expected_columns": {
            "inex_ckd_date_egfr0": date(2020, 6, 1),
            "inex_dem_bin_is_registered": True,
            "inex_dem_bin_12m_registered": True,
            "inex_ckd_bin_same_registration": False,
        },
    },

    # ---------------------------------------------------------------------------------------
    # DEMOGRAPHICS
    # ---------------------------------------------------------------------------------------

    67: {   # died (primary care record) ON the index date -> not alive

        "patients": {"date_of_birth": date(1952, 1, 1), "sex": "female", "date_of_death": date(2022, 8, 1)},
        "practice_registrations": registered_2010(),
        "clinical_events": [
            scr(date(2021, 1, 1), HIGH),
            scr(date(2022, 4, 1), LOW),
            scr(date(2022, 8, 1), LOW),
        ],

        "expected_in_population": True,
        "expected_columns": {
            "inex_ckd_date_index_date": date(2022, 8, 1),
            "inex_dem_bin_alive": False,
        },
    },

    73: {   # ONS death the day after the index date -> alive

        "patients": female_1952(),
        "ons_deaths": {"date": date(2022, 8, 2)},
        "practice_registrations": registered_2010(),
        "clinical_events": [
            scr(date(2021, 1, 1), HIGH),
            scr(date(2022, 4, 1), LOW),
            scr(date(2022, 8, 1), LOW),
        ],

        "expected_in_population": True,
        "expected_columns": {
            "inex_ckd_date_index_date": date(2022, 8, 1),
            "inex_dem_bin_alive": True,
        },
    },

    76: {   # aged 17 on the index date -> age exclusion (creatinine 300 used as eGFR is higher when young)

        "patients": {"date_of_birth": date(2004, 9, 1), "sex": "female"},
        "practice_registrations": registered_2010(),
        "clinical_events": [
            scr(date(2021, 1, 1), HIGH),
            scr(date(2022, 4, 1), 300),
            scr(date(2022, 8, 1), 300),
        ],

        "expected_in_population": True,
        "expected_columns": {
            "inex_ckd_date_index_date": date(2022, 8, 1),
            "inex_dem_num_age": 17,
            "inex_dem_bin_age_include": False,
        },
    },

    # ---------------------------------------------------------------------------------------
    # KIDNEY REPLACEMENT THERAPY
    # ---------------------------------------------------------------------------------------

    78: {   # primary care dialysis code before the index date

        "patients": female_1952(),
        "practice_registrations": registered_2010(),
        "clinical_events": [
            scr(date(2021, 1, 1), HIGH),
            scr(date(2022, 4, 1), LOW),
            scr(date(2022, 8, 1), LOW),
            {"date": date(2022, 7, 1), "snomedct_code": "105502003"},    # dependence on renal dialysis
        ],

        "expected_in_population": True,
        "expected_columns": {
            "inex_krt_bin_has_primary_care_krt_code": True,
            "inex_krt_cat_primary_care_krt_type": "dialysis",
            "inex_krt_bin_secondary_care_only": False,
        },
    },

    79: {   # secondary care dialysis procedure only -> secondary care only flag

        "patients": female_1952(),
        "practice_registrations": registered_2010(),
        "clinical_events": [
            scr(date(2021, 1, 1), HIGH),
            scr(date(2022, 4, 1), LOW),
            scr(date(2022, 8, 1), LOW),
        ],
        "apcs": [
            {"admission_date": date(2022, 7, 1), "all_diagnoses": "", "all_procedures": "X401"},    # renal dialysis
        ],

        "expected_in_population": True,
        "expected_columns": {
            "inex_krt_bin_has_primary_care_krt_code": False,
            "inex_krt_bin_has_secondary_care_krt_code": True,
            "inex_krt_cat_secondary_care_krt_type": "dialysis",
            "inex_krt_bin_secondary_care_only": True,
        },
    },

    80: {   # primary care dialysis code ON the index date -> counts

        "patients": female_1952(),
        "practice_registrations": registered_2010(),
        "clinical_events": [
            scr(date(2021, 1, 1), HIGH),
            scr(date(2022, 4, 1), LOW),
            scr(date(2022, 8, 1), LOW),
            {"date": date(2022, 8, 1), "snomedct_code": "105502003"},
        ],

        "expected_in_population": True,
        "expected_columns": {
            "inex_krt_bin_has_primary_care_krt_code": True,
        },
    },

    81: {   # primary care dialysis code AFTER the index date -> does not count

        "patients": female_1952(),
        "practice_registrations": registered_2010(),
        "clinical_events": [
            scr(date(2021, 1, 1), HIGH),
            scr(date(2022, 4, 1), LOW),
            scr(date(2022, 8, 1), LOW),
            {"date": date(2022, 8, 2), "snomedct_code": "105502003"},
        ],

        "expected_in_population": True,
        "expected_columns": {
            "inex_krt_bin_has_primary_care_krt_code": False,
        },
    },

    # ---------------------------------------------------------------------------------------
    # MEDICATION COUNTS
    # ---------------------------------------------------------------------------------------

    87: {   # one prescription 10 days and one 100 days before index -> 1 in 90 days, 2 in 180 days

        "patients": female_1952(),
        "practice_registrations": registered_2010(),
        "clinical_events": [
            scr(date(2021, 1, 1), HIGH),
            scr(date(2022, 4, 1), LOW),
            scr(date(2022, 8, 1), LOW),
        ],
        "medications": [
            {"date": date(2022, 7, 22), "dmd_code": "42295711000001101"},
            {"date": date(2022, 4, 23), "dmd_code": "42295711000001101"},
        ],

        "expected_in_population": True,
        "expected_columns": {
            "inex_med_num_90": 1,
            "inex_med_num_180": 2,
        },
    },

    # ---------------------------------------------------------------------------------------
    # POPULATION
    # ---------------------------------------------------------------------------------------

    4: {    # not in the second pass G4 output -> not in population

        "patients": female_1952(),
        "practice_registrations": registered_2010(),
        "clinical_events": [
            scr(date(2021, 1, 1), HIGH),
            scr(date(2022, 4, 1), LOW),
            scr(date(2022, 8, 1), LOW),
        ],

        "expected_in_population": False,
    },

}

# assure needs every table used by the dataset for every patient, even if empty
empty_tables = {
    "clinical_events": [],
    "practice_registrations": [],
    "apcs": [],
    "medications": [],
    "ons_deaths": {},
}
for patient in test_data.values():
    for table, empty in empty_tables.items():
        patient.setdefault(table, empty)
