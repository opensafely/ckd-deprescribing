##########################################################################
# This script does the following:
# 1. Loads output/dataset_inex.arrow created by generate_dataset_inex
# 2. Modifies the dummy data if being run locally
# 3. Type formats the variables
# 4. Applies QA criteria and inclusion/exclusion criteria
# 5. Compiles flow table a sensitivity table of varying CKD definitions
# 6. Tabulates medication counts 90 + 180 days before index date
# 7. Saves cleaned dataset, med-summary, tables and description files
##########################################################################

# Import libraries and functions -----------------------------------------
message("Import libraries and functions \n")
library(fs)
library(here)
library(arrow)
library(tidyverse)
source(here::here("analysis", "r_functions", "utilities", "fn_preprocess.r"))
source(here::here(
  "analysis",
  "r_functions",
  "utilities",
  "fn_modify_dummy_data.r"
))
source(here::here(
  "analysis",
  "r_functions",
  "utilities",
  "fn_data_describing.r"
))
source(here::here(
  "analysis",
  "r_functions",
  "utilities",
  "fn_disclosure_control.r"
))
source(here::here("analysis", "r_functions", "inex_criteria", "fn_qa.r"))
source(here::here(
  "analysis",
  "r_functions",
  "inex_criteria",
  "fn_dem_inex_criteria.r"
))
source(here::here(
  "analysis",
  "r_functions",
  "inex_criteria",
  "fn_ckd_inex_criteria.r"
))
source(here::here(
  "analysis",
  "r_functions",
  "inex_criteria",
  "fn_apply_flow_filter.r"
))

# Create output folders --------------------------------------------------
message("Create output folders")
dir_create(here::here("output", "data"))
dir_create(here::here("output", "data_descriptions", "cleaning_inex"))

# Import dates -----------------------------------------------------------
message("Import dates")
source(here::here("analysis", "config", "config.r"))
study_dates <- lapply(study_dates, function(x) as.Date(x))

# Load dataset, keeping in arrow format for speed ------------------------
message("Load the dataset for lazy processing")
input_filename <- "dataset_inex.arrow"
data_input <- arrow::open_dataset(
  here::here("output", input_filename),
  format = "ipc"
)

# Initialise the flow data frame -----------------------------------------
flow <- data.frame(
  Description = "Input",
  N = data_input |> summarise(n = n()) |> collect() |> pull(n),
  stringsAsFactors = FALSE
)

# Preprocess data: transform variables and modify dummy data -------------
data_preprocessed <- fn_preprocess(
  arrow_data = data_input,
  project_stage = "cleaning_inex",
  index_date = study_dates$index_date,
  one_row_per_patient = TRUE
)
flow <- fn_add_flow_row(
  data_preprocessed,
  flow,
  "Preprocessed: Removed rows with missing patient_id"
)

# Apply qa criteria ------------------------------------------------------
qa_output_list <- fn_qa(
  arrow_data = data_preprocessed,
  flow = flow,
  describe = FALSE # too memory intensive in real data
)
data_qa_applied <- qa_output_list$data
flow <- qa_output_list$flow

# Apply demographic inclusion and exclusion criteria ---------------------
dem_inex_output_list <- fn_dem_inex_criteria(
  arrow_data = data_qa_applied,
  flow = flow,
  describe = TRUE
)
data_dem_inex_applied <- dem_inex_output_list$data
flow <- dem_inex_output_list$flow

# Apply CKD inclusion criteria -------------------------------------------
ckd_inex_output_list <- fn_ckd_inex_criteria(
  arrow_data = data_dem_inex_applied,
  flow = flow,
  index_date = study_dates$index_date,
  describe = TRUE
)
data_ckd_inex_applied <- ckd_inex_output_list$data
flow <- ckd_inex_output_list$flow

# Apply KRT exclusion criteria -------------------------------------------
dialysis_inex_output_list <- fn_krt_inex_criteria_dialysis(
  arrow_data = data_ckd_inex_applied,
  flow = flow,
  describe = TRUE
)
data_dialysis_inex_applied <- dialysis_inex_output_list$data
flow <- dialysis_inex_output_list$flow

transplant_inex_output_list <- fn_krt_inex_criteria_transplant(
  arrow_data = data_dialysis_inex_applied,
  flow = flow,
  describe = TRUE
)
data_transplant_inex_applied <- transplant_inex_output_list$data
flow <- transplant_inex_output_list$flow

# SENSITIVITY: population n if KRT defined with 2ndary care too
sensitivity_krt_output <- data_transplant_inex_applied |>
  mutate(no_secondary_krt = !inex_krt_bin_secondary_care_only) |>
  fn_apply_flow_filter(
    flow,
    "no_secondary_krt",
    "SENSITIVITY ONLY: numbers if KRT definition also used secondary care codes"
  )
flow <- sensitivity_krt_output$flow

# SENSITIVITY: counts if definition of CKD allowed to vary
ckd_sensitivity_counts <- fn_ckd_def_sensitivity_checks(
  arrow_data_pre_filter = ckd_inex_output_list$data_pre_filter
)

# Rename cleaned dataset for clarity -------------------------------------
dataset_inex_cleaned <- data_transplant_inex_applied

# Tabulate the rough medication counts to help guide future medication parameters
med_counts <- dataset_inex_cleaned |>
  select(inex_med_num_90, inex_med_num_180) |>
  collect()

max_med_count <- max(med_counts, na.rm = TRUE)
message("Maximum medication count: ", max_med_count) # log only
candidate_max_meds <- seq(0, max_med_count, by = 5)

# SDC applied to output:
# - only rows where n_at_least > 7 are displayed so max_med_count is not inferred
# - row values (and population size) are rounded to nearest 5
med_count_summary <- expand_grid(
  time_window = names(med_counts),
  n_meds = candidate_max_meds
) |>
  rowwise() |>
  mutate(
    n_at_least = sum(med_counts[[time_window]] >= n_meds, na.rm = TRUE)
  ) |>
  ungroup() |>
  filter(n_at_least > 7) |>
  mutate(
    n_at_least = fn_apply_sdc(n_at_least),
    pct_at_least = round(100 * n_at_least / fn_apply_sdc(nrow(med_counts)), 1)
  )


# Save all  outputs -------------------------------------------------------
message("\nSave outputs:")

message(
  "Save medication count summary to output/data_descriptions/cleaning_inex/"
)
write_csv(
  med_count_summary,
  here::here(
    "output",
    "data_descriptions",
    "cleaning_inex",
    "med_count_summary.csv"
  )
)

message("Save cleaned dataset to output/data/")
dataset_inex_cleaned |>
  arrow::write_feather(
    here::here("output", "data", "dataset_inex_cleaned.arrow")
  )

message("Save flow table to output/data_descriptions/cleaning_inex/")
flow <- flow |> mutate(N = fn_apply_sdc(N)) # Apply SDC to the N column
write_csv(
  flow,
  here::here("output", "data_descriptions", "cleaning_inex", "data_flow.csv")
)

message(
  "Save CKD def sensitivity counts to output/data_descriptions/cleaning_inex/"
)
ckd_sensitivity_counts <- ckd_sensitivity_counts |> mutate(N = fn_apply_sdc(N))
write_csv(
  ckd_sensitivity_counts,
  here::here(
    "output",
    "data_descriptions",
    "cleaning_inex",
    "ckd_sensitivity_counts.csv"
  )
)
