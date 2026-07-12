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
    "gatewaylab": "GatewayLab",
    "componenthub": "ComponentHub",
    "meteohub": "MeteoHub",
}

# Services surveillés par sonde réseau plutôt que par systemd.
# MeteoHub tourne sur un ESP32 : on ne peut pas l'interroger avec
# « systemctl », on teste donc l'accès à son serveur web.
NETWORK_SERVICES = {
    "gatewaylab": {
        "host": "gatewaylab.local",  # nom mDNS ou IP fixe de l'ESP32
        "port": 80,
        "timeout": 1.0,            # secondes ; borne le temps d'attente si hors ligne
    },
    "componenthub": {
        "host": "componenthub.local",  # nom mDNS ou IP fixe de l'ESP32
        "port": 80,
        "timeout": 1.0,            # secondes ; borne le temps d'attente si hors ligne
    },
    "meteohub": {
        "host": "meteohub.local",  # nom mDNS ou IP fixe de l'ESP32
        "port": 80,
        "timeout": 1.0,            # secondes ; borne le temps d'attente si hors ligne
    },
}

# Délai de grâce avant la première sonde réseau (secondes d'uptime système).
# La sonde résout un nom mDNS (requêtes multicast sur wlan0) : on attend que
# le WiFi soit associé et stabilisé pour ne pas perturber sa connexion au
# démarrage. La puce MeteoHub reste rouge tant que ce délai n'est pas écoulé.
NETWORK_PROBE_GRACE = 45