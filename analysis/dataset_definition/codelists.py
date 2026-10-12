##########################################################################
# This script does the following:
# 1. Loads clinical codelists from the codelists/ directory
# 2. Stores them as variables for use in dataset definitions
##########################################################################

from ehrql import codelist_from_csv
import csv

##########################################################################
# KIDNEY FUNCTION CODELISTS
##########################################################################

# CKD codes ---------------------------------------------------------------------

# CKD stages 1-3 to be taken from OpenSAFELY all stages codelist
primary_care_ckd_all_stages_codes = codelist_from_csv(
    "codelists/opensafely-chronic-kidney-disease-codes-all-stages-with-numeric-column.csv",
    column="code",
    category_column="stage"
)

# CKD stages 4-5
primary_care_ckd4_codes = codelist_from_csv(
    "codelists/user-mletts92-chronic-kidney-disease-stage-4.csv",
    column="code"
)
primary_care_ckd5_codes = codelist_from_csv(
    "codelists/user-mletts92-chronic-kidney-disease-stage-5-not-receiving-kidney-replacement-therapy.csv",
    column="code"
)

# all CKD stages (1-5) as one {code: stage} dict
primary_care_ckd_stage_codes = (
    {code: "1" for code, stage in primary_care_ckd_all_stages_codes.items() if stage == "1"}
    | {code: "2" for code, stage in primary_care_ckd_all_stages_codes.items() if stage == "2"}
    | {code: "3" for code, stage in primary_care_ckd_all_stages_codes.items() if stage == "3"}
    | {code: "4" for code in primary_care_ckd4_codes}
    | {code: "5" for code in primary_care_ckd5_codes}
)

# creatinine values -------------------------------------------------------------
creatinine_codes = codelist_from_csv(
    "codelists/nhsd-primary-care-domain-refsets-cre_cod.csv",
    column="code"
)

##########################################################################
# KIDNEY REPLACEMENT THERAPY CODELISTS
##########################################################################
# Same methods as in this paper: https://bmjmedicine.bmj.com/content/3/1/e000807

## primary care KRT codes (all SNOMED CT)
# dialysis, ktx (transplant), then all krt
primary_care_dialysis_codes = codelist_from_csv(
    "codelists/nhsd-primary-care-domain-refsets-dialysis_cod.csv",
    column="code"
)
primary_care_ktx_codes = codelist_from_csv(
    "codelists/nhsd-primary-care-domain-refsets-renaltransp_cod.csv",
    column="code"
)
primary_care_krt_codes = primary_care_dialysis_codes + primary_care_ktx_codes 


## secondary care KRT codes (ICD10 and OPCS-4)
# icd10 - dialysis, ktx then all krt
secondary_care_dialysis_codes_icd10 = codelist_from_csv(
    "codelists/ukrr-dialysis-icd10.csv",
    column="code"
)
secondary_care_dialysis_codes_icd10 = secondary_care_dialysis_codes_icd10 + [
    code + "X" for code in secondary_care_dialysis_codes_icd10 if len(code) == 3
] # deal with three character icd10 codes queried against APCS
# https://docs.opensafely.org/ehrql/how-to/codelists/#using-an-icd-10-codelist-with-the-apcs-dataset

secondary_care_ktx_codes_icd10 = ["Z940"] # only one code for kidney transplant
secondary_care_unclear_krt_codes_icd10 = ["T861"] # "complications of kidney transplant"; may refer to transplant failure hence unknown treatment modality
secondary_care_krt_codes_icd10 = (
    secondary_care_dialysis_codes_icd10 
    + secondary_care_ktx_codes_icd10 
    + secondary_care_unclear_krt_codes_icd10
)

# opcs4 - dialysis, ktx then all krt
secondary_care_dialysis_codes_opcs4 = codelist_from_csv(
    "codelists/ukrr-dialysis-opcs-4.csv",
    column="code"
)
secondary_care_ktx_codes_opcs4 = codelist_from_csv(
    "codelists/user-mletts92-kidney-transplant-opcs4.csv",
    column="code"
)
secondary_care_unclear_krt_codes_opcs4 = ["M023", "M026", "M027", "X412"]
# all indicating kidney failure but unknown treatment modality
# M023 - bilateral nephrectomy; 
# M026 - excision of rejected transplanted kidney; 
# M027 - excision of transplanted kidney NEC; 
# X412 - removal of ambulatory peritoneal dialysis catheter
secondary_care_krt_codes_opcs4 = (
    secondary_care_dialysis_codes_opcs4
    + secondary_care_ktx_codes_opcs4 
    + secondary_care_unclear_krt_codes_opcs4  
)


