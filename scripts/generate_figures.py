"""
WASH Ghana — Stage 10/11 Task 16 figure generator
Produces 6 publication-quality figures (300 DPI):
  Fig 1 — Choropleth U5MR (matplotlib polygon plot from GeoJSON)
  Fig 2 — Choropleth Improved water + Open defecation (2-panel)
  Fig 3 — LISA cluster map of U5MR (with p<0.05 significance mask)
  Fig 4 — Bivariate LISA map: Open defecation × U5MR
  Fig 5 — Correlation heatmap (full symmetric, EX-021)
  Fig 6 — Permutation importance bar chart (EX-022)
"""
import os, sys, json
import numpy as np, pandas as pd
from pathlib import Path
import matplotlib.pyplot as plt
from matplotlib.collections import PatchCollection
from matplotlib.patches import Polygon as MplPolygon
import matplotlib.colors as mcolors
import seaborn as sns

BASE_DIR = Path(os.path.dirname(os.path.abspath(__file__))).parent
RAW = BASE_DIR / "data" / "raw"
OUT_DATA = BASE_DIR / "outputs" / "data"
OUT_FIG = BASE_DIR / "outputs" / "figures"
OUT_FIG.mkdir(parents=True, exist_ok=True)

# Style
plt.rcParams.update({
    'font.family':'DejaVu Serif','font.size':11,
    'axes.spines.top':False,'axes.spines.right':False,
    'figure.facecolor':'white','axes.facecolor':'#fafafa',
})

# Load data
m = pd.read_csv(OUT_DATA / "WASH_Ghana_District_Master.csv")
with open(RAW / "Ghana_New_260_District.geojson") as fh:
    geo = json.load(fh)

# Build district→variable lookup using the IsMapped mask
m_mapped = m[m["IsMapped"]].copy().reset_index(drop=True)

def norm(s):
    if pd.isna(s): return None
    return (str(s).strip().upper().replace("-"," ").replace("/"," ")
            .replace("MUNICIPAL","").replace("METROPOLITAN","").replace("METROPOLIS","")
            .replace(".","").replace(",","").replace("  "," ").strip())

m_mapped["Match_key"] = m_mapped["GeoJSON_District"].apply(norm)


def plot_choropleth(ax, value_col, title, cmap="YlOrRd", vmin=None, vmax=None,
                    cbar_label=None, source_df=None):
    if source_df is None:
        source_df = m_mapped
    # Build key→value map
    val_map = dict(zip(source_df["Match_key"], source_df[value_col]))
    patches, vals = [], []
    for f in geo["features"]:
        k = norm(f["properties"]["DISTRICT"])
        if k not in val_map: continue
        v = val_map[k]
        geom = f["geometry"]
        if geom["type"] == "Polygon":
            for ring in geom["coordinates"]:
                patches.append(MplPolygon(ring, closed=True))
                vals.append(v)
        elif geom["type"] == "MultiPolygon":
            for poly in geom["coordinates"]:
                for ring in poly:
                    patches.append(MplPolygon(ring, closed=True))
                    vals.append(v)
    vals = np.array(vals)
    norm_obj = mcolors.Normalize(vmin=vmin or vals.min(), vmax=vmax or vals.max())
    pc = PatchCollection(patches, cmap=cmap, edgecolor='white', linewidth=0.2, alpha=0.95)
    pc.set_array(vals); pc.set_norm(norm_obj)
    ax.add_collection(pc)
    ax.set_aspect('equal')
    ax.set_xlim(-3.5, 1.5); ax.set_ylim(4.4, 11.4)
    ax.set_xticks([]); ax.set_yticks([])
    ax.set_title(title, fontsize=13, fontweight='bold', pad=10)
    cbar = plt.colorbar(pc, ax=ax, fraction=0.04, pad=0.02)
    cbar.set_label(cbar_label or value_col, fontsize=10)
    cbar.ax.tick_params(labelsize=9)


# ===================== FIGURE 1 — U5MR Choropleth ===========================
fig, ax = plt.subplots(figsize=(8, 9), dpi=300)
plot_choropleth(ax, "U5MR_per_1000", "Under-five mortality rate — Ghana, 260 districts",
                cmap="YlOrRd", cbar_label="U5MR per 1,000 LB")
plt.figtext(0.5, 0.05,
            "Figure 1. Choropleth of under-five mortality rate (U5MR) per 1,000 live births across 260 mapped Ghana "
            "districts. Guan district (Oti) is excluded from the spatial map (GeoJSON limitation) but included in tabular "
            "analyses. Data: DHS Ghana 2022 mapped to districts via Master Sheet 2021 Census. Global Moran's I = 0.83, "
            "p < 0.001 (KNN k=4 weights, 999 permutations).",
            ha='center', fontsize=10, fontstyle='italic', color='#333', wrap=True)
