#####################################################################
# This script provides the logic for the inex_ckd_cohort dataset
# definition. This is:
# - the meat of the creatinine/eGFR based detection of people living 
#   with incident CKD of varying stages
# - and then the inclusion/exclusion criteria on the cohort index dates
#####################################################################

#####################################################################
# IMPORTS
#####################################################################

from ehrql import days, case, when, months

from ehrql.tables.tpp import (
    practice_registrations, 
    patients, 
    ons_deaths,
    apcs,
    clinical_events
)

from variable_helper_functions import (
    ever_matching_event_clinical_snomed_before,
    count_recent_meds
)    

from fn_inex_second_pass import egfr_ckdepi2009

from codelists import (
    primary_care_krt_codes,
    primary_care_dialysis_codes,
    primary_care_ktx_codes,
    secondary_care_krt_codes_opcs4,
    secondary_care_dialysis_codes_opcs4,
    secondary_care_ktx_codes_opcs4,
    secondary_care_krt_codes_icd10,
    secondary_care_dialysis_codes_icd10,
    secondary_care_ktx_codes_icd10
)

#####################################################################
# CKD cohort computation
#####################################################################

def define_ckd_cohorts(
    study_window_end,
    upper_limit,
    k_loops
):

    scr, egfr = egfr_ckdepi2009(study_window_end)

    # Define two event frames based on whether the eGFRs are above
    # or below (high or low) the upper limit for this stage of CKD
    all_low_egfrs = scr.where(egfr < upper_limit)
    all_high_egfrs = scr.where(egfr >= upper_limit)

    # eGFR1 = first eGFR ever that is below the limit
    egfr1_date = all_low_egfrs.date.minimum_for_patient()

    # loop through eGFRs to find the first low ones that are not broken
    # by a value higher than the limit. 
    n_loop_restarts = 0
    for loop_n in range(k_loops + 1):

        # eGFR2 = the first eGFR that is 90+ days after eGFR1 and below the limit
        egfr2_date = all_low_egfrs.where(
            all_low_egfrs.date.is_on_or_after(egfr1_date + days(90))
        ).date.minimum_for_patient()

        # eGFR3 = the last eGFR between eGFR1 and eGFR2 that is above the limit
        egfr3_date = all_high_egfrs.where(
            all_high_egfrs.date.is_after(egfr1_date)
            & all_high_egfrs.date.is_before(egfr2_date)
        ).date.maximum_for_patient()

        # n_loop_restarts counts how many iterations of this loop each person needs -1
        egfr3_exists = egfr3_date.is_not_null()
        n_loop_restarts = n_loop_restarts + case(when(egfr3_exists).then(1), otherwise=0)

        if loop_n < k_loops:
            egfr1_date = case(
                when(egfr3_date.is_not_null()).then(
                    all_low_egfrs.where(
                        all_low_egfrs.date.is_after(egfr3_date)
                    ).date
                    .minimum_for_patient()
                ),
                otherwise=egfr1_date
            )
    
    unresolved = egfr3_date.is_not_null()
    no_egfr2 = egfr2_date.is_null()

    # eGFR0 = the last eGFR on or above the limit before eGFR1
    egfr0_date = all_high_egfrs.where(
        all_high_egfrs.date.is_before(egfr1_date)
    ).date.maximum_for_patient()

    no_egfr0 = egfr0_date.is_null()

    # for interest: flag when a single registration spans eGFR0 to eGFR2
    same_registration = (
        practice_registrations
        .spanning(egfr0_date, egfr2_date)
        .exists_for_patient()
    )

    return {

        "inex_ckd_date_egfr1": egfr1_date,
        "inex_ckd_date_index_date": egfr2_date,
        "inex_ckd_bin_no_egfr0": no_egfr0,
        "inex_ckd_date_egfr0": egfr0_date,
        "inex_ckd_bin_unresolved": unresolved,
        "inex_ckd_bin_no_egfr2": no_egfr2,
        "inex_ckd_num_n_loop_restarts": n_loop_restarts,
        "inex_ckd_bin_same_registration": same_registration

    }

#####################################################################
# Demographics variables
#####################################################################

def add_demographic_inex_variables(
    index_date
):

    age = patients.age_on(index_date)

    alive = (
        ((patients.date_of_death.is_null()) |
             (patients.date_of_death.is_after(index_date))) &
            ((ons_deaths.date.is_null()) |
             (ons_deaths.date.is_after(index_date)))
    )

    is_registered = (
            practice_registrations
            .where(
                practice_registrations.start_date.is_on_or_before(index_date) &
                (
                    practice_registrations.end_date.is_null() |
                    practice_registrations.end_date.is_after(index_date)
                )
            )
        ).exists_for_patient(
    )
    
    registered_12m = (
            practice_registrations
            .where(
                practice_registrations.start_date.is_on_or_before(index_date - months(12)) &
                (
                    practice_registrations.end_date.is_null() |
                    practice_registrations.end_date.is_after(index_date)
                )
            )
        ).exists_for_patient(
    )

    return {

        "inex_dem_bin_alive": alive,
        "inex_dem_bin_age_include": (age >= 18) & (age <= 110),
        "inex_dem_bin_is_registered": is_registered,
        "inex_dem_bin_12m_registered": registered_12m, 
        "inex_dem_num_age": age,
        "inex_dem_cat_sex": patients.sex,

    }

#####################################################################
# KRT variables
#####################################################################
# Primary care codes used for exclusion; secondary care codes kept
# with a sensitivity flag (inex_krt_bin_secondary_care_only)

