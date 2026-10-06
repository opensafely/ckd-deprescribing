##########################################################################
# Helper to add a row to the flow table for the medication processing
# Works with long format data to pull n_patients and n_prescriptions
##########################################################################

fn_add_med_flow_row <- function(data, flow, description) {
  require(dplyr)

  n_patients <- n_distinct(data$patient_id)
  n_prescriptions <- sum(!is.na(data$dmd_code))
  message(sprintf(
    "%s: %d patients | %d prescriptions",
    description,
    n_patients,
    n_prescriptions
  ))

  flow <- rbind(
    flow,
    data.frame(
      Description = description,
      N_patients = n_patients,
      N_prescriptions = n_prescriptions,
      stringsAsFactors = FALSE
    )
  )
  return(flow)
}