plt.tight_layout(rect=[0, 0.12, 1, 1])
plt.savefig(OUT_FIG / "Fig1_U5MR_choropleth.png", dpi=300, bbox_inches='tight')
plt.close()
print("  ✓ Fig 1 — U5MR choropleth")

# ===================== FIGURE 2 — WASH 2-panel ==============================
fig, axes = plt.subplots(1, 2, figsize=(15, 8), dpi=300)
plot_choropleth(axes[0], "Improved_water_pct", "(A) Improved water source coverage (%)",
                cmap="Blues", cbar_label="% households")
plot_choropleth(axes[1], "Open_defecation_pct", "(B) Open defecation prevalence (%)",
                cmap="Reds", cbar_label="% households")
plt.figtext(0.5, 0.03,
            "Figure 2. Spatial distribution of two WASH indicators across Ghana's 260 mapped districts. "
            "(A) Improved water source coverage shows a north-south gradient (range 59.3–98.5%). "
            "(B) Open defecation prevalence shows the inverse pattern, concentrated in northern districts (range 5.0–71.1%). "
            "Both indicators exhibit strong spatial clustering: Improved water Moran's I = 0.77, p < 0.001; "
            "Open defecation Moran's I = 0.96, p < 0.001.",
            ha='center', fontsize=10, fontstyle='italic', color='#333', wrap=True)
plt.tight_layout(rect=[0, 0.10, 1, 1])
plt.savefig(OUT_FIG / "Fig2_WASH_2panel.png", dpi=300, bbox_inches='tight')
plt.close()
print("  ✓ Fig 2 — WASH 2-panel choropleth")

# ===================== FIGURE 3 — LISA cluster map ==========================
lisa = pd.read_csv(OUT_DATA / "lisa_univariate_results.csv")
lisa["Match_key"] = lisa["GeoJSON_District"].apply(norm)

LISA_COLOURS = {"HH":"#d7301f", "LL":"#2c7fb8", "HL":"#fdae61",
                "LH":"#abd9e9", "NS":"#eeeeee"}

fig, ax = plt.subplots(figsize=(9, 9), dpi=300)
patches, colors = [], []
val_map = dict(zip(lisa["Match_key"], lisa["LISA_U5MR_per_1000_cluster"]))
for f in geo["features"]:
    k = norm(f["properties"]["DISTRICT"])
    if k not in val_map: continue
    c = LISA_COLOURS.get(val_map[k], "#eeeeee")
    geom = f["geometry"]
    if geom["type"] == "Polygon":
        for ring in geom["coordinates"]:
            patches.append(MplPolygon(ring, closed=True)); colors.append(c)
    elif geom["type"] == "MultiPolygon":
        for poly in geom["coordinates"]:
            for ring in poly:
                patches.append(MplPolygon(ring, closed=True)); colors.append(c)
pc = PatchCollection(patches, facecolors=colors, edgecolor='white', linewidth=0.25, alpha=0.95)
ax.add_collection(pc)
ax.set_aspect('equal'); ax.set_xlim(-3.5, 1.5); ax.set_ylim(4.4, 11.4)
ax.set_xticks([]); ax.set_yticks([])
ax.set_title("Univariate LISA cluster map — U5MR (Rook contiguity, p < 0.05)",
             fontsize=13, fontweight='bold', pad=10)
# Legend
from matplotlib.patches import Patch
legend_handles = [
    Patch(facecolor=LISA_COLOURS["HH"], edgecolor='black', label='High-High (n=25)'),
    Patch(facecolor=LISA_COLOURS["LL"], edgecolor='black', label='Low-Low (n=35)'),
    Patch(facecolor=LISA_COLOURS["HL"], edgecolor='black', label='High-Low (n=0)'),
    Patch(facecolor=LISA_COLOURS["LH"], edgecolor='black', label='Low-High (n=0)'),
    Patch(facecolor=LISA_COLOURS["NS"], edgecolor='black', label='Not significant (n=200)'),
]
ax.legend(handles=legend_handles, loc='lower right', frameon=True, fontsize=10,
          title='LISA cluster type', title_fontsize=11)
plt.figtext(0.5, 0.05,
            "Figure 3. Univariate LISA cluster map for U5MR using Rook contiguity weights with 999 permutations. "
            "High-High clusters (25 districts) are concentrated in the northern regions (Northern, North East, Savannah, "
            "Upper East, Upper West); Low-Low clusters (35 districts) dominate the south (Greater Accra, Central, "
            "Eastern). Only districts significant at p < 0.05 are coloured by cluster type.",
            ha='center', fontsize=10, fontstyle='italic', color='#333', wrap=True)
