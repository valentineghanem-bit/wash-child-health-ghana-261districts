# Dissemination Package — WASH Ghana 261 Districts

**Project:** Water, Sanitation, and Hygiene Determinants of Childhood Diarrhoea and Under-Five Mortality in Ghana: A 261-District Spatial Machine-Learning Mediation Analysis
**Author:** Valentine Golden Ghanem, ORCID 0009-0002-8332-0220
**Date prepared:** 2026-05-14
**QA badge:** QA_PASSED_2026-05-14.txt — `/disseminate` UNLOCKED

---

## 1. Cover letter — International Journal of Environmental Research and Public Health (primary target)

**Dr. Editor-in-Chief**
*International Journal of Environmental Research and Public Health (IJERPH)*
MDPI AG, St Alban-Anlage 66, 4052 Basel, Switzerland

Dear Editor,

I submit for your consideration the manuscript "Water, Sanitation, and Hygiene Determinants of Childhood Diarrhoea and Under-Five Mortality in Ghana: A 261-District Spatial Machine-Learning Mediation Analysis", for publication as an Article in IJERPH.

This study addresses a measurable gap in the West African public-health literature. Subnational evidence on the relative contribution of water, sanitation, and hygiene (WASH) services to under-five mortality through childhood diarrhoea — as distinct from direct WASH effects — has been sparse, despite policy relevance for targeted intervention design. Using Ghana's full 261-district administrative grid (260 mapped polygons plus Guan district in Oti Region), the 2022 Demographic and Health Survey, and the 2021 Population and Housing Census, we decompose the WASH-to-mortality pathway into diarrhoea-mediated and direct channels using formal causal mediation analysis (Baron-Kenny, 1 000 bootstrap iterations, Vanderweele E-value sensitivity bounds) alongside spatial machine learning under region-stratified leave-one-region-out cross-validation.

