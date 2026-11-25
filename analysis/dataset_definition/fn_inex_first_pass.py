#####################################################################
# This script defines the screening variables for the CKD cohorts.
# These are all time-fixed or over the whole time window to make the 
# population smaller before moving onto the CKD cohort logic.
#####################################################################

#####################################################################
# IMPORTS
#####################################################################

from ehrql import case, when

from ehrql.tables.tpp import (
    patients,
    clinical_events,
    ons_deaths
)

from variable_helper_functions import (
    two_values_90d_apart,
    ever_matching_event_clinical_snomed_before
)

from codelists import creatinine_codes, uacr_codes_snomed
from datetime import date

#####################################################################
# QA SCREENING VARIABLES
#####################################################################
# generates booleans for each of the quality assurance criteria

def add_qa_inex_variables():
    
    today = date.today()

    dob_known = patients.date_of_birth.is_not_null()

    dob_before_dod_patients = (
        patients.date_of_death.is_null() |
        patients.date_of_birth.is_on_or_before(patients.date_of_death)
    )

    dob_before_dod_ons = (
        ons_deaths.date.is_null() |
        patients.date_of_birth.is_on_or_before(ons_deaths.date)
    )

    dob_before_dod = dob_before_dod_patients & dob_before_dod_ons

    dob_not_future = patients.date_of_birth.is_on_or_before(today)

    dod_not_future = (
        (patients.date_of_death.is_null() | patients.date_of_death.is_on_or_before(today)) &
        (ons_deaths.date.is_null() | ons_deaths.date.is_on_or_before(today))
    )

    return {
        "inex_qa_bin_dob_known": dob_known,
        "inex_qa_bin_dob_before_dod": dob_before_dod,
        "inex_qa_bin_dob_not_future": dob_not_future,
        "inex_qa_bin_dod_not_future": dod_not_future,
    }


#####################################################################
# DEMOGRAPHIC SCREENING VARIABLES
#####################################################################
# Simple booleans that will exclude people who would never make it 
# into any study cohort

def add_first_pass_dem_variables(study_window_start, study_window_end):

    known_sex = (
        (patients.sex == "male") |
        (patients.sex == "female")
    )

    age_possible = (
        (patients.age_on(study_window_end) >= 18)
        & (patients.age_on(study_window_start) <= 110)
    )

    alive_study_window_start = (
        (patients.date_of_death.is_null() | patients.date_of_death.is_after(study_window_start))
        & (ons_deaths.date.is_null() | ons_deaths.date.is_after(study_window_start))
    )

    return {
        "inex_dem_bin_sex": known_sex,
        "inex_dem_bin_age_possible": age_possible,
        "inex_dem_bin_alive_study_window_start": alive_study_window_start,
    }

#####################################################################
# CKD SCREENING VARIABLES
#####################################################################
# This flags people who would never make it into any CKD cohort as
# they don't have creatinine and/or uACR measurements

def add_first_pass_ckd_variables(
    study_window_start,
    study_window_end,
    scr_cutoff_female,
    scr_cutoff_male,
    uacr_cutoff,
):

    scr_cutoff = case(
        when(
            patients.sex == "male"
            ).then(scr_cutoff_male),
        otherwise=scr_cutoff_female # unknown sex will be removed later
    )

    all_scr_above_cutoff = ever_matching_event_clinical_snomed_before(
        creatinine_codes,
        study_window_end,
        where=(
            (clinical_events.numeric_value >= 20)
            & (clinical_events.numeric_value <= 3000)
            & (clinical_events.numeric_value > scr_cutoff)
        )
    )

    all_uacr_raised = ever_matching_event_clinical_snomed_before(
        uacr_codes_snomed,
        study_window_end,
        where=clinical_events.numeric_value > uacr_cutoff,
    )

    return {
        "inex_ckd_bin_two_scr_above_cutoff": two_values_90d_apart(
            all_scr_above_cutoff, study_window_start, study_window_end
        ),
        "inex_ckd_bin_two_uacr_raised": two_values_90d_apart(
            all_uacr_raised, study_window_start, study_window_end
        ),
    }

#####################################################################
# COMBINE ALL ABOVE VARIABLES TO ADD TO DATASET
#####################################################################

def add_inex_first_pass_variables(
    dataset, 
    study_window_start, 
    study_window_end,
    scr_cutoff_female,
    scr_cutoff_male,
    uacr_cutoff
):

    columns = {
        **add_qa_inex_variables(),
        **add_first_pass_dem_variables(
            study_window_start=study_window_start, 
            study_window_end=study_window_end
        ),
        **add_first_pass_ckd_variables(
            study_window_start=study_window_start, 
            study_window_end=study_window_end,
            scr_cutoff_female=scr_cutoff_female,
            scr_cutoff_male=scr_cutoff_male,
            uacr_cutoff=uacr_cutoff,
        )
    }

    for name, expr in columns.items():
        dataset.add_column(name, expr)
        