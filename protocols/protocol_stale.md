## Covariates

Covariates have been chosen for two different reasons:

- It is hypothesised that they will likely have an impact on medication discontinuation.
- To promote analytical inclusivity, by exploring variations by protected characteristics.

Covariates, which will be defined on the index date, are described in the table below.

+----------------------------+---------------+----------------------------------------------+
| **Covariate**              | **Type**      | **Definition**                               |
+============================+===============+==============================================+
| Age                        | Continuous    | Age in years calculated from year of birth.  |
|                            |               | Will be modelled using splines               |
|                            |               |                                              |
|                            |               | Strata: 18–49, 50–64, 65–74, 75–84, ≥85      |
+----------------------------+---------------+----------------------------------------------+
| Sex                        | Categorical   | Male or female                               |
+----------------------------+---------------+----------------------------------------------+
| Ethnicity                  | Categorical   | Derived from GP record and NHS               |
|                            |               | Secondary Uses Service data, using           |
|                            |               | the most recent non-missing value. Strata:   |
|                            |               |                                              |
|                            |               | White\                                       |
|                            |               | Mixed / Multiple ethnic\                     |
|                            |               | Asian / Asian British\                       |
|                            |               | Black / African / Caribbean / Black British\ |
|                            |               | Other ethnic group\                          | 
|                            |               | Not stated / Not known\                      |
+----------------------------+---------------+----------------------------------------------+
| Deprivation                | Categorical   | Deciles of Index of Multiple Deprivation     |
|                            |               | (IMD) based on address on index date         | 
+----------------------------+---------------+----------------------------------------------+
| eGFR                       | Continuous    | Estimated glomerular filtration rate         |
|                            |               | on the index date, calculated from           |
|                            |               | the most recent serum creatinine             |
|                            |               | using the 2009 CKD-EPI equation              |
+----------------------------+---------------+----------------------------------------------+
| Number of chronic          | Continuous    | Count of distinct included chronic           |
| prescriptions              |               | medications on the index date                |
+----------------------------+---------------+----------------------------------------------+
| Region                     | Categorical   | East of England\                             |
|                            |               | London\                                      | 
|                            |               | Midlands\                                    |
|                            |               | North East and Yorkshire\                    |
|                            |               | North West\                                  |
|                            |               | South East\                                  |
|                            |               | South West\                                  |
+----------------------------+---------------+----------------------------------------------+
| Frailty                    | Categorical   | Characterised using the electronic           |
|                            |               | frailty index (eFI, ideally eFI2             |
|                            |               | [@Best2025]), a widely used metric           |
|                            |               | for identifying frailty in                   |
|                            |               | electronic health records.                   |
|                            |               | This is all tbc - watch the OS Slack         |
|                            |               | Strata: non-frail, mildly frail,             |
|                            |               | moderately frail, severely frail             |
+----------------------------+---------------+----------------------------------------------+
| Care home status           | Binary        | Using TPP's algorithm to determine if a      |
|                            |               | person is a likely care home resident        |
+----------------------------+---------------+----------------------------------------------+
| Consultation rate          | Continuous    | Number of GP consultations 12 months         |
|                            |               | prior to the index date                      |
+----------------------------+---------------+----------------------------------------------+
| Dementia                   | Binary        | 1 if diagnosis present; 0 otherwise          |
|                            |               | I could try to make this more granular?      |
+----------------------------+---------------+----------------------------------------------+
| Liver disease              | Binary        | 1 if diagnosis present; 0 otherwise          |
+----------------------------+---------------+----------------------------------------------+
| Cancer                     | Categorical   | 1 if diagnosis present; 0 otherwise          |
+----------------------------+---------------+----------------------------------------------+
| Diabetes                   | Binary        | 1 if diagnosis present; 0 otherwise          |
+----------------------------+---------------+----------------------------------------------+
| Cambridge Multimorbidity   | Strata        | Strata: quartiles of CMS                     |
| Score (CMS)                |               |                                              |
+----------------------------+---------------+----------------------------------------------+
| COPD                       | Binary        | 1 if diagnosis present; 0 otherwise          |
+----------------------------+---------------+----------------------------------------------+
| Risk of mortality          | Continuous /  | Estimated 4-year risk of mortality           |
|                            | categorical   | using the CKD G4+ prediction tool            |
|                            |               | [@Grams2018]. This tool is suggested for use |
|                            |               | in the 2024 KDIGO CKD management guideline   |
|                            |               | [@Stevens2024]. It requires 8 variables:     |
|                            |               | Requires: age (30–85),                       |
|                            |               | sex, race (black or white),                  |
|                            |               | proteinuria (uPCR or uACR), smoking          |
|                            |               | status, diabetes status, history of          |
|                            |               | cardiovascular disease, eGFR (15–30),        |
|                            |               | systolic BP (90–180).                        |
|                            |               |                                              |
|                            |               | Strata: <25%, 25–49%, 50–74%, ≥75%           |
+----------------------------+---------------+----------------------------------------------+
