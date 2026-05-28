# WASH Determinants of Child Health, Ghana 261 Districts: A Spatial Machine-Learning Mediation Analysis

[![CI](https://github.com/valentineghanem-bit/wash-child-health-ghana-261districts/actions/workflows/ci.yml/badge.svg)](https://github.com/valentineghanem-bit/wash-child-health-ghana-261districts/actions) [![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE) [![Python 3.12](https://img.shields.io/badge/python-3.12-blue.svg)](https://www.python.org/) [![R 4.3+](https://img.shields.io/badge/R-4.3+-blue.svg)](https://www.r-project.org/) [![ORCID](https://img.shields.io/badge/ORCID-0009--0002--8332--0220-green.svg)](https://orcid.org/0009-0002-8332-0220)

**Author:** Valentine Golden Ghanem | Ghana COCOBOD Cocoa Clinic, Accra, Ghana
**ORCID:** [0009-0002-8332-0220](https://orcid.org/0009-0002-8332-0220)
**Affiliation:** Ghana COCOBOD Cocoa Clinic, Accra, Ghana
**Reporting standard:** STROBE · RECORD-Spatial · TRIPOD+AI
**Date:** 2026
**Status:** Manuscript in preparation

---

## 1. Abstract

This study quantifies the direct and indirect (diarrhoea-mediated) pathways through which water, sanitation, and hygiene (WASH) access affects under-five mortality (U5MR) across Ghana's 261 health districts. Spatial autocorrelation analysis reveals strong clustering of U5MR (Global Moran's I = 0.83, p < 0.001), with 25 High-High LISA hotspots concentrated in northern Ghana. Bootstrapped mediation analysis estimates that approximately 36% of the improved-water → U5MR association is mediated through diarrhoea reduction. Random Forest permutation importance identifies open defecation prevalence and unimproved sanitation as the dominant WASH predictors. Region-stratified leave-one-region-out cross-validation (LOROCV R² ≈ 0) exposes the ecological-prediction ceiling when district-level variation is explained primarily by regional structure.

---

## 2. Research Question & Aims

- **Primary:** Quantify the direct and mediated effects of WASH access on child mortality across Ghana's 261 districts.
- **Secondary:** (a) Map spatial clustering of U5MR and diarrhoea using LISA, bivariate LISA, and Getis-Ord Gi*; (b) estimate the proportion of the WASH → U5MR effect mediated through diarrhoea reduction; (c) rank WASH and socioeconomic predictors using Random Forest permutation importance; (d) assess model generalisability under honest spatial leave-one-region-out cross-validation.

---

## 3. Methods Summary

| Method | Tool | Purpose |
|--------|------|---------|
| Global Moran's I (KNN k=8) | esda / libpysal | U5MR and diarrhoea spatial autocorrelation |
| Bivariate LISA | esda | Open defecation × U5MR co-clustering |
| Getis-Ord Gi* | esda | Hotspot / coldspot detection |
| Bootstrapped mediation analysis (B=1,000) | Custom / scipy | WASH → diarrhoea → U5MR pathway decomposition |
| Random Forest (permutation importance) | scikit-learn | WASH predictor ranking |
| Region-stratified LOROCV | scikit-learn | Honest spatial cross-validation |
| Directed Acyclic Graph (DAG) | Mermaid | Causal assumption transparency |
| Spatial regression diagnostics | spdep / spatialreg (R) | OLS / SLM / SEM model selection |

---

## 4. Data Sources

| Source | Variables | Year | Access |
|--------|-----------|------|--------|
| Ghana DHS 2022 | Regional diarrhoea prevalence, U5MR, WASH indicators, IYCF | 2022 | [dhsprogram.com](https://dhsprogram.com) (registration) |
| Ghana Statistical Service 2021 Census | District population, poverty, literacy, insurance coverage | 2021 | [statsghana.gov.gh](https://statsghana.gov.gh) |
| Ghana 260-district boundary GeoJSON | Polygon geometries (Guan district tabular-only) | 2021 | [statsghana.gov.gh](https://statsghana.gov.gh) |

> DHS data accessed under standard DHS Programme Data Use Agreement. No individual participant data redistributed.

---

## 5. Key Findings

| Metric | Value |
|--------|-------|
| U5MR Global Moran's I | 0.83 (z = 20.69, p < 0.001) |
| LISA High-High hotspots (U5MR) | 25 districts (northern Ghana) |
| LISA Low-Low clusters | 35 districts (southern Ghana) |
| Diarrhoea-mediated fraction (improved water → U5MR) | ~36% |
| LOROCV R² | ≈ 0 (ecological-prediction ceiling) |
| Top WASH predictor (RF) | Open defecation prevalence |
| Districts analysed | 261 (Guan tabular-only; 260 polygon geometries) |

---

## 6. Repository Structure

```
wash-child-health-ghana-261districts/
├── scripts/
│   ├── build_master_data.py
│   ├── apply_district_corrections.py
│   ├── stage3_distillation.py
│   ├── spatial_analytics.py
│   ├── ml_pipeline.py
│   ├── mediation_analysis.py
│   ├── generate_figures.py
│   ├── build_poster_and_dashboard.py
│   ├── spatial_utils.py            # Reusable spatial analysis utilities
│   └── spatial_diagnostics.R       # R: spatial autocorrelation diagnostics
├── app.py                          # Plotly Dash interactive application
├── analysis.R                      # R: spatial regression + mediation diagnostics
├── dashboard/
│   └── WASH_Ghana_Dashboard.html
├── poster/
│   └── WASH_Ghana_Poster.html
├── outputs/
│   ├── data/                       # Master CSV, LISA/Gi* results, mediation output
│   ├── figures/                    # Publication figures (PNG, 300 DPI)
│   └── tables/                     # Summary tables (CSV)
├── tests/
│   └── test_canonical_values.py
├── requirements.txt
├── CITATION.cff
└── README.md
```

---

## 7. Reproducibility

### 7.1 Requirements

- Python 3.12 (pinned in `requirements.txt`)
- R 4.3+ with packages: spdep, spatialreg, dplyr (see `analysis.R` header)
- Random seed: 42 throughout; bootstrap iterations: 1,000
- Estimated runtime: ~10–15 minutes on a standard laptop
- Tested on: Ubuntu 22.04 / macOS 14 / Windows 11 (CI: GitHub Actions)

### 7.2 Clone & install

```bash
git clone https://github.com/valentineghanem-bit/wash-child-health-ghana-261districts.git
cd wash-child-health-ghana-261districts
pip install -r requirements.txt
```

### 7.3 Run the analytical pipeline

```bash
python scripts/build_master_data.py
python scripts/apply_district_corrections.py
python scripts/stage3_distillation.py
python scripts/spatial_analytics.py
python scripts/ml_pipeline.py
python scripts/mediation_analysis.py
python scripts/generate_figures.py
python scripts/build_poster_and_dashboard.py
```

### 7.4 Run the test suite

```bash
pytest tests/ -v
```

### 7.5 Launch the interactive Dash application

```bash
python app.py
# Visit http://127.0.0.1:8050
```

### 7.6 Open the static HTML dashboard

```bash
# macOS
open dashboard/WASH_Ghana_Dashboard.html
# Windows
start dashboard/WASH_Ghana_Dashboard.html
# Linux
xdg-open dashboard/WASH_Ghana_Dashboard.html
```

---

## 8. Outputs

| Output | Description |
|--------|-------------|
| `outputs/data/` | Master CSV, LISA results, mediation estimates, ML predictions |
| `outputs/figures/` | Publication-quality PNG figures (300 DPI) |
| `outputs/tables/` | Summary tables (Table 1, spatial summary, model comparison) |
| `dashboard/` | Self-contained interactive HTML dashboard |
| `poster/` | A0 conference poster (HTML, print-ready) |

## 8a. Downloadable Artefacts (HTML)

Both the interactive dashboard and the conference poster are committed as self-contained HTML files — no server, no build step required.

| Artefact | View on GitHub | Live preview | Direct download (raw HTML) |
|----------|---------------|--------------|---------------------------|
| Interactive dashboard | [View](https://github.com/valentineghanem-bit/wash-child-health-ghana-261districts/blob/main/dashboard/WASH_Ghana_Dashboard.html) | [Preview](https://htmlpreview.github.io/?https://github.com/valentineghanem-bit/wash-child-health-ghana-261districts/blob/main/dashboard/WASH_Ghana_Dashboard.html) | [Download](https://raw.githubusercontent.com/valentineghanem-bit/wash-child-health-ghana-261districts/main/dashboard/WASH_Ghana_Dashboard.html) |
| Conference poster | [View](https://github.com/valentineghanem-bit/wash-child-health-ghana-261districts/blob/main/poster/WASH_Ghana_Poster.html) | [Preview](https://htmlpreview.github.io/?https://github.com/valentineghanem-bit/wash-child-health-ghana-261districts/blob/main/poster/WASH_Ghana_Poster.html) | [Download](https://raw.githubusercontent.com/valentineghanem-bit/wash-child-health-ghana-261districts/main/poster/WASH_Ghana_Poster.html) |

> **Tip:** The dashboard works fully offline once downloaded. The poster is print-ready at A0 (841 × 1189 mm).

---

## 9. Reporting Standard

This study follows the **STROBE** (Strengthening the Reporting of Observational Studies in Epidemiology) reporting guideline for observational ecological studies. Machine learning components follow **TRIPOD+AI**; spatial statistical components follow **RECORD-Spatial**.

---

## 10. Ethical Statement

This study analyses publicly released aggregate data from the Ghana Demographic and Health Survey 2022 (ICF International) and the Ghana Statistical Service 2021 Population and Housing Census. No individual participant data were accessed. All inputs are de-identified district and regional summary statistics. Ethical review was not required for analysis of publicly available aggregate statistics; DHS data were accessed under the standard DHS Programme Data Use Agreement.

---

## 11. Citation

**APA:**
Ghanem, V. G. (2026). *WASH Determinants of Child Health, Ghana 261 Districts: A Spatial Machine-Learning Mediation Analysis.* GitHub. https://github.com/valentineghanem-bit/wash-child-health-ghana-261districts

**BibTeX:**
```bibtex
@misc{ghanem2026wash,
  author = {Ghanem, Valentine Golden},
  title  = {WASH Determinants of Child Health, Ghana 261 Districts: A Spatial Machine-Learning Mediation Analysis},
  year   = {2026},
  url    = {https://github.com/valentineghanem-bit/wash-child-health-ghana-261districts}
}
```

A machine-readable citation is provided in `CITATION.cff`.

---

## 12. License

Code is released under the **MIT License** — see [LICENSE](LICENSE) for details.
Outputs and figures: **CC BY 4.0**.

---

## 13. Author & Contact

**Valentine Golden Ghanem**
Ghana COCOBOD Cocoa Clinic, Accra, Ghana
Email: valentineghanem@gmail.com
ORCID: [0009-0002-8332-0220](https://orcid.org/0009-0002-8332-0220)

---

## 14. Acknowledgements

The author thanks the DHS Programme and ICF International for the Ghana DHS 2022, and the Ghana Statistical Service for the 2021 Census district files and boundary GeoJSON. Spatial analysis relied on esda, libpysal, spdep, and spatialreg. Machine learning used scikit-learn. The mediation framework applies Baron-Kenny decomposition extended with bootstrapped confidence intervals for indirect effects.
