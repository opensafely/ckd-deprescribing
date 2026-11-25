##########################################################################
# This script defines fn_inex_ckd_cohort_criteria() which applies the
# CKD cohort definition and index date criteria for each CKD stage.
# Refer to docs/figures/ckd-cohort-logic.drawio.svg for the exclusions
#
# Excludes:
# - eGFR pair still interrupted by an eGFR at or above the limit after
#   k_loops restarts (unresolved)
# - no second eGFR below the limit >=90 days after the first found during
#   the loop (everyone still in the cohort after this has a qualifying pair)
# - no eGFR prior to the qualifying pair at or above the limit (not incident)
# - index date outside the study window
# - not registered on index date
# - not registered 12+ months by index date
# - not alive on index date
# - not aged 18-110 on index date
# - most recent primary care KRT code before index is dialysis
# - most recent primary care KRT code before index is transplant
#
# Then counts and records exclusions at each step
##########################################################################

fn_inex_ckd_cohort_criteria <- function(
  arrow_data,
  flow,
  upper,
  k_loops
) {
  require(arrow)
  require(dplyr)

  # Create KRT flags so that TRUE = keep
  data <- arrow_data |>
    mutate(
      inex_krt_bin_no_dialysis = !(inex_krt_bin_has_primary_care_krt_code &
        inex_krt_cat_primary_care_krt_type == "dialysis"),
      inex_krt_bin_no_transplant = !(inex_krt_bin_has_primary_care_krt_code &
        inex_krt_cat_primary_care_krt_type == "transplant")
    )

  # Filter and count the numbers with each pass
  message("\nCKD cohort exclusions:")
  interim_list <- fn_apply_flow_filter(
    data,
    flow,
    "inex_ckd_bin_resolved",
    sprintf(
      "CKD cohort: Resolved within %s loop restarts",
      k_loops
    )
  )
  interim_list <- fn_apply_flow_filter(
    interim_list$data,
    interim_list$flow,
    "inex_ckd_bin_has_egfr2",
    sprintf(
      "CKD cohort: Second eGFR <%s >=90 days after the first found during the loop",
      upper
    )
  )
  interim_list <- fn_apply_flow_filter(
    interim_list$data,
    interim_list$flow,
    "inex_ckd_bin_has_egfr0",
    sprintf("CKD cohort: Earlier eGFR >=%s found (i.e. incident)", upper)
  )
  interim_list <- fn_apply_flow_filter(
    interim_list$data,
    interim_list$flow,
    "inex_ckd_bin_index_in_window",
    "CKD cohort: Index date within study window"
  )
  interim_list <- fn_apply_flow_filter(
    interim_list$data,
    interim_list$flow,
    "inex_dem_bin_is_registered",
    "CKD cohort: Registered on index date"
  )
  interim_list <- fn_apply_flow_filter(
    interim_list$data,
    interim_list$flow,
    "inex_dem_bin_12m_registered",
    "CKD cohort: Registered for 12+ months on index date"
  )
  interim_list <- fn_apply_flow_filter(
    interim_list$data,
    interim_list$flow,
    "inex_dem_bin_alive",
    "CKD cohort: Alive at index date"
  )
  interim_list <- fn_apply_flow_filter(
    interim_list$data,
    interim_list$flow,
    "inex_dem_bin_age_include",
    "CKD cohort: Aged between 18 and 110 on index date"
  )
  interim_list <- fn_apply_flow_filter(
    interim_list$data,
    interim_list$flow,
    "inex_krt_bin_no_dialysis",
    "CKD cohort: Most recent primary care KRT code before index is not dialysis"
  )
  output_list <- fn_apply_flow_filter(
    interim_list$data,
    interim_list$flow,
    "inex_krt_bin_no_transplant",
    "CKD cohort: Most recent primary care KRT code before index is not transplant"
  )

  return(output_list)
}
