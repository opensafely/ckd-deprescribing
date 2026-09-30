##########################################################################
# This script defines four functions used to apply inclusion and
# exclusion criteria related to CKD and KRT
#   fn_egfr_ckdepi2009() - calculates eGFR from serum creatinine
#   fn_ckd_inex_criteria() - applies CKD stage 4/5 inclusion criteria
#   fn_krt_inex_criteria_dialysis() - applies dialysis exclusion criteria
#   fn_krt_inex_criteria_transplant() - applies transplant exclusion criteria
##########################################################################

##########################################################################
# fn_egfr_ckdepi2009()
#
# Calculates eGFR (mL/min/1.73m²) from serum creatinine (umol/L), age,
# and sex using the CKD-EPI 2009 equation without race coefficient, as
# recommended by UKKA/NICE.
#
# Reference:
# https://www.niddk.nih.gov/research-funding/research-programs/
# kidney-clinical-research-epidemiology/laboratory/
# glomerular-filtration-rate-equations/adults/previous
##########################################################################

fn_egfr_ckdepi2009 <- function(
  creat_umol,
  age,
  sex
) {
  kappa <- case_when(
    sex == "female" ~ 61.9,
    sex == "male" ~ 79.6
  )
  alpha <- case_when(
    sex == "female" ~ -0.329,
    sex == "male" ~ -0.411
  )
  female_multiplier <- case_when(
    sex == "female" ~ 1.018,
    sex == "male" ~ 1.0
  )

  ratio <- creat_umol / kappa

  141 *
    pmin(ratio, 1)^alpha *
    pmax(ratio, 1)^-1.209 *
    (0.993^age) *
    female_multiplier
}


##########################################################################
# fn_ckd_inex_criteria()
#
# Applies CKD stage 4/5 inclusion criteria and adds eGFR-derived
# staging variables. Steps:
#
# 1. For patients with 2+ serum creatinine measurements, calculate eGFR
#    at each measurement date and classify into G4, G5, or G4/G5.
#    Age at the time of each measurement is used (not age at index date).
# 2. Join CKD stages back to the full dataset; patients without
#    2 creatinine measurements default to FALSE / "not G4/G5".
# 3. Include patients with either a CKD 4/5 code OR eGFR-derived CKD 4/5.
# 4. Recalculate eGFR for all included patients post-filter (captures
#    those included via CKD code who may only have one SCr value).
# 5. Add the post-filter count to the flow table.
##########################################################################