def add_krt_inex_variables(
    index_date,
):
   
    ### Primary care codes - all SNOMED CT ###
   
    # SNOMED krt events before index date
    primary_care_krt_code = ever_matching_event_clinical_snomed_before(
        primary_care_krt_codes, index_date
    )

    # binary flag if a person has a primary care krt code prior to index date
    has_primary_care_krt_code = primary_care_krt_code.exists_for_patient()

    # most recent primary care krt event
    most_recent_primary_care_krt_code = (
        primary_care_krt_code
        .sort_by(clinical_events.date)
        .last_for_patient()
    )

    # type of most recent krt code (dialysis/transplant)
    primary_care_krt_type = case(
        when(
            most_recent_primary_care_krt_code.snomedct_code.is_in(primary_care_dialysis_codes)
        ).then("dialysis"),
        when(
             most_recent_primary_care_krt_code.snomedct_code.is_in(primary_care_ktx_codes)
        ).then("transplant"),
        otherwise=None,
    )

    
    ### Secondary care codes - ICD10 and OPCS4 ###
       
    # OPCS4 or ICD10 code before index date
    secondary_care_krt_code = (
        apcs
        .where(
            apcs.all_diagnoses.contains_any_of(secondary_care_krt_codes_icd10)
            | apcs.all_procedures.contains_any_of(secondary_care_krt_codes_opcs4)
        )
        .where(apcs.admission_date.is_on_or_before(index_date))
    )

    # binary flag if a person has a secondary care krt code
    has_secondary_care_krt_code = secondary_care_krt_code.exists_for_patient()

    # Most recent spell containing a secondary care krt code
    most_recent_secondary_care_krt_code = (
        secondary_care_krt_code
        .sort_by(apcs.admission_date)
        .last_for_patient()
    )

    # Importantly any spell can contain both transplant and dialysis codes so need
    # quite complex logic to decide whether to categorise as dialysis or transplant
    secondary_care_krt_type = case(
        # sort edge case first where BOTH dialysis AND transplant in same spell → unknown
        when(
            (
                most_recent_secondary_care_krt_code.all_procedures.contains_any_of(
                    secondary_care_dialysis_codes_opcs4
                )
                | most_recent_secondary_care_krt_code.all_diagnoses.contains_any_of(
                    secondary_care_dialysis_codes_icd10
                )
            )
            &
            (
                most_recent_secondary_care_krt_code.all_procedures.contains_any_of(
                    secondary_care_ktx_codes_opcs4
                )
                | most_recent_secondary_care_krt_code.all_diagnoses.contains_any_of(
                    secondary_care_ktx_codes_icd10
                )
            )
        ).then("unknown"),
        # Dialysis only
        when(
            most_recent_secondary_care_krt_code.all_procedures.contains_any_of(
                secondary_care_dialysis_codes_opcs4
            )
            | most_recent_secondary_care_krt_code.all_diagnoses.contains_any_of(
                secondary_care_dialysis_codes_icd10
            )
        ).then("dialysis"),
        # Transplant only
        when(
            most_recent_secondary_care_krt_code.all_procedures.contains_any_of(
                secondary_care_ktx_codes_opcs4
            )
            | most_recent_secondary_care_krt_code.all_diagnoses.contains_any_of(
                secondary_care_ktx_codes_icd10
            )
        ).then("transplant"),
        # Any other KRT-related spell
        when(
            most_recent_secondary_care_krt_code.apcs_ident.is_not_null()
        ).then("unknown"),

        otherwise=None,
    )
    
    ### Return variables ###

    return {

        # Primary care only
        "inex_krt_bin_has_primary_care_krt_code": has_primary_care_krt_code,
        "inex_krt_cat_primary_care_krt_type": primary_care_krt_type,

        # Secondary care only
        "inex_krt_bin_has_secondary_care_krt_code": has_secondary_care_krt_code,
        "inex_krt_cat_secondary_care_krt_type": secondary_care_krt_type,

        # Sensitivity flag: secondary care evidence without primary care evidence
        "inex_krt_bin_secondary_care_only": (
            has_secondary_care_krt_code & ~has_primary_care_krt_code
        ),

    }

#######################################################################
# simple pre-index medication counts
#######################################################################

def add_medication_inex_variables(
    index_date
):

    return {
        "inex_med_num_90": (
            count_recent_meds(index_date, days_before_index=90)
        ),

        "inex_med_num_180": (
            count_recent_meds(index_date, days_before_index=180)
        )
    }


#####################################################################
# COMBINE ALL ABOVE VARIABLES INTO ONE FUNCTION TO ADD TO DATASET
#####################################################################

def add_inex_ckd_cohort_variables(
    dataset,
    study_window_start,
    study_window_end,
    upper_limit,
    k_loops
):

    ckd_cohort = define_ckd_cohorts(
        study_window_end=study_window_end,
        upper_limit=upper_limit,
        k_loops=k_loops
    )

    # the index date is the date of eGFR2
    index_date = ckd_cohort["inex_ckd_date_index_date"]

    columns = {
        **ckd_cohort,
        **add_demographic_inex_variables(index_date),
        **add_krt_inex_variables(index_date),
        **add_medication_inex_variables(index_date),
        "inex_ckd_bin_index_in_window": index_date.is_on_or_between(
            study_window_start, study_window_end
        ),
    }

    for name, expr in columns.items():
        dataset.add_column(name, expr)

