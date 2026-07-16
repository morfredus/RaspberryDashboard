import os
import runpy
from pathlib import Path

# ---------------------------------------------------------------------
# Chemins
# ---------------------------------------------------------------------

PROJECT_DIR = Path(__file__).resolve().parent
ASSETS_DIR = PROJECT_DIR / "assets"
LOGO_FILE = ASSETS_DIR / "logo.png"
FONTS_DIR = ASSETS_DIR / "fonts"

# ---------------------------------------------------------------------
# Polices
# ---------------------------------------------------------------------
# DejaVu Sans Mono : police monospace nette, fournie dans le dépôt pour un
# rendu identique quel que soit l'OS. Le monospace garde les colonnes
# alignées (libellés/valeurs). Repli sur la police PIL par défaut si absente.

FONT_REGULAR = FONTS_DIR / "DejaVuSansMono.ttf"
FONT_BOLD = FONTS_DIR / "DejaVuSansMono-Bold.ttf"

FONT_SIZE = 14        # texte courant
TITLE_FONT_SIZE = 12  # bandeau supérieur (en gras)

# Rendu du texte — à juger sur l'écran réel.
FONT_ANTIALIAS = False  # False = bords nets sans lissage (parfois plus lisible en petit)
FONT_BODY_BOLD = True  # True = texte courant en gras (souvent plus lisible sur petit LCD)


def load_font(size=FONT_SIZE, bold=False):
    """Charge une police TrueType du dépôt ; repli sur la police par défaut."""
    from PIL import ImageFont
    path = FONT_BOLD if bold else FONT_REGULAR
    try:
        return ImageFont.truetype(str(path), size)
    except Exception:
        return ImageFont.load_default()

# ---------------------------------------------------------------------
# Affichage
# ---------------------------------------------------------------------

WIDTH = 240
HEIGHT = 320

UPDATE_INTERVAL = 2

# Pilote d'écran : "ili9341" ou "st7789".
DISPLAY_DRIVER = "st7789"

# Décalage de la dalle ST7789 (0 pour un panneau 240 × 320 plein cadre ;
# certaines dalles 240 × 240 demandent un offset, ex. Y = 80).
ST7789_X_OFFSET = 0
ST7789_Y_OFFSET = 0

# Orientation ST7789 (registre MADCTL 0x36). Les panneaux diffèrent : si
# l'image est tête-bêche et/ou en miroir, essayer une de ces valeurs.
#   0x00  portrait
#   0xC0  portrait à 180° (tête-bêche)   ← essai n°1 si tête-bêche
#   0x80  miroir vertical (MY)
#   0x40  miroir horizontal (MX)
# Ajouter 0x08 (bit BGR) si le rouge et le bleu sont intervertis, ex. 0xC8.
ST7789_MADCTL = 0x00

# Inversion d'affichage ST7789. True = INVON (0x21), False = INVOFF (0x20).
# Si les couleurs sortent « en négatif », basculer cette valeur.
ST7789_INVERT = True

# ---------------------------------------------------------------------
# GPIO
# ---------------------------------------------------------------------

DC_PIN = 24
RST_PIN = 25
# CS = CE0 (GPIO 8) : géré en MATÉRIEL par le driver SPI (spidev, device 0).
# Ne pas le piloter via RPi.GPIO sous Bookworm/lgpio -> « GPIO not allocated ».
CS_PIN = 8
LED_PIN = 18

SPI_BUS = 0
SPI_DEVICE = 0
SPI_SPEED = 40_000_000

# ---------------------------------------------------------------------
# Rétroéclairage (backlight sur LED_PIN)
# ---------------------------------------------------------------------
# Le rétroéclairage est piloté par LED_PIN. En PWM on peut faire varier sa
# luminosité (0 = éteint, 100 = plein) ; sinon c'est du tout-ou-rien. GPIO18
# supporte le PWM ; ici PWM logiciel (RPi.GPIO), suffisant pour deux niveaux.
# Passer à pigpio (PWM matériel) plus tard si un léger scintillement apparaît.
BACKLIGHT_PWM = True         # False = tout-ou-rien (>0 allumé, 0 éteint)
BACKLIGHT_FREQ_HZ = 1000     # fréquence du PWM logiciel
BACKLIGHT_FULL = 100         # niveau (%) en fonctionnement normal

