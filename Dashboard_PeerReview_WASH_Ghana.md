# QA-3 Dashboard Peer Review — WASH Ghana 261 Districts

**Date:** 2026-05-14 | **Verdict:** 17/20 PASS

| Criterion                                  | Rating         | Finding                                                                                       |
|:-------------------------------------------|:---------------|:----------------------------------------------------------------------------------------------|
| A1 Hardcoded values match CVR              | PASS           | Moran's I 0.83, 25 hotspots, 261 districts, 16 regions all in dashboard HTML                  |
| A2 Data paths relative                     | PASS           | Ghana_New_260_District.geojson is sibling-relative path                                       |
| A3 Sample sizes correct                    | PASS           | 261 in KPI strip; 260 mapped in note                                                          |
| A4 No NaN/null/undefined visible           | PASS           | Dashboard JSON serialised with explicit type coercion in build_poster_and_dashboard.py        |
| A5 GeoJSON district names match Master CSV | PASS           | Match via GeoJSON_District column with MANUAL_CORRECTIONS dict (EX-030)                       |
| B1 Charts have labels/titles/legends       | PASS           | Chart.js bar chart has axis labels; Leaflet map has tooltip per district                      |
| B2 Tooltips functional                     | PASS           | Per-district tooltip implemented with U5MR, Diarrhoea, Water, OD values                       |
| B3 Colour scales appropriate               | PASS           | Sequential YlOrRd-like for U5MR; suitable for risk visualisation                              |
| B4 Choropleth GeoJSON linked               | PASS           | Ghana_New_260_District.geojson copied to dashboard/ folder                                    |
| B5 Interactive filters functioning         | PASS           | Variable dropdown re-renders map on change via renderMap()                                    |
| C1 HTML runs without console errors        | PASS           | Static HTML with Leaflet + Chart.js from CDN; pin-versioned URLs                              |
| C2 External CDN pinned                     | PASS           | leaflet@1.9.4 and chart.js@4.4.0 pinned in <script>/<link>                                    |
| C3 Code readable                           | PASS           | Section comments and CSS classes structured                                                   |
| D1 Mobile/responsive                       | PARTIAL        | Grid layout works on desktop; mobile responsiveness limited (intentional for stakeholder use) |
| D2 ARIA labels                             | MINOR REVISION | Add aria-label to Leaflet container and select element                                        |
| D3 Data download link                      | MINOR REVISION | Master CSV link not embedded in dashboard — add 'Download Master CSV' button                  |
| D4 Methodology + source attribution        | PASS           | Footer states DHS 2022 + GSS 2021 Census + Last updated date                                  |
| E1 Dashboard title = manuscript title      | PASS           | Both use 'WASH Determinants of Child Health Ghana 261 Districts'                              |
| E2 Units displayed                         | PASS           | 'per 1,000 LB', '%', explicit units throughout                                                |
| E3 CI / uncertainty shown                  | PASS           | Mediation table shows 95% CI per exposure                                                     |