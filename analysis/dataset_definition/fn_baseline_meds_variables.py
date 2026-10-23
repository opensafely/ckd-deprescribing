##########################################################################
# This script writes functions to extract medication-related variables for
# use in dataset_definition_baseline_meds.py
##########################################################################

from ehrql import days
from ehrql.tables.tpp import medications

####################################################################################
# add_recent_prescriptions
# ##################################################################################
# This function returns prescriptions on or before the index date 
# It looks in windows of length window_days backward from the index date, and 
# pulls med_slots worth of medicines. It then iterates n_windows times.
# Windows keep each med_slots low to prevent memory issues in the backend

# Output columns are med_dmd_code_1, med_date_1, med_dmd_code_2, med_date_2, etc.
# med_dmd_code_1 is the most recent prescription and slots are numbered across
# windows.

# Same-day prescriptions are ordered lexicographically by dmd_code string
# (not numerically). Rows with identical date and dmd_code are treated as duplicates 
# and collapsed to one entry.
####################################################################################

def add_recent_prescriptions(index_date, med_slots=20, window_days=7, n_windows=26):

    output = {}

    for i in range(n_windows):
        
        window_end = index_date - days(i * window_days) # window 0 ends on the index date, window 1 the week before, etc.
        window_start = window_end - days(window_days - 1)

        remaining = medications.where(
            medications.date.is_on_or_before(window_end) &
            medications.date.is_on_or_after(window_start)
        ).sort_by(
            medications.date,
            medications.dmd_code,
        )

        for j in range(1, med_slots + 1):

            current = remaining.last_for_patient() # most recent still remaining
            current_date = current.date
            current_code = current.dmd_code

            # store the current dates and codes in the output
            slot = i * med_slots + j
            output[f"med_dmd_code_{slot}"] = current_code
            output[f"med_date_{slot}"] = current_date

            # remaining = remaining prescriptions
            remaining = remaining.where(
                medications.date.is_before(current_date) |
                (
                    (medications.date == current_date) &
                    (medications.dmd_code != current_code)
                )
            )

    return output


#############################################################################
# add_prescription_columns
#############################################################################
# this simply adds the columns defined in add_recent_prescriptions() to the
# dataset.
#############################################################################

def add_prescription_columns(dataset, index_date, med_slots=20, window_days=7, n_windows=26):

    for name, expr in add_recent_prescriptions(
        index_date,
        med_slots=med_slots,
        window_days=window_days,
        n_windows=n_windows
        ).items():
        dataset.add_column(name, expr)