plt.tight_layout(rect=[0, 0.10, 1, 1])
plt.savefig(OUT_FIG / "Fig3_LISA_U5MR.png", dpi=300, bbox_inches='tight')
plt.close()
print("  ✓ Fig 3 — LISA cluster map U5MR")

# ===================== FIGURE 4 — Bivariate LISA OD × U5MR ==================
bv = pd.read_csv(OUT_DATA / "lisa_bivariate_results.csv")
bv["Match_key"] = bv["GeoJSON_District"].apply(norm)
bv_col = "BV_Open_defecation_pct_X_U5MR_per_1000_cluster"
val_map = dict(zip(bv["Match_key"], bv[bv_col]))

fig, ax = plt.subplots(figsize=(9, 9), dpi=300)
patches, colors = [], []
for f in geo["features"]:
    k = norm(f["properties"]["DISTRICT"])
    if k not in val_map: continue
    c = LISA_COLOURS.get(val_map[k], "#eeeeee")
    geom = f["geometry"]
    if geom["type"] == "Polygon":
        for ring in geom["coordinates"]:
            patches.append(MplPolygon(ring, closed=True)); colors.append(c)
    elif geom["type"] == "MultiPolygon":
        for poly in geom["coordinates"]:
            for ring in poly:
                patches.append(MplPolygon(ring, closed=True)); colors.append(c)
pc = PatchCollection(patches, facecolors=colors, edgecolor='white', linewidth=0.25)
ax.add_collection(pc)
ax.set_aspect('equal'); ax.set_xlim(-3.5, 1.5); ax.set_ylim(4.4, 11.4)
ax.set_xticks([]); ax.set_yticks([])
ax.set_title("Bivariate LISA — Open defecation × U5MR (Rook, p < 0.05)",
             fontsize=13, fontweight='bold', pad=10)
counts = bv[bv_col].value_counts()
legend_handles = [
    Patch(facecolor=LISA_COLOURS["HH"], edgecolor='black',
          label=f'High OD - High U5MR (n={counts.get("HH",0)})'),
    Patch(facecolor=LISA_COLOURS["LL"], edgecolor='black',
          label=f'Low OD - Low U5MR (n={counts.get("LL",0)})'),
    Patch(facecolor=LISA_COLOURS["HL"], edgecolor='black',
          label=f'High OD - Low U5MR (n={counts.get("HL",0)})'),
    Patch(facecolor=LISA_COLOURS["LH"], edgecolor='black',
          label=f'Low OD - High U5MR (n={counts.get("LH",0)})'),
    Patch(facecolor=LISA_COLOURS["NS"], edgecolor='black',
          label=f'Not significant (n={counts.get("NS",0)})'),
]
ax.legend(handles=legend_handles, loc='lower right', frameon=True, fontsize=10,
          title='Bivariate cluster', title_fontsize=11)
plt.figtext(0.5, 0.05,
            "Figure 4. Bivariate LISA cluster map: Open defecation prevalence (focal x) × U5MR neighbour mean (lagged y). "
            "23 districts show High-High co-clustering — high open defecation paired with neighbouring high U5MR — "
            "concentrated in the northern savannah regions. 36 districts show the converse Low-Low pattern in the south.",
            ha='center', fontsize=10, fontstyle='italic', color='#333', wrap=True)
plt.tight_layout(rect=[0, 0.10, 1, 1])
plt.savefig(OUT_FIG / "Fig4_BvLISA_OD_U5MR.png", dpi=300, bbox_inches='tight')
plt.close()
print("  ✓ Fig 4 — Bivariate LISA OD × U5MR")

# ===================== FIGURE 5 — Full correlation heatmap (EX-021) ========
heatmap_vars = [
    "U5MR_per_1000", "IMR_per_1000", "NMR_per_1000",
    "Diarrhoea_prevalence_pct",
    "Improved_water_pct", "Improved_sanitation_pct", "Open_defecation_pct",
    "Water_treated_pct",
    "Incidence of Poverty", "Illiteracy_rate_pct", "Uninsurance_rate_pct",
    "Total Population", "Youth_dependency_ratio",
    "EBF_within_1hr_pct", "Child_anaemia_any_pct",
]
short_labels = {
    "U5MR_per_1000":"U5MR","IMR_per_1000":"IMR","NMR_per_1000":"NMR",
    "Diarrhoea_prevalence_pct":"Diarrhoea %",
    "Improved_water_pct":"Improved Water","Improved_sanitation_pct":"Improved San.",
    "Open_defecation_pct":"Open Defec.","Water_treated_pct":"Water Treated",
    "Incidence of Poverty":"Poverty Inc.","Illiteracy_rate_pct":"Illiteracy",
    "Uninsurance_rate_pct":"Uninsured","Total Population":"Total Pop",
    "Youth_dependency_ratio":"Youth Dep.",
    "EBF_within_1hr_pct":"EBF <1hr","Child_anaemia_any_pct":"Anaemia",
}
corr = m_mapped[heatmap_vars].corr()
corr.index = [short_labels[c] for c in corr.index]
corr.columns = [short_labels[c] for c in corr.columns]

