# ckd-deprescribing

Details of the purpose and any published outputs from this project can be found on the [OpenSAFELY website](https://www.opensafely.org/project/pos-2026-3016/)

The contents of this repository MUST NOT be considered an accurate or valid representation of the study or its purpose. This repository may reflect an incomplete or incorrect analysis with no further ongoing work. The content has ONLY been made public to support the OpenSAFELY [open science and transparency principles](https://www.opensafely.org/about/#contributing-to-best-practice-around-open-science) and to support the sharing of re-usable code for other subsequent users. No clinical, policy or safety conclusions must be drawn from the contents of this repository.

# About this study

This study analyses prescribing and medication discontinuation patterns in people living with chronic kidney disease (CKD) stage 4 and 5 who are not on kidney replacement therapy (KRT). This group of people experience disproportionately high levels of medication related harm because:
- Most of them live with multiple long term conditions and are therefore prescribed many medicines (polypharmacy). 
- Medicines are handled unpredictably by the body when kidney function is low so they can interact and accumulate in unexpected ways.

Additionally, research into the effects of medicines often excludes people with low kidney function. So less is known about the risks and benefits of medicines in this group. 

The aims of this study are:
- To briefly describe prescribing in this population
- To find out which medicines are being discontinued and for which people, and see what predicts discontinuation, and if discontinuation occurs equally across groups. 
- To estimate the effects of discontinuing certain types of medications and see if it is safe or effective to do so.

This will lead to the development of guidance about medication discontinuation in people with CKD stage 4 and 5, and help patients and their clinicians to feel more comfortable about discontinuation decisions. We are also testing new methods that will hopefully be reusable for other medicines and other patient groups in the future.


# Pipeline overview

The analytical pipeline is defined in `project.yaml` and runs as a series of dependent actions:
See [project_pipeline.md](./project_pipeline.md) for a diagram of the analysis flow.

# Repository structure

```
analysis/
  config/                   # Files containing study-wide parameters
  dataset_analysis/         # Data analysis scripts (R)
  dataset_definition/       # Scripts for data extraction (ehrQL and python)
  dataset_processing/       # Data cleaning and processing scripts (R)
  discontinuation/          # Subfolder for discontinuation analyses
  r_functions/              # R functions sourced by other scripts
codelists/                  # Codelists sourced from https://www.opencodelists.org/
docs/                       # Reference files and pipeline diagram
dummy_tables/               # Tables used for local testing only
local_processing/ 
  generate_dummy_tables/    # Functions to create dummy tables - local testing only
  medication_lookup_tables/ # Scripts and lookups used for medication mapping
  discontinuation/          # Local scripts for outputs used in discontinuation work 
protocols/                  # Study protocol
```

# About the OpenSAFELY framework

The OpenSAFELY framework is a Trusted Research Environment (TRE) for electronic
health records research in the NHS, with a focus on public accountability and
research quality.

Read more at [OpenSAFELY.org](https://opensafely.org).

# Licences
As standard, research projects have a MIT license. 
