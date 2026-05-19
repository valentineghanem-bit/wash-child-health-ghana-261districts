"""
WASH Determinants of Child Health, Ghana 260 Districts
Data harmonisation + Master CSV builder

Two-layer design:
  Layer 1 — Longitudinal panel (10 pre-2018 regions × all DHS rounds 1988-2022)
  Layer 2 — Cross-sectional district-level Master CSV (260 districts, 2022 most-recent)

EX-026: relative paths via os.path.dirname(os.path.abspath(__file__))
EX-030: MANUAL_CORRECTIONS dict + audit CSV for SPAT-006 prevention
ML-005: region-stratified CV grouping column built into Layer 2
"""

import os
import json
import pandas as pd
import numpy as np
from pathlib import Path

# --------------------------------------------------------------------------- #
# PATHS (EX-026)
# --------------------------------------------------------------------------- #
BASE_DIR = Path(os.path.dirname(os.path.abspath(__file__)))
RAW = BASE_DIR.parent / "data" / "raw"
OUT_DATA = BASE_DIR.parent / "outputs" / "data"
OUT_DATA.mkdir(parents=True, exist_ok=True)

# --------------------------------------------------------------------------- #
# REGION HARMONISATION MAP — post-2018 → pre-2018 (for longitudinal panel)
# --------------------------------------------------------------------------- #
POST_TO_PRE = {
    # Stable regions (no change)
    "Ashanti": "Ashanti",
    "Central": "Central",
    "Eastern": "Eastern",
    "Greater Accra": "Greater Accra",
    "Upper East": "Upper East",
    "Upper West": "Upper West",
    # Brong-Ahafo split (2018) → 3 children
    "Ahafo": "Brong-Ahafo",
    "Bono": "Brong-Ahafo",
    "Bono East": "Brong-Ahafo",
    "Brong-Ahafo": "Brong-Ahafo",
    # Northern split (2018) → 3 children (DHS uses "..NAME" prefix for post-split)
    "..Northern(post 2022)": "Northern",
    "..Northeast": "Northern",
    "..Savannah": "Northern",
    "Northern (pre 2022)": "Northern",
    # Volta split (2018) → 2 children
    "Volta (post 2022)": "Volta",
    "Oti": "Volta",
    "Volta (pre 2022)": "Volta",
    # Western split (2018) → 2 children
    "Western (post 2022)": "Western",
    "Western North": "Western",
    "Western (pre 2022)": "Western",
    # Drop DHS multi-region aggregates
    "Northern, Upper West, Upper East": None,
}

# --------------------------------------------------------------------------- #
# Map DHS post-2018 labels to Master Sheet 16-region scheme (for Layer 2)
# --------------------------------------------------------------------------- #
DHS_TO_MS16 = {
    "Ashanti": "Ashanti",
    "Central": "Central",
    "Eastern": "Eastern",
    "Greater Accra": "Greater Accra",
    "Upper East": "Upper East",
    "Upper West": "Upper West",
    "Ahafo": "Ahafo",
    "Bono": "Bono",
    "Bono East": "Bono East",
    "..Northern(post 2022)": "Northern",
    "..Northeast": "North East",
    "..Savannah": "Savannah",
    "Volta (post 2022)": "Volta",
    "Oti": "Oti",
    "Western (post 2022)": "Western",
    "Western North": "Western North",
}

# --------------------------------------------------------------------------- #
# Key analytical indicators we need from each DHS file
# --------------------------------------------------------------------------- #
KEY_INDICATORS = {
    "water": {
        "Households using an improved water source": "Improved_water_pct",
        "Households using an unimproved water source": "Unimproved_water_pct",
        "Households using an appropriate treatment method": "Water_treated_pct",
    },
    "toilet": {
        "Households with an improved sanitation facility": "Improved_sanitation_pct",
        "Households with an unimproved sanitation facility": "Unimproved_sanitation_pct",
        "Households using open defecation": "Open_defecation_pct",
    },
    "diarrhea": {
        "Children with diarrhea": "Diarrhoea_prevalence_pct",
    },
    "child-mortality-rates": {
        "Under-five mortality rate": "U5MR_per_1000",
        "Infant mortality rate": "IMR_per_1000",
        "Neonatal mortality rate": "NMR_per_1000",
    },
    "iycf": {
        "Children who started breastfeeding within 1 hour of birth": "EBF_within_1hr_pct",
        "Children ever breastfed": "Ever_breastfed_pct",
    },
    "anemia": {
        "Children with any anemia": "Child_anaemia_any_pct",
        "Children with severe anemia": "Child_anaemia_severe_pct",
    },
}

DHS_FILES = {
    "water": "water_subnational_gha.csv",
    "toilet": "toilet-facilities_subnational_gha.csv",
    "diarrhea": "diarrhea_subnational_gha.csv",
    "child-mortality-rates": "child-mortality-rates_subnational_gha.csv",
    "iycf": "iycf_subnational_gha.csv",
    "anemia": "anemia_subnational_gha.csv",
}


