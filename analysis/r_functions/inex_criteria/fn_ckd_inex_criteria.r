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
# Applies CKD stage 4/5 inclusion criteria and adds CKD stage variable
#
# 1. Calculates eGFR based on creatinine values
# 2. Applies inclusion and exclusion criteria based on eGFR rules and
#    CKD codes (see protocol)
# 3. Groups included individuals into either CKD 4 or CKD 5
# 4. Saves output list (main $data and $flow, but also $data_pre_filter to
#    sensitivity test the CKD inclusion logic
##########################################################################

fn_ckd_inex_criteria <- function(
  arrow_data,
  flow,
  index_date,
  describe = TRUE
) {
  require(arrow)
  require(dplyr)

  # Firstly define people for inclusion (inex_bin_ckd_include = TRUE)
  arrow_data <- arrow_data |>
    mutate(
      # 1. Calculate eGFRs for each creatinine
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
      # 2. Include by route A - 2x eGFR ≥90 days apart both <30ml/min
      # Exclude people with 2x eGFR ≥30 - do not have CKD 4 or 5
      inex_cat_ckd_route_a = case_when(
        (inex_num_egfr_1 < 30) & (inex_num_egfr_2 < 30) ~ "Include",
        (inex_num_egfr_1 >= 30) & (inex_num_egfr_2 >= 30) ~ "Exclude",
        TRUE ~ "Maybe" # discordant pair, or less than 2x SCr values
      ),
      # 3. Move on to route B for route A - maybes
      # Include if most recent CKD code was stage 4 or 5
      inex_cat_ckd_route_b = case_when(
        inex_cat_ckd_route_a != "Maybe" ~ NA_character_,
        (inex_ckd_cat_most_recent_ckd_code_stage %in% c("4", "5")) ~ "Include",
        TRUE ~ "Exclude"
      ),
      # 4. Combine
      inex_bin_ckd_include = case_when(
        inex_cat_ckd_route_a == "Include" ~ TRUE,
        inex_cat_ckd_route_b == "Include" ~ TRUE,
        TRUE ~ FALSE
      )
    )

  # Then categorise included people into either CKD 4 or CKD 5
  arrow_data <- arrow_data |>
    mutate(
      # 1. CKD 4 or 5 based on most recent eGFR and most recent code
      ckd_stage_egfr = case_when(
        inex_num_egfr_1 < 15 ~ "5",
        inex_num_egfr_1 < 30 ~ "4",
        TRUE ~ NA_character_
      ),
      ckd_stage_code = case_when(
        inex_ckd_cat_most_recent_ckd_code_stage %in% c("4", "5") ~
          inex_ckd_cat_most_recent_ckd_code_stage,
        TRUE ~ NA_character_
      ),
      # 2. Categorise
      inex_cat_ckd_stage = case_when(
        !inex_bin_ckd_include ~ NA_character_,
        is.na(ckd_stage_code) ~ ckd_stage_egfr,
        is.na(ckd_stage_egfr) ~ ckd_stage_code,
        # in the case of relevant eGFR AND codes - most recent wins
        inex_ckd_date_scr_date_1 >=
          inex_ckd_date_most_recent_ckd_code ~ ckd_stage_egfr,
        TRUE ~ ckd_stage_code
      )
    ) |>
    select(-ckd_stage_egfr, -ckd_stage_code)

  # Apply CKD inclusion and add flow row
  message("\nCKD 4/5 inclusion criteria:")
  ckd_output_list <- fn_apply_flow_filter(
    arrow_data,
    flow,
    "inex_bin_ckd_include",
    "Kidney function: CKD G4/G5 by eGFR pair (Route A) or most recent CKD code (Route B)"
  )

  # All patients pre-filter, kept for sensitivity counts
  ckd_output_list$data_pre_filter <- arrow_data

  if (isTRUE(describe)) {
    fn_describe_data(
      data = collect(ckd_output_list$data),
      filepath = here::here(
        "output",
        "data_descriptions",
        "cleaning_inex",
        "ckd_inex_applied.txt"
      )
    )
  }

  return(ckd_output_list)
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
