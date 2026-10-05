##########################################################################
# This script defines fn_modify_dummy_data() which replaces OpenSAFELY's
# synthetic dummy data with more plausible data for local testing
#
# The project stage argument allows for different modifications to be
# applied depending on when the function is passed e.g. "baseline_meds"
#
# Adapted from:
#   https://github.com/opensafely/waning-ve-2dose-1year
#   https://github.com/opensafely/post-covid-vaccinated
#   https://github.com/opensafely/post-covid-neurodegenerative
##########################################################################

fn_modify_dummy_data <- function(
  arrow_data,
  project_stage,
  index_date
) {
  require(arrow)
  require(dplyr)

  # Collect arrow project_stage into an R data.frame for modification ----
  dummy_data <- arrow_data |> collect()

  # # for tinkering
  # dummy_data <- project_stage_cleaning_inex_1_input |> collect()
  # skimr::skim(dummy_data)

  set.seed(234)

  if (project_stage == "cleaning_inex") {
    dummy_data <- dummy_data |>

      ##  Demographic variables ##

      mutate(
        inex_dem_bin_alive = as.logical(rbinom(n(), 1, p = 0.99)),
        inex_dem_bin_age_include = as.logical(rbinom(n(), 1, p = 0.95)),
        inex_dem_bin_12m_registered = as.logical(rbinom(n(), 1, p = 0.95)),
        inex_dem_num_age = sample(18:110, n(), replace = TRUE),
        inex_dem_cat_sex = as.factor(sample(
          x = c("female", "male", "intersex", "unknown"),
          size = n(),
          replace = TRUE,
          prob = c(0.49, 0.49, 0.01, 0.01)
        )),
        inex_dem_bin_sex = inex_dem_cat_sex %in% c("male", "female"),
        inex_dem_bin_region = as.logical(rbinom(n(), 1, p = 0.99)),
        inex_dem_bin_imd = as.logical(rbinom(n(), 1, p = 0.99))
      ) |>

      ## CKD variables ##

      # Serum creatinine values
      mutate(
        # SCR value 1 - normally distributed around 200 umol/L with min 30 and max 500
        inex_ckd_num_scr_value_1 = round(
          pmax(30, pmin(500, rnorm(nrow(dummy_data), mean = 200, sd = 100))),
          0
        ),
        # SCR value 2 - similar to value 1 but with some variation
        inex_ckd_num_scr_value_2 = round(
          pmax(
            30,
            pmin(
              500,
              inex_ckd_num_scr_value_1 +
                rnorm(nrow(dummy_data), mean = 0, sd = 20)
            )
          ),
          0
        ),
        # 10% missing both, additional 5% missing SCr2 only
        missing_both = runif(nrow(dummy_data)) < 0.10,
        missing_scr2_only = !missing_both & runif(nrow(dummy_data)) < 0.05,
        inex_ckd_num_scr_value_1 = if_else(
          missing_both,
          NA_real_,
          inex_ckd_num_scr_value_1
        ),
        inex_ckd_num_scr_value_2 = if_else(
          missing_both | missing_scr2_only,
          NA_real_,
          inex_ckd_num_scr_value_2
        )
      ) |>
      select(-missing_both, -missing_scr2_only) |>
      mutate(
        inex_ckd_bin_has_two_scr = !is.na(inex_ckd_num_scr_value_1) &
          !is.na(inex_ckd_num_scr_value_2)
      ) |>

      # serum creatinine dates
      mutate(
        # Date 1 - must be before index_date
        # only for those with SCR1 value, 0.05% missing
        inex_ckd_date_scr_date_1 = if_else(
          !is.na(inex_ckd_num_scr_value_1) & runif(nrow(dummy_data)) > 0.005,
          as.Date("2017-01-01") +
            days(sample(
              0:as.integer(as.Date(index_date) - as.Date("2017-01-01")),
              nrow(dummy_data),
              replace = TRUE
            )),
          NA_Date_
        ),
        # Date 2 - must be 90+ days before date 1,
        # only for those with SCR2 value, 0.05% missing
        inex_ckd_date_scr_date_2 = if_else(
          !is.na(inex_ckd_num_scr_value_2) & runif(nrow(dummy_data)) > 0.005,
          inex_ckd_date_scr_date_1 -
            days(sample(90:1000, nrow(dummy_data), replace = TRUE)),
          NA_Date_
        )
      ) |>

      # CKD45 codes - probability scales with creatinine value
      # this creates roughly 40% TRUE and 60% FALSE
      mutate(
        inex_ckd_bin_has_ckd45_code = as.logical(rbinom(
          nrow(dummy_data),
          1,
          prob = case_when(
            inex_ckd_num_scr_value_1 < 100 ~ 0.005,
            inex_ckd_num_scr_value_1 < 150 ~ 0.02,
            inex_ckd_num_scr_value_1 < 200 ~ 0.2,
            inex_ckd_num_scr_value_1 < 300 ~ 0.5,
            TRUE ~ 0.85
          )
        ))
      ) |>

      mutate(
        # Most recent CKD code stage - depends on whether ever had a 4/5 code
        # with 4/5 code: mostly 4/5, ~15% a less severe CKD code
        # without: stage 1-3 or no CKD code
        inex_ckd_cat_most_recent_ckd_code_stage = as.factor(case_when(
          inex_ckd_bin_has_ckd45_code ~ sample(
            c("1", "2", "3", "4", "5"),
            n(),
            replace = TRUE,
            prob = c(0.02, 0.02, 0.11, 0.45, 0.40)
          ),
          TRUE ~ sample(
            c("1", "2", "3", NA),
            n(),
            replace = TRUE,
            prob = c(0.05, 0.05, 0.15, 0.75)
          )
        )),
        inex_ckd_date_most_recent_ckd_code = if_else(
          !is.na(inex_ckd_cat_most_recent_ckd_code_stage),
          as.Date("2017-01-01") +
            days(sample(
              0:as.integer(as.Date(index_date) - as.Date("2017-01-01")),
              n(),
              replace = TRUE
            )),
          NA_Date_
        )
      ) |>

      ## KRT variables ##

      # Primary care codes
      mutate(
        inex_krt_bin_has_primary_care_krt_code = as.logical(rbinom(
          nrow(dummy_data),
          1,
          prob = case_when(
            inex_ckd_cat_most_recent_ckd_code_stage == "5" ~ 0.20,
            inex_ckd_cat_most_recent_ckd_code_stage == "4" ~ 0.10,
            TRUE ~ 0.03
          )
        )),
        # Type - only for those with a KRT code
        inex_krt_cat_primary_care_krt_type = as.factor(case_when(
          !inex_krt_bin_has_primary_care_krt_code ~ NA_character_,
          TRUE ~ sample(
            x = c("dialysis", "transplant"),
            size = nrow(dummy_data),
            replace = TRUE,
            prob = c(0.5, 0.5)
          )
        ))
      ) |>

      # Secondary care codes
      mutate(
        inex_krt_bin_has_secondary_care_krt_code = as.logical(rbinom(
          nrow(dummy_data),
          1,
          prob = case_when(
            inex_krt_bin_has_primary_care_krt_code ~ 0.80,
            inex_ckd_cat_most_recent_ckd_code_stage == "5" ~ 0.05,
            inex_ckd_cat_most_recent_ckd_code_stage == "4" ~ 0.01,
            TRUE ~ 0.005
          )
        )),
        inex_krt_cat_secondary_care_krt_type = as.factor(case_when(
          !inex_krt_bin_has_secondary_care_krt_code ~ NA_character_,
          TRUE ~ sample(
            c("dialysis", "transplant", "unknown"),
            nrow(dummy_data),
            replace = TRUE,
            prob = c(0.50, 0.45, 0.05)
          )
        )),
        inex_krt_bin_secondary_care_only = inex_krt_bin_has_secondary_care_krt_code &
          !inex_krt_bin_has_primary_care_krt_code
      ) |>

      ## Reapply QA criteria from fn_inex_variables.py ##

      mutate(
        inex_qa_bin_dob_known = as.logical(rbinom(n(), 1, p = 0.99)),
        inex_qa_bin_dob_before_dod = as.logical(rbinom(n(), 1, p = 0.99)),
        inex_qa_bin_dob_not_future = as.logical(rbinom(n(), 1, p = 0.99)),
        inex_qa_bin_dod_not_future = as.logical(rbinom(n(), 1, p = 0.99))
      )
  } else if (project_stage == "process_baseline_meds") {
    # intentionally leave blank - no modifications to dummy data
  } else if (project_stage == "process_moi_at_baseline") {
    # intentionally leave blank - no modifications to dummy data
  } else {
    stop(paste0(
      "Unknown project_stage: ",
      project_stage,
      ". Please ensure project_stage argument = (project_stage_)type."
    ))
  }

  # Convert back to Arrow ----
  dummy_data <- as_arrow_table(dummy_data)
  return(dummy_data)
}
