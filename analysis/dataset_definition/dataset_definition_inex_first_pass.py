##########################################################################
# This script does the following:
# 1. Reads the study parameters from output/ckd_cohort_config.json
# 2. Defines the population as everyone registered at a TPP practice at
#    any point in the study window
# 3. Adds the first pass variables (QA, sex, age, alive, creatinine/uACR)
#
# Output: output/dataset_inex_first_pass.arrow
# Test: test_dataset_definition_inex_first_pass.py
##########################################################################

from ehrql import create_dataset
from ehrql.tables.tpp import practice_registrations
import json
from fn_inex_first_pass import add_inex_first_pass_variables


with open("output/ckd_cohort_config.json") as f:
    config = json.load(f)
study_window_start = config["study_window_start"]
study_window_end = config["study_window_end"]
scr_cutoff_female = config["first_pass_scr_cutoff"["female"]]
scr_cutoff_male = config["first_pass_scr_cutoff"["male"]]
uacr_cutoff = config["first_pass_uacr_cutoff"]

# initialise the dataset
dataset = create_dataset()
dataset.configure_dummy_data(population_size=1000)

# population denominator = registered at some point in the study period
registered_in_window = (
    practice_registrations.where(
        practice_registrations.start_date.is_on_or_before(study_window_end)
        & 
        (
            practice_registrations.end_date.is_null()
            | practice_registrations.end_date.is_on_or_after(study_window_start)
        )
    )
)

dataset.define_population(registered_in_window.exists_for_patient())

# add the first pass booleans to the dataset
add_inex_first_pass_variables(
    dataset, 
    study_window_start, 
    study_window_end,
    scr_cutoff_female,
    scr_cutoff_male,
    uacr_cutoff
)
