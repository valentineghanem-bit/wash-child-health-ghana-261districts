"""
WASH Ghana — Canonical-value pytest suite (EX-016)

Asserts that the Master CSV and Panel CSV match the canonical values from
Stage 3 Table 1. Run before every QA iteration to catch silent value drift.

Pinned to:
  • WASH_Ghana_District_Master.csv (261 × 44)
  • WASH_Ghana_Panel_RegionYear.csv (87 × 16)
"""
import os
import pytest
import pandas as pd
import numpy as np
from pathlib import Path

BASE_DIR = Path(os.path.dirname(os.path.abspath(__file__))).parent
DATA = BASE_DIR / "outputs" / "data"


@pytest.fixture(scope="module")
def master():
    df = pd.read_csv(DATA / "WASH_Ghana_District_Master.csv")
    return df


@pytest.fixture(scope="module")
def panel():
    df = pd.read_csv(DATA / "WASH_Ghana_Panel_RegionYear.csv")
    return df


# --------------------------------------------------------------------------- #
# STRUCTURAL ASSERTIONS
# --------------------------------------------------------------------------- #

def test_master_shape(master):
    """Master CSV is 261 districts × 44 columns."""
    assert master.shape == (261, 44), f"Master shape mismatch: {master.shape}"


def test_master_district_count(master):
    """All 261 districts present (260 mapped + Guan tabular-only)."""
    assert len(master) == 261
    assert master["IsMapped"].sum() == 260
    assert (~master["IsMapped"]).sum() == 1


def test_guan_is_tabular_only(master):
    """Guan in Oti is the 261st district, IsMapped=False."""
    guan = master[master["District"] == "Guan"]
    assert len(guan) == 1
    assert guan["Region"].iloc[0] == "Oti"
    assert guan["IsMapped"].iloc[0] == False


def test_master_region_count(master):
    """16 administrative regions."""
    assert master["Region"].nunique() == 16


def test_panel_shape(panel):
    """Panel CSV is 87 region-years × 16 columns."""
    assert panel.shape == (87, 16), f"Panel shape: {panel.shape}"


def test_panel_regions_are_10(panel):
    """Panel uses 10 pre-2018 regions."""
    assert panel["Region"].nunique() == 10


def test_panel_year_range(panel):
    """Panel covers 1988–2022 DHS rounds."""
    assert panel["Year"].min() == 1988
    assert panel["Year"].max() == 2022


# --------------------------------------------------------------------------- #
# CANONICAL VALUE ASSERTIONS (from Stage 3 Table 1)
# --------------------------------------------------------------------------- #

def test_u5mr_range(master):
    """U5MR district range: 20 (Greater Accra) to 72 (Northern). Mean = 43.15."""
    assert master["U5MR_per_1000"].min() == 20
    assert master["U5MR_per_1000"].max() == 72
    assert 40 < master["U5MR_per_1000"].mean() < 44


def test_diarrhoea_range(master):
    """Diarrhoea prevalence district range: 4.9% to 22.0%."""
    assert master["Diarrhoea_prevalence_pct"].min() == 4.9
    assert master["Diarrhoea_prevalence_pct"].max() == 22.0


def test_improved_water_range(master):
    """Improved water coverage: 59.3% (North East) to 98.5% (Greater Accra)."""
    assert master["Improved_water_pct"].min() == 59.3
    assert master["Improved_water_pct"].max() == 98.5


def test_open_defecation_range(master):
    """Open defecation district range: 5% (Greater Accra) to 71.1% (North East/Northern)."""
    assert master["Open_defecation_pct"].min() == 5.0
    assert master["Open_defecation_pct"].max() == 71.1


def test_improved_sanitation_range(master):
    """Improved sanitation: 21.9% (North East) to 91.4% (Greater Accra)."""
    assert master["Improved_sanitation_pct"].min() == 21.9
    assert master["Improved_sanitation_pct"].max() == 91.4


def test_greater_accra_low_burden(master):
    """Greater Accra is the low-burden region by Stage 3 Table 1."""
    gar = master[master["Region"] == "Greater Accra"]
    assert gar["U5MR_per_1000"].mean() < 25
    assert gar["Improved_water_pct"].mean() > 95
    assert gar["Open_defecation_pct"].mean() < 10


def test_north_east_high_burden(master):
    """North East is the high-burden region by Stage 3 Table 1."""
    ne = master[master["Region"] == "North East"]
    assert ne["Open_defecation_pct"].mean() > 60
    assert ne["Child_anaemia_any_pct"].mean() > 60
    assert ne["Illiteracy_rate_pct"].mean() > 45


def test_data_source_columns_present(master):
    """Data source attribution columns present per EX-003."""
    assert "Data_Source_Demographics" in master.columns
    assert "Data_Source_WASH" in master.columns
    assert "Data_Source_ChildHealth" in master.columns


def test_no_data_source_nulls(master):
    """Data source attribution columns are fully populated."""
    for col in ["Data_Source_Demographics", "Data_Source_WASH", "Data_Source_ChildHealth"]:
        assert master[col].notna().all(), f"{col} has nulls"


def test_master_primary_vars_complete(master):
    """All primary analytical variables have 0% missingness (per Stage 3 finding)."""
    primary = [
        "U5MR_per_1000", "Diarrhoea_prevalence_pct",
        "Improved_water_pct", "Open_defecation_pct",
        "Improved_sanitation_pct", "Incidence of Poverty",
        "Illiteracy_rate_pct", "Total Population",
    ]
    for v in primary:
        assert master[v].notna().all(), f"{v} has missing values"


def test_panel_year_count(panel):
    """Panel has 9 DHS rounds × 10 regions ≈ 87 region-years (some indicators missing pre-2003 anaemia)."""
    n_years = panel["Year"].nunique()
    assert n_year