def load_dhs(domain, fname):
    """Load a DHS subnational CSV and return cleaned long-format dataframe."""
    df = pd.read_csv(RAW / fname, low_memory=False)
    df = df[df["ISO3"] == "GHA"].copy()
    df["SurveyYear"] = pd.to_numeric(df["SurveyYear"], errors="coerce")
    df["Value"] = pd.to_numeric(df["Value"], errors="coerce")
    df = df.dropna(subset=["SurveyYear", "Value", "Location", "Indicator"])
    df["SurveyYear"] = df["SurveyYear"].astype(int)
    df["Domain"] = domain
    return df[["SurveyYear", "Location", "Indicator", "Value", "Domain"]]


# --------------------------------------------------------------------------- #
# LOAD ALL DHS FILES
# --------------------------------------------------------------------------- #
print("=" * 70)
print("STEP 1: Loading DHS files")
print("=" * 70)
all_dhs = []
for domain, fname in DHS_FILES.items():
    df = load_dhs(domain, fname)
    print(f"  {domain:25s}: {len(df):>6,} rows, "
          f"{df['SurveyYear'].nunique()} years, "
          f"{df['Location'].nunique()} locations")
    all_dhs.append(df)
dhs = pd.concat(all_dhs, ignore_index=True)
print(f"\nCombined DHS long-format: {dhs.shape}")

# Keep only the key indicators (using exact string match where possible)
key_inds_flat = {k: v for d in KEY_INDICATORS.values() for k, v in d.items()}
dhs_keep = dhs[dhs["Indicator"].isin(key_inds_flat.keys())].copy()
dhs_keep["VarName"] = dhs_keep["Indicator"].map(key_inds_flat)
print(f"After filtering to {len(key_inds_flat)} key indicators: {dhs_keep.shape}")

# --------------------------------------------------------------------------- #
# STEP 2: LAYER 1 — Longitudinal panel (10 pre-2018 regions)
# --------------------------------------------------------------------------- #
print("\n" + "=" * 70)
print("STEP 2: Layer 1 — Longitudinal panel (10 pre-2018 regions)")
print("=" * 70)

dhs_keep["Region_pre2018"] = dhs_keep["Location"].map(POST_TO_PRE)
panel_long = dhs_keep.dropna(subset=["Region_pre2018"]).copy()

# Aggregate post-2018 splits back to pre-2018 parent by simple mean
# (population-weighted aggregation is better but requires denominators per region)
panel_agg = panel_long.groupby(
    ["SurveyYear", "Region_pre2018", "VarName"], as_index=False
)["Value"].mean()

# Pivot to wide: one row per (Region, Year)
panel = panel_agg.pivot_table(
    index=["Region_pre2018", "SurveyYear"],
    columns="VarName",
    values="Value",
    aggfunc="mean"
).reset_index()
panel.columns.name = None
panel = panel.rename(columns={"Region_pre2018": "Region", "SurveyYear": "Year"})
print(f"Panel shape: {panel.shape}")
print(f"Regions in panel: {panel['Region'].nunique()} — {sorted(panel['Region'].unique())}")
print(f"Years in panel: {sorted(panel['Year'].unique())}")
print(f"\nFirst 5 rows:")
print(panel.head().to_string())
print(f"\nMissing data (column-wise %):")
print((panel.isna().sum() / len(panel) * 100).round(1).to_string())

panel.to_csv(OUT_DATA / "WASH_Ghana_Panel_RegionYear.csv", index=False)
print(f"\nSaved: {OUT_DATA / 'WASH_Ghana_Panel_RegionYear.csv'}")

# --------------------------------------------------------------------------- #
# STEP 3: LAYER 2 — 2022 cross-section (16 regions → 260 districts)
# --------------------------------------------------------------------------- #
print("\n" + "=" * 70)
print("STEP 3: Layer 2 — 2022 cross-section, 16 regions → 260 districts")
print("=" * 70)

# Most recent year available per indicator (2022 for most; fall back if missing)
def latest_value(group):
    return group.sort_values("SurveyYear").iloc[-1]

# Map DHS Location to 16-region scheme
dhs_keep["Region16"] = dhs_keep["Location"].map(DHS_TO_MS16)
dhs_2022 = dhs_keep.dropna(subset=["Region16"]).copy()

# For each (Region16, VarName), take most recent value
ranked = dhs_2022.sort_values(["Region16", "VarName", "SurveyYear"])
latest = ranked.groupby(["Region16", "VarName"], as_index=False).tail(1)
print(f"After taking latest value per region × variable: {latest.shape}")

# Pivot to wide
region16 = latest.pivot_table(
    index="Region16",
    columns="VarName",
    values="Value",
    aggfunc="mean"
).reset_index()
region16.columns.name = None
print(f"Region-16 wide table: {region16.shape}")
print(f"Columns: {list(region16.columns)}")

# Save the intermediate 16-region table
region16.to_csv(OUT_DATA / "WASH_Ghana_Region16_Wide.csv", index=False)

