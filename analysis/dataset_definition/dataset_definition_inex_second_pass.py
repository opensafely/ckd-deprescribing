##########################################################################
# This script does the following:
# 1. Reads the study parameters from output/ckd_cohort_config.json
# 2. Defines the population from dataset_inex_first_pass_processed.arrow
# 3. Adds a flag for each CKD stage that the person could be in
#
# Output: output/dataset_inex_second_pass.arrow
# Test: test_dataset_definition_inex_second_pass.py
##########################################################################

from ehrql import create_dataset, table_from_file
import json
from fn_inex_second_pass import add_inex_second_pass_variables


with open("output/ckd_cohort_config.json") as f:
    config = json.load(f)
study_window_start = config["study_window_start"]
study_window_end = config["study_window_end"]
ckd_stages = config["ckd_stages"]

# population denominator = present after inex first pass
first_pass = table_from_file(
    "output/data/dataset_inex_first_pass_processed.arrow",
    columns={}
)

# initialise the dataset
dataset = create_dataset()
dataset.define_population(first_pass.exists_for_patient())

# add the second pass
add_inex_second_pass_variables(dataset, study_window_start, study_window_end, ckd_stages)