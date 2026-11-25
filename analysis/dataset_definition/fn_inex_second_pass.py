#####################################################################
# This script provides the logic for the inex_second_pass dataset
# definition. this dataset definition flags people who COULD qualify
# for entry in the CKD cohorts based on the presence of 2+ eGFR 
# values below the stage thresholds
#####################################################################

#####################################################################
# IMPORTS
#####################################################################

from ehrql.tables.tpp import patients

from variable_helper_functions import (
    two_values_90d_apart,
    creatinine_events_before,
    egfr_ckdepi2009
)

#####################################################################
# eGFR SCREENING VARIABLES
#####################################################################
# This adds 4 columns to the dataset. These are designed to flag the 
# people who COULD be in the CKD cohorts based on eGFR measurements
# one flag per CKD stage if the individual has 2x eGFRs below the 
# stage's upper limit >= 90 days apart with the second in the study 
# window

def add_inex_second_pass_variables(
    dataset,
    study_window_start,
    study_window_end,
    ckd_stages
):

    scr = creatinine_events_before(study_window_end)
    egfr = egfr_ckdepi2009(scr.numeric_value, patients.age_on(scr.date), patients.sex)

    prior_flag = None

    # Loop through CKD 3a, 3b, 4 then 5
    for stage_name, stage_range in ckd_stages.items():
        upper = stage_range["upper"]

        # T/F test over the event frame: is eGFR below upper range?
        below_upper = egfr < upper

        # Prior flag = T/F per patient based on inclusion in earlier stage
        # Logic: to have an eGFR <15, MUST have flagged eGFR <30.
        # This restricts the patient numbers for each pass.
        if prior_flag is not None:
            below_upper = prior_flag & below_upper

        # Two_below_upper = T/F per patient
        two_below_upper = two_values_90d_apart(
            scr.where(below_upper), study_window_start, study_window_end
        )

        dataset.add_column(f"inex_ckd_bin_two_egfr_below_{upper}", two_below_upper)

        # flag those who met that stage's criteria for the next loop
        prior_flag = two_below_upper
