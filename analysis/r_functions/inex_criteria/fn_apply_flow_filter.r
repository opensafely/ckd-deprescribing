##########################################################################
# Small helper functions to help with inclusion/exclusion
#
# fn_add_flow_row takes arrow_data, counts the rows and adds the count (N)
# to a flow df with description column
#
# fn_apply_flow_filter envelopes the above flow function but also
# filters the dataset on a boolean variable (criterion_col)
##########################################################################

fn_add_flow_row <- function(arrow_data, flow, description) {
  require(arrow)
  require(dplyr)

  n <- arrow_data |> summarise(n = n()) |> collect() |> pull(n)
  message(sprintf("%s: N = %d", description, n))

  flow <- rbind(
    flow,
    data.frame(Description = description, N = n, stringsAsFactors = FALSE)
  )
  return(flow)
}


fn_apply_flow_filter <- function(arrow_data, flow, criterion_col, description) {
  require(arrow)
  require(dplyr)

  arrow_data_filtered <- arrow_data |> filter(.data[[criterion_col]])
  flow <- fn_add_flow_row(arrow_data_filtered, flow, description)
  return(list(data = arrow_data_filtered, flow = flow))
}
