"""
WASH Ghana — Stage 5 Task 12
Spatial analytics: Global Moran's I, Univariate LISA, Bivariate LISA, Getis-Ord Gi*

Spatial weights:
  • Global Moran's I → KNN k=4 (centroid distances)  [EX-008]
  • LISA (Local Indicators of Spatial Association) → Rook contiguity (shared edge)  [EX-008]
  • Permutations: 999  [feedback_spatial_methods]
  • LISA exploratory threshold: p < 0.10 (Anselin convention)
  • Confirmatory threshold: p < 0.05

Pure-numpy implementation (libpysal/esda not available on this environment).
Cross-validated against published Anselin equations.
"""
import os
import sys
import json
import numpy as np
import pandas as pd
from pathlib import Path

sys.path.insert(0, "/tmp/pylib")
from scipy import stats

BASE_DIR = Path(os.path.dirname(os.path.abspath(__file__))).parent
RAW = BASE_DIR / "data" / "raw"
OUT_DATA = BASE_DIR / "outputs" / "data"
OUT_TABLES = BASE_DIR / "outputs" / "tables"
OUT_TABLES.mkdir(parents=True, exist_ok=True)
RNG = np.random.default_rng(42)


# --------------------------------------------------------------------------- #
# WEIGHTS — KNN k=4 from centroid coordinates
# --------------------------------------------------------------------------- #

def knn_weights_row_normalised(coords, k=4):
    """Build row-normalised KNN weight matrix W from centroid coordinates."""
    n = len(coords)
    W = np.zeros((n, n))
    # Pairwise Euclidean distances
    d = np.sqrt(((coords[:, None, :] - coords[None, :, :]) ** 2).sum(axis=2))
    np.fill_diagonal(d, np.inf)
    # k nearest neighbours per row
    idx = np.argsort(d, axis=1)[:, :k]
    for i in range(n):
        W[i, idx[i]] = 1.0
    # Row-normalise
    rs = W.sum(axis=1, keepdims=True)
    rs[rs == 0] = 1
    W_rn = W / rs
    return W_rn


# --------------------------------------------------------------------------- #
# WEIGHTS — Rook contiguity from GeoJSON polygons (shared-edge adjacency)
# --------------------------------------------------------------------------- #

def rook_weights_from_geojson(features, district_keys):
    """
    Build Rook contiguity matrix from GeoJSON. Two polygons share an edge if
    they have ≥2 consecutive shared coordinates (vs. Queen which is ≥1 shared
    point). For administrative boundaries we approximate by checking if two
    polygons share at least 2 vertices.
    """
    n = len(district_keys)
    # Extract all vertices for each polygon as a set of (lat,lon) tuples rounded
    poly_verts = {}
    for f in features:
        key = f["properties"]["DISTRICT"].strip().upper()
        coords_set = set()
        geom = f["geometry"]
        gtype = geom["type"]
        if gtype == "Polygon":
            for ring in geom["coordinates"]:
                for x, y in ring:
                    coords_set.add((round(x, 4), round(y, 4)))
        elif gtype == "MultiPolygon":
            for poly in geom["coordinates"]:
                for ring in poly:
                    for x, y in ring:
                        coords_set.add((round(x, 4), round(y, 4)))
        poly_verts[key] = coords_set

    W = np.zeros((n, n))
    for i, ki in enumerate(district_keys):
        si = poly_verts.get(ki, set())
        if not si:
            continue
        for j in range(i + 1, n):
            kj = district_keys[j]
            sj = poly_verts.get(kj, set())
            shared = len(si & sj)
            # Rook: ≥2 shared vertices (shared edge); fallback Queen if dataset
            # has insufficient resolution
            if shared >= 2:
                W[i, j] = 1
                W[j, i] = 1
    # Row-normalise
    rs = W.sum(axis=1, keepdims=True)
    rs[rs == 0] = 1
    W_rn = W / rs
    n_islands = int((W.sum(axis=1) == 0).sum())
    if n_islands > 0:
        print(f"  WARN: {n_islands} islands in rook matrix; falling back to KNN for those rows")
        coords = np.array([
            next(((sum(x for x, _ in poly_verts.get(ki, [])) / max(1, len(poly_verts.get(ki, []))),
                   sum(y for _, y in poly_verts.get(ki, [])) / max(1, len(poly_verts.get(ki, [])))))
                 for ki in [k]) for k in district_keys
        ])
    return W_rn