fig, ax = plt.subplots(figsize=(12, 10), dpi=300)
sns.heatmap(corr, annot=True, fmt=".2f", cmap="RdBu_r", center=0,
            vmin=-1, vmax=1, square=True, linewidths=0.5,
            cbar_kws={"shrink":0.7, "label":"Pearson r"}, annot_kws={"fontsize":9}, ax=ax)
ax.set_title("Full correlation matrix — analytical variables (n = 260 mapped districts)",
             fontsize=13, fontweight='bold', pad=14)
plt.xticks(rotation=45, ha='right', fontsize=10)
plt.yticks(rotation=0, fontsize=10)
plt.figtext(0.5, 0.02,
            "Figure 5. Pearson correlation matrix for all primary analytical variables. The matrix is symmetric and "
            "complete (no triangle masking, EX-021). Strong positive associations are visible among open defecation, "
            "illiteracy, child anaemia, and U5MR; strong negative associations between improved water/sanitation and "
            "U5MR/diarrhoea. The mediator (Diarrhoea %) shows moderate correlations with both WASH exposures and U5MR.",
            ha='center', fontsize=10, fontstyle='italic', color='#333', wrap=True)
plt.tight_layout(rect=[0, 0.06, 1, 1])
plt.savefig(OUT_FIG / "Fig5_correlation_matrix.png", dpi=300, bbox_inches='tight')
plt.close()
print("  ✓ Fig 5 — Correlation matrix")

# ===================== FIGURE 6 — Permutation importance (EX-022) ===========
imp = pd.read_csv(BASE_DIR / "outputs" / "tables" / "permutation_importance.csv")
imp = imp.sort_values("PermImportance_mean", ascending=True).tail(12)

human_labels = {
    "Improved_water_pct":"Improved water source",
    "Improved_sanitation_pct":"Improved sanitation",
    "Open_defecation_pct":"Open defecation",
    "Water_treated_pct":"Water treatment at home",
    "Diarrhoea_prevalence_pct":"Childhood diarrhoea",
    "EBF_within_1hr_pct":"Early breastfeeding (<1h)",
    "Child_anaemia_any_pct":"Child anaemia",
    "Incidence of Poverty":"Poverty incidence",
    "Intensity of Poverty":"Poverty intensity",
    "Illiteracy_rate_pct":"Adult illiteracy",
    "Uninsurance_rate_pct":"Health insurance non-enrolment",
    "Unemployment_rate_pct":"Unemployment",
    "Total Population":"Total population",
    "Youth_dependency_ratio":"Youth dependency ratio",
}
imp["Label"] = imp["Feature"].map(human_labels).fillna(imp["Feature"])

fig, ax = plt.subplots(figsize=(14, 10), dpi=300)
colors_bar = plt.cm.Blues(np.linspace(0.35, 0.95, len(imp)))
bars = ax.barh(imp["Label"], imp["PermImportance_mean"],
               xerr=imp["PermImportance_SD"], color=colors_bar, edgecolor='black',
               error_kw={'ecolor':'#666','capsize':3})
for bar, val in zip(bars, imp["PermImportance_pct"]):
    ax.text(bar.get_width() + 0.005, bar.get_y() + bar.get_height()/2,
            f"{val:.1f}%", va='center', fontsize=11)
ax.set_xlabel("Permutation importance (mean decrease in R²)",
              fontsize=12, fontweight='semibold', labelpad=8)
ax.set_title("Random Forest permutation importance — drivers of U5MR (region-LOROCV)",
             fontsize=13, fontweight='bold', pad=12)
plt.figtext(0.5, 0.02,
            "Figure 6. Permutation importance from the full-feature Random Forest model (n=500 trees, seed=42, 10 "
            "permutation repeats). Percentages on each bar show share of total permutation-importance. SHAP was "
            "unavailable on this analytical environment; permutation importance is the documented substitute. Top "
            "three drivers — improved water (47.0%), child anaemia (27.1%), early breastfeeding (23.5%) — together "
            "account for ~98% of explainable variance.",
            ha='center', fontsize=10, fontstyle='italic', color='#333', wrap=True)
plt.tight_layout(rect=[0, 0.06, 1, 1])
plt.savefig(OUT_FIG / "Fig6_permutation_importance.png", dpi=300, bbox_inches='tight')
plt.close()
print("  ✓ Fig 6 — Permutation importance")

print("\nAll 6 figures rendered at 300 DPI.")
print(f"Output: {OUT_FIG}")