# --------------------------------------------------------------------------- #
# Load Master Sheet and merge by Region
# --------------------------------------------------------------------------- #
ms = pd.read_excel(RAW / "Master Sheet.xlsx")
ms = ms.rename(columns={
    "Metropolitan, Municipal, and District Assemblies (MMDA's)": "District",
})
print(f"\nMaster Sheet: {ms.shape}")
print(f"Regions in MS: {sorted(ms['Region'].unique())}")

# Confirm region naming match
ms_regions = set(ms["Region"].unique())
dhs_regions = set(region16["Region16"].unique())
print(f"In MS not in DHS-16: {ms_regions - dhs_regions}")
print(f"In DHS-16 not in MS: {dhs_regions - ms_regions}")

# Merge: each district gets its region's DHS values (ecological assignment)
master = ms.merge(region16, left_on="Region", right_on="Region16", how="left")
master = master.drop(columns=["Region16"])
print(f"\nAfter merge: {master.shape}")

# --------------------------------------------------------------------------- #
# Derive district-level rates from Master Sheet counts
# --------------------------------------------------------------------------- #
master["Illiteracy_rate_pct"] = (
    master["Illiterate Population"] / master["Total Population"] * 100
).round(2)
master["Uninsurance_rate_pct"] = (
    master["Uninsured Population"] / master["Total Population"] * 100
).round(2)
master["Under5_population"] = (
    (master["Male Population 0-14"] + master["Female Population 0-14"]) * 0.30
).round(0).astype(int)  # ~30% of 0-14 are under 5 (Ghana DHS demographic structure)
master["Youth_dependency_ratio"] = (
    (master["Male Population 0-14"] + master["Female Population 0-14"]) /
    (master["Male Population 15-64"] + master["Female Population 15-64"])
).round(3)
master["Unemployment_rate_pct"] = (
    master["Unemployed Population"] /
    (master["Employed Population"] + master["Unemployed Population"]) * 100
).round(2)

# --------------------------------------------------------------------------- #
# STEP 4: District name reconciliation with GeoJSON (SPAT-006, EX-030)
# --------------------------------------------------------------------------- #
print("\n" + "=" * 70)
print("STEP 4: District name reconciliation (SPAT-006, EX-030)")
print("=" * 70)

with open(RAW / "Ghana_New_260_District.geojson") as fh:
    g = json.load(fh)
geo_districts = [(feat["properties"]["REGION"], feat["properties"]["DISTRICT"])
                 for feat in g["features"]]
geo_df = pd.DataFrame(geo_districts, columns=["GeoRegion", "GeoDistrict"])
print(f"GeoJSON: {len(geo_df)} features × 16 regions")

# Normalise both sides
def norm(s):
    return (s.strip().upper()
            .replace("-", " ")
            .replace("MUNICIPAL", "")
            .replace("METROPOLITAN", "")
            .replace("METROPOLIS", "")
            .replace(".", "")
            .replace(",", "")
            .replace("  ", " ")
            .strip())

master["District_key"] = master["District"].apply(norm)
geo_df["District_key"] = geo_df["GeoDistrict"].apply(norm)

direct_match = master["District_key"].isin(geo_df["District_key"]).sum()
print(f"Direct matches after normalisation: {direct_match} / {len(master)}")

# Build MANUAL_CORRECTIONS for the unmatched
unmatched_master = master[~master["District_key"].isin(geo_df["District_key"])]
unmatched_geo = geo_df[~geo_df["District_key"].isin(master["District_key"])]
print(f"Unmatched on MS side: {len(unmatched_master)}")
print(f"Unmatched on GeoJSON side: {len(unmatched_geo)}")

# Save the unmatched lists for manual review and correction
unmatched_master[["Region", "District", "District_key"]].to_csv(
    OUT_DATA / "district_unmatched_MS.csv", index=False)
unmatched_geo.to_csv(OUT_DATA / "district_unmatched_GeoJSON.csv", index=False)
print(f"\nUnmatched lists saved to:")
print(f"  {OUT_DATA / 'district_unmatched_MS.csv'}")
print(f"  {OUT_DATA / 'district_unmatched_GeoJSON.csv'}")

# --------------------------------------------------------------------------- #
# Save the provisional Master CSV (joined, pre-manual-correction)
# --------------------------------------------------------------------------- #
master.to_csv(OUT_DATA / "WASH_Ghana_District_Master_PROVISIONAL.csv", index=False)
print(f"\nProvisional Master CSV: {OUT_DATA / 'WASH_Ghana_District_Master_PROVISIONAL.csv'}")
print(f"  Shape: {master.shape}")
print(f"  Columns: {list(master.columns)}")

print("\n" + "=" * 70)
print("STAGE 2 PROVISIONAL BUILD COMPLETE")
print("=" * 70)
print(f"  Layer 1 (panel)         : {panel.shape}")
print(f"  Layer 2 (district pre-) : {master.shape}")
print(f"  Direct district matches  : {direct_match}/{len(master)}")
print(f"  Manual corrections needed: {len(unmatched_master)} MS-side, {len(unmatched_geo)} Geo-side")
print()
print("Next: build MANUAL_CORRECTIONS dict from the two unmatched lists, re-run.")