# ---------------------------------------------------------------------
# Mise en veille (écran de veille anti-marquage / économie d'énergie)
# ---------------------------------------------------------------------
# Sans capteur physique, la présence est déduite de l'activité SSH (voir
# activity.py). Après SCREENSAVER_IDLE_SECONDS sans activité, l'écran bascule
# sur un cadre minimal mobile (heure, uptime, état global du système) et le
# rétroéclairage descend à SCREENSAVER_BACKLIGHT. La moindre activité SSH
# (frappe ou sortie d'une commande) réveille l'écran immédiatement.
SCREENSAVER_ENABLED = True       # False = dashboard permanent, jamais de veille
SCREENSAVER_IDLE_SECONDS = 60    # délai d'inactivité SSH avant la veille
SCREENSAVER_BACKLIGHT = 15       # niveau (%) du rétroéclairage en veille

# ---------------------------------------------------------------------
# Détection de présence par capteur (service morfSensor)
# ---------------------------------------------------------------------
# Source de réveil SUPPLÉMENTAIRE à l'activité SSH : un capteur de présence
# (radar LD2410C, etc.) géré par le service autonome « morfSensor ». Le dashboard
# ne pilote PAS le capteur : il interroge l'API HTTP de morfSensor à l'URL
# ci-dessous et lit le champ booléen « present ». Une présence détectée réveille
# l'écran comme le ferait une frappe SSH (voir presence_sensor.py + dashboard.py).
#
# morfSensor tourne en local sur le Raspberry (service systemd « morfsensor »).
# Si le service est absent ou injoignable, la détection est simplement ignorée :
# le comportement historique (réveil SSH seul) reste intact.
PRESENCE_SENSOR_ENABLED = True                              # False = ignorer le capteur
PRESENCE_SENSOR_URL = "http://127.0.0.1:8788/presence"     # endpoint /presence de morfSensor
PRESENCE_SENSOR_TIMEOUT = 0.5                              # s ; borne le temps d'attente HTTP

# ---------------------------------------------------------------------
# Alertes importantes via morfNotify
# ---------------------------------------------------------------------
# Le dashboard reste autonome : il POSTe vers morfNotify si disponible, avec
# timeout court et erreurs ignorees. morfNotify distribue ensuite vers la
# destination configuree (par defaut "email"). Une alerte n'est envoyee que si
# l'etat critique dure assez longtemps, ou si un service reste defaillant.

ALERT_NOTIFY_ENABLED = True
ALERT_NOTIFY_URL = "http://127.0.0.1:8789/notify"
ALERT_NOTIFY_TARGETS = ["email"]
ALERT_NOTIFY_TIMEOUT = 1.0

# Metriques critiques : attendre avant de prevenir pour eviter les pics brefs.
ALERT_MIN_DURATION_SECONDS = 5 * 60

# Services/applications hors ligne : alerte plus rapide, mais pas instantanee.
ALERT_SERVICE_MIN_DURATION_SECONDS = 2 * 60

# Rappel si le probleme persiste longtemps.
ALERT_REPEAT_COOLDOWN_SECONDS = 6 * 60 * 60

# Envoie un message de retour a la normale apres une alerte deja envoyee.
ALERT_RECOVERY_NOTIFY = True

# ---------------------------------------------------------------------
# Couleurs
# ---------------------------------------------------------------------

BLACK = "black"
WHITE = "white"
GRAY = "gray"
GREEN = "lightgreen"
RED = "red"
BLUE = "#0055A5"
ORANGE = "orange"
YELLOW = "yellow"
CYAN = "lightblue"

# ---------------------------------------------------------------------
# Seuils de santé (en %, sauf température en °C)
# ---------------------------------------------------------------------

CPU_WARNING = 70
CPU_CRITICAL = 90
CPU_ELEVATED = 50   # charge modérée (jaune) — pastille « charge CPU » de la veille

RAM_WARNING = 80
RAM_CRITICAL = 95

SWAP_WARNING = 20
SWAP_CRITICAL = 50

TEMP_WARNING = 65
TEMP_CRITICAL = 75

SSD_WARNING = 85
SSD_CRITICAL = 95

# Charge système, en % des cœurs (100 % = tous les cœurs pleinement occupés)
LOAD_WARNING = 100
LOAD_CRITICAL = 150

# ---------------------------------------------------------------------
# Alerte reboot non demandé
# ---------------------------------------------------------------------
# Le script de surveillance cree un dossier par reboot inattendu, par exemple :
# /home/morfredus/Logs/Boot_2026-07-12T15-19-07+02-00_pi4fred_d3ff81ab
# L'alerte ne tient compte que du dossier Boot_* correspondant au boot actuel.