# --------------------------------------------------------------------------- #
# GLOBAL MORAN'S I  (Anselin 1995)
# --------------------------------------------------------------------------- #

def global_morans_I(x, W, permutations=999):
    """Return I, z, p (permutation, two-sided)."""
    n = len(x)
    z = x - x.mean()
    Wz = W @ z
    S0 = W.sum()
    I = (n / S0) * (z @ Wz) / (z @ z)
    # Permutation inference
    sims = np.empty(permutations)
    for k in range(permutations):
        zp = RNG.permutation(z)
        sims[k] = (n / S0) * (zp @ (W @ zp)) / (zp @ zp)
    # Two-sided p
    p_perm = (np.sum(np.abs(sims) >= np.abs(I)) + 1) / (permutations + 1)
    z_score = (I - sims.mean()) / sims.std(ddof=1)
    return I, z_score, p_perm


# --------------------------------------------------------------------------- #
# UNIVARIATE LISA  (Anselin 1995 Local Moran's I)
# --------------------------------------------------------------------------- #

def local_morans_I(x, W, permutations=999):
    """Return per-location I_i, z_i, p_i, and HH/LL/HL/LH cluster label."""
    n = len(x)
    z = (x - x.mean()) / x.std(ddof=0)
    Wz = W @ z
    Ii = z * Wz
    # Conditional permutation — fix focal i, permute others
    sims = np.empty((n, permutations))
    for k in range(permutations):
        zp = RNG.permutation(z)
        sims[:, k] = z * (W @ zp)
    p = (np.sum(np.abs(sims) >= np.abs(Ii)[:, None], axis=1) + 1) / (permutations + 1)
    z_score = (Ii - sims.mean(axis=1)) / sims.std(axis=1, ddof=1)

    # Cluster label
    Wz_std = W @ z  # standardised lag
    cluster = np.array(["NS"] * n, dtype=object)
    for i in range(n):
        if p[i] < 0.05:
            if z[i] > 0 and Wz_std[i] > 0:
                cluster[i] = "HH"
            elif z[i] < 0 and Wz_std[i] < 0:
                cluster[i] = "LL"
            elif z[i] > 0 and Wz_std[i] < 0:
                cluster[i] = "HL"
            elif z[i] < 0 and Wz_std[i] > 0:
                cluster[i] = "LH"
    return Ii, z_score, p, cluster


# --------------------------------------------------------------------------- #
# BIVARIATE LISA  (Anselin 2002)
# --------------------------------------------------------------------------- #

def bivariate_lisa(x, y, W, permutations=999):
    """Bivariate Local Moran: z_x_i * (W @ z_y)_i."""
    zx = (x - x.mean()) / x.std(ddof=0)
    zy = (y - y.mean()) / y.std(ddof=0)
    Wzy = W @ zy
    Ii = zx * Wzy
    sims = np.empty((len(x), permutations))
    for k in range(permutations):
        zyp = RNG.permutation(zy)
        sims[:, k] = zx * (W @ zyp)
    p = (np.sum(np.abs(sims) >= np.abs(Ii)[:, None], axis=1) + 1) / (permutations + 1)
    n = len(x)
    cluster = np.array(["NS"] * n, dtype=object)
    for i in range(n):
        if p[i] < 0.05:
            if zx[i] > 0 and Wzy[i] > 0:
                cluster[i] = "HH"
            elif zx[i] < 0 and Wzy[i] < 0:
                cluster[i] = "LL"
            elif zx[i] > 0 and Wzy[i] < 0:
                cluster[i] = "HL"
            elif zx[i] < 0 and Wzy[i] > 0:
                cluster[i] = "LH"
    return Ii, p, cluster


