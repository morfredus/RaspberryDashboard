from pathlib import Path

# ---------------------------------------------------------------------
# Chemins
# ---------------------------------------------------------------------

PROJECT_DIR = Path(__file__).resolve().parent
ASSETS_DIR = PROJECT_DIR / "assets"
LOGO_FILE = ASSETS_DIR / "logo.png"

# ---------------------------------------------------------------------
# Affichage
# ---------------------------------------------------------------------

WIDTH = 240
HEIGHT = 320

UPDATE_INTERVAL = 2

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
# Libellés d'affichage des services (clé systemd -> nom lisible)
# ---------------------------------------------------------------------

SERVICE_LABELS = {
    "dashboard": "Dashboard",
    "gatewaylab": "GatewayLab",
    "componenthub": "ComponentHub",
}