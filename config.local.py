# Configuration locale RaspberryDashboard.
#
# Copier vers /etc/morfdashboard/config.local.py puis adapter. Seules les
# constantes a surcharger sont necessaires ici ; config.py fournit les defauts.

# Exemple : choisir les canaux morfNotify utilises par les alertes persistantes.
# ALERT_NOTIFY_TARGETS = ["email"]
ALERT_NOTIFY_TARGETS = ["telegram"]
# ALERT_NOTIFY_TARGETS = ["email", "telegram"]

# Exemple : desactiver les notifications sans toucher au code installe.
# ALERT_NOTIFY_ENABLED = False

# Exemple : adapter les services surveilles.
SERVICE_LABELS = {
    "morfdashboard": "DashBoard", # service systemd local (systemctl is-active)
    "morfsync": "morfSync",       # service systemd local (Syncronisation de données)
    "morfsensor": "morfSensor",   # service systemd local (Ecoute de capteurs)
    "morfnotify": "morfNotify",   # service systemd local (Notifications)
    "morfanalytics": "morfAnalytics", # service systemd local (Analyse de données)
}
