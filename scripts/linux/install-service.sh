#!/usr/bin/env bash
#
# install-service.sh — Installe RaspberryDashboard en service systemd robuste.
#
# Copie l'application dans un dossier FIXE (par défaut /opt/morfdashboard),
# hors du clone git, puis installe/active le service « dashboard » pointant là.
# Ainsi, déplacer le dépôt (ou une synchro Syncthing) ne casse plus rien.
#
# Usage :
#   sudo ./scripts/linux/install-service.sh
#   sudo RD_APP_DIR=/opt/rdash ./scripts/linux/install-service.sh   # autre dossier
#   sudo ./scripts/linux/install-service.sh --uninstall

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

# --- Désinstallation ------------------------------------------------------
if [[ "${1:-}" == "--uninstall" ]]; then
    echo "Désinstallation de $SERVICE_NAME…"
    systemctl disable --now "$SERVICE_NAME" 2>/dev/null || true
    rm -f "$UNIT_DEST"
    systemctl daemon-reload
    echo "Service supprimé. (Application $APP_DIR conservée — la retirer : sudo rm -rf $APP_DIR)"
    exit 0
fi

echo "Utilisateur  : $RUN_USER"
echo "Source       : $REPO_ROOT"
echo "Installation : $APP_DIR"

# --- 1. Arrêter l'ancien lancement ---------------------------------------
systemctl stop "$SERVICE_NAME" 2>/dev/null || true

# --- 2. Copier l'application dans le dossier fixe -------------------------
mkdir -p "$APP_DIR"
if command -v rsync >/dev/null; then
    rsync -a --exclude='.git' --exclude='__pycache__' --exclude='*.pyc' \
             --exclude='*_preview.png' "$REPO_ROOT"/ "$APP_DIR"/
else
    cp -a "$REPO_ROOT"/. "$APP_DIR"/
    rm -rf "$APP_DIR/.git" "$APP_DIR"/**/__pycache__ 2>/dev/null || true
fi
chown -R "$RUN_USER:$RUN_USER" "$APP_DIR"
echo "Application copiée dans $APP_DIR"

# --- 3. Installer et démarrer le service ---------------------------------
sed -e "s/__RUN_USER__/$RUN_USER/g" -e "s#__APP_DIR__#$APP_DIR#g" \
    "$SCRIPT_DIR/morfdashboard.service" > "$UNIT_DEST"
chmod 0644 "$UNIT_DEST"
systemctl daemon-reload
systemctl enable --now "$SERVICE_NAME"
echo "Service '$SERVICE_NAME' installé (ExecStart -> $APP_DIR/dashboard.py) et démarré."

# --- 4. Détecter d'autres démarrages automatiques (à nettoyer à la main) --
echo
echo "Vérification d'anciens lancements résiduels…"
FOUND=0
if crontab -u "$RUN_USER" -l 2>/dev/null | grep -iqE "dashboard|RaspberryDashboard"; then
    echo "  ⚠ crontab de $RUN_USER contient une entrée dashboard — à retirer :  crontab -u $RUN_USER -e"; FOUND=1
fi
if [[ -f /etc/rc.local ]] && grep -iqE "dashboard|RaspberryDashboard" /etc/rc.local; then
    echo "  ⚠ /etc/rc.local référence dashboard — à retirer manuellement"; FOUND=1
fi
for f in "/home/$RUN_USER/.config/autostart/"*dashboard* "/home/$RUN_USER/.config/autostart/"*Dashboard*; do
    [[ -e "$f" ]] && { echo "  ⚠ autostart bureau : $f — à retirer"; FOUND=1; }
done
[[ "$FOUND" -eq 0 ]] && echo "  Aucun autre lancement automatique détecté. Le service 'morfdashboard' a remplacé l'ancien."

echo
sleep 1
systemctl --no-pager --lines=0 status "$SERVICE_NAME" || true
echo
echo "Journaux :  journalctl -u $SERVICE_NAME -f"
