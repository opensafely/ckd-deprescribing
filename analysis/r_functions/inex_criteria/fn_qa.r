##########################################################################
# This script Defines fn_qa() which applies quality assurance
# exclusion criteria to the dataset:
# 1. Excludes patients with implausible data
# 2. Counts and records exclusions at each step
##########################################################################

fn_qa <- function(
  arrow_data,
  flow,
  describe = TRUE
) {
  require(arrow)
  require(dplyr)

  # Count the numbers that fail each qa criteria respectively
  message("\nQA exclusions:")
  interim_list <- fn_apply_flow_filter(
    arrow_data,
    flow,
    "inex_qa_bin_dob_known",
    "Quality Assurance: Date of birth not missing"
  )
  interim_list <- fn_apply_flow_filter(
    interim_list$data,
    interim_list$flow,
    "inex_qa_bin_dob_before_dod",
    "Quality Assurance: Date of birth before date of death"
  )
  interim_list <- fn_apply_flow_filter(
    interim_list$data,
    interim_list$flow,
    "inex_qa_bin_dob_not_future",
    "Quality Assurance: Date of birth not in future"
  )
  output_list <- fn_apply_flow_filter(
    interim_list$data,
    interim_list$flow,
    "inex_qa_bin_dod_not_future",
    "Quality Assurance: Date of death not in future"
  )

  if (isTRUE(describe)) {
    fn_describe_data(
      data = collect(output_list$data),
      filepath = here::here(
        "output",
        "data_descriptions",
        "cleaning_inex",
        "qa_applied.txt"
      )
    )
  }

  return(output_list)
}