##########################################################################
# COVARIATE CODELISTS
##########################################################################
# TODO: This is a work in progress. Filling in as go.

# ethnicity codelist -----------------------------------------------------
ethnicity_codes = codelist_from_csv(
    "codelists/opensafely-ethnicity-snomed-0removed.csv",
    column="code",
    category_column="Grouping_6"
)

# systolic blood pressure codelist
sbp_codes = codelist_from_csv(
    "codelists/nhsd-primary-care-domain-refsets-sysbp_cod.csv",
    column="code"
)

# Myocardial infarction codelists 
# Primary + secondary care as MI mainly hospital-based diagnosis
mi_codes_snomed = codelist_from_csv(
    "codelists/nhsd-primary-care-domain-refsets-mi_cod.csv",
    column="code"
)

mi_codes_icd10 = codelist_from_csv(
    "codelists/reducehf-myocardial-infarction-icd10.csv",
    column="code"
)
mi_codes_icd10 = mi_codes_icd10 + [
    code + "X" for code in mi_codes_icd10 if len(code) == 3
] # as above 3 character padded to 4 with X

# Coronary revascularisation codelist
coronary_revasc_codes_opcs4 = codelist_from_csv(
    "codelists/user-mletts92-coronary-artery-interventions.csv",
    column="code"
)

# Stroke codelists
# Primary + secondary care as CVA mainly hospital-based diagnosis
cva_codes_snomed = codelist_from_csv(
    "codelists/nhsd-primary-care-domain-refsets-strk_cod.csv",
    column="code"
)

cva_codes_icd10 = codelist_from_csv(
    "codelists/user-mletts92-stroke-secondary-care-codes.csv",
    column="code"
)
cva_codes_icd10 = cva_codes_icd10 + [
    code + "X" for code in cva_codes_icd10 if len(code) == 3
] # as above 3 character padded to 4 with X

# Heart failure codelists
# Primary + secondary care as HF often diagnosed in hospital
hf_codes_snomed = codelist_from_csv(
    "codelists/pincer-hf.csv",
    column="code"
)

hf_codes_icd10 = codelist_from_csv(
    "codelists/reducehf-heart-failure-primary-outcome-icd.csv",
    column="code"
)
hf_codes_icd10 = hf_codes_icd10 + [
    code + "X" for code in hf_codes_icd10 if len(code) == 3
] # as above 3 character padded to 4 with X

# Diabetes codelists
# Primary care dm codes only - diabetes activity coded well in primary care
dm_not1_codes_snomed = codelist_from_csv(
    "codelists/nhsd-primary-care-domain-refsets-dmnontype1_cod.csv",
    column="code"
)

dm1_codes_snomed = codelist_from_csv(
    "codelists/nhsd-primary-care-domain-refsets-dmtype1_cod.csv",
    column="code"
)

# hba1c codes, just the IFCC standardised units code 
hba1c_codes_snomed = codelist_from_csv(
    "codelists/opensafely-glycated-haemoglobin-hba1c-tests-numerical-value.csv",
    column="code"
)

# diabetes drugs
dm_drug_codes_dmd = codelist_from_csv(
    "codelists/user-mletts92-definite-diabetes-drugs-dmd.csv",
    column="code"
)

# Clinical values (most-recent numeric before index) ---------------------
# BMI
bmi_value_codes_snomed = codelist_from_csv(
    "codelists/nhsd-primary-care-domain-refsets-bmival_cod.csv",
    column="code"
)

