##########################################################################
# This script Defines fn_qa() which applies quality assurance
# exclusion criteria to the dataset:
# 1. Excludes patients with implausible data
# 2. Counts and records exclusions at each step
##########################################################################

fn_qa <- function(
  arrow_data
) {
  require(arrow)
  require(dplyr)

  # Count the numbers that fail each qa criteria respectively
  counts <- arrow_data |>
    summarise(
      n_before = n(),
      n_dob_unknown = sum(!inex_qa_bin_dob_known, na.rm = TRUE),
      n_dob_after_dod = sum(!inex_qa_bin_dob_before_dod, na.rm = TRUE),
      n_dob_future = sum(!inex_qa_bin_dob_not_future, na.rm = TRUE),
      n_dod_future = sum(!inex_qa_bin_dod_not_future, na.rm = TRUE)
    ) |>
    collect()

  # Print exclusion counts
  message("\nQA exclusions:")
  message("n before QA exclusions: ", counts$n_before)
  message("Missing date of birth: ", counts$n_dob_unknown)
  message("Date of birth after date of death: ", counts$n_dob_after_dod)
  message("Date of birth in the future: ", counts$n_dob_future)
  message("Date of death in the future: ", counts$n_dod_future)

  # Apply QA filters lazily
  arrow_data_qa_applied <- arrow_data |>
    filter(
      inex_qa_bin_dob_known,
      inex_qa_bin_dob_before_dod,
      inex_qa_bin_dob_not_future,
      inex_qa_bin_dod_not_future
    )

  return(arrow_data_qa_applied)
}
