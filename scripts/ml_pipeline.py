"""
WASH Ghana — Stage 5 Task 13
ML pipeline with REGION-STRATIFIED LEAVE-ONE-REGION-OUT CV (ML-005 prevention)

Models:
  • Primary  : RandomForestRegressor (sklearn 1.7.2)
  • Secondary: GradientBoostingRegressor (sklearn 1.7.2)
  Stacked ensemble (EX-029) — XGBoost-free sklearn-only path

Outcome: U5MR_per_1000
Mediator-as-outcome (for downstream mediation): Diarrhoea_prevalence_pct

Random seed: 42 throughout (ML-002)
SHAP not available on this environment; using permutation-importance via
sklearn.inspection (acceptable substitute; document in Methods).
"""
import os
import sys
import json
import numpy as np
import pandas as pd
from pathlib import Path

sys.path.insert(0, "/tmp/pylib")
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.model_selection import LeaveOneGroupOut
from sklearn.inspection import permutation_importance
from sklearn.metrics import mean_squared_error, r2_score

SEED = 42
np.random.seed(SEED)

BASE_DIR = Path(os.path.dirname(os.path.abspath(__file__))).parent
OUT_DATA = BASE_DIR / "outputs" / "data"
OUT_TABLES = BASE_DIR / "outputs" / "tables"
OUT_TABLES.mkdir(parents=True, exist_ok=True)

# --------------------------------------------------------------------------- #
# Load Master CSV (mapped 260 districts only — spatial analyses subset)
# --------------------------------------------------------------------------- #
master = pd.read_csv(OUT_DATA / "WASH_Ghana_District_Master.csv")
master = master[master["IsMapped"]].copy().reset_index(drop=True)
print("=" * 78)
print("STAGE 5 TASK 13 — ML PIPELINE WITH REGION-STRATIFIED LOROCV")
print("=" * 78)
print(f"Analytical set: {len(master)} mapped districts")
print(f"Regions (LOROCV groups): {master['Region'].nunique()}")

# --------------------------------------------------------------------------- #
# Feature set
# --------------------------------------------------------------------------- #
# Primary exposures (WASH)
wash = ["Improved_water_pct", "Improved_sanitation_pct",
        "Open_defecation_pct", "Water_treated_pct"]
# Mediator
mediator = ["Diarrhoea_prevalence_pct"]
# Socioeconomic + demographic confounders (genuine district-level variation)
confounders = ["Incidence of Poverty", "Intensity of Poverty",
               "Illiteracy_rate_pct", "Uninsurance_rate_pct",
               "Unemployment_rate_pct", "Total Population",
               "Youth_dependency_ratio"]
# Mechanistic competing pathway
mech = ["EBF_within_1hr_pct", "Child_anaemia_any_pct"]

ALL_FEATURES = wash + mediator + confounders + mech
features_no_mediator = wash + confounders + mech  # for total-effect model
y_col = "U5MR_per_1000"

print(f"\nFeatures (total-effect model): {len(features_no_mediator)}")
for f in features_no_mediator:
    print(f"  • {f}")

X_total = master[features_no_mediator].values
X_full = master[ALL_FEATURES].values
y = master[y_col].values
groups = master["Region"].values

