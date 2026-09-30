##########################################################################
# This script defines fn_dem_inex_criteria() which applies
# demographic inclusion and exclusion criteria
# - Excludes patients who are not alive at index date
# - Excludes patients outside the eligible age range at index date
# - Excludes patients without 12 months of continuous registration
#    prior to index date
# - Excludes patients with missing sex, region or IMD
# - Counts N at each step and adds to flow table
##########################################################################

fn_dem_inex_criteria <- function(
  arrow_data,
  flow,
  describe = TRUE
) {
  require(arrow)
  require(dplyr)

  # Filter and count the numbers with each demographic criteria pass
  message("\nDemographic exclusions:")
  interim_list <- fn_apply_flow_filter(
    arrow_data,
    flow,
    "inex_dem_bin_alive",
    "Demographic: Alive at index date"
  )
  interim_list <- fn_apply_flow_filter(
    interim_list$data,
    interim_list$flow,
    "inex_dem_bin_age_include",
    "Demographic: Aged between 18 and 110 on index date"
  )
  interim_list <- fn_apply_flow_filter(
    interim_list$data,
    interim_list$flow,
    "inex_dem_bin_12m_registered",
    "Demographic: Registered for 12+ months on index date"
  )
  interim_list <- fn_apply_flow_filter(
    interim_list$data,
    interim_list$flow,
    "inex_dem_bin_sex",
    "Demographic: Known sex that is male or female"
  )
  interim_list <- fn_apply_flow_filter(
    interim_list$data,
    interim_list$flow,
    "inex_dem_bin_region",
    "Demographic: Known region"
  )
  output_list <- fn_apply_flow_filter(
    interim_list$data,
    interim_list$flow,
    "inex_dem_bin_imd",
    "Demographic: Known deprivation level"
  )

  if (isTRUE(describe)) {
    fn_describe_data(
      data = collect(output_list$data),
      filepath = here::here(
        "output",
        "data_descriptions",
        "cleaning_inex",
        "dem_inex_applied.txt"
      )
    )
  }

  return(output_list)
}