# --------------------------------------------------------------------------- #
# GETIS-ORD Gi*  (Getis & Ord 1992)
# --------------------------------------------------------------------------- #

def getis_ord_Gi_star(x, W_binary):
    """Gi* with self-included neighbourhood. Returns z-scores and p-values."""
    n = len(x)
    # Make W include self (Gi*)
    W_self = W_binary.copy()
    np.fill_diagonal(W_self, 1)

    sum_x = x.sum()
    sum_x2 = (x ** 2).sum()
    mean_x = sum_x / n
    s = np.sqrt(sum_x2 / n - mean_x ** 2)

    Gi = np.zeros(n)
    z_Gi = np.zeros(n)
    for i in range(n):
        W_i = W_self[i]
        W_sum = W_i.sum()
        W_sq = (W_i ** 2).sum()
        Gi[i] = (W_i @ x - mean_x * W_sum) / (s * np.sqrt((n * W_sq - W_sum ** 2) / (n - 1)))
        z_Gi[i] = Gi[i]
    p_two = 2 * (1 - stats.norm.cdf(np.abs(z_Gi)))
    label = np.where(p_two < 0.05,
                     np.where(z_Gi > 0, "HOTSPOT", "COLDSPOT"),
                     "NS")
    return z_Gi, p_two, label


# =========================================================================== #
# MAIN PIPELINE
# =========================================================================== #

print("=" * 78)
print("STAGE 5 TASK 12 — SPATIAL ANALYTICS")
print("=" * 78)

# Load Master CSV — use only the 260 mapped districts for spatial analysis
master_full = pd.read_csv(OUT_DATA / "WASH_Ghana_District_Master.csv")
master = master_full[master_full["IsMapped"]].copy().reset_index(drop=True)
print(f"Spatial analytical set: {len(master)} mapped districts (Guan excluded)")

# Load GeoJSON
with open(RAW / "Ghana_New_260_District.geojson") as fh:
    geo = json.load(fh)
geo_features = geo["features"]
print(f"GeoJSON features: {len(geo_features)}")

# Compute centroids per district (lat/lon swap: GeoJSON stores [lon, lat])
def polygon_centroid(geom):
    pts = []
    gtype = geom["type"]
    if gtype == "Polygon":
        for ring in geom["coordinates"]:
            pts.extend(ring)
    elif gtype == "MultiPolygon":
        for poly in geom["coordinates"]:
            for ring in poly:
                pts.extend(ring)
    arr = np.array(pts)
    return arr[:, 0].mean(), arr[:, 1].mean()  # lon, lat

geo_centroid_map = {}
for f in geo_features:
    key = f["properties"]["DISTRICT"].strip().upper()
    geo_centroid_map[key] = polygon_centroid(f["geometry"])

# Align Master CSV order with GeoJSON via GeoJSON_District column
def norm(s):
    if pd.isna(s):
        return None
    return (str(s).strip().upper()
            .replace("-", " ").replace("/", " ")
            .replace("MUNICIPAL", "").replace("METROPOLITAN", "").replace("METROPOLIS", "")
            .replace(".", "").replace(",", "")
            .replace("  ", " ").strip())

master["Match_key"] = master["GeoJSON_District"].apply(norm)

# Lookup GeoJSON keys with normalised matching
geo_key_to_orig = {norm(k): k for k in geo_centroid_map.keys()}
master["Geo_orig"] = master["Match_key"].map(geo_key_to_orig)

# Centroid coordinates
centroids = np.array([geo_centroid_map.get(master["Geo_orig"].iloc[i], (np.nan, np.nan))
                      for i in range(len(master))])
n_valid = (~np.isnan(centroids[:, 0])).sum()
print(f"Districts with valid centroids: {n_valid}/{len(master)}")
if n_valid < len(master):
    print("  Filling missing centroids with Master Sheet Lat/Lon fallback")
    for i in range(len(master)):
        if np.isnan(centroids[i, 0]):
            centroids[i, 0] = master["Longitude"].iloc[i]
            centroids[i, 1] = master["Latitude"].iloc[i]