Three findings merit attention. First, under-five mortality is strongly spatially clustered across the 261 districts (Global Moran's I = 0.83, z = 20.69, p < 0.001), with 25 high-high Local Indicators of Spatial Association clusters concentrated in the Northern, North East, Savannah, Upper East, and Upper West regions. Second, approximately 36% of the improved-water-to-mortality association operates indirectly through reductions in childhood diarrhoea, with the remaining 64% reflecting direct WASH effects on respiratory infection, undernutrition, and broader infectious-disease co-exposure. Third, region-stratified cross-validation revealed near-null out-of-region predictive power for machine-learning models built on regional Demographic and Health Survey exposures, an honest result that standard k-fold cross-validation would have inflated through within-region homogeneity — we believe this is a methodological contribution that future ecological machine-learning analyses should adopt.

The manuscript is original, has not been published elsewhere, and is not under consideration by another journal. All authors have read and approved the submission. The work was conducted in accordance with the STROBE reporting guideline for observational studies, TRIPOD+AI for machine-learning components, and RECORD-Spatial for spatial-statistical components. All analytical code, the master dataset, and supplementary materials are openly available at the project repository.

I welcome the editor's consideration and am happy to address any reviewer feedback.

Yours sincerely,

**Valentine Golden Ghanem**
Principal Biomedical Scientist · Cocoa Clinic, Ghana COCOBOD, Accra · valentineghanem@gmail.com · ORCID: 0009-0002-8332-0220

---

## 2. Anticipated reviewer critiques and response templates

### Critique 1 — Ecological fallacy

**Anticipated reviewer comment:** *"District-level associations between WASH and U5MR cannot license individual-level causal claims. The authors should temper their language throughout."*

**Author response:** We agree, and we have stated this limitation explicitly in Methods 2.3, Discussion paragraph 4, and the third bullet of the Conclusions. Throughout the manuscript we use language such as "associated with", "co-clustered", and "predicted" rather than "causes" or "leads to", and we have flagged the ecological-fallacy risk in the bullet list of Limitations. The policy implications target district-level intervention decisions, not individual-child claims.

### Critique 2 — Counter-intuitive open-defecation effect

**Anticipated reviewer comment:** *"The negative total effect of open defecation on U5MR is implausible. Either the analysis is wrong or the framing is misleading."*

**Author response:** The counter-intuitive sign reflects residual regional confounding rather than a protective effect, and we addressed this in Discussion paragraph 3 and the Stress Test report (Supplementary). The Vanderweele E-value of 1.09 indicates that modest unmeasured confounding could overturn the estimate. A sensitivity analysis restricted to the high-burden northern bloc (where open-defecation prevalence is consistently above 30%) yielded the expected positive total effect. We have added this sensitivity analysis explicitly to Methods 2.7 and Results 3.6.

### Critique 3 — Near-null cross-validation R²

**Anticipated reviewer comment:** *"The Random Forest cross-validated R² is essentially zero. This calls the entire machine-learning section into question."*

**Author response:** The near-null R² is the intended honest result and the methodological contribution we wish to highlight. Region-stratified leave-one-region-out cross-validation correctly reveals that regionally-assigned Demographic and Health Survey exposures cannot predict mortality in held-out regions, because within-region predictor variation is zero by data design. Standard 5- or 10-fold cross-validation would have inflated R² through within-region homogeneity; we believe reporting this inflation as model performance would be misleading. We have clarified the framing in Methods 2.6 and Results 3.5. Permutation importance from the in-sample fit identifies the dominant within-sample associations; we do not interpret this as out-of-sample predictive validity.

---

## 3. medRxiv preprint checklist

- [x] Manuscript file (.pdf converted from .docx) ready
- [x] Author ORCID supplied (0009-0002-8332-0220)
- [x] Funding statement: no external funding received
- [x] Competing interests: none declared
- [x] Data availability statement: master dataset + analysis code openly available at `github.com/valentineghanem-bit/wash-child-health-ghana-261-districts`
- [x] Ethics statement: secondary analysis of public-domain de-identified DHS and Census data; exempt under Ghana Health Service Ethics Review Board common rule
- [x] Title length within 250 characters
- [x] Abstract structured (Background / Methods / Results / Conclusion), within 350 words
- [x] Keywords aligned with MeSH

---

## 4. Plain-language summary (≤200 words — ResearchGate / ORCID / preprint summary)

Where you live in Ghana shapes how likely a child is to survive their first five years. This study examined every one of the country's 261 health districts to ask whether better water, sanitation, and hygiene services reduce under-five deaths primarily through preventing diarrhoea, or through other pathways as well. Using the 2022 national health survey and the 2021 census, and applying spatial-statistical methods alongside formal causal mediation analysis, the study found that under-five mortality is strongly concentrated in the northern regions and that improved water coverage is associated with lower mortality. About one third of that association operates by reducing diarrhoea; the remaining two thirds reflects other channels including respiratory infection prevention and better nutrition. The findings suggest that water and sanitation investments in northern Ghana will be most effective when paired with broader child-health programmes such as oral rehydration distribution and case-management training, rather than treated as diarrhoea-only interventions. The full analysis code and dataset are freely available for replication and extension.

---

## 5. Reporting guideline compliance statement

This study followed:
- **STROBE** (Strengthening the Reporting of Observational Studies in Epidemiology) for the observational ecological design
- **TRIPOD+AI** (Transparent Reporting of a Multivariable Prediction Model for Individual Prognosis or Diagnosis, AI extension) for the machine-learning components
- **RECORD-Spatial** for spatial-statistical components

Completed checklists are provided as Supplementary Materials.

---

## 6. Five-Deliverable Closure Statement (Tenet 11)

- [x] Manuscript — `WASH_Ghana_Manuscript.docx` (4.5 MB, IMRAD, embedded figures)
- [x] Poster — `WASH_Ghana_Poster.html` (A0, 9 required sections)
- [x] Dashboard — `WASH_Ghana_Dashboard.html` (Leaflet + Chart.js, interactive)
- [x] Master CSV — `WASH_Ghana_District_Master.csv` (261 × 44, data-source attribution)
- [x] GitHub Repository scaffold — README + LICENSE + requirements.txt + CITATION.cff + .gitattributes

## 7. QA Final Gate (Tenet 18 — HARDCODED)

- [x] `/qa WASH_Ghana` executed: YES
- [x] `QA_PASSED_2026-05-14.txt` badge present: YES
- [x] Publication Readiness Score: PASS (88% reproducibility, 100% reconciliation)
- [x] /disseminate UNLOCKED: YES

## 8. Cross-Artifact Sync (Tenet 20)

- [ ] `/github-publish` SYNC_PASS: pending (Sync Manifest extraction + verification due during git push)
- [ ] Commit pushed to https://github.com/valentineghanem-bit/wash-child-health-ghana-261-districts: pending

Until SYNC_PASS issues, **GITHUB COMMIT IS BLOCKED**.

---

## 9. GitHub publish — COMPLETE 2026-05-16

- Repository: https://github.com/valentineghanem-bit/wash-child-health-ghana-261-districts
- Latest commit: dc3da8a (main)
- Initial release: bcc20d9 — "Initial release v1.0.0 — WASH Ghana 261-district spatial ML mediation"
- All deliverables present except the manuscript .docx (intentionally redacted per Tenet 20)
