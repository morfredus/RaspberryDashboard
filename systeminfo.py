import socket
import shutil
import subprocess
from datetime import datetime

import psutil

from config import (
    PROJECT_DIR,
    SERVICE_LABELS,
    NETWORK_SERVICES,
    NETWORK_PROBE_GRACE,
    BEACON_APPS,
    GREEN, RED, ORANGE,
)

from beacon_listener import status as beacon_status

try:
    from reboot_alert import get_reboot_alert
except Exception:
    def get_reboot_alert():
        return {"active": False, "count": 0, "latest": None}


def _read_version():
    try:
        return (PROJECT_DIR / "VERSION").read_text().strip() or "dev"
    except Exception:
        return "dev"


VERSION = _read_version()


def _get_ip(interface: str):
    try:
        result = subprocess.check_output(
            ["ip", "-4", "addr", "show", interface],
            text=True
        )

        for line in result.splitlines():
            line = line.strip()
            if line.startswith("inet "):
                return line.split()[1].split("/")[0]

    except Exception:
        pass

    return None


def _cpu_temp():
    try:
        with open("/sys/class/thermal/thermal_zone0/temp") as f:
            return round(float(f.read()) / 1000, 1)
    except Exception:
        return None


def _uptime_seconds():
    """Uptime système en secondes. Fail-open (grand nombre) si illisible."""
    try:
        with open("/proc/uptime") as f:
            return float(f.readline().split()[0])
    except Exception:
        return float("inf")


def _uptime():
    try:
        with open("/proc/uptime") as f:
            seconds = float(f.readline().split()[0])

        days = int(seconds // 86400)
        hours = int((seconds % 86400) // 3600)
        minutes = int((seconds % 3600) // 60)

        if days:
            return f"{days}j {hours}h"

        return f"{hours}h {minutes}m"

    except Exception:
        return "?"
def _service_running(service: str):
    try:
        subprocess.check_output(
            ["systemctl", "is-active", "--quiet", service]
        )
        return True
    except subprocess.CalledProcessError:
        return False


def _network_service_online(config: dict):
    """Vrai si une connexion TCP aboutit (ex. serveur web de l'ESP32)."""
    try:
        with socket.create_connection(
            (config["host"], config["port"]),
            timeout=config.get("timeout", 1.0),
        ):
            return True
    except OSError:
        return False


def _service_state(name: str, network_ready: bool = True):
    """État d'un service : sonde réseau si déclaré, sinon systemd.

    La sonde réseau résout un nom mDNS (« .local »), ce qui émet des
    requêtes multicast sur wlan0. On ne sonde que lorsque le réseau est
    « prêt » : une IP est présente ET l'uptime dépasse le délai de grâce.
    Cela évite de perturber la connexion WiFi pendant qu'elle s'établit
    au démarrage (au prix d'une puce MeteoHub qui verdit avec un léger
    délai après le boot).
    """
    if name in NETWORK_SERVICES:
        if not network_ready:
            return False
        return _network_service_online(NETWORK_SERVICES[name])
    return _service_running(name)


def _beacon_color(online: bool, state):
    """Couleur de la pastille d'une application supervisee par heartbeat."""
    if not online:
        return RED
    if state == "warning":
        return ORANGE
    if state == "error":
        return RED
    return GREEN


def get_system_info():

    disk = shutil.disk_usage("/")

    # Résolues une seule fois : servent aussi de feu vert à la sonde réseau.
    # On ne sonde (mDNS) que si une IP est présente ET que le système est
    # démarré depuis assez longtemps pour ne pas gêner l'association WiFi.
    eth = _get_ip("eth0")
    wifi = _get_ip("wlan0")
    network_ready = bool(eth or wifi) and _uptime_seconds() >= NETWORK_PROBE_GRACE

    # Services affiches : d'abord les services systeme/reseau (systemd + sondes
    # ESP32), puis les applications de bureau vues par heartbeat morfBeacon.
    # Chaque entree porte deja son libelle et sa couleur de pastille -> l'affichage
    # n'a plus qu'a les disposer.
    services = []
    for key in SERVICE_LABELS:
        online = _service_state(key, network_ready)
        services.append({
            "label": SERVICE_LABELS[key],
            "color": GREEN if online else RED,
        })
    for app, label in BEACON_APPS.items():
        online, state = beacon_status(app)
        services.append({
            "label": label,
            "color": _beacon_color(online, state),
        })

    return {

        "hostname": socket.gethostname(),

        "version": VERSION,

        "time": datetime.now().strftime("%H:%M:%S"),

        "eth": eth,

        "wifi": wifi,

        "cpu": psutil.cpu_percent(),

        "cpu_cores": psutil.cpu_count() or 1,

        "load": psutil.getloadavg(),

        "temp": _cpu_temp(),

        "ram_percent": psutil.virtual_memory().percent,

        "swap_percent": psutil.swap_memory().percent,

        "disk_percent": round(disk.used / disk.total * 100, 1),

        "disk_used_gb": round(disk.used / (1024**3), 1),

        "disk_free_gb": round(disk.free / (1024**3), 1),

        "disk_total_gb": round(disk.total / (1024**3), 1),

        "uptime": _uptime(),

        "reboot_alert": get_reboot_alert(),

        "services": services,
    }


if __name__ == "__main__":

    from pprint import pprint

    pprint(get_system_info())