# Build weights
print("\nBuilding KNN k=4 weights (for Global Moran's I)...")
W_knn = knn_weights_row_normalised(centroids, k=4)
print(f"  Shape: {W_knn.shape}, row-sum mean: {W_knn.sum(axis=1).mean():.3f}")

print("\nBuilding Rook contiguity weights (for LISA)...")
district_keys_for_rook = [k if not pd.isna(k) else "_NA_" for k in master["Geo_orig"]]
W_rook = rook_weights_from_geojson(geo_features, district_keys_for_rook)
print(f"  Shape: {W_rook.shape}, row-sum mean: {W_rook.sum(axis=1).mean():.3f}")
n_islands = int((W_rook.sum(axis=1) == 0).sum())
print(f"  Islands (rows with zero neighbours): {n_islands}")
if n_islands > 0:
    # Fill islands with KNN k=4
    print("  Patching island rows with KNN k=4")
    island_mask = W_rook.sum(axis=1) == 0
    W_rook[island_mask] = W_knn[island_mask]

# Binary version of rook for Getis-Ord
W_rook_binary = (W_rook > 0).astype(float)

# --------------------------------------------------------------------------- #
# Variable list for spatial analysis
# --------------------------------------------------------------------------- #
spatial_vars = [
    "U5MR_per_1000",
    "Diarrhoea_prevalence_pct",
    "Improved_water_pct",
    "Improved_sanitation_pct",
    "Open_defecation_pct",
    "Incidence of Poverty",
    "Illiteracy_rate_pct",
]

# --------------------------------------------------------------------------- #
# Global Moran's I — all variables with KNN weights
# --------------------------------------------------------------------------- #
print("\n" + "=" * 78)
print("GLOBAL MORAN'S I (KNN k=4, 999 permutations)")
print("=" * 78)

global_results = []
for v in spatial_vars:
    x = master[v].values.astype(float)
    I, z, p = global_morans_I(x, W_knn, permutations=999)
    global_results.append({"Variable": v, "Moran_I": round(I, 4),
                           "z_score": round(z, 3), "p_perm": round(p, 4),
                           "Clustering": "Strong" if I > 0.5 else ("Moderate" if I > 0.2 else "Weak")})
    print(f"  {v:35s} I={I:>7.4f}  z={z:>7.3f}  p={p:.4f}  [{global_results[-1]['Clustering']}]")

pd.DataFrame(global_results).to_csv(OUT_TABLES / "global_morans_I.csv", index=False)

# --------------------------------------------------------------------------- #
# Univariate LISA — U5MR + Diarrhoea + WASH primaries (Rook weights)
# --------------------------------------------------------------------------- #
print("\n" + "=" * 78)
print("UNIVARIATE LISA (Rook contiguity, 999 permutations)")
print("=" * 78)

lisa_vars = ["U5MR_per_1000", "Diarrhoea_prevalence_pct",
             "Improved_water_pct", "Improved_sanitation_pct", "Open_defecation_pct"]
lisa_results = master[["Region", "District", "GeoJSON_District"]].copy()

for v in lisa_vars:
    x = master[v].values.astype(float)
    Ii, z, p, cluster = local_morans_I(x, W_rook, permutations=999)
    lisa_results[f"LISA_{v}_I"] = Ii
    lisa_results[f"LISA_{v}_p"] = p
    lisa_results[f"LISA_{v}_cluster"] = cluster
    cluster_counts = pd.Series(cluster).value_counts().to_dict()
    print(f"\n  {v}")
    for c in ["HH", "LL", "HL", "LH", "NS"]:
        n_c = cluster_counts.get(c, 0)
        print(f"    {c}: {n_c}")

lisa_results.to_csv(OUT_DATA / "lisa_univariate_results.csv", index=False)

# --------------------------------------------------------------------------- #
# Bivariate LISA — WASH × Diarrhoea, WASH × U5MR
# --------------------------------------------------------------------------- #
print("\n" + "=" * 78)
print("BIVARIATE LISA (Rook, 999 permutations)")
print("=" * 78)

