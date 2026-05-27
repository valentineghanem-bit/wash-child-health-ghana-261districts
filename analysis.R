# analysis.R — WASH Determinants of Child Health, Ghana 261 Districts
# Spatial regression (SLM/SEM) + mediation diagnostics
# Author: Valentine Golden Ghanem | ORCID: 0009-0002-8332-0220
# Usage:  Rscript analysis.R
#
# Primary outcomes: Diarrhoea_prevalence_pct · U5MR_per_1000 · IMR_per_1000 · Child_anaemia_any_pct
# WASH predictors:  Improved_water_pct · Improved_sanitation_pct · Open_defecation_pct · Water_treated_pct
# Spatial weights:  KNN-8 from district centroids (Latitude/Longitude in master CSV)
# Outputs written to outputs/data/

suppressPackageStartupMessages({
  library(spdep)
  library(spatialreg)
  library(dplyr)
  library(readr)
})
set.seed(42)

DATA_PATH <- "outputs/data/WASH_Ghana_District_Master.csv"
OUT_DIR   <- "outputs/data"

cat("── WASH Child Health Ghana 261 Districts — analysis.R ────────────────\n")
df <- read_csv(DATA_PATH, show_col_types = FALSE)
n  <- nrow(df)
cat(sprintf("Loaded: %d districts × %d variables\n", n, ncol(df)))

# ── Primary outcomes and WASH predictors ──────────────────────────────────────
OUTCOMES <- intersect(
  c("Diarrhoea_prevalence_pct", "U5MR_per_1000", "IMR_per_1000",
    "NMR_per_1000", "Child_anaemia_any_pct"),
  names(df)
)
WASH_VARS <- intersect(
  c("Improved_water_pct", "Improved_sanitation_pct",
    "Open_defecation_pct", "Water_treated_pct"),
  names(df)
)
COVARS <- intersect(
  c("Illiteracy_rate_pct", "Uninsurance_rate_pct",
    "Unemployment_rate_pct", "Incidence of Poverty", "Youth_dependency_ratio"),
  names(df)
)
cat(sprintf("Outcomes  : %s\n", paste(OUTCOMES, collapse = ", ")))
cat(sprintf("WASH vars : %s\n", paste(WASH_VARS, collapse = ", ")))
cat(sprintf("Covariates: %s\n", paste(COVARS, collapse = ", ")))

# ── 1. Spatial weights (KNN-8, district centroids) ────────────────────────────
cat("\n── Spatial weights (KNN-8) ───────────────────────────────────────────\n")
lat_col <- names(df)[grepl("^Latitude$|^lat$", names(df), ignore.case = TRUE)][1]
lon_col <- names(df)[grepl("^Longitude$|^lon$", names(df), ignore.case = TRUE)][1]

if (!is.na(lat_col) && !is.na(lon_col)) {
  coords <- cbind(df[[lon_col]], df[[lat_col]])
  cat(sprintf("  Coordinates from '%s', '%s'\n", lon_col, lat_col))
} else {
  coords <- cbind(seq_len(n), rep(0, n))
  message("  lat/lon not found — using index coordinates (approximate)")
}

knn8 <- knearneigh(coords, k = 8, longlat = TRUE)
W    <- nb2listw(knn2nb(knn8), style = "W")
cat(sprintf("  KNN-8 weights: %d districts\n", n))

# ── 2. Global Moran's I ───────────────────────────────────────────────────────
cat("\n── Global Moran's I ──────────────────────────────────────────────────\n")
moran_rows <- list()
for (v in OUTCOMES) {
  vals <- df[[v]]
  if (all(is.na(vals))) next
  mi <- tryCatch(
    moran.test(vals, W, randomisation = TRUE, na.action = na.exclude, zero.policy = TRUE),
    error = function(e) NULL
  )
  if (is.null(mi)) next
  cat(sprintf("  %-35s  I=%.4f  z=%6.3f  p=%.4f\n",
              v, mi$estimate[1], mi$statistic, mi$p.value))
  moran_rows[[v]] <- data.frame(
    outcome    = v,
    moran_I    = round(mi$estimate[1], 4),
    z_score    = round(mi$statistic, 3),
    p_value    = round(mi$p.value, 4),
    weight_type = "knn8"
  )
}
if (length(moran_rows) > 0) {
  write_csv(do.call(rbind, moran_rows),
            file.path(OUT_DIR, "r_moran_global.csv"))
  cat(sprintf("  → Saved: %s/r_moran_global.csv\n", OUT_DIR))
}

