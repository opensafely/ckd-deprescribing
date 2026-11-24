#####################################################################
# This script provides the logic for the inex_ckd_cohort dataset
# definition. This is the meat of the creatinine/eGFR based detection
# of people living with incident CKD of varying stages
#####################################################################

#####################################################################
# IMPORTS
#####################################################################

from ehrql import days, case, when
from ehrql.tables.tpp import practice_registrations
from fn_inex_second_pass import egfr_ckdepi2009


def add_inex_ckd_cohort_variables(
    dataset,
    study_window_start,
    study_window_end,
    ckd_stage,
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
            .date.minimum_for_patient()
        )

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

    # eGFR0 = the last eGFR on or above the limit before eGFR1
    egfr0_date = all_high_egfrs.where(
        all_high_egfrs.date.is_before(egfr1_date)
    ).date.maximum_for_patient()

    # registration rule - STILL NEEDS DEFINING
    registration = practice_registrations.for_patient_on(egfr2_date)
    same_registration = egfr0_date.is_on_or_after(registration.start_date)

    dataset.add_column("inex_date_egfr0", egfr0_date)
    dataset.add_column("inex_date_egfr1", egfr1_date)
    dataset.add_column("inex_date_index_date", egfr2_date)
    dataset.add_column("inex_ckd_bin_unresolved", unresolved)
    dataset.add_column("inex_num_n_loop_restarts", n_loop_restarts)
    dataset.add_column("inex_ckd_bin_same_registration", same_registration)


