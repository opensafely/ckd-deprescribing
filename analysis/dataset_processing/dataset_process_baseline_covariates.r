##########################################################################
# This script does the following:
# 1. Loads general baseline covariates, plus any medicine-specific
#    covariate datasets in the .yaml args, and joins them on patient_id
# 2. Preprocesses data (type formatting, dummy data modification)
# 3. Sets factor reference levels and handles missingness (fn_ref)
# 4. Saves dataset_baseline_covariates_{label}_processed.arrow
##########################################################################

# Import libraries and functions -----------------------------------------
message("Import libraries and functions")
library(fs)
library(here)
library(arrow)
library(tidyverse)
source(here::here("analysis", "config", "config.r"))
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
  "fn_ref.r"
))
source(here::here(
  "analysis",
  "r_functions",
  "utilities",
  "fn_data_describing.r"
))

# Create output folders --------------------------------------------------
message("Create output folders")
dir_create(here::here("output", "data"))
dir_create(here::here(
  "output",
  "data_descriptions",
  "process_baseline_covariates"
))

# Import dates -----------------------------------------------------------
message("Import dates")
study_dates <- lapply(study_dates, function(x) as.Date(x))

# Check args passed in with project.yaml, and create output_file_label ---
# Probably only ever one arg but scaffolded for >1 just in case
message("Read .yaml arguments")

args <- commandArgs(trailingOnly = TRUE)
message("args: ", paste(args, collapse = ", "))
output_file_label <- if (length(args) == 0) {
  "general"
} else {
  paste(args, collapse = "_")
}

# Load baseline covariates datasets -------------------------------
# General covariates
message("Load the dataset")
input_filename <- "dataset_baseline_covariates_general.arrow"
data_input <- arrow::open_dataset(
  here::here("output", input_filename),
  format = "ipc"
)

# Medicine specific covariates - if specified
for (name in args) {
  other_covariates <- arrow::open_dataset(
    here::here(
      "output",
      sprintf("dataset_baseline_covariates_%s.arrow", name)
    ),
    format = "ipc"
  )
  data_input <- left_join(data_input, other_covariates, by = "patient_id")
}

# Preprocess data: transform variables and modify dummy data -------------
data_preprocessed <- fn_preprocess(
  arrow_data = data_input,
  project_stage = "process_baseline_covariates",
  index_date = study_dates$index_date
) |>
  collect()

# fn_ref() handles missingness and sorts factor reference levels ---------
data_ref <- fn_ref(
  input = data_preprocessed,
  suffix = "process_baseline_covariates",
  describe = FALSE
)

# Break certain continuous variables into categories ---------------------
data_ref <- data_ref |>
  mutate(
    basecov_gen_cat_n_scr_tests = cut(
      basecov_gen_num_n_scr_tests,
      breaks = c(-Inf, 1, 3, 5, Inf),
      labels = c("0-1", "2-3", "4-5", "6+")
    )
  )

data_ref <- data_ref |>
  mutate(
    basecov_gen_cat_cms = cut(
      percent_rank(basecov_gen_num_cms),
      breaks = c(0, 0.25, 0.5, 0.75, 1),
      labels = c("Q1", "Q2", "Q3", "Q4"),
      include.lowest = TRUE
    )
  )

# Save cleaned dataset to output folder ----------------------------------
message("Saving cleaned dataset to output folder")

data_ref |>
  arrow::write_feather(
    here::here(
      "output",
      "data",
      sprintf(
        "dataset_baseline_covariates_%s_processed.arrow",
        output_file_label
      )
    )
  )
