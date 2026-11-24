##########################################################################
# This script does the following:
# 1. Reads in the project config from output/ckd_cohort_config.json
# 2. Reads in the CKD stage from the --ckd_stage parameter in the .yaml
# 3. Defines the population: dataset_inex_second_pass_processed_{ckd_stage}.arrow
# 4. Runs the CKD cohort logic as defined in fn_inex_ckd_cohort.py
#
# Output: output/dataset_inex_ckd_cohort_{ckd_stage}.arrow
# Test: test_dataset_definition_inex_ckd_cohort.py
##########################################################################

from ehrql import create_dataset, table_from_file, get_parameter
import json
from fn_inex_ckd_cohort import add_inex_ckd_cohort_variables

# Read the .yaml parameter
ckd_stage = get_parameter(name="ckd_stage", type=str, default="")

# Load the config elements
with open("output/ckd_cohort_config.json") as f:
    config = json.load(f)
study_window_start = config["study_window_start"]
study_window_end = config["study_window_end"]
upper_limit = config["ckd_stages"][ckd_stage]["upper"]
k_loops = config["k_loops"]

# population denominator = present after inex second pass
second_pass = table_from_file(
    f"output/data/dataset_inex_second_pass_processed_{ckd_stage}.arrow",
    columns={}
)

# initialise the dataset
dataset = create_dataset()
dataset.define_population(second_pass.exists_for_patient())

# add the ckd_cohort variables
add_inex_ckd_cohort_variables(dataset, study_window_start, study_window_end, ckd_stage, upper_limit, k_loops)