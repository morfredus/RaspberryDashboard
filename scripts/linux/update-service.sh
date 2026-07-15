#!/usr/bin/env bash
#
# update-service.sh — Met à jour RaspberryDashboard installé en service.
#
# Récupère le code (git pull), recopie l'application dans le dossier fixe, puis
# redémarre le service. Sans compilation (Python). Complément de install-service.sh.
#
# Usage :
#   sudo ./scripts/linux/update-service.sh          # git pull + recopie + restart
#   sudo ./scripts/linux/update-service.sh --no-pull # recopie seulement

set -euo pipefail

SERVICE_NAME="morfdashboard"
UNIT_DEST="/etc/systemd/system/$SERVICE_NAME.service"
APP_DIR="${RD_APP_DIR:-/opt/morfdashboard}"

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
RUN_USER="${SUDO_USER:-$(logname 2>/dev/null || echo root)}"

if [[ "${EUID}" -ne 0 ]]; then
    echo "Ce script doit être lancé avec sudo :  sudo $0 $*" >&2
    exit 1
fi
if [[ ! -f "$UNIT_DEST" ]]; then
    echo "Service '$SERVICE_NAME' non installé. Lance d'abord :  sudo ./scripts/linux/install-service.sh" >&2
    exit 1
fi

# --- Récupérer le code (en tant que l'utilisateur) -----------------------
if [[ "${1:-}" != "--no-pull" ]]; then
    echo "git pull (utilisateur $RUN_USER)…"
    sudo -u "$RUN_USER" bash -c "cd '$REPO_ROOT' && git pull --ff-only"
fi

# --- Recopier l'application ----------------------------------------------
echo "Recopie vers $APP_DIR…"
if command -v rsync >/dev/null; then
    rsync -a --exclude='.git' --exclude='__pycache__' --exclude='*.pyc' \
             --exclude='*_preview.png' "$REPO_ROOT"/ "$APP_DIR"/
else
    cp -a "$REPO_ROOT"/. "$APP_DIR"/
fi
chown -R "$RUN_USER:$RUN_USER" "$APP_DIR"

# --- Redémarrer ----------------------------------------------------------
systemctl restart "$SERVICE_NAME"
sleep 1
echo "Mise à jour appliquée."
systemctl --no-pager --lines=0 status "$SERVICE_NAME" || true
