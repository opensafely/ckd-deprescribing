##############################################################################
# This script is reused from Bristol EHR group template: e.g. see
# https://github.com/opensafely/polypharmacy-deprescribing-dementia/
# It takes each categorical variable, handles missingness in the variable,
# and sets the reference levels when converting them to factors.
##############################################################################

fn_ref <- function(input, suffix = "", describe = TRUE) {
  ##############################################################################
  # Missing values
  # Many of these are defensive checks - the ehrQL should manage most of these
  # situations by itself, but not harmful to keep them
  ##############################################################################
  # Handle missing values in basecov_gen_cat_sex ---------------------------------------
  print("Handle missing values in basecov_gen_cat_sex")

  if ("basecov_gen_cat_sex" %in% names(input)) {
    input$basecov_gen_cat_sex <- if_else(
      input$basecov_gen_cat_sex %in% c("male", "female"),
      input$basecov_gen_cat_sex,
      "Missing"
    )
    if ("Missing" %in% unique(input$basecov_gen_cat_sex)) {
      stop("basecov_gen_cat_sex contains missing values.")
    }
  }

  # Handle missing values in basecov_gen_cat_imd ---------------------------------------
  print('Handle missing values in basecov_gen_cat_imd')

  if ("basecov_gen_cat_imd" %in% names(input)) {
    imd_max <- max(
      as.integer(sub(" .*", "", unique(input$basecov_gen_cat_imd))),
      na.rm = TRUE
    )
    imd_levels <- c(
      "1 (most deprived)",
      as.character(seq(2, imd_max - 1)),
      sprintf("%i (least deprived)", imd_max)
    )

    input$basecov_gen_cat_imd <- if_else(
      input$basecov_gen_cat_imd %in%
        imd_levels,
      input$basecov_gen_cat_imd,
      "Missing"
    )
  }

  # Handle missing values in basecov_gen_cat_ethnicity ---------------------------------
  if ("basecov_gen_cat_ethnicity" %in% names(input)) {
    print('Handle missing values in basecov_gen_cat_ethnicity')
    input$basecov_gen_cat_ethnicity <- if_else(
      input$basecov_gen_cat_ethnicity %in%
        c(
          # 6 category labels
          "White",
          "Mixed",
          "Asian",
          "Black",
          "Other",
          # 16 category labels
          "Other White",
          "White and African",
          "All other ethnic groups",
          "African",
          "White Irish",
          "Other Mixed",
          "White British",
          "Caribbean",
          "Other Black",
          "White and Caribbean",
          "Other Asian",
          "Chinese",
          "Pakistani",
          "White and Asian",
          "Indian",
          "Bangladeshi"
        ),
      input$basecov_gen_cat_ethnicity,
      "Missing"
    )
  }

  # Handle missing values in basecov_gen_cat_region ---------------------------------
  if ("basecov_gen_cat_region" %in% names(input)) {
    print("Handle missing values in basecov_gen_cat_region")
    input$basecov_gen_cat_region <- if_else(
      input$basecov_gen_cat_region %in%
        c(
          "East",
          "East Midlands",
          "London",
          "North East",
          "North West",
          "South East",
          "South West",
          "West Midlands",
          "Yorkshire and The Humber"
        ),
      input$basecov_gen_cat_region,
      "Missing"
    )
  }

  # Handle missing values in basecov_gen_cat_smoker_status ------------------------
  if ("basecov_gen_cat_smoker_status" %in% names(input)) {
    print('Handle missing values in basecov_gen_cat_smoker_status')
    input$basecov_gen_cat_smoker_status <- if_else(
      input$basecov_gen_cat_smoker_status %in% c("E", "N", "S"),
      input$basecov_gen_cat_smoker_status,
      "M"
    )
  }

  # Handle missing values in basecov_gen_cat_bmi_category ----------------------
  if ("basecov_gen_cat_bmi_category" %in% names(input)) {
    print("Handle missing values in basecov_gen_cat_bmi_category")
    input$basecov_gen_cat_bmi_category <- if_else(
      input$basecov_gen_cat_bmi_category %in%
        c(
          "Underweight (<18.5)",
          "Healthy weight (18.5-24.9)",
          "Overweight (25-29.9)",
          "Obese (>=30)"
        ),
      input$basecov_gen_cat_bmi_category,
      "Missing"
    )
  }

  # Recode missing values in binary variables as FALSE -------------------------
  print("Recode missing values in binary variables as FALSE")

  input <- input |>
    mutate(across(contains("_bin_"), ~ ifelse(. == TRUE, TRUE, FALSE))) |>
    mutate(across(contains("_bin_"), ~ replace_na(., FALSE)))

  ##############################################################################
  # Set reference levels for factors
  ##############################################################################
  print("Set reference levels for factors")

  input <- input |>
    mutate(across(contains("_cat_"), ~ factor(., ordered = FALSE)))

  # Set reference level for variable: basecov_gen_cat_sex ------------------------------
  if ("basecov_gen_cat_sex" %in% names(input)) {
    print("Set reference level for variable: basecov_gen_cat_sex")
    levels(input$basecov_gen_cat_sex) <- list(
      "Female" = "female",
      "Male" = "male"
    )
    input$basecov_gen_cat_sex <- relevel(
      input$basecov_gen_cat_sex,
      ref = "Female"
    )
  }

  # Set reference level for variable: basecov_gen_cat_imd ------------------------------
  if ("basecov_gen_cat_imd" %in% names(input)) {
    print('Set reference level for variable: basecov_gen_cat_imd')
    input$basecov_gen_cat_imd <- factor(
      input$basecov_gen_cat_imd,
      levels = c(imd_levels, "Missing")
    )
  }

  # Set reference level for variable: basecov_gen_cat_ethnicity --------------------
  if ("basecov_gen_cat_ethnicity" %in% names(input)) {
    print('Set reference level for variable: basecov_gen_cat_ethnicity')
    if ("White British" %in% unique(input$basecov_gen_cat_ethnicity)) {
      input$basecov_gen_cat_ethnicity <- relevel(
        input$basecov_gen_cat_ethnicity,
        ref = "White British"
      )
      input$basecov_gen_cat_ethnicity <- fct_relevel(
        input$basecov_gen_cat_ethnicity,
        "Missing",
        after = Inf
      ) # move Missing to the end
    } else {
      input$basecov_gen_cat_ethnicity <- factor(
        input$basecov_gen_cat_ethnicity,
        levels = c("White", "Mixed", "Asian", "Black", "Other", "Missing")
      ) # the standard ONS ordering
    }
  }

  # Set reference level for variable: basecov_gen_cat_region ---------------------------
  if ("basecov_gen_cat_region" %in% names(input)) {
    print("Set reference level for variable: basecov_gen_cat_region")
    input$basecov_gen_cat_region <- relevel(
      input$basecov_gen_cat_region,
      ref = "East"
    )
  }

  # Set reference level for variable: basecov_gen_cat_smoker_status --------------------------
  if ("basecov_gen_cat_smoker_status" %in% names(input)) {
    print('Set reference level for variable: basecov_gen_cat_smoker_status')
    levels(input$basecov_gen_cat_smoker_status) <- list(
      "Ex-smoker" = "E",
      "Missing" = "M",
      "Never smoker" = "N",
      "Current smoker" = "S"
    )
    input$basecov_gen_cat_smoker_status <- factor(
      input$basecov_gen_cat_smoker_status,
      levels = c("Never smoker", "Ex-smoker", "Current smoker", "Missing")
    )
  }

  # Set reference level for variable: basecov_gen_cat_bmi_category ------------
  if ("basecov_gen_cat_bmi_category" %in% names(input)) {
    print("Set reference level for variable: basecov_gen_cat_bmi_category")
    input$basecov_gen_cat_bmi_category <- factor(
      input$basecov_gen_cat_bmi_category,
      levels = c(
        "Healthy weight (18.5-24.9)",
        "Underweight (<18.5)",
        "Overweight (25-29.9)",
        "Obese (>=30)",
        "Missing"
      )
    )
  }

  # Set reference level for variable: basecov_gen_cat_uacr_category -----------
  if ("basecov_gen_cat_uacr_category" %in% names(input)) {
    print("Set reference level for variable: basecov_gen_cat_uacr_category")
    input$basecov_gen_cat_uacr_category <- factor(
      input$basecov_gen_cat_uacr_category,
      levels = c("A1", "A2", "A3", "Missing")
    )
  }

  # Set reference level for variable: basecov_gen_cat_uacr_source -------------
  if ("basecov_gen_cat_uacr_source" %in% names(input)) {
    print("Set reference level for variable: basecov_gen_cat_uacr_source")
    input$basecov_gen_cat_uacr_source <- factor(
      input$basecov_gen_cat_uacr_source,
      levels = c("uACR", "uPCR", "Missing")
    )
  }

  # Describe data ----------------------------------------------------------------------
  if (isTRUE(describe)) {
    fn_describe_data(
      data = input,
      filepath = here::here(
        "output",
        "data_descriptions",
        suffix,
        "post-ref.txt"
      )
    )
  }

  return(input)
}
