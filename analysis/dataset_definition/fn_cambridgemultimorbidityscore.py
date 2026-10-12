### FROM ROB/ZOE

from codelists import multimorbidity_codelists_dict
from ehrql.tables.tpp import patients, clinical_events, medications
from functools import reduce
from ehrql import case, when, days
import operator
from variable_helper_functions import (
    ever_matching_event_clinical_snomed_before, 
    ever_matching_med_dmd_before
)

# Small functions that combine lists of T/F 
# conditions with OR (any_of) or AND (all_of)
def any_of(conditions):
    return reduce(operator.or_, conditions)
def all_of(conditions):
    return reduce(operator.and_, conditions)

# Check a date is 'plausible': not missing, not before DOB, and not after date of death
# If date is plausible, function just returns the date, otherwise returns NULL
def check_date_validity(
    date_to_check,
    death_date,
    check_not_before_dob=True,
    check_not_after_death=True
):

    # Collect each validity check in conditions list
    conditions = []

    ## Firstly date must not be null
    conditions.append(date_to_check.is_not_null())

    ## Check date not before DOB
    if check_not_before_dob:
        conditions.append(
            patients.date_of_birth.is_null()
            | (date_to_check.is_on_or_after(patients.date_of_birth))
        )

    ## Check date not after death
    if check_not_after_death:
        conditions.append(
            death_date.is_null()
            | (date_to_check.is_on_or_before(death_date))
        )

    ## Combine all validity conditions with AND
    is_valid = all_of(conditions)

    return case(
        when(is_valid).then(date_to_check),
        otherwise=None
    )

def has_condition_before(
    index_date,
    death_date,
    snomed=None,
    dmd1=None,
    dmd2=None,
    where=True,
    snomed_window_days=None,
    dmd_window_days=None,    
    dmd_min_count=1,          
    combine="any"
):
    conditions = []

    if snomed is not None:
        filtered = ever_matching_event_clinical_snomed_before(
            snomed, 
            index_date, 
            where=where
        )

        if snomed_window_days is not None:
            filtered = filtered.where(filtered.date.is_after(index_date - days(snomed_window_days)))

        conditions.append(
            filtered.where(
                check_date_validity(
                    filtered.date, 
                    death_date = death_date
                    ).is_not_null()
                ).exists_for_patient()
            )

    for dmd in [dmd1, dmd2]:
        if dmd is not None:
            filtered = ever_matching_med_dmd_before(
                dmd, 
                index_date, 
                where=where
            )

            if dmd_window_days is not None:
                filtered = filtered.where(filtered.date.is_after(index_date - days(dmd_window_days)))

            conditions.append(
                filtered.where(
                    check_date_validity(
                        filtered.date, 
                        death_date=death_date
                        ).is_not_null()
                ).count_for_patient() >= dmd_min_count
            )

    if not conditions:
        raise ValueError(
            "Must provide at least one SNOMED or DMD codelist."
        )

    return all_of(conditions) if combine == "all" else any_of(conditions)

## This code is adapted from Zoe Zou at https://github.com/opensafely/cambridge-multimorbidity-score/tree/Codelists-for-CMS
## It calculates the cambridge mulimorbidity score for a patient based on their clinical events and medications, using the specified index date.
## It can return either the total score or the individual components of the score.
def get_cms_on_date(index_date, death_date, return_components=False):

    mm = multimorbidity_codelists_dict

    # List of all the CMS conditions in the format:
    #  name, weight, rules (dict listing has_condition_before arguments that differ from the defaults) 
    cms_conditions = [
        ("alcohol", 0.65, dict(snomed=mm["MS_AlcoholProblem_snomed"])),
        ("anxiety", 0.50, dict(snomed=mm["MS_AnxietyDepression_snomed"], dmd1=mm["MS_AnxietyDepression_dmd"], snomed_window_days=365, dmd_window_days=365, dmd_min_count=4)),
        ("asthma", 0.19, dict(snomed=mm["MS_Asthma_snomed"], dmd1=mm["MS_Asthma_dmd"], dmd_window_days=365, combine="all")),
        ("af", 1.34, dict(snomed=mm["MS_AF_snomed"])),
        ("cancer", 1.53, dict(snomed=mm["MS_Cancer_snomed"])), # need to think about how to define first cancer code < 5 years ago
        # (ckd, 0.53 not unpacking here - all pts have CKD - added as a constant below)
        ("constipation", 1.12, dict(dmd1=mm["MS_Constipation_dmd"], dmd_window_days=365, dmd_min_count=4)),
        ("copd", 1.46, dict(snomed=mm["MS_COPD_snomed"])),
        ("ctd", 0.43, dict(snomed=mm["MS_CTD_snomed"])),
        ("chd", 0.49, dict(snomed=mm["MS_CHD_snomed"])),
        ("dementia", 2.50, dict(snomed=mm["MS_Dementia_snomed"])),
        ("diabetes", 0.75, dict(snomed=mm["MS_Diabetes_snomed"])),
        ("epilepsy", 0.92, dict(snomed=mm["MS_Epilepsy_snomed"], dmd1=mm["MS_Epilepsy_dmd"], dmd_window_days=365, combine="all")),
        ("hearing_loss", 0.09, dict(snomed=mm["MS_HL_snomed"])),
        ("hf", 1.18, dict(snomed=mm["MS_HF_snomed"])),
        ("hypertension", 0.08, dict(snomed=mm["MS_Hypertension_snomed"])),
        ("ibs", 0.21, dict(snomed=mm["MS_IBS_snomed"], dmd1=mm["MS_IBS_dmd"], dmd_window_days=365, dmd_min_count=4)),
        ("psychosis", 0.64, dict(snomed=mm["MS_Psychosis_snomed"], dmd1=mm["MS_Psychosis_dmd"])),
        ("stroke", 0.80, dict(snomed=mm["MS_StrokeTIA_snomed"])),
        ("pain", 0.92, dict(dmd1=mm["MS_PC_Analgesics_dmd"], dmd2=mm["MS_PC_Antiepileptic_dmd"], dmd_window_days=365, dmd_min_count=4)), # antiepileptic dmd codes should only count if no epilepsy code
    ]

    # Initiate CMS: patient-level series -> int -> float. 
    # Everyone gets 0.53 for having CKD
    cms = clinical_events.exists_for_patient().as_int().as_float() * 0 + 0.53
    components = {}

    for name, weight, rules in cms_conditions:
        binary = has_condition_before(
            index_date=index_date,
            death_date=death_date,
            **rules # unpacks dicts into named arguments
        ).as_int()

        cms += binary.as_float() * weight

        if return_components:
            components[name] = binary

    if return_components:
        components["cms"] = cms
        return components

    return cms