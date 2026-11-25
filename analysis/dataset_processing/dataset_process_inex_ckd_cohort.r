##########################################################################
# This script does the following:
# 1. Loads output/dataset_inex_ckd_cohort_{ckd_stage}.arrow
# 2. Type formats the variables
# 3. Computes the numbers that are excluded at each step of the CKD
#    cohort definition and demographic inclusions and exclusions and
#    then compiles into a flow table
# 6. Tabulates medication counts 90 + 180 days before index date
# 7. Saves cleaned dataset, med-summary, flow-tables and description files
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
  "inex_criteria",
  "fn_inex_ckd_cohort_criteria.r"
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
  "process_inex_ckd_cohort"
))

# Import config ----------------------------------------------------------
message("Import config")
config <- read_json(
  here::here("output", "ckd_cohort_config.json"),
  simplifyVector = TRUE
)

# Load first and second pass flow tables ---------------------------------
message("Load first and second pass flow tables")
first_pass_flow <- read_csv(
  here::here(
    "output",
    "data_descriptions",
    "process_inex_first_pass",
    "data_flow.csv"
  ),
  show_col_types = FALSE
)
second_pass_flow <- read_csv(
  here::here(
    "output",
    "data_descriptions",
    "process_inex_second_pass",
    "data_flow.csv"
  ),
  show_col_types = FALSE
)

# Initialise the diagnostic output tables
med_count_summary <- data.frame()
egfr_gap_summary <- data.frame()
index_year_summary <- data.frame()
loop_restart_summary <- data.frame()
secondary_krt_summary <- data.frame()


# Big loop through each included CKD stage -----------------------------------
for (stage_name in config$ckd_stages_included) {
  message(sprintf("\nProcess CKD cohort: %s", stage_name))

  # Load the dataset
  data_input <- arrow::open_dataset(
    here::here(
      "output",
      paste0("dataset_inex_ckd_cohort_", stage_name, ".arrow")
    ),
    format = "ipc"
  )

  # Type format the variables
  data_preprocessed <- fn_preprocess(
    arrow_data = data_input,
    one_row_per_patient = TRUE
  )

  # skimr() the input file for diagnostics
  fn_describe_data(
    data = collect(data_preprocessed),
    filepath = here::here(
      "output",
      "data_descriptions",
      "process_inex_ckd_cohort",
      paste0(stage_name, "_input.txt")
    )
  )

  # Initialise a stage_flow table
  stage_flow <- data.frame(
    Description = character(),
    N = numeric(),
    stringsAsFactors = FALSE
  )

  # Apply CKD cohort definition inex criteria
  cohort_output_list <- fn_inex_ckd_cohort_criteria(
    arrow_data = data_preprocessed,
    flow = stage_flow,
    upper = config$ckd_stages[[stage_name]]$upper,
    k_loops = config$k_loops
  )

  # skimr() the output file for diagnostics
  cohort_data <- collect(cohort_output_list$data)
  fn_describe_data(
    data = cohort_data,
    filepath = here::here(
      "output",
      "data_descriptions",
      "process_inex_ckd_cohort",
      paste0(stage_name, "_cohort.txt")
    )
  )

  # Tabulate the rough medication counts to help guide future medication parameters
  med_counts <- cohort_data |>
    select(inex_med_num_90, inex_med_num_180)

  max_med_count <- max(med_counts, na.rm = TRUE)
  message("Maximum medication count: ", max_med_count) # log only
  med_sequence <- seq(0, max_med_count, by = 5)

  stage_med_count_summary <- expand_grid(
    time_window = names(med_counts),
    n_meds = med_sequence
  ) |>
    rowwise() |>
    mutate(
      n_at_least = sum(med_counts[[time_window]] >= n_meds, na.rm = TRUE)
    ) |>
    ungroup() |>
    filter(n_at_least > 7) |> # only rows where n_at_least > 7 are displayed
    mutate(
      n_at_least = fn_apply_sdc(n_at_least), # row values rounded to 5
      pct_at_least = round(
        100 * n_at_least / fn_apply_sdc(nrow(med_counts)),
        1
      ),
      stage = stage_name
    )

  med_count_summary <- bind_rows(med_count_summary, stage_med_count_summary)

  # Tabulate the gaps between eGFR0, eGFR1 and eGFR2
  stage_egfr_gap_summary <- cohort_data |>
    transmute(
      egfr0_to_egfr1 = as.numeric(inex_ckd_date_egfr1 - inex_ckd_date_egfr0),
      egfr1_to_index = as.numeric(
        inex_ckd_date_index_date - inex_ckd_date_egfr1
      ),
      egfr0_to_index = as.numeric(
        inex_ckd_date_index_date - inex_ckd_date_egfr0
      )
    ) |>
    pivot_longer(everything(), names_to = "gap", values_to = "days") |>
    mutate(
      band = cut(
        days,
        breaks = c(0, 90, 180, 365, 730, 1826, Inf),
        labels = c(
          "0-90 days",
          "91-180 days",
          "181-365 days",
          "1-2 years",
          "2-5 years",
          ">5 years"
        )
      )
    ) |>
    count(gap, band, .drop = FALSE) |>
    mutate(
      n = fn_apply_sdc(n),
      stage = stage_name
    )

  egfr_gap_summary <- bind_rows(egfr_gap_summary, stage_egfr_gap_summary)

  # Tabulate the index dates by calendar year
  stage_index_year_summary <- cohort_data |>
    mutate(index_year = year(inex_ckd_date_index_date)) |>
    count(index_year) |>
    mutate(
      n = fn_apply_sdc(n),
      stage = stage_name
    )

  index_year_summary <- bind_rows(index_year_summary, stage_index_year_summary)

  # Tabulate the number of loop restarts in everyone entering the stage
  stage_loop_restart_summary <- data_preprocessed |>
    count(inex_ckd_num_n_loop_restarts) |>
    collect() |>
    arrange(inex_ckd_num_n_loop_restarts) |>
    mutate(
      n = fn_apply_sdc(n),
      stage = stage_name
    )

  loop_restart_summary <- bind_rows(
    loop_restart_summary,
    stage_loop_restart_summary
  )

  # Tabulate secondary care KRT evidence in the final cohort
  stage_secondary_krt_summary <- cohort_data |>
    mutate(
      secondary_care_krt_type = coalesce(
        inex_krt_cat_secondary_care_krt_type,
        "none" # none if inex_krt_cat_secondary_care_krt_type is NA
      )
    ) |>
    count(secondary_care_krt_type) |>
    mutate(
      n = fn_apply_sdc(n),
      stage = stage_name
    )

  secondary_krt_summary <- bind_rows(
    secondary_krt_summary,
    stage_secondary_krt_summary
  )

  # Save dataset - only columns that are needed
  message(sprintf("Save %s cohort to output/data/", stage_name))
  cohort_data |>
    select(
      patient_id,
      inex_ckd_date_index_date,
      inex_ckd_date_egfr0,
      inex_ckd_date_egfr1,
      inex_ckd_bin_same_registration,
      inex_krt_bin_secondary_care_only
    ) |>
    arrow::write_feather(
      here::here(
        "output",
        "data",
        paste0("dataset_inex_ckd_cohort_processed_", stage_name, ".arrow")
      )
    )

  # Build the stage flow table, apply SDC and save
  stage_flow <- bind_rows(
    first_pass_flow,
    second_pass_flow |> filter(stage == stage_name) |> select(-stage),
    cohort_output_list$flow
  ) |>
    mutate(N = fn_apply_sdc(N))

  message(sprintf(
    "Save %s flow table to output/data_descriptions/process_inex_ckd_cohort/",
    stage_name
  ))
  write_csv(
    stage_flow,
    here::here(
      "output",
      "data_descriptions",
      "process_inex_ckd_cohort",
      paste0("data_flow_", stage_name, ".csv")
    )
  )
}

