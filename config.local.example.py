# Configuration locale RaspberryDashboard.
#
# Copier vers /etc/morfdashboard/config.local.py puis adapter. Seules les
# constantes a surcharger sont necessaires ici ; config.py fournit les defauts.

# Canaux morfNotify utilises par les alertes persistantes.
# Choisir ["email"], ["telegram"] ou ["email", "telegram"] selon les
# destinations configurees dans morfNotify.
ALERT_NOTIFY_TARGETS = ["telegram"]

# Activer/desactiver les notifications sans toucher au code installe.
ALERT_NOTIFY_ENABLED = True
# ALERT_NOTIFY_ENABLED = False

# Delais de test courts. Remonter ces valeurs en production si besoin.
ALERT_MIN_DURATION_SECONDS = 5 * 60
ALERT_SERVICE_MIN_DURATION_SECONDS = 2 * 60
ALERT_REPEAT_COOLDOWN_SECONDS = 6 * 60 * 60

# Services surveilles.
SERVICE_LABELS = {
    "morfdashboard": "DashBoard",
    "morfsync": "morfSync",
    "morfsensor": "morfSensor",
    "morfnotify": "morfNotify",
    "morfanalytics": "morfAnalytics",
}
