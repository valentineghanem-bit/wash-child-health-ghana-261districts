#!/usr/bin/env bash
# /github-publish — WASH Ghana 261 Districts
# Pattern: EX-007 (/tmp clone-and-push) — git operations on mnt/ fail
#
# Usage:
#   1. Ensure ~/.claude/github.env contains:
#        export GITHUB_PAT=ghp_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
#   2. Run: bash push_to_github.sh
#
# Prerequisites confirmed:
#   ✓ QA_PASSED_2026-05-14.txt badge present
#   ✓ SYNC_PASS issued (42/48 = 87.5%, above 85% threshold)
#   ✓ Reconciliation Matrix 20/20 (100%)
#
# Repo URL: https://github.com/valentineghanem-bit/wash-child-health-ghana-261-districts
set -euo pipefail

SRC="/sessions/awesome-peaceful-davinci/mnt/Public Health & Epidemiology Research Skills/9. WASH Determinants of Child Health Ghana 261 Districts"
TMP="/tmp/wash_ghana_clean_repo"
REPO_SLUG="wash-child-health-ghana-261-districts"
GH_USER="valentineghanem-bit"

# Load PAT (do not log)
if [[ -f ~/.claude/github.env ]]; then
  source ~/.claude/github.env
elif [[ -z "${GITHUB_PAT:-}" ]]; then
  echo "ERROR: GITHUB_PAT not set. Add ghp_... to ~/.claude/github.env"
  exit 1
fi

echo "[1/6] Clone source to /tmp (EX-007 — /mnt/ git ops fail)"
rm -rf "$TMP"
mkdir -p "$TMP"
# Copy everything EXCEPT manuscript (.docx never pushed per Tenet 20 redaction rules)
rsync -a --exclude='*.docx' --exclude='.git' --exclude='*_draft.*' --exclude='*_identifiable.*' \
      --exclude='AIPOCH_Learning_Log*.md' \
      "$SRC/" "$TMP/"

echo "[2/6] Initialise git + LFS"
cd "$TMP"
git init -q
git lfs install 2>/dev/null || true
git lfs track "*.png" "*.geojson" 2>/dev/null || true
git add .gitattributes

echo "[3/6] Configure remote and identity"
git config user.email "valentineghanem@gmail.com"
git config user.name "Valentine Golden Ghanem"
git remote add origin "https://${GH_USER}:${GITHUB_PAT}@github.com/${GH_USER}/${REPO_SLUG}.git"

echo "[4/6] Stage and commit"
git add -A
git commit -q -m "Initial release v1.0.0 — WASH Ghana 261-district spatial ML mediation

QA_PASSED 2026-05-14. SYNC_PASS 87.5%.
Reconciliation Matrix 20/20 (100%). Reproducibility 88%.

- Master CSV: 261 × 44, data-source attribution
- Spatial: Moran's I 0.83, 25 LISA HH, 29 Getis-Ord hotspots
- Mediation: ~36% via diarrhoea (E-value 1.11)
- ML: Region-stratified LOROCV, RF+GB stacked (sklearn 1.7.2)
- 6 figures, manuscript+poster+dashboard+repo scaffold"

echo "[5/6] Push to main"
git branch -M main
git push -u origin main 2>&1 | grep -v "^remote: "

echo "[6/6] Confirm"
echo ""
echo "Published: https://github.com/${GH_USER}/${REPO_SLUG}"
echo "Latest commit: $(git rev-parse --short HEAD)"
echo "SYNC_REPORT: SYNC_REPORT_2026-05-14.md"
echo "QA badge: QA_PASSED_2026-05-14.txt"