# # Total cholesterol
# cholesterol_codes_snomed = codelist_from_csv(
#     #"codelists/user-mletts92-total-cholesterol.csv",
#     column="code"
# )
# Urinary albumin:creatinine ratio (uACR)
uacr_codes_snomed = codelist_from_csv(
    "codelists/bristol-urine-albumin-creatinine-ratio.csv",
    column="code"
)
# Urinary protein:creatinine ratio (uPCR)
upcr_codes_snomed = codelist_from_csv(
    "codelists/bristol-urine-protein-creatinine-ratio.csv",
    column="code"
)


# # Smoking status --------------------------------------------------------
smoking_clear = codelist_from_csv(
    "codelists/opensafely-smoking-clear.csv",
    column="CTV3Code",
    category_column="Category"
)

# # Comorbidities ---------------------------------------------------------
# liver_disease_codes_snomed = codelist_from_csv(
#     #"codelists/user-mletts92-liver-disease.csv",
#     column="code"
# )
# liver_disease_codes_icd10 = codelist_from_csv(
#     #"codelists/user-mletts92-liver-disease-icd10.csv",
#     column="code"
# )
# cancer_codes_snomed = codelist_from_csv(
#     #"codelists/user-mletts92-cancer.csv",
#     column="code"
# )
# cancer_codes_icd10 = codelist_from_csv(
#     #"codelists/user-mletts92-cancer-icd10.csv",
#     column="code"
# )
# dementia_codes_snomed = codelist_from_csv(
#     #"codelists/user-mletts92-dementia.csv",
#     column="code"
# )
# dementia_codes_icd10 = codelist_from_csv(
#     #"codelists/user-mletts92-dementia-icd10.csv",
#     column="code"
# )
# copd_codes_snomed = codelist_from_csv(
#     #"codelists/user-mletts92-copd.csv",
#     column="code"
# )
# copd_codes_icd10 = codelist_from_csv(
#     #"codelists/user-mletts92-copd-icd10.csv",
#     column="code"
# )


# # Recent events (primary care SNOMED) ------------------------------------
# structured_med_review_codes_snomed = codelist_from_csv(
#     #"codelists/user-mletts92-structured-medication-review.csv",
#     column="code"
# )
# care_facility_move_codes_snomed = codelist_from_csv(
#     #"codelists/user-mletts92-care-home-admission.csv",
#     column="code"
# )
# falls_codes_snomed = codelist_from_csv(
#     #"codelists/user-mletts92-falls.csv",
#     column="code"
# )
# falls_codes_icd10 = codelist_from_csv(
#     #"codelists/user-mletts92-falls-icd10.csv",
#     column="code"
# )

# # GI bleeding:
# gi_bleed_codes_snomed = codelist_from_csv(
#     #"codelists/user-mletts92-gi-bleeding.csv",
#     column="code"
# )
# gi_bleed_codes_icd10 = codelist_from_csv(
#     #"codelists/user-mletts92-gi-bleeding-icd10.csv",
#     column="code"
# )
# # AKI / electrolyte disturbance (hyponatraemia, hypomagnesaemia)
# electrolyte_codes_snomed = codelist_from_csv(
#     #"codelists/user-mletts92-aki-electrolyte-disturbance.csv",
#     column="code"
# )
# electrolyte_codes_icd10 = codelist_from_csv(
#     #"codelists/user-mletts92-aki-electrolyte-disturbance-icd10.csv",
#     column="code"
# )
# Medication codelists ------------------------------------------------------------------

# All the paths to medications_of_interest codelists are defined
# in analysis/config/medication_of_interest.csv (this is the central source of truth)
# Below code loops over csv rows and builds a dict with each medicine/codelist in it:

# {
#    "statin": <codelist>
#    "other": <codelist>
# }

with open("analysis/config/medication_of_interest.csv") as f:
    medication_of_interest_codelists = {}
    for row in csv.DictReader(f):
        medication_of_interest_codelists[row["name"]] = codelist_from_csv(
            row["codelist_path"],
            column="code"
        )

###########################
# Cambridge multimorbidity score

