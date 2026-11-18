##########################################################################
# This script defines fn_inex_first_pass_criteria() which applies
# first pass (screening) criteria. Excludes:
# - unknown sex, incompatible age, or not alive at study start date
# - no two creatinines consistent with eGFR < 60 (or raised uACR)
# Then counts and records exclusions at each step
##########################################################################

fn_inex_first_pass_criteria <- function(
  arrow_data,
  flow,
  first_pass_filter
) {
  require(arrow)
  require(dplyr)

  # Filter and count the numbers with each pass
  message("\nFirst pass exclusions:")
  interim_list <- fn_apply_flow_filter(
    arrow_data,
    flow,
    "inex_dem_bin_sex",
    "First pass: Sex recorded as male or female"
  )
  interim_list <- fn_apply_flow_filter(
    interim_list$data,
    interim_list$flow,
    "inex_dem_bin_age_possible",
    "First pass: Could be aged 18-110 during the study window"
  )
  interim_list <- fn_apply_flow_filter(
    interim_list$data,
    interim_list$flow,
    "inex_dem_bin_alive_study_window_start",
    "First pass: Alive at study window start"
  )

  if ("uacr" %in% first_pass_filter) {
    data <- interim_list$data |>
      mutate(
        inex_ckd_bin_first_pass = inex_ckd_bin_two_scr_above_cutoff |
          inex_ckd_bin_two_uacr_raised
      )

    output_list <- fn_apply_flow_filter(
      data,
      interim_list$flow,
      "inex_ckd_bin_first_pass",
      "First pass: Two creatinine values consistent with eGFR <60, or two raised uACR, >=90 days apart"
    )
  } else {
    output_list <- fn_apply_flow_filter(
      interim_list$data,
      interim_list$flow,
      "inex_ckd_bin_two_scr_above_cutoff",
      "First pass: Two creatinine values consistent with eGFR <60, >=90 days apart"
    )
  }

  return(output_list)
}
