##########################################################################
# This script does the following:
# 1. Loads output/dataset_inex.arrow created by generate_dataset_inex
# 2. Modifies the dummy data if being run locally
# 3. Type formats the variables
# 4. Applies QA criteria and inclusion/exclusion criteria and compiles flow table
# 5. Plots and tabulates medication counts 90 + 180 days before index date
# 6. Saves cleaned dataset, plots, data-flow table and description files
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
dir_create(here::here("output", "figures", "cleaning_inex"))

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
  describe = TRUE
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
# 4 new variables added to data:
# 1. inex_num_egfr_1 - numerical value of most recent eGFR
# 2. inex_num_egfr_2 - numerical value of most recent eGFR 90+ days prior
#    to inex_num_egfr_1
# 3. inex_bin_has_ckd45_by_scr - boolean TRUE if eGFRs consistent
#    with CKD G4 or G5
# 4. inex_cat_ckd_stage_by_scr - category of eGFR derived CKD
#    (G4, G5, G4/G5, or no G4/G5)
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

# Rename cleaned dataset for clarity -------------------------------------
dataset_inex_cleaned <- data_transplant_inex_applied

# Examine medication counts in 90 and 180 days prior to index date -------
message("\nTabulate the medication counts")
med_count_summary <- dataset_inex_cleaned |>
  summarise(
    across(
      c(inex_med_num_90, inex_med_num_180),
      list(
        mean = ~ mean(.x, na.rm = TRUE),
        median = ~ median(.x, na.rm = TRUE),
        p90 = ~ quantile(.x, 0.9, na.rm = TRUE),
        p95 = ~ quantile(.x, 0.95, na.rm = TRUE)
      )
    )
  ) |>
  collect()

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

message("Save graph of medication counts")
plot_med_count_distribution <-
  dataset_inex_cleaned |>
  select(inex_med_num_90, inex_med_num_180) |>
  collect() |>
  pivot_longer(
    # necessary for ggplot to colour by time window
    cols = everything(),
    names_to = "time_window",
    values_to = "n_prescriptions"
  ) |>
  mutate(
    time_window = case_when(
      time_window == "inex_med_num_90" ~ "90 days",
      time_window == "inex_med_num_180" ~ "180 days"
    )
  ) |>
  ggplot(aes(x = n_prescriptions, colour = time_window, fill = time_window)) +
  geom_freqpoly(binwidth = 1, linewidth = 0.8) +
  labs(
    title = "Distribution of medication counts before index date",
    x = "Number of prescriptions",
    y = "Number of patients",
    colour = "Time window"
  )

ggsave(
  filename = here::here(
    "output",
    "figures",
    "cleaning_inex",
    "plot_med_count_distribution.png"
  ),
  plot = plot_med_count_distribution,
  width = 8,
  height = 6,
  dpi = 300
)

message("Save cleaned dataset to output/data/")
dataset_inex_cleaned |>
  arrow::write_feather(
    here::here("output", "data", "dataset_inex_cleaned.arrow"),
  )

message("Save flow table to to output/data_descriptions/cleaning_inex/")
write_csv(
  flow,
  here::here("output", "data_descriptions", "cleaning_inex", "data_flow.csv")
)
