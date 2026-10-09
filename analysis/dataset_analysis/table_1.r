##########################################################################
# This script does the following:
# 1. Imports and streamlines the dataset which table 1 will build over
# 2. Defines categorical, continuous and strata variables
# 3. Computes counts (by strata) of the categorical variables (SDC applied)
# 4. Computes median [IQR] (by strata) for the continuous variables
# 5. Combines 3 and 4 into a table 1 and saves output
##########################################################################

# Import libraries and functions -----------------------------------------
message("Import libraries and functions")
library(here)
library(fs)
library(arrow)
library(tidyverse)
source(here::here(
  "analysis",
  "r_functions",
  "utilities",
  "fn_disclosure_control.r"
))
source(here::here(
  "analysis",
  "r_functions",
  "utilities",
  "fn_data_describing.r"
))

# Create output folders --------------------------------------------------
message("Create output folder")
dir_create(here::here("output", "tables"))

# Load the population dataset --------------------------------------------
message("Load the desired columns of the dataset")

# wanted_cols <- c(
#   "patient_id",
#   "inex_dem_num_age",
#   "inex_dem_cat_sex",
#   "inex_num_egfr_1",
#   "inex_cat_ckd_stage"
#   # add more as desired
# )

input_filename <- "dataset_baseline_covariates_general.arrow"
dataset <- arrow::open_dataset(
  here::here("output", input_filename),
  format = "ipc"
) |>
  collect()

# Process the dataset -------------------------------------
message("Process the dataset")

# Create a CKD stage column
dataset <- dataset |>
  mutate(
    ckd_stage = paste0("G", basecov_gen_cat_ckd_stage)
  )

# Define the variables of interest for the table
message("Define the variables of interest")

strata_var <- "ckd_stage"

continuous_vars <- c(
  "basecov_gen_num_age",
  "basecov_gen_num_egfr_1"
  # add more
)
categorical_vars <- c(
  "basecov_gen_cat_sex",
  "basecov_gen_cat_ethnicity",
  "basecov_gen_cat_imd",
  "basecov_gen_cat_region",
  "basecov_gen_bin_care_home",
  "basecov_gen_bin_dm",
  "basecov_gen_bin_cvd_history"
  # add more
)

# Calculate SDC_applied denominators
message("Calculate denominators")

totals <- dataset |>
  # total numbers of people in the strata
  count(across(all_of(strata_var)), name = "stratum_N_sdc_applied") |>
  mutate(
    stratum_N_sdc_applied = as.integer(fn_apply_sdc(stratum_N_sdc_applied))
  ) |>
  # add in overall total n for whole dataset
  bind_rows(tibble(
    !!strata_var := "Overall",
    stratum_N_sdc_applied = as.integer(fn_apply_sdc(nrow(dataset)))
  ))

############################################################################
# Deal with the categorical variables first ---------------------------------
############################################################################
message("Categorical variables")

# Enforce they are all strings
dataset <- dataset |>
  mutate(across(all_of(categorical_vars), as.character))

# Pivot long - allows for easy counts across each categorical variable.
# Resulting columns:
# - patient_id
# - strata_var (whether that patient had CKD 4 or 5)
# - characteristic (which is one row per patient per categorical_var)
# - category (the patient's value for the given characteristic)
message("---Pivot long for easy counting")
categorical_vars_long <- dataset |>
  select(patient_id, all_of(strata_var), all_of(categorical_vars)) |>
  pivot_longer(
    cols = -c(patient_id, all_of(strata_var)),
    names_to = "characteristic",
    values_to = "category"
  ) |>
  mutate(
    category = case_when(
      is.na(category) ~ "Missing",
      category == "" ~ "Missing",
      category == "unknown" ~ "Missing",
      TRUE ~ as.character(category)
    )
  )

# Count the number of people in each characteristic/category/strata_var group
message("---Count numbers in each category by strata_var")
categorical_vars_counts <- categorical_vars_long |>
  count(
    characteristic,
    category,
    across(all_of(strata_var)),
    sort = TRUE,
    name = "N"
  )

