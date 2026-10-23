###########################################################################
# Test data for dataset_definition_baseline_meds.py
#
# This test checks the performance of add_prescription_columns(), which is
# the main component of dataset_definition_baseline_meds.py 
#
# Note: as dataset_definition_baseline_meds filters to patients in
# dataset_inex_cleaned.arrow, patient IDs here must also appear in that
# dataset - this test can only be performed locally, as will not know
# patient IDs in real data.
#
# opensafely exec ehrql:v1 assure analysis/dataset_definition/test_dataset_definition_baseline_meds.py
###########################################################################

from datetime import date
from dataset_definition_baseline_meds import dataset

test_data = {
    
    2: {    # simple case with only one medication data row 
        "patients": { # one row per patient
            "date_of_birth": date(1910, 1, 1), # always first day of month, never NULL
            },

        "medications": [ # many rows per patient
            { 
                "date": date(2022, 3, 1), # index date should be included
                "dmd_code": "34953211000001105", # Rosuvastatin 10mg tablets (Aristo Pharma Ltd)
            },
        ],

        "expected_in_population": True,
        "expected_columns": {
            "med_dmd_code_1": "34953211000001105",
            "med_date_1": date(2022, 3, 1),
            "med_dmd_code_2": None,
            "med_date_2": None,
            "med_dmd_code_3": None,
            "med_date_3": None,
            "med_dmd_code_4": None,
            "med_date_4": None,
            "med_dmd_code_5": None,
            "med_date_5": None
        },
    },


    5: {    # 2nd medicine prescribed before 90 day window around index date
        
        "patients": { # one row per patient
            "date_of_birth": date(1910, 1, 1), # always first day of month, never NULL
            },

        "medications": [
            {
                "date": date(2022, 3, 2), # day after index date - should not be captured
                "dmd_code": "360711000001100" # Lisinopril 20mg tablets (Zentiva)
            },
            {
                "date": date(2022, 3, 1), # index date - last day of window 0
                "dmd_code": "34953211000001105", # Rosuvastatin 10mg tablets (Aristo Pharma Ltd)
            },
            {
                "date": date(2022, 2, 23), # first day of window 0
                "dmd_code": "34953211000001105", # Rosuvastatin 10mg tablets (Aristo Pharma Ltd)
            },
            {
                "date": date(2022, 2, 22), # last day of window 1
                "dmd_code": "34953211000001105", # Rosuvastatin 10mg tablets (Aristo Pharma Ltd)
            },
            {
                "date": date(2022, 2, 2), # first day of window 3
                "dmd_code": "34953211000001105", # Rosuvastatin 10mg tablets (Aristo Pharma Ltd)
            }
        ],

        "expected_in_population": True,
        "expected_columns": {
            "med_dmd_code_1": "34953211000001105",
            "med_date_1": date(2022, 3, 1),
            "med_dmd_code_2": "34953211000001105",
            "med_date_2": date(2022, 2, 23),
            "med_dmd_code_3": None,
            "med_date_3": None,
            # ...
            "med_dmd_code_21": "34953211000001105",
            "med_date_21": date(2022, 2, 22),
            "med_dmd_code_22": None,
            "med_date_22": None,
            "med_dmd_code_23": None,
            "med_date_23": None,
            # ...
            "med_dmd_code_41": None,
            "med_date_41": None,
            # ...
            "med_dmd_code_61": "34953211000001105",
            "med_date_61": date(2022, 2, 2),
            "med_dmd_code_62": None,
            "med_date_62": None,

        },
    },

    8: {    # multiple different prescriptions on the same day 
        
        "patients": { # one row per patient
            "date_of_birth": date(1910, 1, 1), # always first day of month, never NULL
            },

        "medications": [ # many rows per patient
            { 
                "date": date(2022, 2, 20),
                "dmd_code": "34953211000001105", # Rosuvastatin 10mg tablets (Aristo Pharma Ltd)
            },
            {
                "date": date(2022, 2, 20), # same date 
                "dmd_code": "360711000001100" # Lisinopril 20mg tablets (Zentiva)
            }
        ],

        "expected_in_population": True,
        "expected_columns": {
            "med_dmd_code_21": "360711000001100",
            "med_date_21": date(2022, 2, 20),
            "med_dmd_code_22": "34953211000001105",
            "med_date_22": date(2022, 2, 20),
            "med_dmd_code_3": None,
            "med_date_3": None,
            "med_dmd_code_4": None,
            "med_date_4": None,
            "med_dmd_code_5": None,
            "med_date_5": None
        },
    },



    10: {    # duplicated date and code
        
        "patients": { # one row per patient
            "date_of_birth": date(1910, 1, 1), # always first day of month, never NULL
            },

        "medications": [ # many rows per patient
            {
                "date": date(2022, 2, 12),
                "dmd_code": "34953211000001105", # Rosuvastatin 10mg tablets (Aristo Pharma Ltd)
            },
            {
                "date": date(2022, 2, 12), # same date
                "dmd_code": "34953211000001105" # Rosuvastatin 10mg tablets (Aristo Pharma Ltd)
            }
        ],

        "expected_in_population": True,
        "expected_columns": {
            "med_dmd_code_41": "34953211000001105",
            "med_date_41": date(2022, 2, 12),
            "med_dmd_code_42": None,
            "med_date_42": None,
            "med_dmd_code_3": None,
            "med_date_3": None,
            "med_dmd_code_4": None,
            "med_date_4": None,
            "med_dmd_code_5": None,
            "med_date_5": None
        },
    },



    12: {   # more realistic patient, shows that function is ordering dm+d codes lexicographically rather than numerically. 
            # ordering doesn't really matter as long as consistent
        
        "patients": { # one row per patient
            "date_of_birth": date(1910, 1, 1), # always first day of month, never NULL
            },

        "medications": [ # many rows per patient
            {
                "date": date(2022, 3, 1),
                "dmd_code": "34953211000001105", # Rosuvastatin 10mg tablets (Aristo Pharma Ltd)
            },
            {
                "date": date(2022, 3, 1), # same date
                "dmd_code": "360711000001100" # Lisinopril 20mg tablets (Zentiva)
            },
            {
                "date": date(2022, 3, 1), # same date
                "dmd_code": "21801411000001101" # Bisoprolol 5mg tablets (Waymade Healthcare Plc)
            },
            {
                "date": date(2022, 3, 1), # same date
                "dmd_code": "9557111000001102" # Amlodipine 5mg tablets (Zentiva)
            },

            # same medicines again but a week earlier (window 1)

            {
                "date": date(2022, 2, 22),
                "dmd_code": "34953211000001105" # Rosuvastatin 10mg tablets (Aristo Pharma Ltd)
            },
            {
                "date": date(2022, 2, 22),
                "dmd_code": "360711000001100" # Lisinopril 20mg tablets (Zentiva)
            },
            {
                "date": date(2022, 2, 22),
                "dmd_code": "21801411000001101" # Bisoprolol 5mg tablets (Waymade Healthcare Plc)
            },
            {
                "date": date(2022, 2, 22),
                "dmd_code": "9557111000001102" # Amlodipine 5mg tablets (Zentiva)
            }
        ],

        "expected_in_population": True,
        "expected_columns": {
            # window 0
            "med_dmd_code_1": "9557111000001102",
            "med_date_1": date(2022, 3, 1),
            "med_dmd_code_2": "360711000001100",
            "med_date_2": date(2022, 3, 1),
            "med_dmd_code_3": "34953211000001105",
            "med_date_3": date(2022, 3, 1),
            "med_dmd_code_4": "21801411000001101",
            "med_date_4": date(2022, 3, 1),
            "med_dmd_code_5": None,
            "med_date_5": None,
            # window 1
            "med_dmd_code_21": "9557111000001102",
            "med_date_21": date(2022, 2, 22),
            "med_dmd_code_22": "360711000001100",
            "med_date_22": date(2022, 2, 22),
            "med_dmd_code_23": "34953211000001105",
            "med_date_23": date(2022, 2, 22),
            "med_dmd_code_24": "21801411000001101",
            "med_date_24": date(2022, 2, 22),
            "med_dmd_code_25": None,
            "med_date_25": None
        },
    },


    16: {   # tests max_meds=15 logic.
            # Exactly 16 distinct prescriptions — verifies all slots filled and slot 15 contains
            # the oldest prescription bar 1 
        "patients": { # one row per patient
            "date_of_birth": date(1910, 1, 1), # always first day of month, never NULL
            },

        "medications": [ # many rows per patient
            {
                "date": date(2022, 3, 1), 
                "dmd_code": "10000000000000001"
            },
            {
                "date": date(2022, 3, 1),
                "dmd_code": "10000000000000002"
            },
            {
                "date": date(2022, 3, 1),
                 "dmd_code": "10000000000000005"
            },
            {
                "date": date(2022, 3, 1),
                 "dmd_code": "10000000000000006"
            },
            {
                "date": date(2022, 3, 1),
                 "dmd_code": "10000000000000007"
            },
            {
                "date": date(2022, 3, 1),
                 "dmd_code": "10000000000000003"
            },
            {
                "date": date(2022, 3, 1),
                 "dmd_code": "10000000000000008"
            },
            {
                "date": date(2022, 3, 1),
                 "dmd_code": "10000000000000009"
            },
            {
                "date": date(2022, 3, 1),
                 "dmd_code": "10000000000000010"
            },
            {
                "date": date(2022, 3, 1),
                 "dmd_code": "10000000000000004"
            },
            {
                "date": date(2022, 3, 1),
                 "dmd_code": "10000000000000011"
            },
            {
                "date": date(2022, 3, 1),
                 "dmd_code": "10000000000000012"
            },
            {
                "date": date(2022, 3, 1),
                 "dmd_code": "10000000000000013"
            },
            {
                "date": date(2022, 3, 1),
                 "dmd_code": "10000000000000014"
            },
            {
                "date": date(2022, 3, 1),
                 "dmd_code": "10000000000000015"
            },
            {
                "date": date(2022, 3, 1),
                 "dmd_code": "10000000000000016"
            },
            {
                "date": date(2022, 3, 1),
                 "dmd_code": "10000000000000017"
            },
            {
                "date": date(2022, 3, 1),
                 "dmd_code": "10000000000000018"
            },
            {
                "date": date(2022, 3, 1),
                 "dmd_code": "10000000000000019"
            },
            {
                "date": date(2022, 3, 1),
                 "dmd_code": "10000000000000020"
            },
            {
                "date": date(2022, 2, 23), # oldest in window 0 — should be dropped
                "dmd_code": "10000000000000021"
            },
            {
                "date": date(2022, 2, 22), # window 1 — should be in slot 21
                "dmd_code": "10000000000000022"
            }
        ],

        "expected_in_population": True,
        "expected_columns": {
            # window 0 - full
            "med_dmd_code_1": "10000000000000020",
            "med_date_1": date(2022, 3, 1),
            "med_dmd_code_2": "10000000000000019",
            "med_date_2": date(2022, 3, 1),
            "med_dmd_code_3": "10000000000000018",
            "med_date_3": date(2022, 3, 1),
            "med_dmd_code_4": "10000000000000017",
            "med_date_4": date(2022, 3, 1),
            "med_dmd_code_5": "10000000000000016",
            "med_date_5": date(2022, 3, 1),
            "med_dmd_code_6": "10000000000000015",
            "med_date_6": date(2022, 3, 1),
            "med_dmd_code_7": "10000000000000014",
            "med_date_7": date(2022, 3, 1),
            "med_dmd_code_8": "10000000000000013",
            "med_date_8": date(2022, 3, 1),
            "med_dmd_code_9": "10000000000000012",
            "med_date_9": date(2022, 3, 1),
            "med_dmd_code_10": "10000000000000011",
            "med_date_10": date(2022, 3, 1),
            "med_dmd_code_11": "10000000000000010",
            "med_date_11": date(2022, 3, 1),
            "med_dmd_code_12": "10000000000000009",
            "med_date_12": date(2022, 3, 1),
            "med_dmd_code_13": "10000000000000008",
            "med_date_13": date(2022, 3, 1),
            "med_dmd_code_14": "10000000000000007",
            "med_date_14": date(2022, 3, 1),
            "med_dmd_code_15": "10000000000000006",
            "med_date_15": date(2022, 3, 1),
            "med_dmd_code_16": "10000000000000005",
            "med_date_16": date(2022, 3, 1),
            "med_dmd_code_17": "10000000000000004",
            "med_date_17": date(2022, 3, 1),
            "med_dmd_code_18": "10000000000000003",
            "med_date_18": date(2022, 3, 1),
            "med_dmd_code_19": "10000000000000002",
            "med_date_19": date(2022, 3, 1),
            "med_dmd_code_20": "10000000000000001",
            "med_date_20": date(2022, 3, 1),
            # window 1
            "med_dmd_code_21": "10000000000000022",
            "med_date_21": date(2022, 2, 22),
            "med_dmd_code_22": None,
            "med_date_22": None
        },
    },

}