##########################################################################
# This script defines fn_dem_inex_criteria() which applies
# demographic inclusion and exclusion criteria
# - Excludes patients who are not alive at index date
# - Excludes patients outside the eligible age range at index date
# - Excludes patients without 12 months of continuous registration
#    prior to index date
# - Excludes patients with missing sex, region or IMD
# - Counts and records exclusions at each step
##########################################################################

fn_dem_inex_criteria <- function(
  arrow_data
) {
  require(arrow)
  require(dplyr)

  # Count the numbers that fail each qa criteria respectively
  counts <- arrow_data |>
    summarise(
      n_before = n(),
      n_not_alive = sum(!inex_dem_bin_alive, na.rm = TRUE),
      n_age_out_of_range = sum(!inex_dem_bin_age_include, na.rm = TRUE),
      n_not_registered_1yr = sum(!inex_dem_bin_12m_registered, na.rm = TRUE),
      n_missing_sex = sum(!inex_dem_bin_sex, na.rm = TRUE),
      n_missing_region = sum(!inex_dem_bin_region, na.rm = TRUE),
      n_missing_imd = sum(!inex_dem_bin_imd, na.rm = TRUE)
    ) |>
    collect()

  # Print exclusion counts
  message("\nDemographic exclusions:")
  message("n before demographic exclusions: ", counts$n_before)
  message("Not alive at index date: ", counts$n_not_alive)
  message("Age out of range: ", counts$n_age_out_of_range)
  message("Registered <1 yr: ", counts$n_not_registered_1yr)
  message("Missing sex: ", counts$n_missing_sex)
  message("Missing region: ", counts$n_missing_region)
  message("Missing deprivation level: ", counts$n_missing_imd)

  # Apply demographic filters lazily
  arrow_data_dem_inex_applied <- arrow_data |>
    filter(
      inex_dem_bin_alive,
      inex_dem_bin_age_include,
      inex_dem_bin_12m_registered,
      inex_dem_bin_sex,
      inex_dem_bin_region,
      inex_dem_bin_imd
    )

  return(arrow_data_dem_inex_applied)
}
