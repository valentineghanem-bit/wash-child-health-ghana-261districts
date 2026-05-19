"""
WASH Ghana — Poster (A0 .html) + Dashboard (.html) + GitHub repo scaffold

Poster: 9 required sections (EX-006). Base64 image embedding.
Dashboard: Self-contained HTML with Leaflet choropleth + Chart.js bars + summary KPIs.
Repo scaffold: README, LICENSE (MIT), requirements.txt, .gitattributes, .gitignore, CITATION.cff
"""
import os, sys, json, base64
from pathlib import Path
import pandas as pd

BASE_DIR = Path(os.path.dirname(os.path.abspath(__file__))).parent
OUT_FIG = BASE_DIR / "outputs" / "figures"
OUT_DATA = BASE_DIR / "outputs" / "data"
OUT_TABLES = BASE_DIR / "outputs" / "tables"
OUT_POSTER = BASE_DIR / "poster"
OUT_DASH = BASE_DIR / "dashboard"
OUT_REPO = BASE_DIR  # repo root IS the project folder
OUT_POSTER.mkdir(parents=True, exist_ok=True)
OUT_DASH.mkdir(parents=True, exist_ok=True)

# Load data
master = pd.read_csv(OUT_DATA / "WASH_Ghana_District_Master.csv")
mediation = pd.read_csv(OUT_TABLES / "mediation_analysis.csv")

def b64(path):
    with open(path, "rb") as f:
        return base64.b64encode(f.read()).decode()

# Embed figures
fig1 = b64(OUT_FIG / "Fig1_U5MR_choropleth.png")
fig2 = b64(OUT_FIG / "Fig2_WASH_2panel.png")
fig3 = b64(OUT_FIG / "Fig3_LISA_U5MR.png")
fig5 = b64(OUT_FIG / "Fig5_correlation_matrix.png")
fig6 = b64(OUT_FIG / "Fig6_permutation_importance.png")

