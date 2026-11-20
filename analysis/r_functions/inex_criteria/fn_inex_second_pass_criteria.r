##########################################################################
# This script defines fn_inex_second_pass_criteria() which applies
# the second pass (eGFR screening) criteria. It counts the numbers of people
# who COULD possibly be included in each CKD cohort:
# - first it splits those who have 2x eGFRs below the upper range value
#   for the CKD stage in question
# - and then removes those who, despite having two values below the upper
#   range value, don't actually then have a value within that CKD range
##########################################################################

fn_inex_second_pass_criteria <- function(
  arrow_data,
  ckd_stages_included,
  ckd_stages
) {
  require(arrow)
  require(dplyr)

  # initialise the output
  output_list <- list()

  for (stage_name in ckd_stages_included) {
    upper <- ckd_stages[[stage_name]]$upper
    lower <- ckd_stages[[stage_name]]$lower

    stage_flow <- data.frame(
      Description = character(),
      N = numeric(),
      stringsAsFactors = FALSE
    )

    message(sprintf("\nSecond pass exclusions: %s", stage_name))
    interim_list <- fn_apply_flow_filter(
      arrow_data,
      stage_flow,
      paste0("inex_ckd_bin_two_egfr_below_", upper),
      sprintf(
        "Second pass: Two eGFRs <%s >=90 days apart, second in study window",
        upper
      )
    )
    output_list[[stage_name]] <- fn_apply_flow_filter(
      interim_list$data,
      interim_list$flow,
      paste0("inex_ckd_bin_possible_", stage_name),
      sprintf(
        "Second pass: Two eGFRs <%s and at least one >=%s",
        upper,
        lower
      )
    )
  }

  return(output_list)
}
