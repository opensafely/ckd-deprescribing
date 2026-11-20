##########################################################################
# This script does the following:
# 1. Loads output/dataset_inex_first_pass.arrow created by yaml action
#    generate_dataset_inex_first_pass
# 2. Modifies the dummy data if being run locally
# 3. Type formats the variables
# 4. Applies QA criteria and first pass screening criteria
# 5. Saves patient ids and flow table
##########################################################################

# Import libraries and functions -----------------------------------------
message("Import libraries and functions \n")
library(fs)
library(here)
library(arrow)
library(tidyverse)
library(jsonlite)
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
  "fn_disclosure_control.r"
))
source(here::here(
  "analysis",
  "r_functions",
  "inex_criteria",
  "fn_apply_flow_filter.r"
))
source(here::here("analysis", "r_functions", "inex_criteria", "fn_qa.r"))
source(here::here(
  "analysis",
  "r_functions",
  "inex_criteria",
  "fn_inex_first_pass_criteria.r"
))

# Create output folders --------------------------------------------------
message("Create output folders")
dir_create(here::here("output", "data"))
dir_create(here::here(
  "output",
  "data_descriptions",
  "cleaning_inex_first_pass"
))

# Import config ----------------------------------------------------------
message("Import config")
config <- read_json(
  here::here("output", "ckd_cohort_config.json"),
  simplifyVector = TRUE
)

# Load dataset, keeping in arrow format for speed ------------------------
message("Load the dataset for lazy processing")
input_filename <- "dataset_inex_first_pass.arrow"
data_input <- arrow::open_dataset(
  here::here("output", input_filename),
  format = "ipc"
)

# Initialise the flow data frame -----------------------------------------
flow <- data.frame(
  Description = "Registered at a TPP practice at any point in the study window",
  N = data_input |> summarise(n = n()) |> collect() |> pull(n),
  stringsAsFactors = FALSE
)

# Preprocess data: transform variables and modify dummy data -------------
data_preprocessed <- fn_preprocess(
  arrow_data = data_input,
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

# Apply first pass criteria ----------------------------------------------
first_pass_output_list <- fn_inex_first_pass_criteria(
  arrow_data = qa_output_list$data,
  flow = qa_output_list$flow,
  first_pass_filter = config$first_pass_filter
)

# Save all  outputs -------------------------------------------------------
message("\nSave outputs:")

message("Save first pass patient ids to output/data/")
first_pass_output_list$data |>
  select(patient_id) |>
  arrow::write_feather(
    here::here("output", "data", "dataset_inex_first_pass_processed.arrow")
  )

message("Save flow table to output/data_descriptions/cleaning_inex_first_pass/")
flow <- first_pass_output_list$flow |> mutate(N = fn_apply_sdc(N)) # Apply SDC to the N column
write_csv(
  flow,
  here::here(
    "output",
    "data_descriptions",
    "cleaning_inex_first_pass",
    "data_flow.csv"
  )
)
