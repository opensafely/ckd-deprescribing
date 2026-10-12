### FROM ROB/ZOE

from codelists import *
from ehrql.tables.tpp import patients, clinical_events, medications

def check_date_validity(
    date_to_check,
    death_date,
    check_not_before_dob=True,
    check_not_after_death=True
):

    conditions = []

    ## Base requirement: must not be null
    conditions.append(date_to_check.is_not_null())

    ## Check not before DOB
    if check_not_before_dob:
        conditions.append(
            patients.date_of_birth.is_null()
            | (date_to_check >= patients.date_of_birth)
        )

    ## Check not after death
    if check_not_after_death:
        conditions.append(
            death_date.is_null()
            | (date_to_check <= death_date)
        )

    ## Combine all validity conditions
    is_valid = conditions[0]
    for cond in conditions[1:]:
        is_valid = is_valid & cond

    return case(
        when(is_valid).then(date_to_check),
        otherwise=None
    )

def any_of(conditions):
    return reduce(operator.or_, conditions)

    def has_condition_before(
    index_date,
    death_date,
    snomed=None,
    dmd1=None,
    dmd2=None,
    where=True,
):
    conditions = []

    if snomed is not None:
        filtered = ever_matching_event_clinical_snomed_before(
            snomed,
            index_date,
            where=where,
        )

        conditions.append(
            filtered.where(
                check_date_validity(
                    filtered.date,
                    death_date=death_date,
                ).is_not_null()
            ).exists_for_patient()
        )

    for dmd in [dmd1, dmd2]:
        if dmd is not None:
            filtered = ever_matching_med_dmd_before(
                dmd,
                index_date,
                where=where,
            )

            conditions.append(
                filtered.where(
                    check_date_validity(
                        filtered.date,
                        death_date=death_date,
                    ).is_not_null()
                ).exists_for_patient()
            )

    if not conditions:
        raise ValueError(
            "Must provide at least one SNOMED or DMD codelist."
        )

    return any_of(conditions)

## This code is borrowed from Zoe Zou at https://github.com/opensafely/cambridge-multimorbidity-score/tree/Codelists-for-CMS
## It calculates the cambridge mulimorbidity score for a patient based on their clinical events and medications, using the specified index date.
## It can return either the total score or the individual components of the score.
def get_cms_on_date(index_date, death_date, return_components=False):

    cms = clinical_events.exists_for_patient().as_int().as_float() * 0
    components = {}

    for name, weight, snomed, dmd1, dmd2 in [
        ("alcohol",      0.65, multimorbidity_dict["MS_AlcoholProblem_snomed"], None, None),
        ("anxiety",      0.50, multimorbidity_dict["MS_AnxietyDepression_snomed"], multimorbidity_dict["MS_AnxietyDepression_dmd"], None),
        ("asthma",       0.19, multimorbidity_dict["MS_Asthma_snomed"], multimorbidity_dict["MS_Asthma_dmd"], None),
        ("af",           1.34, multimorbidity_dict["MS_AF_snomed"], None, None),
        ("cancer",       1.53, multimorbidity_dict["MS_Cancer_snomed"], None, None),
        ("ckd",          0.53, multimorbidity_dict["MS_CKD_snomed"], None, None),
        ("constipation", 1.12, None, multimorbidity_dict["MS_Constipation_dmd"], None),
        ("copd",         1.46, multimorbidity_dict["MS_COPD_snomed"], None, None),
        ("ctd",          0.43, multimorbidity_dict["MS_CTD_snomed"], None, None),
        ("chd",          0.49, multimorbidity_dict["MS_CHD_snomed"], None, None),
        ("dementia",     2.50, multimorbidity_dict["MS_Dementia_snomed"], None, None),
        ("diabetes",     0.75, multimorbidity_dict["MS_Diabetes_snomed"], None, None),
        ("epilepsy",     0.92, multimorbidity_dict["MS_Epilepsy_snomed"], multimorbidity_dict["MS_Epilepsy_dmd"], None),
        ("hearing_loss", 0.09, multimorbidity_dict["MS_HL_snomed"], None, None),
        ("hf",           1.18, multimorbidity_dict["MS_HF_snomed"], None, None),
        ("hypertension", 0.08, multimorbidity_dict["MS_Hypertension_snomed"], None, None),
        ("ibs",          0.21, multimorbidity_dict["MS_IBS_snomed"], multimorbidity_dict["MS_IBS_dmd"], None),
        ("psychosis",    0.64, multimorbidity_dict["MS_Psychosis_snomed"], multimorbidity_dict["MS_Psychosis_dmd"], None),
        ("stroke",       0.80, multimorbidity_dict["MS_StrokeTIA_snomed"], None, None),
        ("pain",         0.92, None,
                        multimorbidity_dict["MS_PC_Analgesics_dmd"],
                        multimorbidity_dict["MS_PC_Antiepileptic_dmd"]),
    ]:

        binary = has_condition_before(
            index_date=index_date,
            death_date=death_date,
            snomed=snomed,
            dmd1=dmd1,
            dmd2=dmd2,
        ).as_int()

        cms += binary.as_float() * weight

        if return_components:
            components[name] = binary

    if return_components:
        components["cms"] = cms
        return components

    return cms


Minimal extension to has_condition_before

def has_condition_before(
    index_date,
    death_date,
    snomed=None,
    dmd1=None,
    dmd2=None,
    where=True,
    snomed_window_days=None,   # NEW: e.g. 365 for anxiety/depression codes
    dmd_window_days=None,      # NEW: e.g. 365 for prescription-defined conditions
    dmd_min_count=1,           # NEW: e.g. 4 for constipation, pain, IBS, anx/dep
    combine="any",             # NEW: "all" for asthma and epilepsy (code AND Rx)
):
    conditions = []

    if snomed is not None:
        filtered = ever_matching_event_clinical_snomed_before(snomed, index_date, where=where)
        if snomed_window_days is not None:
            filtered = filtered.where(filtered.date.is_on_or_after(index_date - days(snomed_window_days)))
        conditions.append(
            filtered.where(
                check_date_validity(filtered.date, death_date=death_date).is_not_null()
            ).exists_for_patient()
        )

    for dmd in [dmd1, dmd2]:
        if dmd is not None:
            filtered = ever_matching_med_dmd_before(dmd, index_date, where=where)
            if dmd_window_days is not None:
                filtered = filtered.where(filtered.date.is_on_or_after(index_date - days(dmd_window_days)))
            conditions.append(
                filtered.where(
                    check_date_validity(filtered.date, death_date=death_date).is_not_null()
                ).count_for_patient() >= dmd_min_count
            )

    if not conditions:
        raise ValueError("Must provide at least one SNOMED or DMD codelist.")

    return all_of(conditions) if combine == "all" else any_of(conditions)
all_of is the reduce(operator.and_, ...) counterpart of their existing any_of.
