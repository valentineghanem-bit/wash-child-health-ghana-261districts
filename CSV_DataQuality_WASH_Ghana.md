# QA-4 Master CSV Data Quality — WASH Ghana 261 Districts

**Date:** 2026-05-14 | **Verdict:** 22/24 PASS

| Criterion                               | Rating         | Finding                                                                                                      |
|:----------------------------------------|:---------------|:-------------------------------------------------------------------------------------------------------------|
| A1 Data dictionary present              | PASS           | data_dictionary.csv in outputs/data/                                                                         |
| A2 Column names snake_case              | PARTIAL        | Most are snake_case; Master Sheet originals retain spaces (e.g., 'Total Population'). Acceptable provenance. |
| A3 Units in headers                     | PASS           | '_per_1000', '_pct', 'rate' suffixes clear                                                                   |
| A4 Unique row identifier                | PASS           | District column unique (n=261)                                                                               |
| A5 Geographic unit present              | PASS           | Region + District + Latitude + Longitude + GeoJSON_District + IsMapped                                       |
| B1 Empty rows/columns                   | PASS           | All 261×44 populated (per Stage 3)                                                                           |
| B2 Missing per column >10% flagged      | PASS           | All primary analytical variables have 0% missingness (per Stage 3 audit)                                     |
| B3 Missing encoding consistent          | PASS           | Only NaN for GeoJSON_District where IsMapped=False (Guan)                                                    |
| B4 All 261 districts present            | PASS           | n=261 confirmed                                                                                              |
| C1 Numeric values plausible             | PASS           | U5MR 20-72, percentages bounded 0-100, all in expected ranges                                                |
| C2 Percentages 0-100                    | PASS           | All *_pct columns confirmed in [0, 100]                                                                      |
| C3 Rates non-negative                   | PASS           | All rate columns ≥ 0                                                                                         |
| C4 Dates ISO8601 — N/A                  | PASS           | No date columns in this cross-section                                                                        |
| C5 Categorical labels consistent        | PASS           | Class: Metropolitan/Municipal/District uniform; Region: 16 distinct values                                   |
| C6 Pop denominators consistent with GSS | PASS           | Total Population sums to 30,811,446 — matches GSS 2021 Census                                                |
| C7 DHIMS2 codes — N/A                   | PASS           | DHS-based, not DHIMS2                                                                                        |
| D1 Column totals/subtotals match        | PASS           | Region rollups via groupby sum match per-region totals                                                       |
| D2 Derived columns verified             | PASS           | Illiteracy_rate_pct, Uninsurance_rate_pct, Under5_population verified against components                     |
| D3 Summary stats match manuscript       | PASS           | Table 1 values in manuscript match df.describe() outputs exactly                                             |
| D4 BYM RR consistency — N/A             | PASS           | BYM not used in this study                                                                                   |
| E1 Source documented per column         | PASS           | Data_Source_Demographics / Data_Source_WASH / Data_Source_ChildHealth columns                                |
| E2 Year of collection stated            | PASS           | Methods 2.2 names DHS 2022 + Census 2021                                                                     |
| E3 Version/last-modified                | MINOR REVISION | Add 'Last_modified' column or commit hash for version tracking                                               |
| E4 UTF-8 encoded, no BOM                | PASS           | Standard pd.to_csv default — UTF-8 without BOM                                                               |