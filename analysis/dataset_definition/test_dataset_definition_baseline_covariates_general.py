##########################################################################
# Test data for dataset_definition_baseline_covariates_general.py
# This test checks the performance of add_baseline_covariates_general()
#
# opensafely exec ehrql:v1 assure analysis/dataset_definition/
# test_dataset_definition_baseline_covariates_general.py
##########################################################################

from datetime import date
from dataset_definition_baseline_covariates_general import dataset

# NB: population is defined by dataset_inex_cleaned.exists_for_patient(), so
# every patient ID below must be in output/data/dataset_inex_cleaned.arrow. 
# The 5 pulled-through columns (age, sex, egfr_1, date_egfr_1, ckd_stage) 
# come from that arrow file,

test_data = {

    8: {
        # tests:
        #   - table_from_file() pulls through from dataset_inex_cleaned
        #   - defaults when patient has no records at all

        "patients": {
            "date_of_birth": date(1950, 1, 1),
            "sex": "female",
        },
        "addresses": [],
        "clinical_events": [],
        "ethnicity_from_sus": {},
        "practice_registrations": [],
        "apcs": [],
        "medications": [],
        "ons_deaths": {},

        "expected_in_population": True,
        "expected_columns": {
            "basecov_gen_num_age": 65,
            "basecov_gen_cat_sex": "female",
            "basecov_gen_num_egfr_1": 15.787086382900743,
            "basecov_gen_date_egfr_1": date(2020, 6, 21),
            "basecov_gen_cat_ckd_stage": "4",

            "basecov_gen_cat_ethnicity": "Missing",
            "basecov_gen_cat_imd": None,
            "basecov_gen_cat_region": None,
            "basecov_gen_bin_care_home": False,
            "basecov_gen_num_sbp": None,
            "basecov_gen_date_sbp": None,
            "basecov_gen_num_uacr": None,
            "basecov_gen_date_uacr": None,
            "basecov_gen_cat_uacr_category": "Missing",
            "basecov_gen_cat_uacr_source": "Missing",
            "basecov_gen_num_bmi_value": None,
            "basecov_gen_cat_bmi_category": "Missing",
            "basecov_gen_date_bmi": None,
            "basecov_gen_cat_smoker_status": "M",
            "basecov_gen_bin_dm": False,
            "basecov_gen_bin_cvd_history": False,
            "basecov_gen_num_n_scr_tests": 0,
            "basecov_gen_num_cms": 0.213652,
            "basecov_gen_bin_cms_alcohol": 0,
            "basecov_gen_bin_cms_af": 0,
            "basecov_gen_bin_cms_copd": 0,
            "basecov_gen_bin_cms_dementia": 0,
            "basecov_gen_bin_cms_diabetes": 0,
            "basecov_gen_bin_cms_hf": 0,
            "basecov_gen_bin_cms_cld": 0,
            "basecov_gen_bin_cms_prostate": 0,
            "basecov_gen_bin_cms_learning": 0,
            "basecov_gen_bin_cms_sclerosis": 0,
            "basecov_gen_bin_cms_parkinsonism": 0,
            "basecov_gen_bin_cms_perivascular_leg": 0,
            "basecov_gen_bin_cms_psychosub_misuse": 0,
            "basecov_gen_bin_cms_cancer": 0,
            "basecov_gen_bin_cms_epilepsy": 0,
            "basecov_gen_bin_cms_bowel": 0,
            "basecov_gen_bin_cms_psychosis": 0,
            "basecov_gen_bin_cms_constipation": 0,
            "basecov_gen_bin_cms_anxiety": 0,
            "basecov_gen_bin_cms_pain": 0,
        },
    },


    2: {
        # tests:
        #   - multiple ethnicity codes in clinical_events table, one after index
        #   - current active address with IMD 3000 that is a care home
        #   - most recent BP null so earlier BP used
        #   - T1DM code (also in CMS diabetes list)
        #   - CVD via MI in primary care only
        #   - BMI 30 boundary -> Obese
        #   - uPCR more recent than uACR -> uPCR used and converted (male)
        #   - most recent smoking code S
        #   - CMS: AF code ever, lithium ever prescribed (psychosis)
        #   - two creatinines on same day count once

        "patients": {
            "date_of_birth": date(1950, 1, 1),
            "sex": "male",
        },

        "addresses": [
            {
                "start_date": date(2010, 1, 1),
                "end_date": None,
                "imd_rounded": 3000, # between 0 and 32800 - multiple of 100
                "care_home_is_potential_match": True,
            },
        ],

        "clinical_events": [
            {
                "date": date(2021, 1, 1),
                "snomedct_code": "185988007",       # African caribbean ethnicity - 4
            },
            {
                "date": date(2020, 1, 1),
                "snomedct_code": "40165009"         # Buriats ethnicity - 3
            },
            {
                "date": date(2023, 1, 1),
                "snomedct_code": "56056003"         # Bulgarian ethnicity - 1 (after index)
            },
            {
                "date": date(2022, 1, 1),
                "snomedct_code": "271649006",       # BP in right date range, but null
                "numeric_value": None
            },
            {
                "date": date(2021, 1, 1),
                "snomedct_code": "100171000000100", # first BP that is not null
                "numeric_value": 158
            },
            {
                "date": date(1950, 1, 1),
                "snomedct_code": "190368000"        # type 1 diabetes ages ago - should flag
            },
            {
                "date": date(2021, 1, 1),
                "snomedct_code": "22298006"         # myocardial infarction
            },
            {
                "date": date(2021, 6, 1),
                "snomedct_code": "60621009",        # BMI
                "numeric_value": 30.0
            },
            {
                "date": date(2021, 1, 1),
                "snomedct_code": "1023491000000104", # uACR - older
                "numeric_value": 50
            },
            {
                "date": date(2021, 6, 1),
                "snomedct_code": "1006631000000104", # uPCR - newer
                "numeric_value": 5.31
            },
            {
                "date": date(2019, 1, 1),
                "ctv3_code": "1371.",               # never smoker
            },
            {
                "date": date(2021, 1, 1),
                "ctv3_code": "1372.",               # smoker - most recent
            },
            {
                "date": date(2015, 1, 1),
                "snomedct_code": "49436004",        # atrial fibrillation
            },
            {
                "date": date(2021, 6, 1),
                "snomedct_code": "1000731000000107", # creatinine
                "numeric_value": 150
            },
            {
                "date": date(2021, 6, 1),
                "snomedct_code": "1000731000000107", # creatinine same day
                "numeric_value": 155
            },
            {
                "date": date(2021, 9, 1),
                "snomedct_code": "1000731000000107", # creatinine
                "numeric_value": 160
            },
        ],

        "ethnicity_from_sus": {},

        "practice_registrations": [
            {
                "start_date": date(2010, 1, 1),
                "end_date": None,
                "practice_nuts1_region_name": "North East",
            },
        ],

        "apcs": [
            {
                "admission_date": date(2021, 1, 1),
                "all_diagnoses": "",       # ICD-10 (mi / cva / hf)
                "all_procedures": "",      # OPCS-4 (coronary revasc)
            },
        ],

        "medications": [
            {
                "date": date(2010, 1, 1),
                "dmd_code": "42295711000001101",    # lithium
            },
        ],

        "ons_deaths": {},

        "expected_in_population": True,
        "expected_columns": {
            "basecov_gen_cat_ethnicity": "Black",
            "basecov_gen_cat_imd": "1 (most deprived)",
            "basecov_gen_cat_region": "North East",
            "basecov_gen_bin_care_home": True,
            "basecov_gen_num_sbp": 158,
            "basecov_gen_date_sbp": date(2021, 1, 1),
            "basecov_gen_num_bmi_value": 30.0,
            "basecov_gen_cat_bmi_category": "Obese (>=30)",
            "basecov_gen_date_bmi": date(2021, 6, 1),
            "basecov_gen_num_uacr": 5.31 / 2.655,
            "basecov_gen_date_uacr": date(2021, 6, 1),
            "basecov_gen_cat_uacr_category": "A1",
            "basecov_gen_cat_uacr_source": "uPCR",
            "basecov_gen_cat_smoker_status": "S",
            "basecov_gen_bin_dm": True,
            "basecov_gen_bin_cvd_history": True,
            "basecov_gen_num_n_scr_tests": 2,
            "basecov_gen_bin_cms_af": 1,
            "basecov_gen_bin_cms_diabetes": 1,
            "basecov_gen_bin_cms_psychosis": 1,
            "basecov_gen_num_cms": 0.213652 + 0.334891 + 0.29467 + 0.482469,
        },
    },


    5: {
        # tests:
        #   - no snomed ethnicity code - so fall back on ethnicity from sus
        #   - address not spanning index so IMD and care home fail
        #   - registration spans index but region null
        #   - most recent BP impossible value so earlier BP used
        #   - hba1c 48 boundary -> diabetes
        #   - CVD history only confirmed through secondary care procedure
        #   - uPCR only, converted (female)
        #   - most recent smoking code E
        #   - CMS: first cancer code within 5 years
        #   - creatinine count: 365-day boundary, null and implausible
        #     values, after index

        "patients": {
            "date_of_birth": date(1950, 1, 1),
            "sex": "female",
        },

        "addresses": [
            {
                "start_date": date(2010, 1, 1),
                "end_date": date(2020, 1, 1), # before index
                "imd_rounded": 3000,
                "care_home_is_potential_match": True,
            },
            {
                "start_date": date(2023, 1, 1), # after index
                "end_date": date(2030, 1, 1),
                "imd_rounded": 3000,
                "care_home_is_potential_match": True,
            },
        ],

        "clinical_events": [
            {
                "date": date(2020, 1, 1),
                "snomedct_code": "271649006",       # earlier BP very high
                "numeric_value": 180
            },
            {
                "date": date(2021, 1, 1),
                "snomedct_code": "100171000000100", # more recent BP improbable value
                "numeric_value": 10
            },
            {
                "date": date(2020, 1, 1),
                "snomedct_code": "999791000000106", # hba1c
                "numeric_value": 48
            },
            {
                "date": date(2021, 6, 1),
                "snomedct_code": "1006631000000104", # uPCR only
                "numeric_value": 17.566
            },
            {
                "date": date(2021, 1, 1),
                "ctv3_code": "1377.",               # ex-smoker
            },
            {
                "date": date(2018, 6, 1),
                "snomedct_code": "254837009",       # breast cancer - first code within 5y
            },
            {
                "date": date(2021, 3, 1),
                "snomedct_code": "1000731000000107", # creatinine - exactly 365 days, excluded
                "numeric_value": 150
            },
            {
                "date": date(2021, 3, 2),
                "snomedct_code": "1000731000000107", # creatinine - counted
                "numeric_value": 150
            },
            {
                "date": date(2021, 6, 1),
                "snomedct_code": "1000731000000107", # creatinine - null value
                "numeric_value": None
            },
            {
                "date": date(2021, 7, 1),
                "snomedct_code": "1000731000000107", # creatinine - implausible value
                "numeric_value": 10
            },
            {
                "date": date(2022, 6, 1),
                "snomedct_code": "1000731000000107", # creatinine - after index
                "numeric_value": 150
            },
        ],

        "ethnicity_from_sus": {
            "code": "A"
        },

        "practice_registrations": [
            {
                "start_date": date(2010, 1, 1),
                "end_date": date(2030, 1, 1),
                "practice_nuts1_region_name": None,
            },
        ],

        "apcs": [
            {
                "admission_date": date(2021, 1, 1),
                "all_diagnoses": None,          # ICD-10 (mi / cva / hf)
                "all_procedures": "||K47",      # OPCS-4 (coronary revasc)
            },
        ],

        "medications": [],

        "ons_deaths": {},

        "expected_in_population": True,
        "expected_columns": {
            "basecov_gen_cat_ethnicity": "White",
            "basecov_gen_cat_imd": None,
            "basecov_gen_cat_region": None,
            "basecov_gen_bin_care_home": False,
            "basecov_gen_num_sbp": 180,
            "basecov_gen_date_sbp": date(2020, 1, 1),
            "basecov_gen_num_uacr": 17.566 / 1.7566,
            "basecov_gen_date_uacr": date(2021, 6, 1),
            "basecov_gen_cat_uacr_category": "A2",
            "basecov_gen_cat_uacr_source": "uPCR",
            "basecov_gen_cat_smoker_status": "E",
            "basecov_gen_bin_dm": True,
            "basecov_gen_bin_cvd_history": True,
            "basecov_gen_num_n_scr_tests": 1,
            "basecov_gen_bin_cms_cancer": 1,
            "basecov_gen_num_cms": 0.213652 + 1.202615,
        },
    },


    10: {
        # tests:
        #   - no snomed or sus ethnicity code - so should be Missing
        #   - two active addresses - most recent start date used
        #   - no active registration at index date
        #   - BP after index or null only
        #   - diabetes drug within the last year
        #   - MI after index only -> no CVD
        #   - uPCR only, converted (male)
        #   - most recent smoking code N but smoked before -> E
        #   - CMS: first cancer code more than 5 years ago, later code ignored

        "patients": {
            "date_of_birth": date(1950, 1, 1),
            "sex": "male",
        },

        "addresses": [
            {
                "start_date": date(2010, 1, 1),
                "end_date": date(2030, 1, 1),
                "imd_rounded": 3000,
                "care_home_is_potential_match": True,
            },
            {
                "start_date": date(2012, 1, 1), # OS prefers the most recent one
                "end_date": None,
                "imd_rounded": 30000,
                "care_home_is_potential_match": False,
            },
        ],

        "clinical_events": [
            {
                "date": date(2023, 1, 1),
                "snomedct_code": "271649006",       # BP after index
                "numeric_value": 150
            },
            {
                "date": date(2022, 1, 1),
                "snomedct_code": "271649006",       # BP in right date range, but null
                "numeric_value": None
            },
            {
                "date": date(2023, 1, 1),
                "snomedct_code": "22298006"         # MI after index
            },
            {
                "date": date(2021, 6, 1),
                "snomedct_code": "1006631000000104", # uPCR only
                "numeric_value": 26.55
            },
            {
                "date": date(2015, 1, 1),
                "ctv3_code": "1372.",               # smoker
            },
            {
                "date": date(2021, 1, 1),
                "ctv3_code": "1371.",               # never smoker - most recent
            },
            {
                "date": date(2016, 1, 1),
                "snomedct_code": "254837009",       # breast cancer - first code > 5y ago
            },
            {
                "date": date(2021, 1, 1),
                "snomedct_code": "254837009",       # breast cancer - later code
            },
        ],

        "ethnicity_from_sus": {},

        "practice_registrations": [
            {
                "start_date": date(2010, 1, 1),
                "end_date": date(2020, 1, 1),
                "practice_nuts1_region_name": "East Midlands",
            },
        ],

        "apcs": [],

        "medications": [
            {
                "date": date(2021, 6, 1),
                "dmd_code": "40033011000001107",    # diabetes drug
            },
        ],

        "ons_deaths": {},

        "expected_in_population": True,
        "expected_columns": {
            "basecov_gen_cat_ethnicity": "Missing",
            "basecov_gen_cat_imd": "5 (least deprived)",
            "basecov_gen_cat_region": None,
            "basecov_gen_bin_care_home": False,
            "basecov_gen_num_sbp": None,
            "basecov_gen_date_sbp": None,
            "basecov_gen_num_uacr": 26.55 / 2.655,
            "basecov_gen_date_uacr": date(2021, 6, 1),
            "basecov_gen_cat_uacr_category": "A2",
            "basecov_gen_cat_uacr_source": "uPCR",
            "basecov_gen_cat_smoker_status": "E",
            "basecov_gen_bin_dm": True,
            "basecov_gen_bin_cvd_history": False,
            "basecov_gen_bin_cms_cancer": 0,
            "basecov_gen_num_cms": 0.213652,
        },
    },


    12: {
        # tests:
        #   - snomed ethnicity used over sus
        #   - IMD 6600 -> group 2
        #   - care home via requires nursing flag only
        #   - most recent BP below range (39) so earlier 40 used
        #   - most recent BMI out of range so earlier 24.9 used
        #   - most recent uACR out of range so earlier used
        #   - smoking code after index ignored -> N
        #   - most recent hba1c out of range so earlier 50 used -> diabetes
        #   - CVD via MI in secondary care only
        #   - CMS: anxiety code within the last year

        "patients": {
            "date_of_birth": date(1950, 1, 1),
            "sex": "male",
        },

        "addresses": [
            {
                "start_date": date(2010, 1, 1),
                "end_date": None,
                "imd_rounded": 6600,
                "care_home_is_potential_match": False,
                "care_home_requires_nursing": True,
            },
        ],

        "clinical_events": [
            {
                "date": date(2020, 1, 1),
                "snomedct_code": "40165009"         # Buriats ethnicity - 3
            },
            {
                "date": date(2021, 1, 1),
                "snomedct_code": "271649006",       # BP lower bound
                "numeric_value": 40
            },
            {
                "date": date(2021, 6, 1),
                "snomedct_code": "271649006",       # BP below range
                "numeric_value": 39
            },
            {
                "date": date(2021, 1, 1),
                "snomedct_code": "60621009",        # BMI
                "numeric_value": 24.9
            },
            {
                "date": date(2021, 6, 1),
                "snomedct_code": "60621009",        # BMI out of range
                "numeric_value": 150
            },
            {
                "date": date(2021, 1, 1),
                "snomedct_code": "1023491000000104", # uACR
                "numeric_value": 5
            },
            {
                "date": date(2021, 6, 1),
                "snomedct_code": "1023491000000104", # uACR out of range
                "numeric_value": 3000
            },
            {
                "date": date(2021, 1, 1),
                "ctv3_code": "1371.",               # never smoker
            },
            {
                "date": date(2022, 6, 1),
                "ctv3_code": "1372.",               # smoker - after index
            },
            {
                "date": date(2021, 1, 1),
                "snomedct_code": "999791000000106", # hba1c
                "numeric_value": 50
            },
            {
                "date": date(2021, 6, 1),
                "snomedct_code": "999791000000106", # hba1c out of range
                "numeric_value": 250
            },
            {
                "date": date(2021, 6, 1),
                "snomedct_code": "21897009",        # generalised anxiety disorder
            },
        ],

        "ethnicity_from_sus": {
            "code": "A"
        },

        "practice_registrations": [],

        "apcs": [
            {
                "admission_date": date(2021, 1, 1),
                "all_diagnoses": "I21",         # MI
                "all_procedures": None,
            },
        ],

        "medications": [],

        "ons_deaths": {},

        "expected_in_population": True,
        "expected_columns": {
            "basecov_gen_cat_ethnicity": "Asian",
            "basecov_gen_cat_imd": "2",
            "basecov_gen_bin_care_home": True,
            "basecov_gen_num_sbp": 40,
            "basecov_gen_date_sbp": date(2021, 1, 1),
            "basecov_gen_num_bmi_value": 24.9,
            "basecov_gen_cat_bmi_category": "Healthy weight (18.5-24.9)",
            "basecov_gen_date_bmi": date(2021, 1, 1),
            "basecov_gen_num_uacr": 5,
            "basecov_gen_date_uacr": date(2021, 1, 1),
            "basecov_gen_cat_uacr_category": "A2",
            "basecov_gen_cat_uacr_source": "uACR",
            "basecov_gen_cat_smoker_status": "N",
            "basecov_gen_bin_dm": True,
            "basecov_gen_bin_cvd_history": True,
            "basecov_gen_bin_cms_anxiety": 1,
            "basecov_gen_num_cms": 0.213652 + 0.324207,
        },
    },


    16: {
        # tests:
        #   - most recent BP above range (301) so earlier 300 used
        #   - BMI 10 lower bound -> Underweight
        #   - uACR after index only -> Missing
        #   - non-T1 diabetes code
        #   - CVD via stroke in primary care
        #   - CMS: anxiety code > 1 year ago and only 3 prescriptions -> no
        #   - CMS: 4 IBS prescriptions in last year -> bowel

        "patients": {
            "date_of_birth": date(1950, 1, 1),
            "sex": "female",
        },

        "clinical_events": [
            {
                "date": date(2021, 1, 1),
                "snomedct_code": "271649006",       # BP upper bound
                "numeric_value": 300
            },
            {
                "date": date(2021, 6, 1),
                "snomedct_code": "271649006",       # BP above range
                "numeric_value": 301
            },
            {
                "date": date(2021, 6, 1),
                "snomedct_code": "60621009",        # BMI
                "numeric_value": 10.0
            },
            {
                "date": date(2022, 6, 1),
                "snomedct_code": "1023491000000104", # uACR after index
                "numeric_value": 50
            },
            {
                "date": date(2015, 1, 1),
                "snomedct_code": "112991000000101", # non-T1 diabetes
            },
            {
                "date": date(2018, 1, 1),
                "snomedct_code": "1078001000000105", # haemorrhagic stroke
            },
            {
                "date": date(2020, 6, 1),
                "snomedct_code": "21897009",        # anxiety - outside last year
            },
        ],

        "medications": [
            {"date": date(2021, 6, 1), "dmd_code": "39704111000001102"},  # sertraline x3
            {"date": date(2021, 9, 1), "dmd_code": "39704111000001102"},
            {"date": date(2021, 12, 1), "dmd_code": "39704111000001102"},
            {"date": date(2021, 4, 1), "dmd_code": "18030911000001104"},  # alverine x4
            {"date": date(2021, 7, 1), "dmd_code": "18030911000001104"},
            {"date": date(2021, 10, 1), "dmd_code": "18030911000001104"},
            {"date": date(2022, 1, 1), "dmd_code": "18030911000001104"},
        ],

        "addresses": [],
        "ethnicity_from_sus": {},
        "practice_registrations": [],
        "apcs": [],
        "ons_deaths": {},

        "expected_in_population": True,
        "expected_columns": {
            "basecov_gen_num_sbp": 300,
            "basecov_gen_date_sbp": date(2021, 1, 1),
            "basecov_gen_num_bmi_value": 10.0,
            "basecov_gen_cat_bmi_category": "Underweight (<18.5)",
            "basecov_gen_num_uacr": None,
            "basecov_gen_cat_uacr_category": "Missing",
            "basecov_gen_cat_uacr_source": "Missing",
            "basecov_gen_bin_dm": True,
            "basecov_gen_bin_cvd_history": True,
            "basecov_gen_bin_cms_anxiety": 0,
            "basecov_gen_bin_cms_bowel": 1,
            "basecov_gen_num_cms": 0.213652 + -0.20368,
        },
    },


    17: {
        # tests:
        #   - BMI 18.4 -> Underweight
        #   - uACR 3 boundary -> A1
        #   - diabetes drug exactly 365 days before index -> excluded
        #   - CVD via stroke in secondary care
        #   - CMS: 4 constipation prescriptions but one on day 365 -> no
        #   - CMS: 4 antiepileptics for pain, no epilepsy code -> pain

        "patients": {
            "date_of_birth": date(1950, 1, 1),
            "sex": "male",
        },

        "clinical_events": [
            {
                "date": date(2021, 6, 1),
                "snomedct_code": "60621009",        # BMI
                "numeric_value": 18.4
            },
            {
                "date": date(2021, 6, 1),
                "snomedct_code": "1023491000000104", # uACR
                "numeric_value": 3.0
            },
        ],

        "apcs": [
            {
                "admission_date": date(2019, 1, 1),
                "all_diagnoses": "I63",         # cerebral infarction
                "all_procedures": None,
            },
        ],

        "medications": [
            {"date": date(2021, 3, 1), "dmd_code": "40033011000001107"},  # diabetes drug - day 365
            {"date": date(2021, 3, 1), "dmd_code": "3476811000001101"},   # ispaghula x4 - first on day 365
            {"date": date(2021, 6, 1), "dmd_code": "3476811000001101"},
            {"date": date(2021, 9, 1), "dmd_code": "3476811000001101"},
            {"date": date(2021, 12, 1), "dmd_code": "3476811000001101"},
            {"date": date(2021, 6, 1), "dmd_code": "42135711000001109"},  # pregabalin x4
            {"date": date(2021, 8, 1), "dmd_code": "42135711000001109"},
            {"date": date(2021, 10, 1), "dmd_code": "42135711000001109"},
            {"date": date(2021, 12, 1), "dmd_code": "42135711000001109"},
        ],

        "addresses": [],
        "ethnicity_from_sus": {},
        "practice_registrations": [],
        "ons_deaths": {},

        "expected_in_population": True,
        "expected_columns": {
            "basecov_gen_num_bmi_value": 18.4,
            "basecov_gen_cat_bmi_category": "Underweight (<18.5)",
            "basecov_gen_num_uacr": 3.0,
            "basecov_gen_cat_uacr_category": "A1",
            "basecov_gen_bin_dm": False,
            "basecov_gen_bin_cvd_history": True,
            "basecov_gen_bin_cms_constipation": 0,
            "basecov_gen_bin_cms_epilepsy": 0,
            "basecov_gen_bin_cms_pain": 1,
            "basecov_gen_num_cms": 0.213652 + 0.445521,
        },
    },


    18: {
        # tests:
        #   - BMI 18.5 boundary -> Healthy weight
        #   - uACR 30 boundary -> A2
        #   - diabetes drug 364 days before index -> included
        #   - CVD via HF in primary care (also in CMS HF list)
        #   - CMS: epilepsy code + pregabalin in last year -> epilepsy
        #   - CMS: 4 antiepileptics for pain but has epilepsy code -> no pain

        "patients": {
            "date_of_birth": date(1950, 1, 1),
            "sex": "female",
        },

        "clinical_events": [
            {
                "date": date(2021, 6, 1),
                "snomedct_code": "60621009",        # BMI
                "numeric_value": 18.5
            },
            {
                "date": date(2021, 6, 1),
                "snomedct_code": "1023491000000104", # uACR
                "numeric_value": 30.0
            },
            {
                "date": date(2019, 1, 1),
                "snomedct_code": "10633002",        # acute congestive heart failure
            },
            {
                "date": date(2000, 1, 1),
                "snomedct_code": "84757009",        # epilepsy
            },
        ],

        "medications": [
            {"date": date(2021, 3, 2), "dmd_code": "40033011000001107"},  # diabetes drug - day 364
            {"date": date(2021, 6, 1), "dmd_code": "42135711000001109"},  # pregabalin x4
            {"date": date(2021, 8, 1), "dmd_code": "42135711000001109"},
            {"date": date(2021, 10, 1), "dmd_code": "42135711000001109"},
            {"date": date(2021, 12, 1), "dmd_code": "42135711000001109"},
        ],

        "addresses": [],
        "ethnicity_from_sus": {},
        "practice_registrations": [],
        "apcs": [],
        "ons_deaths": {},

        "expected_in_population": True,
        "expected_columns": {
            "basecov_gen_num_bmi_value": 18.5,
            "basecov_gen_cat_bmi_category": "Healthy weight (18.5-24.9)",
            "basecov_gen_num_uacr": 30.0,
            "basecov_gen_cat_uacr_category": "A2",
            "basecov_gen_bin_dm": True,
            "basecov_gen_bin_cvd_history": True,
            "basecov_gen_bin_cms_hf": 1,
            "basecov_gen_bin_cms_epilepsy": 1,
            "basecov_gen_bin_cms_pain": 0,
            "basecov_gen_num_cms": 0.213652 + 0.505245 + 0.477465,
        },
    },


    19: {
        # tests:
        #   - BMI 25 boundary -> Overweight
        #   - uACR and uPCR on same day -> uACR used, A3
        #   - most recent hba1c 47 (earlier 60) -> no diabetes
        #   - CVD via HF in secondary care (not in CMS HF)
        #   - CMS: dementia code after ONS death date -> ignored
        #   - CMS: AF code before date of birth -> ignored
        #   - CMS: epilepsy code but prescription > 1 year ago -> no
        #   - CMS: 4 constipation prescriptions in last year -> constipation
        #   - CMS: 4 analgesic prescriptions in last year -> pain
        #   - NB died before index (dummy cohort) - prescriptions before death

        "patients": {
            "date_of_birth": date(1950, 1, 1),
            "sex": "female",
        },

        "ons_deaths": {
            "date": date(2021, 12, 1),
        },

        "clinical_events": [
            {
                "date": date(2021, 6, 1),
                "snomedct_code": "60621009",        # BMI
                "numeric_value": 25.0
            },
            {
                "date": date(2021, 6, 1),
                "snomedct_code": "1023491000000104", # uACR - same day as uPCR
                "numeric_value": 31
            },
            {
                "date": date(2021, 6, 1),
                "snomedct_code": "1006631000000104", # uPCR - same day as uACR
                "numeric_value": 100
            },
            {
                "date": date(2019, 1, 1),
                "snomedct_code": "999791000000106", # hba1c - older
                "numeric_value": 60
            },
            {
                "date": date(2021, 1, 1),
                "snomedct_code": "999791000000106", # hba1c - most recent
                "numeric_value": 47
            },
            {
                "date": date(2022, 1, 1),
                "snomedct_code": "52448006",        # dementia - after death
            },
            {
                "date": date(1940, 1, 1),
                "snomedct_code": "49436004",        # AF - before date of birth
            },
            {
                "date": date(2000, 1, 1),
                "snomedct_code": "84757009",        # epilepsy
            },
        ],

        "apcs": [
            {
                "admission_date": date(2019, 1, 1),
                "all_diagnoses": "I50",         # heart failure
                "all_procedures": None,
            },
        ],

        "medications": [
            {"date": date(2020, 6, 1), "dmd_code": "42137911000001101"},  # valproic acid - > 1 year ago
            {"date": date(2021, 4, 1), "dmd_code": "3476811000001101"},   # ispaghula x4
            {"date": date(2021, 6, 1), "dmd_code": "3476811000001101"},
            {"date": date(2021, 8, 1), "dmd_code": "3476811000001101"},
            {"date": date(2021, 10, 1), "dmd_code": "3476811000001101"},
            {"date": date(2021, 4, 15), "dmd_code": "42009811000001101"}, # co-codamol x4
            {"date": date(2021, 6, 15), "dmd_code": "42009811000001101"},
            {"date": date(2021, 8, 15), "dmd_code": "42009811000001101"},
            {"date": date(2021, 10, 15), "dmd_code": "42009811000001101"},
        ],

        "addresses": [],
        "ethnicity_from_sus": {},
        "practice_registrations": [],

        "expected_in_population": True,
        "expected_columns": {
            "basecov_gen_num_bmi_value": 25.0,
            "basecov_gen_cat_bmi_category": "Overweight (25-29.9)",
            "basecov_gen_num_uacr": 31,
            "basecov_gen_cat_uacr_category": "A3",
            "basecov_gen_cat_uacr_source": "uACR",
            "basecov_gen_bin_dm": False,
            "basecov_gen_bin_cvd_history": True,
            "basecov_gen_bin_cms_hf": 0,
            "basecov_gen_bin_cms_dementia": 0,
            "basecov_gen_bin_cms_af": 0,
            "basecov_gen_bin_cms_epilepsy": 0,
            "basecov_gen_bin_cms_constipation": 1,
            "basecov_gen_bin_cms_pain": 1,
            "basecov_gen_num_cms": 0.213652 + 0.383006 + 0.445521,
        },
    },

}