# ── 3. LISA (Local Moran's I, BH-FDR) ────────────────────────────────────────
cat("\n── LISA clusters (BH-FDR corrected) ─────────────────────────────────\n")
lisa_rows <- list()
for (v in OUTCOMES) {
  vals <- df[[v]]
  if (all(is.na(vals))) next
  lm_i <- tryCatch(
    localmoran(vals, W, na.action = na.exclude, zero.policy = TRUE),
    error = function(e) NULL
  )
  if (is.null(lm_i)) next

  p_raw <- lm_i[, 5]
  p_bh  <- p.adjust(p_raw, method = "BH")
  sig   <- p_bh < 0.05

  z_vals   <- scale(vals)[, 1]
  lag_z_sc <- scale(lag.listw(W, vals, zero.policy = TRUE))[, 1]

  quad <- rep("NS", n)
  quad[sig & z_vals > 0 & lag_z_sc > 0] <- "HH"
  quad[sig & z_vals < 0 & lag_z_sc < 0] <- "LL"
  quad[sig & z_vals > 0 & lag_z_sc < 0] <- "HL"
  quad[sig & z_vals < 0 & lag_z_sc > 0] <- "LH"

  cat(sprintf("  %-35s  HH=%d  LL=%d  HL=%d  LH=%d  NS=%d\n",
              v,
              sum(quad == "HH"), sum(quad == "LL"),
              sum(quad == "HL"), sum(quad == "LH"), sum(quad == "NS")))

  lisa_rows[[v]] <- data.frame(
    district     = seq_len(n),
    outcome      = v,
    local_I      = round(lm_i[, 1], 4),
    p_raw        = round(p_raw, 4),
    p_bh         = round(p_bh, 4),
    quadrant     = quad
  )
}
if (length(lisa_rows) > 0) {
  write_csv(do.call(rbind, lisa_rows),
            file.path(OUT_DIR, "r_lisa_clusters.csv"))
  cat(sprintf("  → Saved: %s/r_lisa_clusters.csv\n", OUT_DIR))
}

# ── 4. OLS → LM tests → SLM / SEM (mediation: WASH → diarrhoea) ─────────────
cat("\n── Spatial model selection (diarrhoea ~ WASH + covariates) ──────────\n")
primary <- if ("Diarrhoea_prevalence_pct" %in% OUTCOMES) "Diarrhoea_prevalence_pct" else OUTCOMES[1]
all_preds <- c(WASH_VARS, COVARS)
all_preds <- all_preds[all_preds %in% names(df)]

if (length(all_preds) > 0) {
  fml <- as.formula(paste(paste0("`", primary, "`"), "~",
                          paste(paste0("`", all_preds, "`"), collapse = " + ")))

  ols <- tryCatch(lm(fml, data = df), error = function(e) NULL)
  if (!is.null(ols)) {
    lm_tests <- tryCatch(
      lm.RStests(ols, W, test = "all", zero.policy = TRUE),
      error = function(e) NULL
    )
    cat(sprintf("  OLS R² = %.3f  AIC = %.2f\n", summary(ols)$r.squared, AIC(ols)))
    if (!is.null(lm_tests)) {
      cat("  LM diagnostics:\n")
      print(lm_tests)
    }

    slm <- tryCatch(lagsarlm(fml, data = df, listw = W, zero.policy = TRUE),
                    error = function(e) NULL)
    sem <- tryCatch(errorsarlm(fml, data = df, listw = W, zero.policy = TRUE),
                    error = function(e) NULL)

    if (!is.null(slm) && !is.null(sem)) {
      comp <- data.frame(
        model   = c("OLS", "SLM (spatial lag)", "SEM (spatial error)"),
        AIC     = round(c(AIC(ols), AIC(slm), AIC(sem)), 2),
        log_lik = round(c(as.numeric(logLik(ols)),
                          as.numeric(logLik(slm)),
                          as.numeric(logLik(sem))), 2)
      )
      cat("\n  Model comparison:\n")
      print(comp)
      write_csv(comp, file.path(OUT_DIR, "r_model_comparison.csv"))
      cat(sprintf("  → Saved: %s/r_model_comparison.csv\n", OUT_DIR))

      # Preferred model coefficients
      best_aic <- which.min(comp$AIC)
      best_mod <- list(ols, slm, sem)[[best_aic]]
      cat(sprintf("\n  Best model: %s (AIC=%.2f)\n",
                  comp$model[best_aic], comp$AIC[best_aic]))
      print(summary(best_mod))
    }
  }
}

# ── 5. WASH exposure summary (high vs low diarrhoea burden) ──────────────────
cat("\n── WASH access by diarrhoea tertile ─────────────────────────────────\n")
if ("Diarrhoea_prevalence_pct" %in% names(df)) {
  df$diarr_tertile <- cut(df$Diarrhoea_prevalence_pct,
                          breaks = quantile(df$Diarrhoea_prevalence_pct,
                                            probs = c(0, 1/3, 2/3, 1), na.rm = TRUE),
                          labels = c("Low", "Mid", "High"), include.lowest = TRUE)
  sum_cols <- intersect(c("Improved_water_pct", "Improved_sanitation_pct",
                           "Open_defecation_pct", "U5MR_per_1000"), names(df))
  if (length(sum_cols) > 0) {
    tbl <- df |>
      group_by(diarr_tertile) |>
      summarise(across(all_of(sum_cols), ~round(mean(.x, na.rm = TRUE), 2)),
                n = n(), .groups = "drop")
    print(tbl)
    write_csv(tbl, file.path(OUT_DIR, "r_wash_tertile_summary.csv"))
    cat(sprintf("  → Saved: %s/r_wash_tertile_summary.csv\n", OUT_DIR))
  }
}

cat("\n── analysis.R complete ───────────────────────────────────────────────\n")
cat(sprintf("All outputs written to %s/\n", OUT_DIR))
