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
CONFIG_DIR="${RD_CONFIG_DIR:-/etc/morfdashboard}"
CONFIG_FILE="$CONFIG_DIR/config.local.py"

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

SERVICE_WAS_ACTIVE=0
if systemctl is-active --quiet "$SERVICE_NAME"; then
    SERVICE_WAS_ACTIVE=1
fi

# --- Arreter avant toute mise a jour ------------------------------------
echo "Arrêt de $SERVICE_NAME avant mise à jour…"
systemctl stop "$SERVICE_NAME" 2>/dev/null || true

# --- Récupérer le code (en tant que l'utilisateur) -----------------------
if [[ "${1:-}" != "--no-pull" ]]; then
    echo "git pull (utilisateur $RUN_USER)…"
    sudo -u "$RUN_USER" bash -c "cd '$REPO_ROOT' && git pull --ff-only"
fi

# --- Recopier l'application ----------------------------------------------
echo "Recopie vers $APP_DIR…"
if command -v rsync >/dev/null; then
    rsync -a --exclude='.git' --exclude='__pycache__' --exclude='*.pyc' \
             --exclude='*_preview.png' --exclude='config.local.py' \
             "$REPO_ROOT"/ "$APP_DIR"/
else
    cp -a "$REPO_ROOT"/. "$APP_DIR"/
    rm -rf "$APP_DIR/.git" "$APP_DIR"/**/__pycache__ "$APP_DIR/config.local.py" 2>/dev/null || true
fi
chown -R "$RUN_USER:$RUN_USER" "$APP_DIR"

# --- Installer la config locale si elle n'existe pas encore --------------
mkdir -p "$CONFIG_DIR"
if [[ ! -f "$CONFIG_FILE" ]]; then
    install -m 0644 "$REPO_ROOT/config.local.example.py" "$CONFIG_FILE"
    echo "Config initiale copiée : $CONFIG_FILE (à adapter si besoin)."
else
    echo "Config existante conservée : $CONFIG_FILE"
fi

# --- Rafraichir l'unite systemd -----------------------------------------
sed -e "s/__RUN_USER__/$RUN_USER/g" -e "s#__APP_DIR__#$APP_DIR#g" \
    "$SCRIPT_DIR/morfdashboard.service" > "$UNIT_DEST"
chmod 0644 "$UNIT_DEST"
systemctl daemon-reload

# --- Redémarrer si le service tournait, sinon le laisser arrêté ----------
if [[ "$SERVICE_WAS_ACTIVE" -eq 1 ]]; then
    systemctl start "$SERVICE_NAME"
else
    echo "Service laissé arrêté (il ne tournait pas avant la mise à jour)."
fi
sleep 1
echo "Mise à jour appliquée."
systemctl --no-pager --lines=0 status "$SERVICE_NAME" || true