REBOOT_ALERT_LOG_DIR = Path("/home/morfredus/Logs")
REBOOT_ALERT_PATTERNS = ("Boot_*",)
REBOOT_ALERT_BOOT_WINDOW_SECONDS = 10 * 60
REBOOT_ALERT_ACK_FILE = Path("/home/morfredus/Logs/.dashboard_reboot_ack")


def health_color(value, warning, critical):
    """Retourne la couleur de la pastille selon la valeur et ses seuils."""
    if value is None:
        return GRAY
    if value >= critical:
        return RED
    if value >= warning:
        return ORANGE
    return GREEN


# ---------------------------------------------------------------------
# Libellés d'affichage des services (clé -> nom lisible)
# ---------------------------------------------------------------------

SERVICE_LABELS = {
    "morfdashboard": "DashBoard",   # service systemd local (systemctl is-active)
    "morfsync": "morfSync",         # service systemd local (Synchro donnees)
    "morfsensor": "morfSensor",     # service systemd local (Ecoute capteurs)
    "morfnotify": "morfNotify",     # service systemd local (Notifications)
}

# Services surveillés par sonde réseau plutôt que par systemd.
# MeteoHub tourne sur un ESP32 : on ne peut pas l'interroger avec
# « systemctl », on teste donc l'accès à son serveur web.
NETWORK_SERVICES = {
#    "gatewaylab": {
#        "host": "gatewaylab.local",  # nom mDNS ou IP fixe de l'ESP32
#        "port": 80,
#        "timeout": 1.0,            # secondes ; borne le temps d'attente si hors ligne
#    },
#    "meteohub": {
#        "host": "meteohub.local",  # nom mDNS ou IP fixe de l'ESP32
#        "port": 80,
#        "timeout": 1.0,            # secondes ; borne le temps d'attente si hors ligne
#    },
}

# Délai de grâce avant la première sonde réseau (secondes d'uptime système).
# La sonde résout un nom mDNS (requêtes multicast sur wlan0) : on attend que
# le WiFi soit associé et stabilisé pour ne pas perturber sa connexion au
# démarrage. La puce MeteoHub reste rouge tant que ce délai n'est pas écoulé.
NETWORK_PROBE_GRACE = 45

# ---------------------------------------------------------------------
# Supervision des applications de bureau par heartbeat (morfBeacon)
# ---------------------------------------------------------------------
# Les applications de bureau (ComponentHub, SiteWatch, et les futurs outils)
# diffusent un petit datagramme UDP « je suis actif » en broadcast sur le LAN
# (protocole morfBeacon). Le dashboard se contente d'ECOUTER : aucune IP a
# connaitre, aucune sonde, decouverte automatique. Une application qui n'emet
# plus pendant BEACON_OFFLINE_AFTER secondes est consideree hors ligne.

# Port UDP commun a tout le parc (identique cote applications).
BEACON_PORT = 45454

# Delai sans heartbeat avant de declarer une application hors ligne (secondes).
BEACON_OFFLINE_AFTER = 60

# Applications a surveiller : cle = nom annonce dans le heartbeat (champ "app"),
# valeur = libelle affiche a l'ecran.
# POUR AJOUTER UN FUTUR PROJET : ajouter une ligne ici, rien d'autre a modifier.
# (Le libelle est tronque a l'affichage s'il est trop long -> le garder court.)
BEACON_APPS = {
    #"ComponentHub": "ComponentHub",
    #"SiteWatch":    "SiteWatch",
    # "GatewayLab": "GatewayLab",
    # "MonOutil":   "Mon outil",
}


def _load_local_config():
    """Charge des surcharges locales sans modifier le fichier versionne."""
    candidates = []
    env_path = os.environ.get("MORFDASHBOARD_CONFIG")
    if env_path:
        candidates.append(Path(env_path))
    candidates.append(Path("/etc/morfdashboard/config.local.py"))
    candidates.append(PROJECT_DIR / "config.local.py")

    for path in candidates:
        if not path.is_file():
            continue
        try:
            values = runpy.run_path(str(path))
        except Exception as exc:
            print(f"Configuration locale ignoree ({path}) : {exc}")
            return
        for key, value in values.items():
            if key.isupper():
                globals()[key] = value
        return


_load_local_config()