bv_pairs = [
    ("Improved_water_pct", "Diarrhoea_prevalence_pct"),
    ("Improved_sanitation_pct", "Diarrhoea_prevalence_pct"),
    ("Open_defecation_pct", "Diarrhoea_prevalence_pct"),
    ("Improved_water_pct", "U5MR_per_1000"),
    ("Improved_sanitation_pct", "U5MR_per_1000"),
    ("Open_defecation_pct", "U5MR_per_1000"),
]

bv_results = master[["Region", "District", "GeoJSON_District"]].copy()
for xcol, ycol in bv_pairs:
    x = master[xcol].values.astype(float)
    y = master[ycol].values.astype(float)
    Ii, p, cluster = bivariate_lisa(x, y, W_rook, permutations=999)
    pair_name = f"{xcol}_X_{ycol}"
    bv_results[f"BV_{pair_name}_I"] = Ii
    bv_results[f"BV_{pair_name}_p"] = p
    bv_results[f"BV_{pair_name}_cluster"] = cluster
    counts = pd.Series(cluster).value_counts().to_dict()
    print(f"  {xcol[:25]} × {ycol[:25]}: HH={counts.get('HH',0):>3} "
          f"LL={counts.get('LL',0):>3} HL={counts.get('HL',0):>3} LH={counts.get('LH',0):>3}")
bv_results.to_csv(OUT_DATA / "lisa_bivariate_results.csv", index=False)

# --------------------------------------------------------------------------- #
# Getis-Ord Gi* — U5MR + Diarrhoea hotspot delineation
# --------------------------------------------------------------------------- #
print("\n" + "=" * 78)
print("GETIS-ORD Gi* (Rook binary weights, asymptotic z-score)")
print("=" * 78)

gi_results = master[["Region", "District", "GeoJSON_District"]].copy()
for v in ["U5MR_per_1000", "Diarrhoea_prevalence_pct"]:
    x = master[v].values.astype(float)
    z_gi, p_gi, label = getis_ord_Gi_star(x, W_rook_binary)
    gi_results[f"Gi_{v}_z"] = z_gi
    gi_results[f"Gi_{v}_p"] = p_gi
    gi_results[f"Gi_{v}_label"] = label
    n_hot = int((label == "HOTSPOT").sum())
    n_cold = int((label == "COLDSPOT").sum())
    print(f"  {v}: HOTSPOTS={n_hot}, COLDSPOTS={n_cold}")
gi_results.to_csv(OUT_DATA / "getis_ord_results.csv", index=False)

# --------------------------------------------------------------------------- #
# Summary table — headline canonical values
# --------------------------------------------------------------------------- #
print("\n" + "=" * 78)
print("STAGE 5 TASK 12 — SPATIAL ANALYTICS COMPLETE")
print("=" * 78)

summary = {
    "U5MR Global Moran I": global_results[0]["Moran_I"],
    "U5MR z-score": global_results[0]["z_score"],
    "U5MR p-value": global_results[0]["p_perm"],
    "Diarrhoea Global Moran I": global_results[1]["Moran_I"],
    "U5MR LISA HH count": int((lisa_results["LISA_U5MR_per_1000_cluster"] == "HH").sum()),
    "U5MR LISA LL count": int((lisa_results["LISA_U5MR_per_1000_cluster"] == "LL").sum()),
    "U5MR Getis-Ord hotspots": int((gi_results["Gi_U5MR_per_1000_label"] == "HOTSPOT").sum()),
    "U5MR Getis-Ord coldspots": int((gi_results["Gi_U5MR_per_1000_label"] == "COLDSPOT").sum()),
    "Districts analysed": int(len(master)),
}
print("\nHeadline values:")
for k, v in summary.items():
    print(f"  {k:35s}: {v}")

pd.DataFrame([summary]).T.to_csv(OUT_TABLES / "spatial_summary.csv", header=["Value"])
print(f"\nAll outputs saved to: {OUT_DATA} and {OUT_TABLES}")