# Dictionary of codelists for Cambridge MultiMorbidityScore
multimorbidity_filepaths_dict = {
    "MS_AlcoholProblem_snomed": "codelists/bristol-multimorbidity_alcoholproblems.csv", # ever recorded
    "MS_AnxietyDepression_snomed": "codelists/bristol-multimorbidity_anxietydepression.csv", 
    # code in last 12 months OR ≥4 anxiolytic/hypnotic prescriptions in last 12 months OR ≥4 anti-depressant prescriptions (excluding low dose tricyclics) in last 12 months
    "MS_AnxietyDepression_dmd": "codelists/user-ZoeMZou-multimorbidity_prescription_anxiolytics_anti_depressants.csv", # as above
    "MS_Asthma_snomed": "codelists/nhsd-primary-care-domain-refsets-ast_cod.csv", # ever recorded AND 1+ prescription in last 12 months
    "MS_Asthma_dmd": "codelists/nhs-drug-refsets-asttrt_cod.csv", # ever recorded AND 1+ prescription in last 12 months
    "MS_AF_snomed": "codelists/bristol-multimorbidity_atrial-fibrillation.csv", # ever recorded
    "MS_Cancer_snomed": "codelists/bristol-multimorbidity_cancer.csv", # FIRST recorded in last 5 years
    "MS_CKD_snomed": "codelists/bristol-multimorbidity_chronic-kidney-disease.csv", # everyone in my study will score for this
    "MS_Constipation_dmd": "codelists/user-ZoeMZou-multimorbidity_prescription_chronic_constipation.csv", # 4+ prescriptions in the last 12 months
    "MS_CTD_snomed": "codelists/bristol-multimorbidity_connective-tissue-disorder.csv", # ever recorded
    "MS_COPD_snomed": "codelists/bristol-multimorbidity_copd.csv", # ever recorded
    "MS_CHD_snomed": "codelists/bristol-multimorbidity_coronary-heart-disease.csv", # ever recorded
    "MS_Dementia_snomed": "codelists/bristol-multimorbidity_dementia.csv", # ever recorded
    "MS_Diabetes_snomed": "codelists/bristol-multimorbidity_diabetes.csv", # ever recorded
    "MS_Epilepsy_snomed": "codelists/bristol-multimorbidity_epilepsy.csv", # ever recorded AND 1+ prescription in last 12 months
    "MS_Epilepsy_dmd": "codelists/user-ZoeMZou-multimorbidity_prescription_epilepsy.csv", # ever recorded AND 1+ prescription in last 12 months
    "MS_HL_snomed": "codelists/bristol-multimorbidity_hearing-loss.csv", # ever recorded
    "MS_HF_snomed": "codelists/bristol-multimorbidity_heart-failure.csv", # ever recorded
    "MS_Hypertension_snomed": "codelists/nhsd-primary-care-domain-refsets-hyp_cod.csv", # ever recorded
    "MS_IBS_snomed": "codelists/bristol-multimorbidity_irritable-bowel-syndrome.csv", # ever recorded OR 4+ antispasmodic prescriptions in last 12 months
    "MS_IBS_dmd": "codelists/user-ZoeMZou-multimorbidity_prescription_anti_spasmodic.csv", # ever recorded OR 4+ antispasmodic prescriptions in last 12 months
    "MS_PC_Analgesics_dmd": "codelists/user-ZoeMZou-multimorbidity_prescription_analgesics_opiods_not_migraine.csv",  # pain (OR below) = 4+ prescriptions in last 12 months
    "MS_PC_Antiepileptic_dmd": "codelists/user-ZoeMZou-multimorbidity_prescription_anti_epileptic_for_pain_only.csv", # pain (OR above) = 4+ prescriptions in last 12 months, only if no epilepsy code
    "MS_Psychosis_snomed": "codelists/bristol-multimorbidity_psychosisbipolar-disorder.csv", # ever recorded OR lithium ever prescribed
    "MS_Psychosis_dmd": "codelists/user-ZoeMZou-multimorbidity_prescription_schizophrenia_bipolar_disorder.csv", # ever recorded OR lithium ever prescribed
    "MS_StrokeTIA_snomed": "codelists/bristol-multimorbidity_stroketransient-ischemic-attack.csv", # ever recorded
}
# Convert to codelist dictionary
multimorbidity_codelists_dict = {
    name: codelist_from_csv(path, column="code") 
    for name, path 
    in multimorbidity_filepaths_dict.items()
}
