"""
WASH Ghana — Stage 2 finalisation
Apply MANUAL_CORRECTIONS dict (EX-030 / SPAT-006) to reconcile 261 Master Sheet
districts with 260 GeoJSON features. Guan (261st, Oti) has no GeoJSON polygon and
is flagged for tabular-only inclusion.
"""

import os
import json
import pandas as pd
import numpy as np
from pathlib import Path

BASE_DIR = Path(os.path.dirname(os.path.abspath(__file__)))
RAW = BASE_DIR.parent / "data" / "raw"
OUT_DATA = BASE_DIR.parent / "outputs" / "data"

# --------------------------------------------------------------------------- #
# MANUAL_CORRECTIONS: Master Sheet district name → GeoJSON district name
# (EX-030, SPAT-006) — keyed by Master Sheet "District" column value
# --------------------------------------------------------------------------- #
MANUAL_CORRECTIONS = {
    # Ashanti
    "Akrofuom": "Adansi Akrofuom",
    "Bosomtwi": "Bosomtwe",
    "Kumasi Metropolitan Area (KMA)-Bantama, Manhyia North, Manhyia South, Nhyiaeso, & Subin": "Kumasi Metropolitan",
    "Sekyere Afram Plains": "Sekyere Afram Plains North",
    # Bono
    "Dormaa Central Municipal": "Dormaa Municipal",
    # Central
    "Assin Central Municipal": "Assin Fosu",
    "Awutu Senya West": "Awutu Senya",
    "Cape Cape Metropolitan Area (CCMA)-Cape Coast South & Cape Coast North": "Cape Coast Metropolitan",
    "Mfantsiman Municipal": "Mfantseman Municipal",
    "Twifo Ati Morkwa": "Twifo Atti-Morkwa",
    "Twifo Heman Lower Denkyira": "Twifo Hemang Lower Denkyira",
    # Eastern
    "Akwapim North Municipal": "Akwapem North",
    "Akwapim South Municipal": "Akwapem South",
    "Akyemansa": "Akyem Mansa",
    "Asene Manso Akroso": "Asene Akroso Manso",
    "Denkyembuor": "Denkyembour",
    "Lower Manya Krobo Municipal": "Lower Manya",
    "Upper Manya Krobo": "Upper Manya",
    # Greater Accra
    "Accra Metropolitan Area (AMA)-Ablekuma South, Ashiedu Keteke & Okaikoi South": "Accra Metropolis",
    "Adentan Municipal": "Adenta Municipal",
    "Ningo-Prampram": "Ningo/Prampram",
    "Okaikoi North Municipal": "Okaikwei North Municipal",
    "Tema Metropolitan Area (TMA)-Tema Central & Tema East": "Tema Metropolitan",
    # Northern
    "Sagnarigu Municipal": "Sagnerigu",
    "Tamale Metropolitan Area (TMA)-Tamale Central & Tamale South": "Tamale Metropolitan",
    # Oti — Guan is the 261st district; legacy GeoJSON omits it
    # No GeoJSON polygon for Guan: tabular-only inclusion, NOT mapped spatially
    "Nkwanta North (Kpassa)": "Nkwanta North",
    # Upper East
    "Bolgatanga East": "Bolga  East",
    "Kasena Nankana Municipal": "Kasena Nankana East",
    # Volta
    "Agortime-Ziope": "Agotime Ziope",
    # Western
    "Sekondi Takoradi Metropolitan Area (STMA)- Takoradi, Sekondi & Essikado-Ketan":
        "Sekondi Takoradi Metropolis",
}

GUAN_DISTRICT = "Guan"  # 261st district, Oti region; no GeoJSON polygon


def norm(s):
    """Aggressive name normalisation for matching."""
    if pd.isna(s):
        return s
    return (str(s).strip().upper()
            .replace("-", " ")
            .replace("/", " ")
            .replace("MUNICIPAL", "")
            .replace("METROPOLITAN", "")
            .replace("METROPOLIS", "")
            .replace(".", "")
            .replace(",", "")
            .replace("  ", " ")
            .replace("  ", " ")
            .strip())


# --------------------------------------------------------------------------- #
# Load provisional Master CSV and apply corrections
# --------------------------------------------------------------------------- #
master = pd.read_csv(OUT_DATA / "WASH_Ghana_District_Master_PROVISIONAL.csv")
print(f"Loaded provisional Master CSV: {master.shape}")
print(f"  Districts: {len(master)} | Expected: 261 (260 mapped + Guan)")

# Add a GeoJSON_District column starting with the original District name
master["GeoJSON_District"] = master["District"].copy()

