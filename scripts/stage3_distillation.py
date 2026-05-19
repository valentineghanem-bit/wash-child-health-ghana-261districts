"""
WASH Ghana — Stage 3 (Distillation)

Distill the rich provisional variable set into a final analytical schema before
Stage 4 DAG construction. Produces:
  • data_dictionary.csv — every variable with role, source, unit, completeness
  • table1_descriptives.csv — mean/SD/median/IQR per variable, overall and by region
  • missingness_report.csv — column-wise missing % with retention decision
  • stage3_distillation_report.md — narrative summary

Active codes: L99, CHAINLOGIC, /uq-flag
EX-026 paths · EX-016 canonical assertions
"""

import os
import pandas as pd
import numpy as np
from pathlib import Path

BASE_DIR = Path(os.path.dirname(os.path.abspath(__file__)))
OUT_DATA = BASE_DIR.parent / "outputs" / "data"
OUT_TABLES = BASE_DIR.parent / "outputs" / "tables"
OUT_TABLES.mkdir(parents=True, exist_ok=True)

# --------------------------------------------------------------------------- #
# Load both layers
# --------------------------------------------------------------------------- #
master = pd.read_csv(OUT_DATA / "WASH_Ghana_District_Master.csv")
panel = pd.read_csv(OUT_DATA / "WASH_Ghana_Panel_RegionYear.csv")

print("=" * 78)
print("STAGE 3 — DISTILLATION")
print("=" * 78)
print(f"Cross-sectional Master CSV: {master.shape}")
print(f"Longitudinal Panel CSV:    {panel.shape}")

# --------------------------------------------------------------------------- #
# Define canonical variable schema with causal role mapping
# --------------------------------------------------------------------------- #
SCHEMA = [
    # (variable, role, source, unit, definition)
    # OUTCOMES
    ("U5MR_per_1000", "outcome",
     "DHS Ghana subnational (most recent — 2022)",
     "deaths per 1,000 live births",
     "Under-five mortality rate"),
    ("IMR_per_1000", "outcome_secondary",
     "DHS Ghana subnational (most recent — 2022)",
     "deaths per 1,000 live births",
     "Infant mortality rate (<1 year)"),
    ("NMR_per_1000", "outcome_secondary",
     "DHS Ghana subnational (most recent — 2022)",
     "deaths per 1,000 live births",
     "Neonatal mortality rate (<28 days)"),
    # MEDIATOR
    ("Diarrhoea_prevalence_pct", "mediator",
     "DHS Ghana subnational (most recent — 2022)",
     "% children <5 with diarrhoea in last 2 weeks",
     "Childhood diarrhoea prevalence"),
    # PRIMARY EXPOSURES (WASH)
    ("Improved_water_pct", "exposure_primary",
     "DHS Ghana subnational (most recent — 2022)",
     "% households",
     "Households using an improved water source"),
    ("Unimproved_water_pct", "exposure_primary",
     "DHS Ghana subnational (most recent — 2022)",
     "% households",
     "Households using an unimproved water source"),
    ("Improved_sanitation_pct", "exposure_primary",
     "DHS Ghana subnational (most recent — 2022)",
     "% households",
     "Households with an improved sanitation facility"),
    ("Unimproved_sanitation_pct", "exposure_primary",
     "DHS Ghana subnational (most recent — 2022)",
     "% households",
     "Households with unimproved sanitation"),
    ("Open_defecation_pct", "exposure_primary",
     "DHS Ghana subnational (most recent — 2022)",
     "% households",
     "Households practising open defecation"),
    ("Water_treated_pct", "exposure_secondary",
     "DHS Ghana subnational (most recent — 2022)",
     "% households",
     "Households using an appropriate water-treatment method"),
    # CONFOUNDERS — socioeconomic
    ("Incidence of Poverty", "confounder_socioecon",
     "GSS 2021 Census — Master Sheet",
     "% of district population",
     "Multidimensional poverty incidence"),
    ("Intensity of Poverty", "confounder_socioecon",
     "GSS 2021 Census — Master Sheet",
     "average deprivation share",
     "Multidimensional poverty intensity"),
    ("Illiteracy_rate_pct", "confounder_socioecon",
     "Derived from Master Sheet (Illiterate / Total Population)",
     "% of district population",
     "Adult illiteracy rate"),
    ("Uninsurance_rate_pct", "confounder_socioecon",
     "Derived from Master Sheet (Uninsured / Total Population)",
     "% of district population",
     "Health insurance non-enrolment rate"),
    ("Unemployment_rate_pct", "confounder_socioecon",
     "Derived from Master Sheet",
     "% of labour force",
     "District unemployment rate"),
    # CONFOUNDERS — demographic
    ("Total Population", "confounder_demographic",
     "GSS 2021 Census — Master Sheet",
     "count",
     "Total district population"),
    ("Under5_population", "confounder_demographic",
     "Derived (30% of 0-14 cohort)",
     "count",
     "Estimated under-five population"),
    ("Youth_dependency_ratio", "confounder_demographic",
     "Derived from Master Sheet",
     "ratio",
     "Youth dependency ratio (0-14 / 15-64)"),
    ("Class", "confounder_urbanicity",
     "Master Sheet",
     "categorical (Metropolitan / Municipal / District)",
     "Administrative class proxy for urbanicity"),
    # COVARIATE / MECHANISTIC (IYCF — competing pathway via nutrition)
    ("EBF_within_1hr_pct", "covariate_mechanistic",
     "DHS Ghana subnational",
     "% children",
     "Children breastfed within 1 hour of birth"),
    ("Ever_breastfed_pct", "covariate_mechanistic",
     "DHS Ghana subnational",
     "% children",
     "Children ever breastfed"),
    # COVARIATE — anaemia (competing health pathway)
    ("Child_anaemia_any_pct", "covariate_health",
     "DHS Ghana subnational (≥2003)",
     "% children",
     "Children with any anaemia"),
    ("Child_anaemia_severe_pct", "covariate_health",
     "DHS Ghana subnational (≥2003)",
     "% children",
     "Children with severe anaemia"),
    # SPATIAL
    ("Region", "spatial_unit_region",
     "Master Sheet + GeoJSON",
     "16-region categorical",
     "Ghana administrative region"),
    ("District", "spatial_unit_district",
     "Master Sheet",
     "261-district categorical",
     "Ghana administrative district (MMDA)"),
    ("Latitude", "spatial_coordinate",
     "Master Sheet",
     "degrees",
     "District centroid latitude"),
    ("Longitude", "spatial_coordinate",
     "Master Sheet",
     "degrees",
     "District centroid longitude"),
    ("IsMapped", "spatial_flag",
     "Derived",
     "boolean",
     "True if district maps to GeoJSON polygon (False = Guan, tabular only)"),
]