# =================== POSTER ===================
poster_html = f"""<!DOCTYPE html>
<html><head><meta charset="utf-8">
<title>WASH Determinants of Child Health, Ghana 261 Districts</title>
<style>
  body {{ font-family: 'Helvetica Neue', Arial, sans-serif; background:#f5f5f5; margin:0;
          color:#222; }}
  .poster {{ width:1189mm; height:841mm; background:white; margin:20px auto; padding:30mm;
             box-sizing:border-box; box-shadow:0 4px 20px rgba(0,0,0,0.15); position:relative; }}
  @media print {{ body{{background:white;}} .poster{{margin:0;box-shadow:none;}} }}
  h1 {{ color:#2E5090; font-size:36pt; margin:0 0 10pt 0; line-height:1.1; }}
  h2 {{ color:#2E5090; font-size:18pt; border-top:3px solid #2E5090; padding-top:6pt;
        margin-top:14pt; margin-bottom:8pt; }}
  .author {{ font-size:14pt; color:#444; margin-bottom:4pt; }}
  .meta {{ font-size:11pt; color:#666; }}
  .grid {{ display:grid; grid-template-columns: 1fr 1fr 1fr 1fr; gap:14mm; margin-top:10mm; }}
  .grid > div {{ background:#fbfbfb; padding:8mm; border-radius:4pt;
                 border-left:4px solid #2E5090; }}
  ul {{ font-size:11pt; line-height:1.5; padding-left:18pt; }}
  li {{ margin-bottom:3pt; }}
  p {{ font-size:11pt; line-height:1.45; }}
  .figure {{ background:white; padding:6pt; border:1px solid #ddd; text-align:center;
              margin:6pt 0; }}
  .figure img {{ max-width:100%; height:auto; }}
  .figure-cap {{ font-size:10pt; font-style:italic; color:#555; padding-top:4pt; }}
  .kpi {{ background:#2E5090; color:white; padding:8mm; text-align:center;
          border-radius:4pt; }}
  .kpi-value {{ font-size:24pt; font-weight:bold; }}
  .kpi-label {{ font-size:10pt; }}
  .refs {{ font-size:9pt; color:#444; }}
  .qr {{ position:absolute; bottom:30mm; right:30mm; width:60mm; }}
</style></head>
<body>
<div class="poster">
  <h1>Water, Sanitation, and Hygiene Determinants of Childhood Diarrhoea and Under-Five
      Mortality in Ghana: A 261-District Spatial Machine-Learning Mediation Analysis</h1>
  <p class="author"><b>Valentine Golden Ghanem</b> — Cocoa Clinic, Ghana COCOBOD, Accra |
     ORCID: 0009-0002-8332-0220 | valentineghanem@gmail.com</p>
  <p class="meta">May 2026 · Target journals: IJERPH · BMC Public Health · Tropical Medicine &amp; Int Health</p>

  <div class="grid">
    <div class="kpi"><div class="kpi-value">0.83</div><div class="kpi-label">Moran's I — U5MR (p&lt;0.001)</div></div>
    <div class="kpi"><div class="kpi-value">25</div><div class="kpi-label">LISA HH hotspots — U5MR</div></div>
    <div class="kpi"><div class="kpi-value">36%</div><div class="kpi-label">Effect mediated via diarrhoea</div></div>
    <div class="kpi"><div class="kpi-value">261</div><div class="kpi-label">Districts (260 mapped + Guan)</div></div>
  </div>

  <div class="grid">
    <div>
      <h2>Background</h2>
      <p>Diarrhoeal disease causes ~297,000 WASH-attributable deaths in children under-5 annually
         worldwide [Prüss-Ustün 2019]. Ghana's 2018 administrative reform expanded the country to
         <b>261 health districts</b>. Subnational evidence on the WASH → diarrhoea → U5MR pathway
         is sparse for West Africa.</p>
      <p><b>Objective:</b> Decompose the WASH effect on U5MR into diarrhoea-mediated (NIE) and
         direct (NDE) channels across all 261 Ghana districts.</p>
      <p><b>Design:</b> Ecological cross-sectional analysis (STROBE + TRIPOD+AI compliant).</p>
    </div>
    <div>
      <h2>Methods</h2>
      <ul>
        <li><b>Data:</b> Ghana DHS 2022 + GSS 2021 Census + 260-district GeoJSON (Guan tabular-only)</li>
        <li><b>Spatial:</b> Global Moran's I (KNN k=4) + LISA (Rook contiguity) + Getis-Ord Gi*</li>
        <li><b>ML:</b> Random Forest + Gradient Boosting with region-stratified LOROCV (16 folds)</li>
        <li><b>Mediation:</b> Baron-Kenny with 1000 bootstrap iterations + Vanderweele E-value</li>
        <li><b>Permutations:</b> 999 for all spatial tests</li>
        <li><b>Software:</b> Python 3.10 · numpy · pandas · scikit-learn 1.7 · matplotlib</li>
      </ul>
    </div>
    <div>
      <h2>Results — Spatial structure</h2>
      <div class="figure">
        <img src="data:image/png;base64,{fig1}" alt="U5MR choropleth">
        <div class="figure-cap">Figure 1. U5MR per 1,000 LB across 260 mapped districts.
        Range 20–72; mean 43.15. Strong north-south gradient.</div>
      </div>
    </div>
    <div>
      <h2>Results — WASH × U5MR co-clustering</h2>
      <div class="figure">
        <img src="data:image/png;base64,{fig3}" alt="LISA U5MR">
        <div class="figure-cap">Figure 3. LISA cluster map. 25 High-High clusters (northern Ghana);
        35 Low-Low clusters (Greater Accra, Central, Eastern).</div>
      </div>
    </div>
  </div>

  <div class="grid">
    <div>
      <h2>Mediation decomposition</h2>
      <p><b>Improved water → U5MR</b><br>
         Total effect: <b>−0.32</b> per pp [95% CI −0.46, −0.16]<br>
         NIE (via diarrhoea): −0.12<br>
         NDE (direct): −0.21<br>
         <b>Proportion mediated: ~36%</b><br>
         E-value: 1.11</p>
      <p><b>Open defecation → U5MR</b><br>
         Total effect: −0.24 [−0.48, −0.05] (regional confounding flagged)<br>
         E-value: 1.09</p>
      <p><b>Improved sanitation → U5MR</b><br>
         Total effect: +0.08 [−0.07, +0.19] — CI crosses null<br>
         E-value: 1.07</p>
    </div>
    <div>
      <h2>ML predictive performance</h2>
      <p><b>Region-stratified LOROCV (honest, not k-fold):</b></p>
      <ul>
        <li>RF (total-effect): RMSE 9.96 ± 8.74, R² ≈ 0</li>
        <li>GB (total-effect): RMSE 9.91 ± 8.35, R² ≈ 0</li>
        <li>Stacked: RMSE 10.85, R² −0.02</li>
      </ul>
      <p style="font-size:9pt;color:#666;">Near-null out-of-region R² is the honest result for
      regionally-assigned DHS predictors. Standard k-fold would have inflated R² owing to within-region
      homogeneity — pre-registered LOROCV reveals the ecological-prediction ceiling.</p>
      <p><b>Top features (permutation importance):</b></p>
      <ol style="font-size:11pt;">
        <li>Improved water source (47.0%)</li>
        <li>Child anaemia (27.1%)</li>
        <li>Early breastfeeding &lt;1h (23.5%)</li>
      </ol>
    </div>
    <div>
      <h2>Conclusions</h2>
      <ol>
        <li><b>U5MR is strongly clustered</b> across Ghana districts (Moran's I = 0.83);
            northern districts carry disproportionate burden.</li>
        <li><b>~36% of the water-U5MR association</b> operates indirectly through diarrhoea;
            the remaining ~64% reflects direct WASH effects (respiratory infection, nutrition,
            broader infectious-disease co-exposure).</li>
        <li><b>Ecological data design limits ML generalisability</b> across regions — honest
            LOROCV R² ≈ 0 should be the new reporting standard for DHS-based predictive work.</li>
      </ol>
    </div>
    <div>
      <h2>Policy implications</h2>
      <ul>
        <li>Couple WASH infrastructure investment with ORS/zinc distribution + case-management
            training in the <b>25 high-high U5MR clusters</b> identified (Northern, North East,
            Savannah, Upper East, Upper West regions).</li>
        <li>Position broader child-health investment alongside WASH — the 64% direct effect
            implies WASH is necessary but not sufficient.</li>
        <li>Sub-region-level analytics must report LOROCV-based metrics; k-fold inflates
            confidence in inferences DHS data cannot support.</li>
      </ul>
    </div>
  </div>

  <h2>References (selected)</h2>
  <div class="refs">
    1. Prüss-Ustün A, et al. <i>Int J Hyg Environ Health</i>. 2019;222:765-77.
    <a href="https://doi.org/10.1016/j.ijheh.2019.05.004">doi:10.1016/j.ijheh.2019.05.004</a> ·
    2. GBD 2021 Diarrhoeal Disease Collaborators. <i>Lancet Infect Dis</i>. 2024;25:519-36.
    <a href="https://doi.org/10.1016/S1473-3099(24)00691-1">doi:10.1016/S1473-3099(24)00691-1</a> ·
    3. Gaffan N, et al. <i>Front Public Health</i>. 2023;11:1136564.
    <a href="https://doi.org/10.3389/fpubh.2023.1136564">doi:10.3389/fpubh.2023.1136564</a> ·
    4. Headey D, Palloni G. <i>Demography</i>. 2019;56:729-52.
    <a href="https://doi.org/10.1007/s13524-019-00760-y">doi:10.1007/s13524-019-00760-y</a> ·
    5. Anselin L. <i>Geogr Anal</i>. 1995;27:93-115.
    <a href="https://doi.org/10.1111/j.1538-4632.1995.tb00338.x">doi:10.1111/j.1538-4632.1995.tb00338.x</a> ·
    6. VanderWeele TJ, Ding P. <i>Ann Intern Med</i>. 2017;167:268-74.
    <a href="https://doi.org/10.7326/M16-2607">doi:10.7326/M16-2607</a>
  </div>

  <p style="margin-top:10mm; font-size:9pt; color:#666; text-align:center;">
    Data: Ghana DHS 2022 (dhsprogram.com) · Ghana 2021 Population &amp; Housing Census (statsghana.gov.gh) ·
    Repository: github.com/valentineghanem-bit/wash-child-health-ghana-261-districts
  </p>
</div>
</body></html>
"""
(OUT_POSTER / "WASH_Ghana_Poster.html").write_text(poster_html)
print(f"  ✓ Poster saved: {OUT_POSTER / 'WASH_Ghana_Poster.html'} ({os.path.getsize(OUT_POSTER / 'WASH_Ghana_Poster.html')/1024:.1f} KB)")

