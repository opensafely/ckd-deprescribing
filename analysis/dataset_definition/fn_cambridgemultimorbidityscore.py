##########################################################################
# Cambridge Multimorbidity Score (CMMS)
#
# Modified SNOMED CT version of the CMMS from Tsang et al. BJGP 2023
# (doi:10.3399/BJGP.2022.0235): 21-condition model with weights for
# 1-year mortality
#
# Acknowledgment to Dr Wen Shi from University of Cambridge and members of
# the Bristol EHR group (Rob Porteous and Dr Zoe Zou) whose ehrQL
# implementations this script reuses/adapts. Check this repo:
# https://github.com/opensafely/NeurodegenerativeDiseaseBurden/blob/main/
# analysis/dataset_definition/variable_helper_functions.py
##########################################################################

from ehrql.tables.tpp import patients, clinical_events
from functools import reduce
from ehrql import case, when, days
import operator
from codelists import cms_codelists_dict
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

# Does the patient meet the Multimorbidity Score criteria on the index date?
#   snomed condition met if EVER has a valid code on or before index date
#       - optional snomed_window_days e.g. code within last year (window = 365)
#       - optional snomed_first_within_days e.g FIRST code within the window
#   dmd1/dmd2 condition met if >= dmd_min_count prescription records EVER
#       - optional last dmd_window_days e.g codes within last year (window = 365)
#   combine: "any" (OR) or "all" (AND) across the criteria

def meets_cms_criteria(
    index_date,
    death_date,
    snomed=None,
    dmd1=None,
    dmd2=None,
    where=True,
    snomed_window_days=None,
    snomed_first_within_days=None,
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

        valid = filtered.where(
            check_date_validity(
                filtered.date,
                death_date=death_date
                ).is_not_null()
            )

        if snomed_first_within_days is not None:
            # only met if the FIRST valid code is within the window
            first_date = (
                valid.sort_by(valid.date)
                .first_for_patient()
                .date
            )
            conditions.append(
                first_date.is_not_null()
                & first_date.is_after(index_date - days(snomed_first_within_days))
            )

        else:
            conditions.append(valid.exists_for_patient())
        

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

## Calculate the total CMS
## It can return either the total score or the individual components of the score.
def get_cms_on_date(index_date, death_date, return_components=False):

    cl = cms_codelists_dict

    # List of all the CMS conditions in the format:
    #  name, weight, rules (dict listing meets_cms_critera() arguments that differ from the defaults) 
    cms_conditions = [

        # any diagnosis ever before
        ("alcohol", 0.792243, dict(snomed=cl["alcohol_snomed"])),
        ("af", 0.334891, dict(snomed=cl["af_snomed"])),
        ("copd", 0.702181, dict(snomed=cl["copd_snomed"])),
        ("dementia", 0.938001, dict(snomed=cl["dementia_snomed"])),
        ("diabetes", 0.29467, dict(snomed=cl["diabetes_snomed"])),
        ("hf", 0.505245, dict(snomed=cl["hf_snomed"])),
        ("cld", 0.68621, dict(snomed=cl["cld_snomed"])),
        ("prostate", -0.18781, dict(snomed=cl["prostate_snomed"])),
        ("learning", 0.637273, dict(snomed=cl["learning_disability_snomed"])),
        ("sclerosis", 0.761606, dict(snomed=cl["ms_snomed"])),
        ("parkinsonism", 0.546194, dict(snomed=cl["parkinsonism_snomed"])),
        ("perivascular_leg", 0.334558, dict(snomed=cl["pvd_snomed"])),
        ("psychosub_misuse", 0.449321, dict(snomed=cl["substance_misuse_snomed"])),

        # cancer = first diagnosis within last 5 years
        ("cancer", 1.202615, dict(snomed=cl["cancer_snomed"], snomed_first_within_days=1825)),

        # ckd (0.213652): added as a constant below - all pts have CKD 4-5

        # Epilepsy = diagnosis ever AND 1+ prescription in the last 12 months
        ("epilepsy", 0.477465, dict(snomed=cl["epilepsy_snomed"], dmd1=cl["epilepsy_dmd"], dmd_window_days=365, combine="all")),

        # IBS = diagnosis ever OR 4+ prescriptions in the last 12 months
        ("bowel", -0.20368, dict(snomed=cl["ibs_snomed"], dmd1=cl["ibs_dmd"], dmd_window_days=365, dmd_min_count=4)),

        # Psychosis/Bipolar = diagnosis ever OR ever prescribed lithium
        ("psychosis", 0.482469, dict(snomed=cl["psychosis_snomed"], dmd1=cl["psychosis_dmd"])),

        # Constipation = no diagnostic code, 4+ prescriptions within the last 12 months
        ("constipation", 0.383006, dict(dmd1=cl["constipation_dmd"], dmd_window_days=365, dmd_min_count=4)),

        # Anxiety/Depression = diagnosis within the last 12 months OR 4+ prescriptions in last 12 months
        ("anxiety", 0.324207, dict(snomed=cl["anxiety_snomed"], dmd1=cl["anxiety_dmd"], snomed_window_days=365, dmd_window_days=365, dmd_min_count=4)),

        # pain = more complex - see below
    ]

    # Initiate CMS: patient-level series -> int -> float. 
    # Everyone gets 0.213652 for having CKD
    cms = clinical_events.exists_for_patient().as_int().as_float() * 0 + 0.213652
    components = {}

    for name, weight, rules in cms_conditions:
        binary = meets_cms_criteria(
            index_date=index_date,
            death_date=death_date,
            **rules # unpacks dicts into named arguments
        ).as_int()

        cms += binary.as_float() * weight

        if return_components:
            components[name] = binary

    # Pain - weighting = 0.445521. Rule = EITHER of the following:
    #   4+ prescriptions from pain_analgesics_dmd in last 12 months OR
    #   4+ prescriptions from pain_antiepileptics_dmd in last 12 months if no diagnosis of epilepsy ever

    pain_med1 = meets_cms_criteria(
        index_date=index_date,
        death_date=death_date,
        dmd1=cl["pain_analgesics_dmd"],
        dmd_window_days=365,
        dmd_min_count=4
    )
    pain_med2 = meets_cms_criteria(
        index_date=index_date,
        death_date=death_date,
        dmd1=cl["pain_antiepileptics_dmd"],
        dmd_window_days=365,
        dmd_min_count=4
    )
    epilepsy_diag = meets_cms_criteria(
        index_date=index_date,
        death_date=death_date,
        snomed=cl["epilepsy_snomed"]
    )
    pain = (pain_med1 | (pain_med2 & ~epilepsy_diag)).as_int()

    cms += pain.as_float() * 0.445521


    if return_components:
        components["pain"] = pain
        components["cms"] = cms
        return components

    return cms