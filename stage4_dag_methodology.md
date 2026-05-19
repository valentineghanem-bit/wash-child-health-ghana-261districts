# Stage 4 — Causal DAG and Methodology Specification
## WASH Determinants of Child Health, Ghana 261 Districts

**Date:** 2026-05-14 | **Framework:** AIPOCH v6.0 | **Author:** Valentine Golden Ghanem

DAG-001 prevention pattern applied. Conceptual audit (Stage 9) absorbed at the end of this document.

---

## 1. CAUSAL FRAMEWORK

The substantive causal claim is that water, sanitation, and hygiene (WASH) conditions at the district level reduce under-five mortality through two channels: (i) an **indirect channel** mediated by childhood diarrhoea — improved water and sanitation reduce diarrhoea exposure, which in turn lowers U5MR; and (ii) a **direct channel** representing residual mechanisms (lower acute respiratory infection, lower undernutrition propagation, fewer infectious-disease co-exposures) that are not captured by diarrhoea alone. The total effect of WASH on U5MR is the sum of these two channels. Quantifying the proportion mediated by diarrhoea informs whether WASH programmes should be coupled with ORS/zinc rollout (if indirect dominates) or with broader maternal-child health infrastructure (if direct dominates).

The DAG (Supplementary Figure S1, rendered in Mermaid) encodes:

- **Exposures (WASH cluster):** improved water source, improved sanitation, open defecation, household water treatment.
- **Mediator:** diarrhoea prevalence in children under five.
- **Primary outcome:** U5MR per 1,000 live births. Secondary outcomes: IMR, NMR.
- **Socioeconomic confounders** (back-door paths into both WASH and U5MR): poverty incidence and intensity, adult illiteracy, health-insurance non-enrolment, unemployment.
- **Demographic / urbanicity confounders:** total district population, youth dependency ratio, urbanicity class (Metropolitan / Municipal / District).
- **Competing pathways:** early initiation of breastfeeding (independent path to diarrhoea and U5MR), child anaemia (independent path to U5MR with potential mediation by infection susceptibility).
- **Unmeasured latent (U):** healthcare access, maternal education, climate. Acknowledged as an open back-door path; sensitivity analysis (E-value) will quantify how strong U would have to be to nullify the indirect effect.

---

## 2. MINIMAL SUFFICIENT ADJUSTMENT SET (MSAS)

Applying the back-door criterion to the DAG:

**For total effect of WASH on U5MR:**
- Poverty (incidence + intensity)
- Illiteracy
- Urbanicity (Class)
- Total population (offset)
- Youth dependency ratio

**For natural direct effect (NDE) of WASH on U5MR via paths not through diarrhoea:**
- All variables in the total-effect MSAS
- Plus mediator-outcome confounders: early initiation of breastfeeding, child anaemia

**For natural indirect effect (NIE) via diarrhoea:**
- All variables above
- The Imai-Keele-Tingley sequential ignorability assumption is required and is stated in Methods 2.7 (Causal mediation analysis).

Unemployment is excluded from MSAS because it is upstream of poverty (mediator on the confounder side); including both would over-control. Insurance non-enrolment is included only in sensitivity analysis because its directionality with respect to WASH at district level is ambiguous in the literature.

---

## 3. METHODS WORK ORDER (Stage 5)

The DAG determines the analytical sequence:

1. **Spatial autocorrelation diagnostics** (Task 12)
   - Global Moran's I (KNN k=4) on U5MR, diarrhoea, and each WASH indicator
   - Univariate LISA (Rook contiguity) per variable
   - Bivariate LISA WASH × diarrhoea and WASH × U5MR
   - Getis-Ord Gi* hotspot delineation
   - Geographically weighted regression (GWR) of U5MR on WASH with poverty + illiteracy + urbanicity covariates

2. **ML pipeline with region-stratified LOROCV** (Task 13)
   - RandomForestRegressor + XGBoost Regressor on U5MR
   - **Cross-validation:** Leave-one-region-out (LOROCV) — mandatory per ML-005 prevention
   - SHAP summary + waterfall + dependence plots, top 5 features
   - Calibration: predicted-vs-observed scatter, RMSE, R² per fold

3. **Formal causal mediation analysis** (Task 14)
   - `causalml` MediationAnalysis or `statsmodels` linear mediation with 1000-bootstrap CIs
   - Report: total effect, NDE, NIE, proportion mediated
   - Sensitivity to unmeasured confounding: E-value per Vanderweele
   - SHAP-mediation as second-opinion: decompose SHAP attribution into WASH→Diarrhoea→U5MR pathway versus residual

4. **Quad-Connector evidence bank** (Task 15)
   - PubMed + Scholar Gateway + Consensus + Scite over WASH–diarrhoea–U5MR literature, 2015–2026, SSA focus
   - Output: `evidence_bank.json` with per-source reliability scores