# Save outputs

# egfr date distribution tables
message(
  "Save eGFR gap summary to output/data_descriptions/process_inex_ckd_cohort/"
)
write_csv(
  egfr_gap_summary,
  here::here(
    "output",
    "data_descriptions",
    "process_inex_ckd_cohort",
    "egfr_gap_summary.csv"
  )
)

# medication table row distribution tables
message(
  "Save medication count summary to output/data_descriptions/process_inex_ckd_cohort/"
)
write_csv(
  med_count_summary,
  here::here(
    "output",
    "data_descriptions",
    "process_inex_ckd_cohort",
    "med_count_summary.csv"
  )
)

# Distribution of index dates by year
message(
  "Save index year summary to output/data_descriptions/process_inex_ckd_cohort/"
)
write_csv(
  index_year_summary,
  here::here(
    "output",
    "data_descriptions",
    "process_inex_ckd_cohort",
    "index_year_summary.csv"
  )
)

# Distribution of loops each person needed to resolve; k_loops + 1 = unresolved
message(
  "Save loop restart summary to output/data_descriptions/process_inex_ckd_cohort/"
)
write_csv(
  loop_restart_summary,
  here::here(
    "output",
    "data_descriptions",
    "process_inex_ckd_cohort",
    "loop_restart_summary.csv"
  )
)

# Tabulation of the secondary care KRT population to see how much difference that would make
message(
  "Save secondary care KRT summary to output/data_descriptions/process_inex_ckd_cohort/"
)
write_csv(
  secondary_krt_summary,
  here::here(
    "output",
    "data_descriptions",
    "process_inex_ckd_cohort",
    "secondary_krt_summary.csv"
  )
)