# --------------------------------------------------------------------------- #
# Train two models with region-stratified LOROCV
# --------------------------------------------------------------------------- #
def lorocv_evaluate(model_cls, model_name, X, y, groups, features, **kwargs):
    """LOROCV with mean ± SD reporting (STAT-007)."""
    logo = LeaveOneGroupOut()
    rmse_list = []
    r2_list = []
    fold_preds = np.zeros(len(y))
    fold_idx = np.zeros(len(y), dtype=int)
    print(f"\n[{model_name}] LOROCV across {len(np.unique(groups))} regions")
    print(f"  Hyperparameters: {kwargs}")
    for fi, (tr, te) in enumerate(logo.split(X, y, groups)):
        m = model_cls(random_state=SEED, **kwargs)
        m.fit(X[tr], y[tr])
        pred = m.predict(X[te])
        rmse = np.sqrt(mean_squared_error(y[te], pred))
        r2 = r2_score(y[te], pred) if len(te) > 1 else np.nan
        rmse_list.append(rmse)
        if not np.isnan(r2):
            r2_list.append(r2)
        fold_preds[te] = pred
        fold_idx[te] = fi
    rmse_arr = np.array(rmse_list)
    r2_arr = np.array(r2_list)
    print(f"  RMSE: {rmse_arr.mean():.3f} ± {rmse_arr.std(ddof=1):.3f}  (range {rmse_arr.min():.2f}–{rmse_arr.max():.2f})")
    print(f"  R²:   {r2_arr.mean():.3f} ± {r2_arr.std(ddof=1):.3f}  (range {r2_arr.min():.2f}–{r2_arr.max():.2f})")
    return {
        "Model": model_name,
        "N_folds": int(len(rmse_arr)),
        "RMSE_mean": round(rmse_arr.mean(), 3),
        "RMSE_SD": round(rmse_arr.std(ddof=1), 3),
        "R2_mean": round(r2_arr.mean(), 3),
        "R2_SD": round(r2_arr.std(ddof=1), 3),
        "R2_min": round(r2_arr.min(), 3),
        "R2_max": round(r2_arr.max(), 3),
        "fold_preds": fold_preds,
    }

# Train on TOTAL-EFFECT feature set (no mediator — for WASH→U5MR total effect)
rf_total = lorocv_evaluate(
    RandomForestRegressor, "RandomForest (total-effect)",
    X_total, y, groups, features_no_mediator,
    n_estimators=500, max_depth=8, min_samples_leaf=3, n_jobs=-1)

gb_total = lorocv_evaluate(
    GradientBoostingRegressor, "GradientBoosting (total-effect)",
    X_total, y, groups, features_no_mediator,
    n_estimators=300, max_depth=4, learning_rate=0.05, subsample=0.8)

# Train on FULL feature set (with diarrhoea mediator — for direct + indirect comparison)
rf_full = lorocv_evaluate(
    RandomForestRegressor, "RandomForest (full+mediator)",
    X_full, y, groups, ALL_FEATURES,
    n_estimators=500, max_depth=8, min_samples_leaf=3, n_jobs=-1)

gb_full = lorocv_evaluate(
    GradientBoostingRegressor, "GradientBoosting (full+mediator)",
    X_full, y, groups, ALL_FEATURES,
    n_estimators=300, max_depth=4, learning_rate=0.05, subsample=0.8)

# --------------------------------------------------------------------------- #
# Permutation importance — SHAP substitute (document in Methods)
# --------------------------------------------------------------------------- #
print("\n" + "=" * 78)
print("PERMUTATION IMPORTANCE (SHAP substitute on this environment)")
print("=" * 78)

# Train one final model on all data for global feature importance
m_final = RandomForestRegressor(n_estimators=500, max_depth=8,
                                min_samples_leaf=3, random_state=SEED, n_jobs=-1)
m_final.fit(X_full, y)
perm = permutation_importance(m_final, X_full, y, n_repeats=30,
                              random_state=SEED, n_jobs=-1)
imp_df = pd.DataFrame({
    "Feature": ALL_FEATURES,
    "PermImportance_mean": perm.importances_mean.round(4),
    "PermImportance_SD": perm.importances_std.round(4),
    "PermImportance_pct": (perm.importances_mean / perm.importances_mean.sum() * 100).round(2),
}).sort_values("PermImportance_mean", ascending=False)
print(imp_df.to_string(index=False))
imp_df.to_csv(OUT_TABLES / "permutation_importance.csv", index=False)

# Also Gini importance from RF (built-in)
gini_df = pd.DataFrame({
    "Feature": ALL_FEATURES,
    "Gini_importance": m_final.feature_importances_.round(4),
    "Gini_pct": (m_final.feature_importances_ / m_final.feature_importances_.sum() * 100).round(2),
}).sort_values("Gini_importance", ascending=False)
print("\n\nGini importance (RF built-in):")
print(gini_df.to_string(index=False))
gini_df.to_csv(OUT_TABLES / "rf_gini_importance.csv", index=False)