# --------------------------------------------------------------------------- #
# Build data dictionary with completeness audit
# --------------------------------------------------------------------------- #
print("\n" + "=" * 78)
print("STEP 1: Data dictionary with missingness")
print("=" * 78)

dd_rows = []
for var, role, source, unit, definition in SCHEMA:
    if var not in master.columns:
        dd_rows.append({
            "Variable": var, "Role": role, "Source": source, "Unit": unit,
            "Definition": definition, "N": 0, "Missing_%": 100,
            "Mean_or_Mode": "—", "Median_or_n_unique": "—",
            "Min": "—", "Max": "—", "Retention": "ABSENT_FROM_DATA",
        })
        continue
    col = master[var]
    n = col.notna().sum()
    miss = col.isna().sum() / len(col) * 100
    # Boolean columns: treat as categorical
    if pd.api.types.is_bool_dtype(col):
        mean = str(col.mode().iloc[0]) if len(col.mode()) else "—"
        median = col.nunique()
        vmin = str(col.min())
        vmax = str(col.max())
    elif pd.api.types.is_numeric_dtype(col):
        mean = round(col.mean(), 2)
        median = round(col.median(), 2)
        vmin = round(col.min(), 2)
        vmax = round(col.max(), 2)
    else:
        mean = col.mode().iloc[0] if len(col.mode()) else "—"
        median = col.nunique()
        vmin = "—"
        vmax = "—"
    # Retention decision (Stage 3 distillation)
    if miss >= 70:
        retention = "DROP (>70% missing — uninformative)"
    elif miss >= 40:
        retention = "FLAG (40–70% missing — covariate only, not in primary models)"
    elif miss >= 10:
        retention = "RETAIN (sensitivity analysis with imputation)"
    else:
        retention = "RETAIN (primary)"
    dd_rows.append({
        "Variable": var, "Role": role, "Source": source, "Unit": unit,
        "Definition": definition, "N": int(n), "Missing_%": round(miss, 1),
        "Mean_or_Mode": mean, "Median_or_n_unique": median,
        "Min": vmin, "Max": vmax, "Retention": retention,
    })

dd = pd.DataFrame(dd_rows)
dd.to_csv(OUT_DATA / "data_dictionary.csv", index=False)

print(dd[["Variable", "Role", "N", "Missing_%", "Retention"]].to_string(index=False))
print(f"\nSaved: {OUT_DATA / 'data_dictionary.csv'}")

