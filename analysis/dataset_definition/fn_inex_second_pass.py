#####################################################################
# This script provides the logic for the inex_second_pass dataset
# definition. this dataset definition flags people who COULD qualify
# for entry in the CKD cohorts based on the presence of 2+ eGFR 
# values below the stage thresholds
#####################################################################

#####################################################################
# IMPORTS
#####################################################################

from ehrql import minimum_of, maximum_of

from ehrql.tables.tpp import patients, clinical_events

from variable_helper_functions import (
    two_values_90d_apart,
    ever_matching_event_clinical_snomed_before
)

from codelists import creatinine_codes

#####################################################################
# eGFR PER CREATININE TEST
#####################################################################
# CKD-EPI 2009 without ethnicity coefficient, age on the test date.
# https://www.niddk.nih.gov/research-funding/research-programs/
# kidney-clinical-research-epidemiology/laboratory/
# glomerular-filtration-rate-equations/adults/previous/

# Returns:
# - scr - event frame of plausible creatinine events before window_end
# - egfr - eGFR value for each row in scr

def egfr_ckdepi2009(study_window_end):

    scr = ever_matching_event_clinical_snomed_before(
        creatinine_codes,
        study_window_end,
        where=(
            (clinical_events.numeric_value >= 20)
            & (clinical_events.numeric_value <= 3000)
        )
    )

    age = patients.age_on(scr.date)
    sex = patients.sex
    kappa = sex.map_values({"female": 61.9, "male": 79.6})
    alpha = sex.map_values({"female": -0.329, "male": -0.411})
    female_multiplier = sex.map_values({"female": 1.018, "male": 1.0})
    ratio = scr.numeric_value / kappa

    egfr = (
        141
        * minimum_of(ratio, 1.0) ** alpha
        * maximum_of(ratio, 1.0) ** -1.209
        * 0.993 ** age.as_float()
        * female_multiplier
    )

    return scr, egfr

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

    scr, egfr = egfr_ckdepi2009(study_window_end)
    
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