fn_ckd_inex_criteria <- function(
  arrow_data,
  flow,
  index_date,
  describe = TRUE
) {
  require(arrow)
  require(dplyr)

  # 1. Calculate eGFR and classify CKD stage for patients with 2+ SCr values
  ckd_flags <- arrow_data |>
    filter(inex_ckd_bin_has_two_scr) |>
    mutate(
      inex_num_egfr_1 = fn_egfr_ckdepi2009(
        creat_umol = inex_ckd_num_scr_value_1,
        age = inex_dem_num_age +
          (as.integer(inex_ckd_date_scr_date_1) - as.integer(index_date)) /
            365.25,
        sex = inex_dem_cat_sex
      ),
      inex_num_egfr_2 = fn_egfr_ckdepi2009(
        creat_umol = inex_ckd_num_scr_value_2,
        age = inex_dem_num_age +
          (as.integer(inex_ckd_date_scr_date_2) - as.integer(index_date)) /
            365.25,
        sex = inex_dem_cat_sex
      ),
      inex_cat_ckd_stage_by_scr = case_when(
        (inex_num_egfr_1 < 15) & (inex_num_egfr_2 < 15) ~ "G5",
        (inex_num_egfr_1 >= 15) &
          (inex_num_egfr_1 < 30) &
          (inex_num_egfr_2 >= 15) &
          (inex_num_egfr_2 < 30) ~ "G4",
        (inex_num_egfr_1 >= 15) &
          (inex_num_egfr_1 < 30) &
          (inex_num_egfr_2 < 15) ~ "G4/G5",
        (inex_num_egfr_1 < 15) &
          (inex_num_egfr_2 >= 15) &
          (inex_num_egfr_2 < 30) ~ "G4/G5",
        TRUE ~ "not G4/G5"
      ),
      inex_bin_has_ckd45_by_scr = inex_cat_ckd_stage_by_scr != "not G4/G5"
    ) |>
    select(patient_id, inex_bin_has_ckd45_by_scr, inex_cat_ckd_stage_by_scr)

  # 2. Join CKD flags back to the full dataset, filling NAs for those
  #    without 2 SCr measurements
  arrow_data <- arrow_data |>
    left_join(ckd_flags, by = "patient_id") |>
    mutate(
      inex_bin_has_ckd45_by_scr = ifelse(
        is.na(inex_bin_has_ckd45_by_scr),
        FALSE,
        inex_bin_has_ckd45_by_scr
      ),
      inex_cat_ckd_stage_by_scr = ifelse(
        is.na(inex_cat_ckd_stage_by_scr),
        "not G4/G5",
        inex_cat_ckd_stage_by_scr
      )
    )

  # 3. Include patients with a CKD 4/5 code OR eGFR-derived CKD 4/5
  arrow_data_ckd_inex_applied <- arrow_data |>
    filter(inex_ckd_bin_has_ckd45_code | inex_bin_has_ckd45_by_scr) |>

    # 4. Recalculate eGFR post-filter for all included patients
    mutate(
      inex_num_egfr_1 = fn_egfr_ckdepi2009(
        creat_umol = inex_ckd_num_scr_value_1,
        age = inex_dem_num_age +
          (as.integer(inex_ckd_date_scr_date_1) - as.integer(index_date)) /
            365.25,
        sex = inex_dem_cat_sex
      ),
      inex_num_egfr_2 = fn_egfr_ckdepi2009(
        creat_umol = inex_ckd_num_scr_value_2,
        age = inex_dem_num_age +
          (as.integer(inex_ckd_date_scr_date_2) - as.integer(index_date)) /
            365.25,
        sex = inex_dem_cat_sex
      )
    )

  # 5. Add flow row
  message("\nCKD 4/5 inclusion criteria:")
  flow <- fn_add_flow_row(
    arrow_data_ckd_inex_applied,
    flow,
    "Kidney function: Has G4/G5 CKD by code or 2x eGFRs"
  )

  if (isTRUE(describe)) {
    fn_describe_data(
      data = collect(arrow_data_ckd_inex_applied),
      filepath = here::here(
        "output",
        "data_descriptions",
        "cleaning_inex",
        "ckd_inex_applied.txt"
      )
    )
  }

  return(list(data = arrow_data_ckd_inex_applied, flow = flow))
}


##########################################################################
# fn_krt_inex_criteria_dialysis()
#
# Excludes patients with primary care dialysis KRT codes prior to index
# date
##########################################################################

fn_krt_inex_criteria_dialysis <- function(
  arrow_data,
  flow,
  describe = TRUE
) {
  require(arrow)
  require(dplyr)

  message("\nKRT exclusion - dialysis (primary care):")
  arrow_data <- arrow_data |>
    mutate(
      no_dialysis = !(inex_krt_bin_has_primary_care_krt_code &
        inex_krt_cat_primary_care_krt_type == "dialysis")
    )

  dialysis_output_list <- fn_apply_flow_filter(
    arrow_data,
    flow,
    "no_dialysis",
    "Primary care KRT code prior to index: Most recent = dialysis"
  )

  dialysis_output_list$data <- dialysis_output_list$data |> select(-no_dialysis)

  if (isTRUE(describe)) {
    fn_describe_data(
      data = collect(dialysis_output_list$data),
      filepath = here::here(
        "output",
        "data_descriptions",
        "cleaning_inex",
        "krt_dialysis_excluded.txt"
      )
    )
  }

  return(dialysis_output_list)
}


##########################################################################
# fn_krt_inex_criteria_transplant()
#
# Excludes patients with primary care kidney transplant codes prior to
# index date
##########################################################################

fn_krt_inex_criteria_transplant <- function(
  arrow_data,
  flow,
  describe = TRUE
) {
  require(arrow)
  require(dplyr)

  message("\nKRT exclusion - transplant (primary care):")
  arrow_data <- arrow_data |>
    mutate(
      no_transplant = !(inex_krt_bin_has_primary_care_krt_code &
        inex_krt_cat_primary_care_krt_type == "transplant")
    )

  transplant_output_list <- fn_apply_flow_filter(
    arrow_data,
    flow,
    "no_transplant",
    "Primary care KRT code prior to index: Most recent = transplant"
  )

  transplant_output_list$data <- transplant_output_list$data |>
    select(-no_transplant)

  if (isTRUE(describe)) {
    fn_describe_data(
      data = collect(transplant_output_list$data),
      filepath = here::here(
        "output",
        "data_descriptions",
        "cleaning_inex",
        "krt_transplant_excluded.txt"
      )
    )
  }

  return(transplant_output_list)
}
