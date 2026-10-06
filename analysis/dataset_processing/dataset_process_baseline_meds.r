##########################################################################
# This script does the following:
# 1. Loads medication dataset (dataset_baseline_meds.arrow) and preprocesses it
# 2. Separates patients with no medications recorded for later reattachment
# 3. Loads pre-built dmd_lookup from local_processing/medication_lookup_tables/
# 4. Converts patient DMD codes to BNF substance codes via join to dmd_lookup
# 5. Applies minimal medication exclusion criteria
# 6. Reattaches patients with no medications
# 7. Saves processed dataset, flow table, and data descriptions
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
  "medications",
  "fn_med_data_conversions.r"
))
source(here::here(
  "analysis",
  "r_functions",
  "medications",
  "fn_med_inex_criteria.r"
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
source(here::here(
  "analysis",
  "r_functions",
  "medications",
  "fn_add_med_flow_row.r"
))


# Create output folders --------------------------------------------------
message("Create output folders")
dir_create(here::here("output", "data"))
dir_create(here::here("output", "data_descriptions", "process_baseline_meds"))

# Import dates -----------------------------------------------------------
message("Import dates")
study_dates <- lapply(study_dates, function(x) as.Date(x))

# Load dataset -----------------------------------------------------------
message("Load the dataset")
input_filename <- "dataset_baseline_meds.arrow"
data_input <- arrow::open_dataset(
  here::here("output", input_filename),
  format = "ipc"
)

# Preprocess data: transform variables and modify dummy data -------------
data_preprocessed <- fn_preprocess(
  arrow_data = data_input,
  project_stage = "process_baseline_meds",
  index_date = study_dates$index_date
) |>
  collect() # have to collect for the next steps

# Full list of patient IDs for denominator in later summaries
all_patient_ids <- tibble(patient_id = data_preprocessed$patient_id)

# Check whether/how many patients med lists exceed the number of slots
dmd_cols <- grep("^med_dmd_code", names(data_preprocessed), value = TRUE)
n_slots <- length(dmd_cols)
last_slot <- paste0("med_dmd_code_", n_slots)
n_patients_at_slot_cap <- data_preprocessed |>
  filter(!is.na(.data[[last_slot]])) |>
  nrow()

if (n_patients_at_slot_cap > 0) {
  warning(sprintf(
    "%d patients filled all %d medication slots: medications may be truncated",
    n_patients_at_slot_cap,
    n_slots
  ))
}

# Initialise the flow data frame -----------------------------------------
# The data are still wide here hence n_prescriptions using unlist()
flow <- data.frame(
  Description = "Input",
  N_patients = data_preprocessed |> summarise(n = n()) |> pull(n),
  N_prescriptions = sum(!is.na(unlist(data_preprocessed[dmd_cols]))),
  stringsAsFactors = FALSE
)

# Separate patients with no medications and record in flow ---------------
data_with_meds <- data_preprocessed |>
  filter(!is.na(med_dmd_code_1)) # if first slot empty, all slots empty

flow <- rbind(
  flow,
  data.frame(
    Description = "Patients with at least one prescription",
    N_patients = data_with_meds |> summarise(n = n()) |> pull(n),
    N_prescriptions = sum(!is.na(unlist(data_with_meds[dmd_cols]))),
    stringsAsFactors = FALSE
  )
)

# Load pre-built medication lookup table ---------------------------------
dmd_lookup <- readRDS(here::here(
  "local_processing",
  "medication_lookup_tables",
  "dmd_lookup.rds"
))

# Convert dmd_codes to BNF codes for categorisation ----------------------
data_dmd_converted <- fn_dmd_to_bnf(
  patient_data = data_with_meds,
  project_stage = "process_baseline_meds",
  dmd_lookup = dmd_lookup,
  output = "long",
  unmapped_action = "drop"
)
flow <- fn_add_med_flow_row(
  data_dmd_converted,
  flow,
  "Dropped prescriptions that could not be mapped dm+d to BNF"
)

# Apply minimal medication exclusion criteria ----------------------------
# Exclude BNF chapters that will never be analysed; no route exclusions
data_exclusions_applied <- data_dmd_converted |>
  mutate(bnf_chapter_code = substr(bnf_substance_code, 1, 2)) |>
  fn_apply_med_inex_criteria(
    project_stage = "process_baseline_meds",
    exclude_bnf_chapters = exclude_bnf_chapters$base,
    exclude_route_cats = NULL
  ) |>
  select(-bnf_chapter_code)
flow <- fn_add_med_flow_row(
  data_exclusions_applied,
  flow,
  "BNF chapters that will not be analysed excluded"
)

# Reattach patients with no medications via left join --------------------
dataset_baseline_meds_processed <- all_patient_ids |>
  left_join(data_exclusions_applied, by = "patient_id") |>
  arrange(patient_id, med_index)
flow <- fn_add_med_flow_row(
  dataset_baseline_meds_processed,
  flow,
  "Processed dataset (those without medications reattached)"
)

# Add diagnostic information to the flow table ----------------------------
# nb. these rows are not steps in the flow

# extent of BNF imputation (from VTM) that is in patient data
n_imputed_prescriptions <- sum(
  data_exclusions_applied$bnf_imputed,
  na.rm = TRUE
)
n_imputed_patients <- data_exclusions_applied |>
  filter(bnf_imputed) |>
  summarise(n = n_distinct(patient_id)) |>
  pull(n)

flow <- rbind(
  flow,
  data.frame(
    Description = c(
      "DIAGNOSTIC: patients with all medication slots filled",
      "DIAGNOSTIC: numbers with BNF code imputed from VTM"
    ),
    N_patients = c(n_patients_at_slot_cap, n_imputed_patients),
    N_prescriptions = c(NA, n_imputed_prescriptions),
    stringsAsFactors = FALSE
  )
)

# Save all output ---------------------------------------------------------
message("Save outputs:")

# skimr() output of processed data for diagnostic checking
message("--- Description of processed dataset")
fn_describe_data(
  data = dataset_baseline_meds_processed,
  filepath = here::here(
    "output",
    "data_descriptions",
    "process_baseline_meds",
    "processed.txt"
  )
)


# Flow table
message("--- Flow table to output/data_descriptions/process_baseline_meds/")
flow <- flow |> mutate(across(c(N_patients, N_prescriptions), fn_apply_sdc))
write_csv(
  flow,
  here::here(
    "output",
    "data_descriptions",
    "process_baseline_meds",
    "data_flow.csv"
  )
)

# Final dataset to carry forward
message("--- Processed dataset to output/data/")
dataset_baseline_meds_processed |>
  arrow::write_feather(
    here::here("output", "data", "dataset_baseline_meds_processed.arrow")
  )
