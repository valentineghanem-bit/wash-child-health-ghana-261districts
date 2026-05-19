# QA Master Summary — WASH Ghana 261 Districts

**Date:** 2026-05-14 | **Framework:** AIPOCH v6.0

## Output verdicts

| Output      | Overall Rating   |   Critical | Action Required                                |
|:------------|:-----------------|-----------:|:-----------------------------------------------|
| Manuscript  | 35/36 PASS       |          0 | None                                           |
| Poster      | 14/16 PASS       |          0 | Body font ≥14pt for A0 print                   |
| Dashboard   | 17/20 PASS       |          0 | ARIA labels + CSV download link                |
| Master CSV  | 22/24 PASS       |          0 | Version column for tracking                    |
| GitHub Repo | 22/25 PASS (88%) |          0 | Build Dash app.py for full Tenet 11 compliance |

## Reconciliation verdict: **PASS**  (20/20 consistent — 100.0%)

## Stress Test verdict: **CONDITIONALLY ROBUST**

## OVERALL QA VERDICT: **QA PASSED**

## Consolidated action items

|   ID | Output     | Issue                                                                                   | Severity   | Fix                                                                                                                                                                                | Stage   |
|-----:|:-----------|:----------------------------------------------------------------------------------------|:-----------|:-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|:--------|
|    1 | Manuscript | Open defecation total effect has counter-intuitive negative sign (regional confounding) | High       | Acknowledged in Discussion; E-value=1.09 reported; sensitivity within high-burden bloc yielded expected positive sign — note added to Limitations                                  | QA-7    |
|    2 | Manuscript | DHS regional values assigned to constituent districts is an ecological-fallacy risk     | High       | Acknowledged in Limitations; LOROCV honest reporting demonstrates the prediction ceiling; future panel work should incorporate routine surveillance data for district-level signal | QA-7    |

## Publication Readiness

- All 5 deliverables: ✓ Present
- Reproducibility: 88%
- Cross-output consistency: 100%
- Critical defects: 0
- /disseminate: UNLOCKED
- /github-publish: PERMITTED (subject to SYNC_PASS)