---

## 4. STATISTICAL SPECIFICATION

- **Spatial unit:** 261 administrative districts; 260 mapped to GeoJSON polygons; Guan (Oti) included in tabular analyses only.
- **Region scheme:** 16 post-2018 regions for cross-sectional Layer 2; 10 pre-2018 regions for longitudinal Layer 1 panel (87 region-years, 1988–2022).
- **Spatial weights:** KNN k=4 for Global Moran's I; Rook contiguity for LISA (per EX-008).
- **Permutations:** 999 for Moran's I and LISA.
- **Significance threshold for LISA exploratory:** p < 0.10 (Anselin convention); confirmatory tests at p < 0.05.
- **ML CV:** Region-stratified LOROCV (16 folds). Report mean ± SD across folds (per STAT-007 and EX-016).
- **ML hyperparameters:** Stated in Methods 2.6 (per ML-003).
- **Random seed:** 42 throughout (per ML-002).
- **Mediation bootstrap iterations:** 1000.
- **Confidence level:** 95% throughout.
- **Reporting guidelines:** STROBE (observational ecological), TRIPOD+AI (ML), RECORD-Spatial.

---

## 5. CONCEPTUAL AUDIT (Stage 9 absorbed)

A `/peer-stress-conceptual` pass on the DAG and framing surfaces five upstream-framing risks that a hostile Reviewer 1 would press on. Each is addressed below.

**Risk 1 — Ecological fallacy.** District-level associations between WASH and U5MR do not automatically translate to individual-level effects. We acknowledge this explicitly in Methods 2.9 (Limitations) and Discussion. Inference is bounded to district-level policy levers, not individual-level intervention claims. Sub-claim: "Districts with higher improved-water coverage had lower U5MR" is supportable; "Children in households without improved water are at higher risk" is not, from this data alone.

**Risk 2 — Unit-of-analysis mismatch between exposure and outcome.** Both WASH and U5MR are DHS regional values assigned to constituent districts. This produces within-region homogeneity. Mitigations: (i) region-stratified LOROCV for ML; (ii) Master Sheet socioeconomic covariates retain genuine within-region variation and carry most of the district-level identifying signal; (iii) explicit Limitation paragraph naming this and stating that observed within-region variation is in the Master Sheet covariates, not in DHS exposures.

**Risk 3 — Reverse causation.** Could high U5MR drive (rather than result from) low WASH coverage? Plausible at long time scales (high-mortality regions attract less infrastructure investment). DAG mitigation: Master Sheet covariates are 2021 Census; DHS values are 2022 (post-Census). Temporal ordering of poverty and demographic covariates with respect to outcome is at least nominally correct. Discussion will note this asymmetry candidly.

**Risk 4 — Mediator-outcome confounding by anaemia and IYCF.** Both early breastfeeding and child anaemia plausibly affect both diarrhoea (mediator) and U5MR (outcome). Without adjusting for these, the NIE via diarrhoea is biased. Mitigation: include EBF_within_1hr and child anaemia in the NDE/NIE adjustment set. The sequential ignorability assumption is named explicitly in Methods 2.7.

**Risk 5 — DAG completeness.** Healthcare access, climate (rainfall, temperature), maternal education, and conflict exposure are unmeasured. The DAG explicitly shows an unmeasured latent U with arrows to W, M, and Y. Quantitative bounding via Vanderweele E-value will report the minimum confounding strength that would nullify the indirect effect. This addresses the Reviewer 1 "what about X" objection without claiming X is captured.

**Strongest residual conceptual risk:** the indirect effect is statistically dependent on within-region variation in diarrhoea given fixed WASH (regional) — and since both WASH and diarrhoea are regional, the NIE may be identified only via between-region contrast. This is a structural feature of the data, not a fixable error. Honest Discussion language: "The indirect pathway is identified primarily through between-region variation in joint WASH–diarrhoea profiles, with district-level socioeconomic covariates providing the within-region adjustment."

---

## 6. WHAT THIS DAG IS NOT CLAIMING

- It is not claiming WASH causes U5MR at the individual child level (see Risk 1).
- It is not claiming the indirect-via-diarrhoea pathway is the dominant pathway — that is an empirical question to be answered, not a structural assumption.
- It is not claiming completeness — the unmeasured U is real and named.
- It is not a structural equation model with parameter constraints; it is the qualitative graph that licenses the adjustment set.

---

## 7. STAGE 4 DELIVERABLES

- `outputs/figures/dag.mermaid` — formal Mermaid DAG (to be rendered to .png at Stage 5 for Figure S1)
- `stage4_dag_methodology.md` — this document
- `tests/test_canonical_values.py` — pytest suite (Task 11)

Stage 4 is complete on the methodology side. Pytest canonical suite next.
