##########################################################################
# This script defines five functions used to apply inclusion and
# exclusion criteria related to CKD and KRT
#   fn_egfr_ckdepi2009() - calculates eGFR from serum creatinine
#   fn_ckd_inex_criteria() - applies CKD stage 4/5 inclusion criteria
#   fn_krt_inex_criteria_dialysis() - applies dialysis exclusion criteria
#   fn_krt_inex_criteria_transplant() - applies transplant exclusion criteria
#   fn_ckd_def_sensitivity_checks() - study population when ckd def varies
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
#    sensitivity test the CKD inclusion logic)
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
  route_counts <- arrow_data |>
    summarise(
      n_route_a = sum(inex_cat_ckd_route_a == "Include", na.rm = TRUE),
      n_route_b = sum(inex_cat_ckd_route_b == "Include", na.rm = TRUE)
    ) |>
    collect()

  ckd_output_list <- fn_apply_flow_filter(
    arrow_data,
    flow,
    "inex_bin_ckd_include",
    sprintf(
      "CKD G4/G5: By most recent eGFR pair (n = %d) or most recent CKD code (n = %d)",
      fn_apply_sdc(route_counts$n_route_a),
      fn_apply_sdc(route_counts$n_route_b)
    )
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

##########################################################################
# fn_ckd_def_sensitivity_checks()
#
# Varies the definition of CKD used and outputs the effect that it would
# have had on the final study population (i.e. after KRT exclusion too)
##########################################################################

fn_ckd_def_sensitivity_checks <- function(
  arrow_data_pre_filter
) {
  require(arrow)
  require(dplyr)
  require(tidyr)

  message("SENSITIVITY: CKD definition sensitivity checks")

  ckd_def_labels <- c(
    included_via_route_a = "Included via Route A (2x eGFR <30, >=90 days apart)",
    included_via_route_b = "Included via Route B (most recent CKD code stage 4/5)",
    route_b_via_discordant_scr_pair = "Route B: discordant eGFR pair (one <30, one >=30)",
    route_b_via_only_one_scr = "Route B: one creatinine (no second >=90 days earlier)",
    route_b_via_zero_scr = "Route B: no creatinine",
    route_a_but_no_ckd_code = "Route A: no CKD code recorded",
    route_a_but_ckd_code1 = "Route A: most recent CKD code stage 1",
    route_a_but_ckd_code2 = "Route A: most recent CKD code stage 2",
    route_a_but_ckd_code3 = "Route A: most recent CKD code stage 3",
    route_a_but_ckd_code4 = "Route A: most recent CKD code stage 4",
    route_a_but_ckd_code5 = "Route A: most recent CKD code stage 5",
    if_route_a_req_scr_gap_less_than_2_years = "Number lost if Route A required eGFR pair to be <=2 years apart",
    if_route_b_ckd45_code_ever = "Number added if Route B accepted any previous CKD 4/5 code"
  )

  ckd_def_sensitivity <- arrow_data_pre_filter |>
    # Restrict to patients passing KRT exclusions (final analysis population)
    filter(
      !(inex_krt_bin_has_primary_care_krt_code &
        inex_krt_cat_primary_care_krt_type %in% c("dialysis", "transplant"))
    ) |>
    summarise(
      # How many of final study pop arrived via route a?
      included_via_route_a = sum(
        inex_cat_ckd_route_a == "Include",
        na.rm = TRUE
      ),
      # How many of final study pop arrived via route b?
      included_via_route_b = sum(
        inex_cat_ckd_route_b == "Include",
        na.rm = TRUE
      ),

      # Of those arriving via route b:
      #    - how many had 2 discordant creatinines?
      route_b_via_discordant_scr_pair = sum(
        (inex_cat_ckd_route_b == "Include") & !is.na(inex_num_egfr_2),
        na.rm = TRUE
      ),
      #    - how many had only 1 creatinine?
      route_b_via_only_one_scr = sum(
        (inex_cat_ckd_route_b == "Include") &
          is.na(inex_num_egfr_2) &
          !is.na(inex_num_egfr_1),
        na.rm = TRUE
      ),
      #    - how many had zero creatinines?
      route_b_via_zero_scr = sum(
        (inex_cat_ckd_route_b == "Include") & is.na(inex_num_egfr_1),
        na.rm = TRUE
      ),

      # Of those arriving via route a:
      #    - how many had no prior CKD code?
      route_a_but_no_ckd_code = sum(
        (inex_cat_ckd_route_a == "Include") &
          is.na(inex_ckd_cat_most_recent_ckd_code_stage),
        na.rm = TRUE
      ),
      #    - how many with most recent CKD code that was stage 1?
      route_a_but_ckd_code1 = sum(
        (inex_cat_ckd_route_a == "Include") &
          (inex_ckd_cat_most_recent_ckd_code_stage == "1"),
        na.rm = TRUE
      ),
      #    - how many with most recent CKD code that was stage 2?
      route_a_but_ckd_code2 = sum(
        (inex_cat_ckd_route_a == "Include") &
          (inex_ckd_cat_most_recent_ckd_code_stage == "2"),
        na.rm = TRUE
      ),
      #    - how many with most recent CKD code that was stage 3?
      route_a_but_ckd_code3 = sum(
        (inex_cat_ckd_route_a == "Include") &
          (inex_ckd_cat_most_recent_ckd_code_stage == "3"),
        na.rm = TRUE
      ),
      #    - how many with most recent CKD code that was stage 4?
      route_a_but_ckd_code4 = sum(
        (inex_cat_ckd_route_a == "Include") &
          (inex_ckd_cat_most_recent_ckd_code_stage == "4"),
        na.rm = TRUE
      ),
      #    - how many with most recent CKD code that was stage 5?
      route_a_but_ckd_code5 = sum(
        (inex_cat_ckd_route_a == "Include") &
          (inex_ckd_cat_most_recent_ckd_code_stage == "5"),
        na.rm = TRUE
      ),

      # How many would have been lost if there was a requirement
      # for the two SCR values to be within 2 years of each other?
      if_route_a_req_scr_gap_less_than_2_years = sum(
        (inex_cat_ckd_route_a == "Include") &
          (as.integer(inex_ckd_date_scr_date_1) -
            as.integer(inex_ckd_date_scr_date_2) >
            730) &
          !(inex_ckd_cat_most_recent_ckd_code_stage %in% c("4", "5")),
        na.rm = TRUE
      ),

      #  # How many would be added if route b had simply been ANY
      # prior CKD 4/5 code (regardless of a more recent CKD 1,2,3 code)?
      if_route_b_ckd45_code_ever = sum(
        (inex_cat_ckd_route_b == "Exclude") &
          inex_ckd_bin_has_ckd45_code,
        na.rm = TRUE
      )
    ) |>
    collect() |>
    pivot_longer(everything(), names_to = "Description", values_to = "N") |>
    mutate(Description = ckd_def_labels[Description])

  return(ckd_def_sensitivity)
}
