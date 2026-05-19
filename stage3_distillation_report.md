# Stage 3 — Distillation Report
## WASH Determinants of Child Health, Ghana 261 Districts

**Date:** 2026-05-14 | **Framework:** AIPOCH v6.0 | **Chain:** D + B | **Author:** Valentine Golden Ghanem

---

## ▸ Variable schema (final)

Twenty-eight variables retained as the primary analytical set. The data dictionary (`outputs/data/data_dictionary.csv`) captures every variable's role, source, unit, definition, descriptive statistics, and retention status. Variables organised by causal role:

**Outcomes**
- `U5MR_per_1000` — primary outcome (under-five mortality rate)
- `IMR_per_1000` — secondary outcome (infant mortality rate)
- `NMR_per_1000` — secondary outcome (neonatal mortality rate)

**Mediator**
- `Diarrhoea_prevalence_pct` — childhood diarrhoea in last 2 weeks

**Primary exposures (WASH)**
- `Improved_water_pct`, `Unimproved_water_pct`
- `Improved_sanitation_pct`, `Unimproved_sanitation_pct`
- `Open_defecation_pct`

**Secondary exposure**
- `Water_treated_pct` — household water treatment

**Socioeconomic confounders**
- `Incidence of Poverty`, `Intensity of Poverty` (multidimensional)
- `Illiteracy_rate_pct`, `Uninsurance_rate_pct`, `Unemployment_rate_pct`

**Demographic confounders**
- `Total Population`, `Under5_population`, `Youth_dependency_ratio`

**Urbanicity confounder**
- `Class` (Metropolitan / Municipal / District — categorical)

**Mechanistic covariates (competing pathway)**
- `EBF_within_1hr_pct`, `Ever_breastfed_pct` (IYCF)
- `Child_anaemia_any_pct`, `Child_anaemia_severe_pct` (competing health)

**Spatial structure**
- `Region` (16), `District` (261), `Latitude`, `Longitude`, `IsMapped`

---

## ▸ Critical finding: ML-005 ecological-artifact signature pre-confirmed

Every DHS-sourced variable shows **0.0% missingness** at the district level. This is not data quality — it is the ML-005 ecological replication signature: regional DHS values have been assigned uniformly to every district within the same region, so within-region variance in WASH and child-health indicators is exactly zero. Master Sheet socioeconomic covariates (poverty, illiteracy, uninsurance, population) are the only variables with **genuine district-level variation**.

**Operational consequence:** Standard k-fold cross-validation will inflate model performance because districts in the test fold inherit regional values from districts in the train fold. **Region-stratified leave-one-region-out CV (LOROCV) is mandatory** for all ML evaluation. This is locked into Task 13 (Stage 4–5 ML pipeline) before any model is fit.

**Manuscript framing consequence:** The Methods Limitations subsection must state explicitly that DHS regional values were ecologically assigned to constituent districts; spatial-pattern claims based on within-region variation in WASH exposures are not supportable. Spatial heterogeneity claims must be anchored on between-region variation plus Master Sheet within-region socioeconomic variation. This is added to the Stage 4 methodology spec.

---

## ▸ Descriptive findings (Table 1 highlights)

District-level central tendency (n = 261; mean, SD, min, median, max):

| Variable | Mean | SD | Min | Median | Max |
|---|---:|---:|---:|---:|---:|
| U5MR_per_1000 | ~42 | ~9 | 20 | ~42 | 48 |
| Diarrhoea_prevalence_pct | ~13 | ~4 | 7.0 | ~13 | 18 |
| Improved_water_pct | ~89 | ~12 | 59.3 | ~92 | 98.5 |
| Open_defecation_pct | ~17 | ~17 | 5.0 | ~12 | 63.6 |
| Improved_sanitation_pct | ~67 | ~22 | 21.9 | ~74 | 91.4 |
| Incidence of Poverty | ~24 | ~10 | — | — | 48.3 |
| Illiteracy_rate_pct | ~29 | ~15 | 5.4 | ~27 | 60.8 |

(Full Table 1 in `outputs/tables/table1_overall.csv`; by-region breakdown in `outputs/tables/table1_by_region.csv`.)

**Substantive observations from the by-region table:**

- The North East / Northern / Savannah cluster is the high-burden region across nearly every indicator: Open defecation 63.6% (North East), Illiteracy 52% (North East), U5MR 41 (North East), child anaemia 65% (North East).
- Greater Accra is the low-burden region: Improved water 98.5%, open defecation 5%, U5MR 20.
- The North vs South gradient is the dominant spatial structure — already visible in Table 1 before any spatial test is run.

---

## ▸ Decision on causal pathway structure (drives Stage 4 DAG)

The variable schema supports the pre-registered causal claim:

```
EXPOSURES (WASH)                       MEDIATOR              OUTCOME
─────────────────                      ────────              ───────
Improved_water_pct  ─┐
Improved_sanitation_pct  ─┼──→  Diarrhoea_prevalence  ──→  U5MR_per_1000
Open_defecation_pct  ─┘                                       ▲
                                                              │
              Direct effect  ────────────────────────────────┘

CONFOUNDERS (back-door paths into both WASH and U5MR)
─ Poverty incidence + intensity
─ Illiteracy, uninsurance, unemployment
─ Total population + youth dependency ratio
─ Urbanicity (Class)

COMPETING PATHWAYS (alternative mediators / effect modifiers)
─ IYCF (early breastfeeding, ever breastfed)
─ Child anaemia (any / severe)
```

The DAG to be drawn at Stage 4 will encode these relationships formally with the minimal sufficient adjustment set for the WASH → U5MR total, direct, and natural-indirect effects.

---

## ▸ Stage 3 deliverables (saved in /tmp scratchpad + workspace)

- `outputs/data/data_dictionary.csv` — 28 rows × 12 columns
- `outputs/tables/table1_overall.csv` — overall descriptives
- `outputs/tables/table1_by_region.csv` — region-stratified descriptives
- `scripts/stage3_distillation.py` — reproducible build script

**Validation gates passed:**
- U5MR, Diarrhoea, Improved_water, Open_defecation all retained
- ≥ 20 variables in data dictionary (28 actual)
- ≥ 5 primary variables (28 actual)
- 261 tabular rows preserved (260 mapped + Guan)

---

## ▸ Ready-state for Stage 4

Stage 4 work order:
1. **DAG construction (DAG-001 prevention)** — draw causal DAG using the schema above; identify minimal sufficient adjustment set; render Mermaid + tldraw; embed as Supplementary Figure S1
2. **Pytest canonical suite (EX-016)** — write ≥ 10 assertions pinned to `WASH_Ghana_District_Master.csv` canonical values from Table 1
3. Then proceed to Stage 4–5 spatial + ML + CMA workflow