# Apply manual corrections
correction_log = []
for ms_name, geo_name in MANUAL_CORRECTIONS.items():
    mask = master["District"] == ms_name
    if mask.sum() == 1:
        master.loc[mask, "GeoJSON_District"] = geo_name
        correction_log.append({
            "MS_District": ms_name,
            "GeoJSON_District": geo_name,
            "Region": master.loc[mask, "Region"].iloc[0],
            "Status": "MAPPED",
        })
    else:
        print(f"  WARN: '{ms_name}' matched {mask.sum()} rows (expected 1)")

# Flag Guan as the unmapped 261st district
guan_mask = master["District"] == GUAN_DISTRICT
if guan_mask.sum() == 1:
    master.loc[guan_mask, "GeoJSON_District"] = pd.NA
    correction_log.append({
        "MS_District": GUAN_DISTRICT,
        "GeoJSON_District": "NOT_IN_GEOJSON",
        "Region": "Oti",
        "Status": "TABULAR_ONLY (261st district; legacy GeoJSON omits)",
    })

# --------------------------------------------------------------------------- #
# Verify match against GeoJSON
# --------------------------------------------------------------------------- #
with open(RAW / "Ghana_New_260_District.geojson") as fh:
    g = json.load(fh)
geo_df = pd.DataFrame([
    (feat["properties"]["REGION"], feat["properties"]["DISTRICT"])
    for feat in g["features"]
], columns=["GeoRegion", "GeoDistrict"])
geo_df["Geo_key"] = geo_df["GeoDistrict"].apply(norm)

master["Match_key"] = master["GeoJSON_District"].apply(norm)
master["IsMapped"] = master["Match_key"].isin(geo_df["Geo_key"])

# Tabular total (should be 261)
n_tabular = len(master)
# Spatial total (should be 260)
n_spatial = master["IsMapped"].sum()

print(f"\nAfter MANUAL_CORRECTIONS application:")
print(f"  Tabular total: {n_tabular} (expected 261)")
print(f"  Spatial mapped: {n_spatial} (expected 260)")
print(f"  Tabular-only (Guan): {(~master['IsMapped']).sum()} (expected 1)")

if n_spatial != 260:
    unmatched = master[~master["IsMapped"]]
    print(f"\n  Still unmatched ({len(unmatched)}):")
    for _, r in unmatched.iterrows():
        print(f"    [{r['Region']}] MS='{r['District']}' → Match_key='{r['Match_key']}'")

# --------------------------------------------------------------------------- #
# Save corrections audit CSV
# --------------------------------------------------------------------------- #
audit = pd.DataFrame(correction_log)
audit.to_csv(OUT_DATA / "district_name_corrections.csv", index=False)
print(f"\nCorrections audit CSV saved: {OUT_DATA / 'district_name_corrections.csv'}")
print(f"  Total corrections logged: {len(audit)}")

# --------------------------------------------------------------------------- #
# Save final Master CSV
# --------------------------------------------------------------------------- #
# Add data source attribution columns (EX-003)
master.insert(3, "Data_Source_Demographics",
              "Ghana Statistical Service 2021 Census — Master Sheet.xlsx")
master.insert(4, "Data_Source_WASH",
              "DHS Ghana 1993–2022 subnational — water/toilet-facilities CSVs")
master.insert(5, "Data_Source_ChildHealth",
              "DHS Ghana 1988–2022 subnational — diarrhea/child-mortality-rates/iycf/anemia CSVs")

master.to_csv(OUT_DATA / "WASH_Ghana_District_Master.csv", index=False)
print(f"\nFinal Master CSV saved: {OUT_DATA / 'WASH_Ghana_District_Master.csv'}")
print(f"  Shape: {master.shape}")

# --------------------------------------------------------------------------- #
# Validation assertions (EX-016 — canonical values)
# --------------------------------------------------------------------------- #
print("\n" + "=" * 70)
print("STAGE 2 VALIDATION ASSERTIONS")
print("=" * 70)
assert len(master) == 261, f"FAIL: expected 261 districts, got {len(master)}"
assert master["IsMapped"].sum() == 260, f"FAIL: expected 260 mapped, got {master['IsMapped'].sum()}"
assert (~master["IsMapped"]).sum() == 1, "FAIL: expected exactly 1 unmapped (Guan)"
assert master.loc[guan_mask, "Region"].iloc[0] == "Oti", "FAIL: Guan should be in Oti"
assert master["Region"].nunique() == 16, "FAIL: expected 16 regions"
print("  ✓ 261 total districts in Master CSV")
print("  ✓ 260 mapped to GeoJSON polygons")
print("  ✓ 1 tabular-only (Guan, Oti region)")
print("  ✓ 16 regions present")
print("  ✓ All MANUAL_CORRECTIONS applied successfully")

print("\n" + "=" * 70)
print("STAGE 2 COMPLETE — Master CSV ready for spatial + ML analysis")
print("=" * 70)
