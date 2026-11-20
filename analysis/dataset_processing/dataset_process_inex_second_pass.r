##########################################################################
# This script does the following:
# 1. Loads output/dataset_inex_second_pass.arrow created by yaml action
#    generate_dataset_inex_second_pass
# 2. Type formats the variables
# 3. Applies eGFR screening criteria for each CKD stage
# 4. Saves patient ids per stage and the flow table
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
  "fn_disclosure_control.r"
))
source(here::here(
  "analysis",
  "r_functions",
  "inex_criteria",
  "fn_inex_second_pass_criteria.r"
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
dir_create(here::here(
  "output",
  "data_descriptions",
  "cleaning_inex_second_pass"
))

# Import config ----------------------------------------------------------
message("Import config")
config <- read_json(
  here::here("output", "ckd_cohort_config.json"),
  simplifyVector = TRUE
)

# Load dataset and inex_first_pass flow table ----------------------------
message("Load the dataset for lazy processing")
input_filename <- "dataset_inex_second_pass.arrow"
data_input <- arrow::open_dataset(
  here::here("output", input_filename),
  format = "ipc"
)
flow <- read_csv(
  here::here(
    "output",
    "data_descriptions",
    "cleaning_inex_first_pass",
    "data_flow.csv"
  ),
  show_col_types = FALSE
)

# Preprocess data: type format variables ----------------------------------
data_preprocessed <- fn_preprocess(
  arrow_data = data_input,
  one_row_per_patient = TRUE
)

# Pass through the eGFR screening filter ---------------------------------
second_pass_output_list <- fn_inex_second_pass_criteria(
  arrow_data = data_preprocessed,
  ckd_stages_included = config$ckd_stages_included,
  ckd_stages = config$ckd_stages
)

# Save all outputs -------------------------------------------------------
message("\nSave outputs:")

for (stage_name in names(second_pass_output_list)) {
  message(sprintf("Save %s patient ids to output/data/", stage_name))
  second_pass_output_list[[stage_name]]$data |>
    select(patient_id) |>
    arrow::write_feather(
      here::here(
        "output",
        "data",
        paste0("dataset_inex_second_pass_", stage_name, ".arrow")
      )
    )

  flow <- bind_rows(flow, second_pass_output_list[[stage_name]]$flow)
}

flow <- flow |> mutate(N = fn_apply_sdc(N))

message(
  "Save flow table to output/data_descriptions/cleaning_inex_second_pass/"
)
write_csv(
  flow,
  here::here(
    "output",
    "data_descriptions",
    "cleaning_inex_second_pass",
    "data_flow.csv"
  )
)
