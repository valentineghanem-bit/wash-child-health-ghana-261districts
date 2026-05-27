# WASH Determinants of Child Health, Ghana 261 Districts

[![CI](https://github.com/valentineghanem-bit/wash-child-health-ghana-261districts/actions/workflows/ci.yml/badge.svg)](https://github.com/valentineghanem-bit/wash-child-health-ghana-261districts/actions) [![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE) [![Python 3.12](https://img.shields.io/badge/python-3.12-blue.svg)](https://www.python.org/) [![R 4.3+](https://img.shields.io/badge/R-4.3+-blue.svg)](https://www.r-project.org/) [![ORCID](https://img.shields.io/badge/ORCID-0009--0002--8332--0220-green.svg)](https://orcid.org/0009-0002-8332-0220)

Spatial machine-learning mediation analysis of water, sanitation, and hygiene (WASH) effects on
childhood diarrhoea and under-five mortality across Ghana's 261 health districts.

## Headline findings

- **U5MR Global Moran's I = 0.83** (z = 20.69, p < 0.001) — strong spatial clustering
- **25 LISA high-high hotspots** in northern Ghana; **35 low-low clusters** in the south
- **~36% of the improved-water → U5MR effect** is mediated through diarrhoea reduction
- **Region-stratified LOROCV R² ≈ 0** — honest reporting of the ecological-prediction ceiling

## Data sources

- Demographic and Health Survey Ghana 2022 (regional → mapped to 261 districts)
- Ghana Statistical Service 2021 Population & Housing Census (Master Sheet)
- Ghana_New_260_District.geojson (260 polygons; Guan district omitted — tabular-only)

## Repository structure

```
.
├── README.md                — this file
├── LICENSE                  — MIT
├── requirements.txt         — pinned Python dependencies
├── .gitattributes           — Git LFS for *.png and *.docx > 5MB
├── .gitignore
├── CITATION.cff
├── manuscript/
│   └── WASH_Ghana_Manuscript.docx
├── poster/
│   └── WASH_Ghana_Poster.html
├── dashboard/
│   └── WASH_Ghana_Dashboard.html
├── scripts/
│   ├── build_master_data.py
│   ├── apply_district_corrections.py
│   ├── stage3_distillation.py
│   ├── spatial_analytics.py
│   ├── ml_pipeline.py
│   ├── mediation_analysis.py
│   ├── generate_figures.py
│   ├── build_manuscript.py
│   └── build_poster_and_dashboard.py
├── tests/
│   └── test_canonical_values.py
└── outputs/
    ├── data/
    │   ├── WASH_Ghana_District_Master.csv
    │   ├── WASH_Ghana_Panel_RegionYear.csv
    │   ├── district_name_corrections.csv
    │   ├── data_dictionary.csv
    │   ├── lisa_univariate_results.csv
    │   ├── lisa_bivariate_results.csv
    │   ├── getis_ord_results.csv
    │   ├── ml_lorocv_predictions.csv
    │   └── evidence_bank.json
    ├── figures/
    │   ├── dag.mermaid
    │   ├── Fig1_U5MR_choropleth.png
    │   ├── Fig2_WASH_2panel.png
    │   ├── Fig3_LISA_U5MR.png
    │   ├── Fig4_BvLISA_OD_U5MR.png
    │   ├── Fig5_correlation_matrix.png
    │   └── Fig6_permutation_importance.png
    └── tables/
        ├── global_morans_I.csv
        ├── permutation_importance.csv
        ├── rf_gini_importance.csv
        ├── ml_model_comparison.csv
        ├── mediation_analysis.csv
        ├── table1_overall.csv
        ├── table1_by_region.csv
        └── spatial_summary.csv
```

## Quick start

```bash
git clone https://github.com/valentineghanem-bit/wash-child-health-ghana-261-districts.git
cd wash-child-health-ghana-261-districts
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
# Reproduce the analysis end-to-end:
python scripts/build_master_data.py
python scripts/apply_district_corrections.py
python scripts/stage3_distillation.py
python scripts/spatial_analytics.py
python scripts/ml_pipeline.py
python scripts/mediation_analysis.py
python scripts/generate_figures.py
python scripts/build_manuscript.py
python scripts/build_poster_and_dashboard.py
# View dashboard:
python -m http.server 8000  # then visit http://localhost:8000/dashboard/
```

## Methods compliance

- STROBE (Strengthening the Reporting of Observational Studies in Epidemiology) for ecological design
- TRIPOD+AI for machine-learning components
- RECORD-Spatial for spatial-statistical components
- DAG-001 prevention pattern: causal directed acyclic graph in outputs/figures/dag.mermaid
- ML-005 prevention pattern: region-stratified leave-one-region-out cross-validation
- SPAT-006 prevention pattern: MANUAL_CORRECTIONS dict + audit CSV for 31 district name variants

## Reproducibility

- Random seed: 42 throughout
- Bootstrap iterations: 1000 for mediation effects
- Permutation iterations: 999 for spatial autocorrelation tests
- Python 3.10, scikit-learn 1.7.2, scipy 1.15.3, pandas 2.3, numpy 2.2

## Citation

If you use this code or data in your work, please cite:

> Ghanem VG. Water, sanitation, and hygiene determinants of childhood diarrhoea and under-five
> mortality in Ghana: a 261-district spatial machine-learning mediation analysis. 2026.

See CITATION.cff for machine-readable citation metadata.

## Licence

MIT License — see LICENSE.