# --------------------------------------------------------------------------- #
# Stacked ensemble (EX-029) — RF + GB average prediction
# --------------------------------------------------------------------------- #
print("\n" + "=" * 78)
print("STACKED ENSEMBLE (EX-029) — RF + GB averaged predictions")
print("=" * 78)

stacked_total_preds = (rf_total["fold_preds"] + gb_total["fold_preds"]) / 2
rmse_stack = np.sqrt(mean_squared_error(y, stacked_total_preds))
r2_stack = r2_score(y, stacked_total_preds)
print(f"  Stacked total-effect: RMSE={rmse_stack:.3f}, R²={r2_stack:.3f}")

stacked_full_preds = (rf_full["fold_preds"] + gb_full["fold_preds"]) / 2
rmse_stack_full = np.sqrt(mean_squared_error(y, stacked_full_preds))
r2_stack_full = r2_score(y, stacked_full_preds)
print(f"  Stacked full+mediator: RMSE={rmse_stack_full:.3f}, R²={r2_stack_full:.3f}")

# --------------------------------------------------------------------------- #
# Save per-district fold predictions
# --------------------------------------------------------------------------- #
out = master[["Region", "District", "U5MR_per_1000"]].copy()
out["RF_LOROCV_pred"] = rf_total["fold_preds"]
out["GB_LOROCV_pred"] = gb_total["fold_preds"]
out["Stacked_LOROCV_pred"] = stacked_total_preds
out["RF_full_pred"] = rf_full["fold_preds"]
out["Stacked_full_pred"] = stacked_full_preds
out.to_csv(OUT_DATA / "ml_lorocv_predictions.csv", index=False)

# --------------------------------------------------------------------------- #
# Summary
# --------------------------------------------------------------------------- #
print("\n" + "=" * 78)
print("STAGE 5 TASK 13 — ML PIPELINE COMPLETE")
print("=" * 78)

summary = pd.DataFrame([
    {"Model": rf_total["Model"], "RMSE": f"{rf_total['RMSE_mean']:.3f} ± {rf_total['RMSE_SD']:.3f}",
     "R²": f"{rf_total['R2_mean']:.3f} ± {rf_total['R2_SD']:.3f}"},
    {"Model": gb_total["Model"], "RMSE": f"{gb_total['RMSE_mean']:.3f} ± {gb_total['RMSE_SD']:.3f}",
     "R²": f"{gb_total['R2_mean']:.3f} ± {gb_total['R2_SD']:.3f}"},
    {"Model": "Stacked (total-effect)", "RMSE": f"{rmse_stack:.3f}", "R²": f"{r2_stack:.3f}"},
    {"Model": rf_full["Model"], "RMSE": f"{rf_full['RMSE_mean']:.3f} ± {rf_full['RMSE_SD']:.3f}",
     "R²": f"{rf_full['R2_mean']:.3f} ± {rf_full['R2_SD']:.3f}"},
    {"Model": gb_full["Model"], "RMSE": f"{gb_full['RMSE_mean']:.3f} ± {gb_full['RMSE_SD']:.3f}",
     "R²": f"{gb_full['R2_mean']:.3f} ± {gb_full['R2_SD']:.3f}"},
    {"Model": "Stacked (full+mediator)", "RMSE": f"{rmse_stack_full:.3f}", "R²": f"{r2_stack_full:.3f}"},
])
print("\n" + summary.to_string(index=False))
summary.to_csv(OUT_TABLES / "ml_model_comparison.csv", index=False)

print(f"\nTop-5 features by permutation importance:")
print(imp_df.head(5)[["Feature", "PermImportance_mean", "PermImportance_pct"]].to_string(index=False))

print("\nALL ML OUTPUTS SAVED. ML-005 prevention applied — LOROCV not k-fold.")