# =================== DASHBOARD ===================
# Use Leaflet for choropleth (loads GeoJSON client-side)
# Use Chart.js for bars

# Build district data JSON for dashboard
dash_data = []
for _, r in master.iterrows():
    dash_data.append({
        "district": r["District"],
        "region": r["Region"],
        "geojson_name": r["GeoJSON_District"] if pd.notna(r["GeoJSON_District"]) else None,
        "u5mr": float(r["U5MR_per_1000"]),
        "diarrhoea": float(r["Diarrhoea_prevalence_pct"]),
        "improved_water": float(r["Improved_water_pct"]),
        "improved_sanitation": float(r["Improved_sanitation_pct"]),
        "open_defecation": float(r["Open_defecation_pct"]),
        "poverty": float(r["Incidence of Poverty"]),
        "illiteracy": float(r["Illiteracy_rate_pct"]),
        "is_mapped": bool(r["IsMapped"]),
    })

dashboard_html = f"""<!DOCTYPE html>
<html><head><meta charset="utf-8">
<title>WASH Ghana 261-District Dashboard</title>
<link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css" />
<script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>
<script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.0/dist/chart.umd.min.js"></script>
<style>
  body {{ font-family: 'Helvetica Neue', Arial, sans-serif; margin:0; background:#f5f7fa; color:#222; }}
  header {{ background:#2E5090; color:white; padding:18px 30px; }}
  header h1 {{ margin:0 0 4px 0; font-size:22px; }}
  header p {{ margin:0; font-size:13px; opacity:0.9; }}
  .container {{ display:grid; grid-template-columns: 1fr 1fr; gap:18px; padding:18px 30px; }}
  .panel {{ background:white; border-radius:8px; box-shadow:0 1px 4px rgba(0,0,0,0.08);
            padding:18px; }}
  .panel h2 {{ margin:0 0 12px 0; color:#2E5090; font-size:16px;
                border-bottom:2px solid #f0f0f0; padding-bottom:8px; }}
  .kpis {{ display:grid; grid-template-columns: repeat(4,1fr); gap:12px; margin-bottom:18px; }}
  .kpi {{ background:white; border-left:4px solid #2E5090; padding:14px;
            border-radius:6px; box-shadow:0 1px 3px rgba(0,0,0,0.06); }}
  .kpi-val {{ font-size:24px; font-weight:bold; color:#2E5090; }}
  .kpi-lab {{ font-size:11px; color:#666; }}
  #map {{ height:480px; border-radius:6px; }}
  select {{ padding:6px 10px; font-size:14px; border:1px solid #ccc; border-radius:4px;
            margin-bottom:10px; }}
  .legend {{ background:rgba(255,255,255,0.95); padding:8px 12px; line-height:1.5;
              border-radius:4px; font-size:12px; }}
  .legend i {{ display:inline-block; width:18px; height:14px; margin-right:6px;
                vertical-align:middle; }}
  table {{ border-collapse:collapse; width:100%; font-size:12px; }}
  th, td {{ padding:6px 10px; text-align:left; border-bottom:1px solid #eee; }}
  th {{ background:#f8f9fa; }}
  .footer {{ padding:14px 30px; font-size:11px; color:#666; }}
</style></head>
<body>
<header>
  <h1>WASH Determinants of Child Health — Ghana 261 Districts Interactive Dashboard</h1>
  <p>Valentine Golden Ghanem · DHS Ghana 2022 + GSS 2021 Census + 261-district administrative units (260 mapped + Guan tabular)</p>
</header>

<div style="padding:18px 30px;">
  <div class="kpis">
    <div class="kpi"><div class="kpi-val">261</div><div class="kpi-lab">Total districts</div></div>
    <div class="kpi"><div class="kpi-val">16</div><div class="kpi-lab">Regions</div></div>
    <div class="kpi"><div class="kpi-val">0.83</div><div class="kpi-lab">Moran's I (U5MR)</div></div>
    <div class="kpi"><div class="kpi-val">25</div><div class="kpi-lab">U5MR HH hotspots</div></div>
  </div>
</div>

<div class="container">
  <div class="panel" style="grid-column:1/3;">
    <h2>Interactive choropleth map</h2>
    <label>Variable: </label>
    <select id="var-sel">
      <option value="u5mr">U5MR per 1,000 LB</option>
      <option value="diarrhoea">Diarrhoea prevalence (%)</option>
      <option value="improved_water">Improved water source (%)</option>
      <option value="improved_sanitation">Improved sanitation (%)</option>
      <option value="open_defecation">Open defecation (%)</option>
      <option value="poverty">Poverty incidence (%)</option>
      <option value="illiteracy">Illiteracy rate (%)</option>
    </select>
    <div id="map"></div>
    <p style="font-size:11px;color:#666;margin-top:8px;">
      Map shows 260 districts with GeoJSON polygons. Guan district (Oti region) is the 261st
      tabular-only district excluded from the map due to GeoJSON limitation.</p>
  </div>

  <div class="panel">
    <h2>Top-10 districts by U5MR</h2>
    <canvas id="bar-chart" height="320"></canvas>
  </div>

  <div class="panel">
    <h2>WASH-diarrhoea-U5MR mediation</h2>
    <table>
      <thead><tr><th>Exposure</th><th>Total effect</th><th>95% CI</th><th>NIE</th><th>NDE</th><th>% mediated</th><th>E-value</th></tr></thead>
      <tbody>
        <tr><td>Improved water</td><td>−0.322</td><td>[−0.462, −0.158]</td><td>−0.116</td><td>−0.207</td><td>~36%</td><td>1.11</td></tr>
        <tr><td>Improved sanitation</td><td>+0.079</td><td>[−0.069, +0.187]</td><td>+0.050</td><td>+0.029</td><td>63%</td><td>1.07</td></tr>
        <tr><td>Open defecation</td><td>−0.244</td><td>[−0.477, −0.049]</td><td>+0.079</td><td>−0.323</td><td>—</td><td>1.09</td></tr>
      </tbody>
    </table>
    <p style="font-size:11px;color:#666;margin-top:10px;">
      Baron-Kenny linear mediation, 1000-bootstrap CIs, adjustment for poverty, illiteracy,
      population, dependency ratio, early breastfeeding, child anaemia.</p>
  </div>
</div>

<div class="footer">
  Data source: Ghana DHS 2022; GSS 2021 Population &amp; Housing Census; Ghana_New_260_District.geojson
  · Repository: github.com/valentineghanem-bit/wash-child-health-ghana-261-districts ·
  Last updated: 2026-05-14
</div>

<script>
const DISTRICT_DATA = {json.dumps(dash_data)};

// Build a lookup for choropleth coloring
const dataLookup = {{}};
DISTRICT_DATA.forEach(d => {{
  if (d.geojson_name) dataLookup[d.geojson_name.toUpperCase()] = d;
}});

// Initialise map
const map = L.map('map').setView([7.95, -1.0], 7);
L.tileLayer('https://{{s}}.tile.openstreetmap.org/{{z}}/{{x}}/{{y}}.png', {{
  attribution: '© OpenStreetMap'
}}).addTo(map);

let geoLayer = null;

function colorScale(v, vmin, vmax) {{
  const t = (v - vmin) / (vmax - vmin);
  if (t < 0.2) return '#fff7bc';
  if (t < 0.4) return '#fee391';
  if (t < 0.6) return '#fec44f';
  if (t < 0.8) return '#fe9929';
  return '#cc4c02';
}}

function renderMap(variable) {{
  const vals = DISTRICT_DATA.filter(d => d.is_mapped).map(d => d[variable]);
  const vmin = Math.min(...vals);
  const vmax = Math.max(...vals);

  if (geoLayer) map.removeLayer(geoLayer);

  fetch('Ghana_New_260_District.geojson')
    .then(r => r.json())
    .then(geo => {{
      geoLayer = L.geoJSON(geo, {{
        style: f => {{
          const name = f.properties.DISTRICT.toUpperCase();
          const d = dataLookup[name];
          return {{
            fillColor: d ? colorScale(d[variable], vmin, vmax) : '#eee',
            weight: 0.5, color: '#666', fillOpacity: 0.85
          }};
        }},
        onEachFeature: (f, layer) => {{
          const name = f.properties.DISTRICT.toUpperCase();
          const d = dataLookup[name];
          if (d) {{
            layer.bindTooltip(
              `<b>${{d.district}}</b><br>${{d.region}} region<br>` +
              `U5MR: ${{d.u5mr.toFixed(1)}}/1000<br>` +
              `Diarrhoea: ${{d.diarrhoea.toFixed(1)}}%<br>` +
              `Improved water: ${{d.improved_water.toFixed(1)}}%<br>` +
              `Open defecation: ${{d.open_defecation.toFixed(1)}}%`
            );
          }}
        }}
      }}).addTo(map);
    }})
    .catch(e => {{
      // Fallback: GeoJSON not available locally
      document.getElementById('map').innerHTML =
        '<p style="padding:20px;color:#666;">Place Ghana_New_260_District.geojson in the same folder as this HTML to enable the choropleth map.</p>';
    }});
}}

document.getElementById('var-sel').addEventListener('change', e => renderMap(e.target.value));
renderMap('u5mr');

// Top-10 bar chart
const top10 = [...DISTRICT_DATA].sort((a,b) => b.u5mr - a.u5mr).slice(0, 10);
new Chart(document.getElementById('bar-chart'), {{
  type: 'bar',
  data: {{
    labels: top10.map(d => d.district + ' (' + d.region + ')'),
    datasets: [{{ label: 'U5MR per 1,000 LB', data: top10.map(d => d.u5mr),
                 backgroundColor: '#cc4c02', borderWidth: 0 }}]
  }},
  options: {{ indexAxis: 'y', responsive: true,
              plugins: {{ legend: {{ display: false }} }},
              scales: {{ x: {{ beginAtZero: true }} }} }}
}});
</script>

</body></html>
"""
(OUT_DASH / "WASH_Ghana_Dashboard.html").write_text(dashboard_html)
print(f"  ✓ Dashboard saved: {OUT_DASH / 'WASH_Ghana_Dashboard.html'} ({os.path.getsize(OUT_DASH / 'WASH_Ghana_Dashboard.html')/1024:.1f} KB)")

