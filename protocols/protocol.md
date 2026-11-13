# Patterns of Prescribing and Medication Discontinuation for People in England who Develop Chronic Kidney Disease Stages G3a to G5: An OpenSAFELY Study Protocol
Matthew Letts<sup>1,2</sup>, Robert Porteous<sup>1</sup>, Rachel
Denholm<sup>1</sup>, Rupert Payne<sup>3</sup>, Jonathan
Sterne<sup>1</sup>, Fergus Caskey<sup>2</sup>

<sup>1</sup> Electronic Health Records Group, Population Health
Sciences, Bristol Medical School, University of Bristol, Bristol, UK

<sup>2</sup> Bristol Renal, Population Health Sciences, Bristol Medical
School, University of Bristol, Bristol, UK

<sup>3</sup> Exeter Collaboration for Academic Primary Care, University
of Exeter, Exeter, UK

------------------------------------------------------------------------

Version date: 13 November 2026. Git version control visible on
[Github](https://github.com/opensafely/ckd-deprescribing/tree/main/protocols)

------------------------------------------------------------------------

# Background

Ninety-six percent of people living with chronic kidney disease (CKD)
stages 3a, 3b, 4 and 5 live with multiple long-term conditions (1).
Resultantly, polypharmacy is highly prevalent. In particular, people
with CKD stages 4 and 5 are prescribed on average 8-9 medicines per day
(and \>100 pills per week) (2). Polypharmacy is well linked to avoidable
harms such as falls and hospitalisations (3) so managing it safely is a
key action area within multiple national and international policy
initiatives (4). Indeed, the World Health Organisation’s currently
active global patient safety challenge is to achieve *Medication Without
Harm* (5). For people with CKD, the risk of medication-related harm is
augmented by unpredictable drug handling and excretion (6), making them
a high priority group to study (7). Added to this, clinical trials that
establish the safety and effectiveness of medicines often exclude people
living with CKD, and do not reflect their comorbidity and diversity (8).

Deprescribing - the systematic process of stopping or reducing
medicines - is a proposed way of reducing the harms associated with
polypharmacy. Within the recently updated KDIGO (Kidney Disease \|
Improving Global Outcomes) CKD practice guideline there is a new chapter
entitled *Medication management and Drug Stewardship*, in which the
authors acknowledge the importance of handling polypharmacy in people
with kidney disease, whilst also stating that evidence to guide practice
in CKD is limited (9). Currently there is little knowledge of how much
deprescribing occurs, and more research into the effects of
deprescribing on clinically-relevant outcomes is needed. In routine
healthcare data, deprescribing is observable as medication
*discontinuation*, so this will therefore be the primary focus of this
study.

In this study we will characterise English population-level prescribing
patterns for people as they develop CKD of varying stages (G3a, G3b, G4,
G5), as this is often a clinical trigger for medication change. We will
then go on to describe the patterns of discontinuation of a select group
of medicine classes over time.

# Objectives

1.  To describe chronic prescribing at the time people first reach CKD
    stages G3a, G3b, G4, and G5.
2.  To describe patterns of discontinuation of commonly prescribed
    medicines in the 4 years after reaching each stage of CKD.
3.  *Only if time, and for a select few medicines* To identify the
    clinical and sociodemographic factors associated with medication
    discontinuation.

# Methods

## Summary of design

We will conduct a retrospective cohort study using English primary care
records. Individuals will enter a separate cohort for each CKD stage
(G3a, G3b, G4, G5) that they reach. Baseline prescribing will be
analysed cross-sectionally at entry to each cohort. Then medication
discontinuation over the subsequent 4 years will be studied.

## Data sources

We will analyse the primary care record data of people living in England
that is stored and managed by The Phoenix Partnership (TPP),
specifically through the OpenSAFELY-TPP secure analytical platform. We
will utilise OpenSAFELY-TPP’s established linkages to:

- Office for National Statistics (ONS) data on registered deaths
- NHS Secondary Uses Service data, which includes information regarding
  hospital admissions, and is used to derive each individual’s ethnicity
- Data on Index of Multiple Deprivation (IMD)

## Study population

### Summary

Individuals will enter the study population on the date(s) that they
reach CKD stages G3a, G3b, G4, or G5 (the **index date(s)**) between 1st
January 2011 and 31st December 2022 (the **study window**). Each person
may contribute to more than one CKD stage cohort if their CKD progresses
over this time. Prescribing will be followed up for 4 years subsequent
to each index date to assess for medication discontinuation.

### Defining chronic kidney disease

Kidney function as measured by estimated glomerular filtration rate
(eGFR) will be calculated from each person’s serum creatinine
measurements using the 2009 CKD-EPI equation without the ethnicity
coefficient (as recommended by the [UK Kidney
Association](https://www.ukkidney.org/health-professionals/information-resources/uk-eckd-guide/measurement-kidney-function)).
Implausible creatinine values (outside of 20-3000 µmol/L) will be
ignored.

CKD stages are defined by the following eGFR ranges (9):

- CKD stage G3a = eGFR 45-59 ml/min/1.73m<sup>2</sup>
- CKD stage G3b = eGFR 30-44 ml/min/1.73m<sup>2</sup>
- CKD stage G4 = eGFR 15-29 ml/min/1.73m<sup>2</sup>
- CKD stage G5 = eGFR \<15 ml/min/1.73m<sup>2</sup>

### Index date

The index date for each CKD cohort will be the date of the second of two
eGFR measurements that are:

- At least 90 days apart
- Both below the upper limit of that CKD stage
- Not separated by a measurement above the upper limit of that CKD stage

The person will be included in the given CKD stage cohort the first time
that these criteria are met, so long as this falls within the study
window. Each qualifying pair counts towards one stage only: the less
advanced stage of the two measurements. People whose kidney function
declines quickly, or who are tested infrequently, may skip stages (see
<a href="#tbl-inc" class="quarto-xref">Table 1</a>)

<div id="tbl-inc">

Table 1: Example patient to demonstrate cohort inclusion logic

| Date       | eGFR | Enters cohort (if so, which one?) |
|------------|------|-----------------------------------|
| 01/01/2012 | 70   | No                                |
| 01/06/2012 | 59   | No                                |
| 01/01/2013 | 51   | Yes (CKD G3a)                     |
| 01/06/2013 | 28   | No                                |
| 01/01/2014 | 20   | Yes (CKD G4)                      |
| 01/06/2014 | 14   | No                                |
| 01/01/2015 | 10   | Yes (CKD G5)                      |

</div>

> **QUESTION:** Is the 2x eGFR values requirement too strict? An
> alternative would be to require two eGFRs ≥90 days apart only for
> first entry, with later stages entered at the first eGFR below that
> stage’s threshold. This would capture more progression but risks
> including AKI episodes, and would mean stage cohorts mix confirmed and
> single-reading entries. I think if we wait until the 2nd confirmed
> eGFR we will miss some deprescribing that has been triggered by the
> first eGFR reading.

> **QUESTION:** Should a SNOMED code indicating CKD G3a-G5 be an
> alternative route to the index date, a sensitivity analysis, or not
> used? I feel the issue with codes is that they are not well aligned to
> the eGFR decline.

> **QUESTION:** How to manage CKD that pre-exists prior to the study
> window? If we really only want incident CKD then probably need to
> additionally require a prior eGFR measurement that is above the stage
> range?

### Inclusion criteria

On each index date individuals must also meet all the following criteria
to be included:

- Alive
- Aged ≥18 and ≤110 years
- Continuous registration at a single GP practice that uses TPP software
  for at least one year prior.
- Known sex that is exactly ‘male’ or ‘female’
- Known region
- Known IMD

### Exclusion criteria

- People who have received kidney replacement therapy (KRT) of any form
  on or before an index date will be excluded. KRT will be defined as a
  SNOMED code indicating receipt of dialysis or transplant ever. This
  method has been shown to be sensitive for identifying the prevalent
  KRT population in England (10).

### Follow up

Study participants will be followed up from the index date until the
earliest of:

- End of maximum follow up period (4 years)
- Death
- Initiation of kidney replacement therapy (dialysis or transplant)
- End of registration with GP practice that uses TPP software

Follow up is not stopped if someone progresses to a more advanced CKD
stage. They continue follow up in their current cohort and enter a new
one.

### Data quality assurance criteria

We will remove patients whose data fails standard quality assurance
checks:

- Year of birth is missing
- Year of birth is after year of death
- Date of death is after date of analysis
- Year of birth is after date of analysis

## Prescribing information

### Prescribing data

In this analysis we will study chronic prescribing on each index date
and the trends of medication discontinuation over the following 4 years.

The medication table within OpenSAFELY-TPP contains information for
every medication that is prescribed in primary care. Each prescription
is recorded using its corresponding NHS dictionary of medicines and
devices (dm+d) code and corresponding date. [dm+d
codes](https://digital.nhs.uk/data-and-information/information-standards/governance/latest-activity/standards-and-collections/scci0052-dictionary-of-medicines-and-devices-dm-d/)
are the preferred mechanism through which medicinal product
identification and communication occurs within the NHS. In OpenSAFELY,
each dm+d code corresponds to the name (e.g. atorvastatin), strength
(e.g. 40mg) and formulation (e.g. tablet) of a prescribed drug. Data on
the dosing recommendation (e.g. take 1 tablet once a day), the quantity
of a medication prescribed (e.g. 28 tablets), whether a prescription was
dispensed, or whether the patient adhered to the medication as
prescribed are not available.

### Prescribing data handling

Each dm+d code has one or more official routes of administration and
these will be mapped to the study data using publicly available [NHS
TRUD](https://isd.digital.nhs.uk/trud/users/guest/filters/0/categories/6)
(Technology Reference data Update Distribution) reference files. Each of
the 79 official routes of administration will be mapped according to
author consensus to one of the following categories: oral, topical,
inhaled, eye/ear/nasal, oromucosal, rectal/vaginal, transdermal,
intramuscular, intravenous, subcutaneous and other. If a dm+d code has
multiple licensed routes it will be classified ‘multiple routes’, and if
no licensed routes, ‘unknown’.

> **QUESTION:** How much of an issue is historical dm+d codes going to
> be now that we are going all the way back to 2011?

Each medication will then have its dm+d code mapped to its corresponding
British National Formulary (BNF) substance code using publicly available
[mapping
data](https://www.nhsbsa.nhs.uk/prescription-data/understanding-our-data/bnf-snomed-mapping).
BNF substance codes will be used to identify individual medicines, which
will then be grouped into clinically meaningful classes.

### Medication inclusion / exclusion criteria

Medicines will be included / excluded in our analysis by considering
their *scope, uniqueness and timeframe* (11).

#### Scope

We will include medications based on their drug type and route.

- Drug type. We will include medications within BNF chapters 1, 2, 3, 4,
  6, 7, 8, 9, and 10. These chapters, mirroring those used by the
  [NHSBSA medicines
  optimisation](https://www.nhsbsa.nhs.uk/access-our-data-products/epact2/dashboards-and-specifications/medicines-optimisation-polypharmacy)
  dashboards, include the medicines that are most likely to be used long
  term. Other BNF chapters include mainly short course treatments
  (e.g. anti-infectives), non-oral and specialist products, and devices
  which are not within the scope of this work.
- Route. We will only include medications that are orally administered.

It will not be possible to distinguish as required (PRN) prescriptions
from regular prescriptions, and so all medications will be assumed
regular.

#### Uniqueness

Medicines will be counted at BNF substance level, so different strengths
and formulations of the same substance count as one medicine.
Combination products have their own BNF substance codes and will be
counted as a single medicine, and not broken down into their constituent
parts.

#### Timeframe

Conceptually, for a medicine to be discontinued, it must be first in
*chronic* use, i.e. being used on the index date, and regularly prior to
that. There is no consensus regarding how to define a chronic
prescription within electronic health record data. OpenSAFELY-TPP lacks
data to show the clinician-intended duration for each prescription, and
therefore assumptions about the length of each prescription are required
to establish what a person could have been taking on any given date. It
has previously been shown that for five of the commonest medicines, 92%
were prescribed for 28 or 56 days, with the remainder being prescribed
for 7 or 84 days (12).

Considering this variability, we will define a medication as chronic,
and include it in our analyses, if all of the following are true:

- In the 180 days up to and including the index date:
  - It is prescribed two or more times (*regular*)
  - There are \>=21 days between the oldest and the most recent
    prescriptions (*sustained*)
- In the 90 days up to and including the index date:
  - It is prescribed once or more (*recent*)

## Outcome - medication discontinuation

### Medications of interest

Chronic use on the index date and discontinuation over the subsequent 4
years will then be assessed at the level of the medication classes
pre-specified in <a href="#tbl-meds" class="quarto-xref">Table 2</a>.
These classes have been chosen to reflect those known to be common in
this population \[REF\], and those identified as targets for
discontinuation (**Triantafylidis?**). A class will be considered in
chronic use if prescriptions of any medicine within it meet the chronic
definition. We will capture the first discontinuation event only, and
switching between medicines within a class will not be counted as
discontinuation.

<div id="tbl-meds">

Table 2: Medication classes that will be studied for discontinuation

| Medication class | BNF level | BNF code(s) |
|----|----|----|
| Proton pump inhibitors | Paragraph | 010305 |
| Thiazides and related diuretics | Paragraph | 020201 |
| Loop diuretics | Paragraph | 020202 |
| Potassium-sparing diuretics | Paragraph | 020203 |
| Beta-adrenoceptor blocking drugs | Section | 0204 |
| Alpha-adrenoceptor blocking drugs | Paragraph | 020504 |
| Renin-angiotensin system drugs | Paragraph | 020505 |
| Calcium-channel blockers | Paragraph | 020602 |
| Direct oral anticoagulants | Substance | 0208020AA (Edoxaban), 0208020X0 (Dabigatran), 0208020Y0 (Rivaroxaban), 0208020Z0 (Apixaban) |
| Lipid-regulating drugs | Section | 0212 |
| Opioid analgesics | Paragraph | 040702 |
| Sulfonylureas | Subparagraph | 0601021 |
| Biguanides | Subparagraph | 0601022 |
| SGLT2 inhibitors | Substance | 0601023AG (Dapagliflozin), 0601023AM (Canagliflozin), 0601023AN (Empagliflozin), 0601023AX (Ertugliflozin) |
| DPP-4 inhibitors | Substance | 0601023AA (Vildagliptin), 0601023AC (Saxagliptin), 0601023AE (Linagliptin), 0601023AK (Alogliptin), 0601023X0 (Sitagliptin) |
| Oral iron | Subparagraph | 0901011 |
| Sodium bicarbonate | Substance | 0902013S0 |
| Phosphate binding agents | Subparagraph | 0905022 |
| NSAIDs | Paragraph | 100101 |

</div>

### Defining discontinuation

Within OpenSAFELY-TPP the duration of each prescription is unknown, and
there is no standardised way of defining discontinuation within
electronic healthcare record data.

In this study, we will firstly calculate the average prescription
duration (APD). Every medication class for every individual will be
placed into a category based on whether it appears to be prescribed
every 7, 14, 28, 56, or 84 days – the typical prescribing durations in
English primary care (12). The APD will be calculated for each substance
in the class from the gaps between its prescriptions in the 180 days up
to and including the index date, rounded to the nearest of 7, 14, 28, 56
or 84 days; the class APD will be the longest of these.

Discontinuation will be characterised by the absence of continued
prescribing. Dose reductions will not be captured, as dosing information
is not easily analysable in OpenSAFELY-TPP.

**Discontinuation** will be defined as the first period of *greater than
APD + 60 days* following the last prescription on or before the index
date, or any subsequent prescription, where there is no further
prescription. The **date of discontinuation** will be defined as the
date of the last prescription before discontinuation plus the APD.

If follow-up ends (including through death or KRT) before APD + 60 days
have passed since the last prescription, the class will not be counted
as discontinued. We will also report the proportion of discontinued
medicine classes that are prescribed again within 12 months of the date
of discontinuation.

## Covariates

We will ascertain the following covariates to describe each cohort:

- Time-fixed covariates:
  - Sex (male, female)
  - Ethnicity (5 categories, plus unknown)
- Time-varying covariates on each index date:
  - Age (years)
  - Index of Multiple Deprivation (IMD) quintile
  - Region
  - Cambridge Multimorbidity Score (CMS) (13)
  - Diabetes (code ever recorded up to and including index date)
  - Previous cardiovascular disease (code ever recorded up to and
    including index date)
  - Albuminuria category - A1 (\<3 mg/mmol), A2 (3-30 mg/mmol), A3 (\>30
    mg/mmol), or not measured using the most recent urine
    albumin:creatinine ratio measurement (or converted urine
    protein:creatinine ratio measurement) in the 24 months up to and
    including the index date (9)
  - eGFR on the index date (the second measurement of the qualifying
    pair)
  - The number of chronic medicines
  - Calendar period of index date (2011-2014, 2015-2018, 2019-2022)

## Statistical methods

All analyses will be conducted separately within each CKD stage cohort
(G3a, G3b, G4, G5). As individuals can contribute to multiple cohorts,
results will not be pooled, and no totals will be presented.

### Cohort characteristics

We will produce a flowchart to show the numbers of individuals that are
included / excluded at each stage of cohort development. The total
number of unique individuals contributing to at least one CKD stage
cohort, and the number contributing to one, two, three or all four
cohorts, will also be reported.

Descriptive statistics will be used to describe baseline characteristics
of each cohort at inclusion: medians and interquartile ranges for
continuous variables, and frequencies and percentages for categorical
variables.

### Baseline prescribing

For each cohort we will present:

1.  The total number of chronic medicines per person on the index date,
    and the proportions without polypharmacy (0-4 medicines), and those
    experiencing polypharmacy (5-9 medicines) and hyperpolypharmacy (10+
    medicines).
2.  The proportions of individuals with chronic use of each medication
    class in <a href="#tbl-meds" class="quarto-xref">Table 2</a>.

The number of chronic medicines will be stratified by age, sex,
ethnicity and deprivation.

### Medication discontinuation

To examine discontinuation during follow up, we will analyse each
medication class in each CKD cohort. Each analysis population will
consist chronic users of that class on the index date.

Time zero will be the index date. Death and initiation of KRT will be
treated as competing events, and individuals will be censored at the end
of the 4-year follow-up period, end of registration, or end of available
data.

Cumulative incidence functions (CIFs) for discontinuation will be
estimated for each medication class within each CKD stage cohort,
accounting for death and initiation of KRT as competing events. For all
medication classes, the cumulative incidence of discontinuation at 1, 2
and 4 years after the index date, and the number of individuals at risk,
will be presented in a summary table. CIF curves will be plotted only
for lipid-regulating drugs and proton-pump inhibitors.

*If time* factors associated with discontinuation of lipid-regulating
drugs and proton pump inhibitors will be explored using regression
models including the covariates listed above.

### Software

All analyses will be run using the OpenSAFELY Data Analytics Platform.
Data extraction scripts will be written using the electronic health
record query language (ehrQL), and data processing and analysis scripts
will be written using R. OpenSAFELY tightly controls the version of R
(4.6.1) and the available packages that can be
[used](https://github.com/opensafely-core/r-docker/blob/main/v3/packages.md)
in order to maximise reproducibility of code, and to enable local
testing.

### Sensitivity analyses

Sensitivity analyses will explore the effect of:

- Varying the definition of a chronic medication use (using different
  numbers and timeframes of prescriptions).
- Defining discontinuation using a fixed gap with no APD, and varying
  the grace period added to the APD.

### Statistical disclosure control

All outputs will adhere to OpenSAFELY’s statistical disclosure control
principles: all counts will be rounded to the nearest 5 and counts of 7
or fewer will be suppressed.

## Tables and figures

- Figure 1: Flowchart of cohort inclusion
- Table 1: Baseline characteristics of the population, by CKD stage
- Table 2: Total numbers of chronic medicines and medicine class use on
  the index date, by CKD stage
- Table 3: Cumulative incidence of discontinuation at 1, 2 and 4 years,
  by medication class and CKD stage
- Figure 2: Cumulative incidence of discontinuation over 4 years for
  lipid-regulating drugs and proton-pump inhibitors, by CKD stage
- *If time* Table 4: Factors associated with discontinuation, just
  lipid-regulating drugs and proton-pump inhibitors, by CKD stage

## Study limitations

- This study makes the strong assumption that all prescriptions issued
  are dispensed and taken by the individual.
- Information on drug quantity and duration is not recorded and
  therefore inference is made about the length of time someone will have
  possession of a given medicine, leading to potential misclassification
  of discontinuation events
- Additionally not all discontinuation is reflective of intentional
  deprescribing. Some of the prescription absences observed may reflect
  poor adherence, the individual obtaining the medication from
  alternative routes, or other reasons.
- Dosage information is not readily available and so dose reductions are
  not captured.
- As-required (PRN) prescriptions cannot be distinguished from regular
  ones.
- Routine creatinine testing is more frequent in some groups
  (e.g. people with diabetes), which may affect when stages are
  detected.
- The study period includes the COVID-19 pandemic, which disrupted
  routine prescribing and monitoring.

# Other information

## Patient and public involvement (PPI)

This study is part of the NIHR funded project **DEPrescribing In peopLe
Living with advanced Chronic Kidney Disease (DEPILL-CKD): understanding
patterns and outcomes**. The wider project benefits from regular
contributions from the 14-person DEPILL-CKD PPI group which consists of
people from diverse communities across a spectrum of ages and genders.

PPI work is also guided by the Bristol grassroots organisation [Caafi
Health](https://www.caafihealth.org.uk/) who have allocated a Health
Ambassador to the project to aid recruitment to the PPI group, help
facilitate PPI meetings and contribute to dissemination of findings.

The PPI group helped to develop this study and led to expansion in the
cohorts to study (including all ages rather than limiting to older
people) and expressed opinions about studying certain types of
medicines. The PPI group will also aid with interpretation and
contextualisation of the study findings and also in dissemination.

## Funding

Matthew Letts, Doctoral Research Fellow \[NIHR306430\] is funded by the
National Institute for Health and Care Research (NIHR) for this research
project. The views expressed are those of the author(s) and not
necessarily those of the NIHR, NHS or the UK Department of Health and
Social Care.

# References

<div id="refs" class="references csl-bib-body">

<div id="ref-Hawthorne2023" class="csl-entry">

<span class="csl-left-margin">1.
</span><span class="csl-right-inline">Hawthorne G, Lightfoot CJ, Smith
AC, Khunti K, Wilkinson TJ. Multimorbidity prevalence and patterns in
chronic kidney disease: Findings from an observational multicentre UK
cohort study. International Urology and Nephrology. 2023;55(8):2047–57.
doi:[10.1007/s11255-023-03516-1](https://doi.org/10.1007/s11255-023-03516-1)</span>

</div>

<div id="ref-vanOosten2021" class="csl-entry">

<span class="csl-left-margin">2.
</span><span class="csl-right-inline">Oosten MJM van, Logtenberg SJJ,
Hemmellder MH, Leegte MJH, Bilo HJG, Jager KJ, et al. Polypharmacy and
medication use in patients with chronic kidney disease with and without
kidney replacement therapy compared to matched controls. Clinical Kidney
Journal. 2021;14(12):2497–523.
doi:[10.1093/ckj/sfab120](https://doi.org/10.1093/ckj/sfab120)</span>

</div>

<div id="ref-Fried2014" class="csl-entry">

<span class="csl-left-margin">3.
</span><span class="csl-right-inline">Fried TR, O’Leary J, Towle V,
Goldstein MK, Trentalange M, Martin DK. Health outcomes associated with
polypharmacy in community-dwelling older adults: A systematic review.
Journal of the American Geriatrics Society. 2014;62(12):2261–72.
doi:[10.1111/jgs.13153](https://doi.org/10.1111/jgs.13153)</span>

</div>

<div id="ref-DHSC2021" class="csl-entry">

<span class="csl-left-margin">4.
</span><span class="csl-right-inline">Health & Social Care UD of. Good
for you, good for us, good for everybody \[Electronic Book\]
\[Internet\]. 2021. Available from:
<https://assets.publishing.service.gov.uk/government/uploads/system/uploads/attachment_data/file/1019475/good-for-you-good-for-us-good-for-everybody.pdf></span>

</div>

<div id="ref-WHO2023" class="csl-entry">

<span class="csl-left-margin">5.
</span><span class="csl-right-inline">World Health Organization.
Medication without harm: Policy brief. World Health Organization;
2023.</span>

</div>

<div id="ref-Laville2020" class="csl-entry">

<span class="csl-left-margin">6.
</span><span class="csl-right-inline"><span class="nocase">Laville SM,
Gras-Champel V, Moragny J, Metzger M, Jacquelinet C, Combe C, et
al.</span> Adverse drug reactions in patients with CKD \[Journal
Article\]. Clinical Journal of the American Society of Nephrology.
2020;15(8):1090–102.
doi:[10.2215/cjn.01030120](https://doi.org/10.2215/cjn.01030120)</span>

</div>

<div id="ref-Mohottige2021" class="csl-entry">

<span class="csl-left-margin">7.
</span><span class="csl-right-inline">Mohottige D, Manley HJ, Hall RK.
Less is more: Deprescribing medications in older adults with kidney
disease: A review. Kidney360. 2021;2(9):1510–22.</span>

</div>

<div id="ref-Colombijn2024" class="csl-entry">

<span class="csl-left-margin">8.
</span><span class="csl-right-inline">Colombijn JMT, Idema DL, Van Beem
S, Blokland AM, Van Der Braak K, Handoko ML, et al. Representation of
patients with chronic kidney disease in clinical trials of
cardiovascular disease medications. JAMA Network Open.
2024;7(3):e240427.
doi:[10.1001/jamanetworkopen.2024.0427](https://doi.org/10.1001/jamanetworkopen.2024.0427)</span>

</div>

<div id="ref-Stevens2024" class="csl-entry">

<span class="csl-left-margin">9.
</span><span class="csl-right-inline">Stevens PE, Ahmed SB, Carrero JJ,
Foster B, Francis A, Hall RK, et al. KDIGO 2024 clinical practice
guideline for the evaluation and management of chronic kidney disease.
Kidney International. 2024;105(4):S117–314.
doi:[10.1016/j.kint.2023.10.018](https://doi.org/10.1016/j.kint.2023.10.018)</span>

</div>

<div id="ref-Santhakumaran2024" class="csl-entry">

<span class="csl-left-margin">10.
</span><span class="csl-right-inline">Santhakumaran S, Fisher L, Zheng
B, Mahalingasivam V, Plumb L, Parker EPK, et al. Identification of
patients undergoing chronic kidney replacement therapy in primary and
secondary care data: Validation study based on OpenSAFELY and UK renal
registry. BMJ Medicine. 2024;3(1):e000807.
doi:[10.1136/bmjmed-2023-000807](https://doi.org/10.1136/bmjmed-2023-000807)</span>

</div>

<div id="ref-Goedken2016" class="csl-entry">

<span class="csl-left-margin">11.
</span><span class="csl-right-inline">Goedken AM, Lund BC, Cook EA,
Schroeder MC, Brooks JM. Application of a framework for determining
number of drugs. BMC Research Notes. 2016;9(1).
doi:[10.1186/s13104-016-2076-5](https://doi.org/10.1186/s13104-016-2076-5)</span>

</div>

<div id="ref-Mackenna2025" class="csl-entry">

<span class="csl-left-margin">12.
</span><span class="csl-right-inline">Mackenna B, Brown AD, Croker R,
Walker AJ, Goldacre B, Tsiachristas A, et al. Variation in duration of
repeat prescriptions: A primary care cohort study in England. British
Journal of General Practice. 2025;75(756):e448–56.
doi:[10.3399/bjgp.2024.0326](https://doi.org/10.3399/bjgp.2024.0326)</span>

</div>

<div id="ref-Tsang2023" class="csl-entry">

<span class="csl-left-margin">13.
</span><span class="csl-right-inline">Tsang RSM, Joy M, Whitaker H,
Sheppard JP, Williams J, Sherlock J, et al. Development of a modified
Cambridge Multimorbidity Score for use with SNOMED CT: An observational
English primary care sentinel network study. British Journal of General
Practice. 2023;73(731):e435–42.
doi:[10.3399/BJGP.2022.0235](https://doi.org/10.3399/BJGP.2022.0235)</span>

</div>

</div>
