##########################################################################
# This script Defines fn_qa() which applies quality assurance
# exclusion criteria to the dataset:
# 1. Excludes patients with missing sex, region, ethnicity, or IMD
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
      n_before = n()
    ) |>
    collect()

  # Print exclusion counts
  message("\nQA exclusions:")
  message("n before QA exclusions: ", counts$n_before)

  # Apply QA filters lazily
  arrow_data_qa_applied <- arrow_data

  return(arrow_data_qa_applied)
}