# =================== GITHUB REPO SCAFFOLD ===================
# README
readme = """# WASH Determinants of Child Health, Ghana 261 Districts

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
"""
(OUT_REPO / "README.md").write_text(readme)
print(f"  ✓ README.md saved")

# LICENSE (MIT)
license_text = """MIT License

Copyright (c) 2026 Valentine Golden Ghanem

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""
(OUT_REPO / "LICENSE").write_text(license_text)
print(f"  ✓ LICENSE saved")

# requirements.txt (pinned)
requirements = """# WASH Ghana 261-District Analysis — pinned dependencies
numpy==2.2.6
pandas==2.3.3
scipy==1.15.3
scikit-learn==1.7.2
matplotlib==3.10.8
seaborn==0.13.2
python-docx==1.2.0
joblib==1.5.3
threadpoolctl==3.6.0
lxml==6.1.0
typing_extensions==4.15.0
openpyxl==3.1.5
pytest==8.0.0  # for canonical-value test suite
"""
(OUT_REPO / "requirements.txt").write_text(requirements)
print(f"  ✓ requirements.txt saved")

# .gitattributes (TECH-004 prevention)
gitattributes = """# Git LFS for large binary research artefacts
*.png filter=lfs diff=lfs merge=lfs -text
*.docx filter=lfs diff=lfs merge=lfs -text
*.pdf filter=lfs diff=lfs merge=lfs -text
*.geojson filter=lfs diff=lfs merge=lfs -text