# Then the overall counts for each characteristic/category
message("---Count overall numbers in each category")
categorical_vars_counts <- categorical_vars_counts |>
  bind_rows(
    categorical_vars_counts |>
      summarise(N = sum(N), .by = c(characteristic, category)) |>
      mutate(!!strata_var := "Overall")
  )


# Add in percentages (using SDC principles)
message("---Add in percentages")
categorical_vars_counts <- categorical_vars_counts |>
  left_join(totals, by = strata_var) |>
  mutate(
    N_sdc_applied = as.integer(fn_apply_sdc(N)),
    percent_sdc_applied = round(100 * N_sdc_applied / stratum_N_sdc_applied, 1)
  )

# Add a row at the top which is the total numbers overall and in strata
message("---And add rows for totals across strata_var")
categorical_vars_counts <- bind_rows(
  categorical_vars_counts |>
    distinct(across(all_of(strata_var)), stratum_N_sdc_applied) |>
    mutate(
      characteristic = "Total",
      category = NA_character_,
      N_sdc_applied = stratum_N_sdc_applied,
      percent_sdc_applied = NA_real_
    ),
  categorical_vars_counts
) |>
  select(-N, -stratum_N_sdc_applied)

# Change to one row per characteristic/category combo
message("---Pivot wide - one row per category")
categorical_vars_wide <- categorical_vars_counts |>
  pivot_wider(
    names_from = all_of(strata_var),
    values_from = c(N_sdc_applied, percent_sdc_applied),
    values_fill = 0 # fill blank values with 0 - non-disclosive
  )


############################################################################
# Now continuous variables -------------------------------------------------
############################################################################
message("Now continuous variables")
continuous_vars_long <- tibble()

# decide number of decimal places to round to for every continuous variable
round_value_lookup <- c(
  basecov_gen_num_age = 0,
  basecov_gen_num_egfr_1 = 1
  # add more as becomes necessary - every continuous var needs to be here
)

# Loop over each continuous variable
for (variable in continuous_vars) {
  message(sprintf("---Loop start - %s", variable))

  # set the round_value
  round_value <- round_value_lookup[[variable]]

  # initially calculate the median_iqr for each strata_var strata
  variable_summary <-
    fn_median_iqr(
      dataset,
      variable,
      "median_iqr",
      strata_var,
      round_value = round_value
    ) |>
    # then bind on the overall median_iqr for that variable
    bind_rows(
      fn_median_iqr(
        dataset,
        variable,
        "median_iqr",
        character(0), # no stratification
        round_value = round_value
      ) |>
        mutate(!!strata_var := "Overall")
    ) |>
    # then add label columns
    mutate(
      characteristic = variable,
      category = "Median (IQR)",
      percent_sdc_applied = NA_real_
    )

  continuous_vars_long <- bind_rows(continuous_vars_long, variable_summary)
  message(sprintf("---Loop end - %s", variable))
}

# have to rename median_iqr to make sure column names match categorical
continuous_vars_long <- continuous_vars_long |>
  rename(N_sdc_applied = median_iqr)

# Change to one row per variable
message("---Pivot wide - one row per continuous variable")
continuous_vars_wide <- continuous_vars_long |>
  pivot_wider(
    names_from = all_of(strata_var),
    values_from = c(N_sdc_applied, percent_sdc_applied)
  )

# Build final table 1
message("Build final table 1")

# Coerce the categorical counts to strings so bind_rows works
categorical_vars_wide <- categorical_vars_wide |>
  mutate(across(starts_with("N_sdc_applied"), as.character))

table_1 <- bind_rows(categorical_vars_wide, continuous_vars_wide)

# Save table 1
message("Save outputs")
write_csv(
  table_1,
  here::here(
    "output",
    "tables",
    "table_1.csv"
  )
)