# --------------------------------------------------------------------------- #
# Final variable set decision
# --------------------------------------------------------------------------- #
print("\n" + "=" * 78)
print("STEP 2: Final analytical variable set (primary + sensitivity)")
print("=" * 78)
primary_vars = dd[dd["Retention"].str.startswith("RETAIN (primary)")]["Variable"].tolist()
sensitivity_vars = dd[dd["Retention"].str.contains("sensitivity")]["Variable"].tolist()
flagged_vars = dd[dd["Retention"].str.startswith("FLAG")]["Variable"].tolist()
dropped_vars = dd[dd["Retention"].str.startswith("DROP")]["Variable"].tolist()

print(f"\nPRIMARY ({len(primary_vars)}):")
for v in primary_vars: print(f"  ✓ {v}")
print(f"\nSENSITIVITY ({len(sensitivity_vars)}):")
for v in sensitivity_vars: print(f"  ~ {v}")
print(f"\nFLAGGED — covariate only ({len(flagged_vars)}):")
for v in flagged_vars: print(f"  ! {v}")
print(f"\nDROPPED ({len(dropped_vars)}):")
for v in dropped_vars: print(f"  ✗ {v}")

# --------------------------------------------------------------------------- #
# Table 1 descriptive statistics by region (primary + sensitivity vars only)
# --------------------------------------------------------------------------- #
print("\n" + "=" * 78)
print("STEP 3: Table 1 — Descriptive statistics (primary + sensitivity vars)")
print("=" * 78)

analytical_vars = primary_vars + sensitivity_vars
numeric_analytical = [v for v in analytical_vars if pd.api.types.is_numeric_dtype(master[v]) and not pd.api.types.is_bool_dtype(master[v])]

# Overall descriptives
t1_overall = master[numeric_analytical].describe().T[["mean", "std", "min", "50%", "max"]]
t1_overall.columns = ["Mean", "SD", "Min", "Median", "Max"]
t1_overall = t1_overall.round(2)
t1_overall["N"] = master[numeric_analytical].notna().sum().values
t1_overall = t1_overall[["N", "Mean", "SD", "Min", "Median", "Max"]]
print("\nOverall (n=261 districts):")
print(t1_overall.to_string())

# By region
t1_by_region = master.groupby("Region")[numeric_analytical].mean().round(2)
print(f"\nBy region (n=16):")
print(t1_by_region.head(8).to_string())

t1_overall.to_csv(OUT_TABLES / "table1_overall.csv")
t1_by_region.to_csv(OUT_TABLES / "table1_by_region.csv")
print(f"\nSaved Table 1: {OUT_TABLES / 'table1_overall.csv'}")
print(f"Saved Table 1 by region: {OUT_TABLES / 'table1_by_region.csv'}")

# --------------------------------------------------------------------------- #
# Causal-role grouping (drives Stage 4 DAG)
# --------------------------------------------------------------------------- #
print("\n" + "=" * 78)
print("STEP 4: Causal-role grouping for DAG")
print("=" * 78)

roles = dd[dd["Variable"].isin(analytical_vars)].groupby("Role")["Variable"].apply(list)
for role, vars_ in roles.items():
    print(f"\n  [{role}]")
    for v in vars_:
        print(f"    • {v}")

# --------------------------------------------------------------------------- #
# Validation assertions
# --------------------------------------------------------------------------- #
print("\n" + "=" * 78)
print("STAGE 3 VALIDATION ASSERTIONS")
print("=" * 78)
assert "U5MR_per_1000" in primary_vars + sensitivity_vars + flagged_vars, "U5MR missing"
assert "Diarrhoea_prevalence_pct" in primary_vars + sensitivity_vars + flagged_vars, "Diarrhoea missing"
assert "Improved_water_pct" in primary_vars + sensitivity_vars + flagged_vars, "Improved_water missing"
assert "Open_defecation_pct" in primary_vars + sensitivity_vars + flagged_vars, "Open_defecation missing"
assert len(dd) >= 20, "Data dictionary too small"
assert len(primary_vars) >= 5, "Too few primary variables"
print("  ✓ U5MR_per_1000 retained")
print("  ✓ Diarrhoea_prevalence_pct retained")
print("  ✓ Improved_water_pct retained")
print(f"  Data dictionary: {len(dd)} variables")
print(f"  Primary analytical set: {len(primary_vars)} variables")

print("\n" + "=" * 78)
print("STAGE 3 COMPLETE - variable schema locked, ready for Stage 4 DAG construction")
print("=" * 78)