# Force text for code
*.py text eol=lf
*.md text eol=lf
*.csv text eol=lf
*.json text eol=lf
"""
(OUT_REPO / ".gitattributes").write_text(gitattributes)
print(f"  ✓ .gitattributes saved")

# .gitignore
gitignore = """__pycache__/
*.pyc
.venv/
.env
.ipynb_checkpoints/
.DS_Store
*.log
"""
(OUT_REPO / ".gitignore").write_text(gitignore)
print(f"  ✓ .gitignore saved")

# CITATION.cff
citation = """cff-version: 1.2.0
message: "If you use this software or data, please cite as follows."
authors:
  - family-names: Ghanem
    given-names: Valentine Golden
    orcid: "https://orcid.org/0009-0002-8332-0220"
    affiliation: "Cocoa Clinic, Ghana COCOBOD, Accra, Ghana"
    email: valentineghanem@gmail.com
title: "Water, Sanitation, and Hygiene Determinants of Childhood Diarrhoea and Under-Five Mortality in Ghana: A 261-District Spatial Machine-Learning Mediation Analysis"
version: 1.0.0
date-released: "2026-05-14"
license: MIT
url: "https://github.com/valentineghanem-bit/wash-child-health-ghana-261-districts"
keywords:
  - WASH
  - under-five mortality
  - spatial epidemiology
  - causal mediation
  - Ghana
  - Demographic Health Survey
"""
(OUT_REPO / "CITATION.cff").write_text(citation)
print(f"  ✓ CITATION.cff saved")

print("\n  ALL DELIVERABLES BUILT (poster, dashboard, repo scaffold).")
